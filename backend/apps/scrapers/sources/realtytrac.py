import asyncio
import json
import re
from typing import List, Optional

from playwright.async_api import async_playwright

from apps.scrapers.base import BaseScraper, RawPropertyData

BASE = "https://www.realtytrac.com"


class RealtyTracScraper(BaseScraper):
    source_name = "realtytrac"
    country = "US"
    base_url = BASE

    async def fetch_listings(self) -> List[RawPropertyData]:
        path = self.source.config.get("path", "/foreclosures/fl/")
        url = f"{BASE}{path}"
        results = []

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            ctx = await self.get_playwright_context(browser)
            try:
                page = await ctx.new_page()
                await page.goto(url, wait_until="networkidle", timeout=45000)
                await asyncio.sleep(4)

                content = await page.content()
                await page.close()

                properties = self._extract_next_data(content)
                self.logger.info(f"[realtytrac] {len(properties)} properties from {url}")

                for prop in properties:
                    raw = self._parse_property(prop)
                    if raw:
                        results.append(raw)

            finally:
                await browser.close()

        return results

    def _extract_next_data(self, html: str) -> list:
        m = re.search(
            r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL
        )
        if not m:
            return []
        try:
            data = json.loads(m.group(1))
            return data["props"]["pageProps"].get("properties", [])
        except (json.JSONDecodeError, KeyError):
            return []

    def _parse_property(self, p: dict) -> Optional[RawPropertyData]:
        prop_id = str(p.get("id", ""))
        if not prop_id:
            return None

        status_obj = p.get("status", {})
        if status_obj.get("bankOwned"):
            auction_type = "foreclosure"
        elif status_obj.get("preForeclosure"):
            auction_type = "foreclosure"
        else:
            auction_type = "foreclosure"

        beds = p.get("beds")
        baths = p.get("baths")
        sqft = p.get("sqft")
        area_sqft = float(sqft) if sqft else None

        price = p.get("recently_sold_price")
        market_value = float(price) if price else None

        status_date_ms = p.get("statusDate")
        auction_date = None
        if status_date_ms:
            from datetime import datetime, timezone as tz
            auction_date = datetime.fromtimestamp(status_date_ms / 1000, tz=tz.utc)

        source_url = f"{BASE}/fl/{p.get('county','').lower().replace(' ', '-')}-county/{p.get('zip', '')}/{prop_id}/"

        return RawPropertyData(
            external_id=prop_id,
            source_url=source_url,
            country="US",
            state_province=p.get("state", ""),
            city=p.get("city", ""),
            county=p.get("county", ""),
            zip_code=p.get("zip", ""),
            address=p.get("fullAddr") or p.get("addr", ""),
            property_type=p.get("type", ""),
            area_sqft=area_sqft,
            bedrooms=int(beds) if beds else None,
            bathrooms=float(baths) if baths else None,
            auction_type=auction_type,
            auction_date=auction_date,
            currency="USD",
            market_value=market_value,
            debt_type="mortgage",
        )

    async def fetch_detail(self, url: str) -> Optional[RawPropertyData]:
        return None
