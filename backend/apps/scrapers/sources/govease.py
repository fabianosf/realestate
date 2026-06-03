import asyncio
import re
from typing import List, Optional

from bs4 import BeautifulSoup

from apps.scrapers.base import BaseScraper, RawPropertyData

BASE = "https://liveauctions.govease.com"


class GovEaseScraper(BaseScraper):
    source_name = "govease"
    country = "US"
    base_url = BASE

    async def fetch_listings(self) -> List[RawPropertyData]:
        auction_path = self.source.config.get("auction_path", "")
        state        = self.source.config.get("state", "AL")
        county       = self.source.config.get("county", "")

        if not auction_path:
            self.logger.error("govease: 'auction_path' missing in config")
            return []

        results = []
        page = 1

        async with self.get_httpx_client() as client:
            while True:
                url  = f"{BASE}{auction_path}?page={page}"
                resp = await client.get(url)
                if resp.status_code != 200:
                    break

                soup = BeautifulSoup(resp.text, "html.parser")
                rows = soup.select("table tbody tr")
                if not rows:
                    break

                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) < 7:
                        continue

                    # col 2 = Unique # (link)
                    link = cells[2].find("a")
                    if not link:
                        continue

                    parcel_id     = link.text.strip()
                    parcel_number = cells[3].text.strip()
                    detail_href   = link.get("href", "")
                    detail_url    = BASE + detail_href if detail_href.startswith("/") else detail_href

                    face_value = self._parse_usd(cells[5].text)   # col 5 = Face Value
                    address    = cells[6].text.strip().title()     # col 6 = Parcel Address (hidden)

                    detail = await self._get_detail(client, detail_url)
                    await asyncio.sleep(1.5)

                    results.append(RawPropertyData(
                        external_id     = parcel_id,
                        source_url      = detail_url,
                        country         = "US",
                        state_province  = state,
                        city            = county,
                        county          = county,
                        address         = address,
                        auction_type    = "tax_lien",
                        auction_number  = parcel_number,
                        currency        = "USD",
                        minimum_bid     = face_value,
                        appraised_value = detail.get("assessed_value"),
                        market_value    = detail.get("true_value"),
                        debt_type       = "property_tax",
                        total_debt      = face_value,
                        extra_data      = detail,
                    ))

                has_next = soup.find("a", string=lambda t: t and "next" in t.lower())
                if not has_next:
                    break
                page += 1
                await asyncio.sleep(2)

        return results

    async def _get_detail(self, client, url: str) -> dict:
        try:
            resp = await client.get(url)
            soup = BeautifulSoup(resp.text, "html.parser")
            text = soup.get_text(" ", strip=True)

            def extract(pattern):
                m = re.search(pattern, text, re.I)
                if m:
                    return self._parse_usd(m.group(1))
                return None

            return {
                "assessed_value": extract(r"Assessed Value[:\s]+\$?([\d,\.]+)"),
                "true_value":     extract(r"(?:Total )?True Value[:\s]+\$?([\d,\.]+)"),
                "land_value":     extract(r"Land Value[:\s]+\$?([\d,\.]+)"),
                "building_value": extract(r"Building Value[:\s]+\$?([\d,\.]+)"),
            }
        except Exception as e:
            self.logger.warning(f"Detail fetch failed {url}: {e}")
            return {}

    async def fetch_detail(self, url: str) -> Optional[RawPropertyData]:
        return None

    @staticmethod
    def _parse_usd(text: str) -> Optional[float]:
        if not text:
            return None
        cleaned = re.sub(r"[^\d.]", "", str(text).replace(",", ""))
        try:
            return float(cleaned) if cleaned else None
        except ValueError:
            return None
