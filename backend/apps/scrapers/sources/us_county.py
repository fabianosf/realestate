import asyncio
import re
from typing import List, Optional

from playwright.async_api import async_playwright

from ..base import BaseScraper, RawPropertyData


class USCountyScraper(BaseScraper):
    """
    Scraper para portais de Tax Lien/Tax Deed de counties americanos.
    Usa Playwright para sites com JavaScript pesado (portais governamentais).
    """
    source_name = "us_county"
    country = "US"
    base_url = "https://county-example.gov"

    async def fetch_listings(self) -> List[RawPropertyData]:
        listings = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await self.get_playwright_context(browser)
            page = await context.new_page()
            try:
                await page.goto(f"{self.base_url}/tax-lien-auction", wait_until='networkidle')
                await page.wait_for_selector('.property-row', timeout=15000)

                while True:
                    rows = await page.query_selector_all('.property-row')
                    for row in rows:
                        href = await row.get_attribute('data-detail-url')
                        if href:
                            detail = await self._scrape_detail(context, href)
                            if detail:
                                listings.append(detail)
                            await asyncio.sleep(1.5)

                    nxt = await page.query_selector('.pagination-next:not([disabled])')
                    if not nxt:
                        break
                    await nxt.click()
                    await page.wait_for_load_state('networkidle')
            finally:
                await browser.close()
        return listings

    async def fetch_detail(self, url: str) -> Optional[RawPropertyData]:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            ctx = await self.get_playwright_context(browser)
            try:
                return await self._scrape_detail(ctx, url)
            finally:
                await browser.close()

    async def _scrape_detail(self, context, url: str) -> Optional[RawPropertyData]:
        page = await context.new_page()
        try:
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)

            async def txt(sel):
                el = await page.query_selector(sel)
                return (await el.inner_text()).strip() if el else ''

            city_state = await txt('.city-state')
            city, state = '', ''
            if ', ' in city_state:
                city, rest = city_state.split(', ', 1)
                state = rest[:2]

            zip_m = re.search(r'\d{5}', city_state)
            pdf_el = await page.query_selector('a[href$=".pdf"]')
            pdf_href = await page.eval_on_selector('a[href$=".pdf"]', 'el => el.href') if pdf_el else ''

            return RawPropertyData(
                external_id=await txt('.parcel-id') or url.split('=')[-1],
                source_url=url,
                country='US',
                state_province=state,
                city=city,
                county=self.source.config.get('county', '') if self.source else '',
                address=await txt('.property-address'),
                zip_code=zip_m.group(0) if zip_m else '',
                auction_type='tax_lien',
                currency='USD',
                minimum_bid=self._parse_usd(await txt('.minimum-bid')),
                appraised_value=self._parse_usd(await txt('.assessed-value')),
                total_debt=self._parse_usd(await txt('.total-taxes-due')),
                debt_type='property_tax',
                pdf_url=pdf_href,
            )
        except Exception as e:
            self.logger.error(f"Detail failed {url}: {e}")
            return None
        finally:
            await page.close()

    def _parse_usd(self, text: str) -> Optional[float]:
        cleaned = re.sub(r'[^\d.]', '', text)
        try:
            return float(cleaned) if cleaned else None
        except ValueError:
            return None
