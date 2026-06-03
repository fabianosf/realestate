import asyncio
import logging
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from django.utils import timezone
from playwright.async_api import Browser, BrowserContext, async_playwright

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.1; rv:109.0) Gecko/20100101 Firefox/121.0",
]


@dataclass
class RawPropertyData:
    external_id: str
    source_url: str
    country: str
    state_province: str
    city: str
    county: str = ""
    address: str = ""
    zip_code: str = ""
    property_type: str = ""
    area_sqm: Optional[float] = None
    area_sqft: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    auction_type: str = ""
    auction_date: Optional[datetime] = None
    auction_number: str = ""
    process_number: str = ""
    currency: str = "BRL"
    appraised_value: Optional[float] = None
    minimum_bid: Optional[float] = None
    market_value: Optional[float] = None
    debt_type: str = ""
    total_debt: Optional[float] = None
    debt_details: List[Dict] = field(default_factory=list)
    pdf_url: str = ""
    extra_data: Dict[str, Any] = field(default_factory=dict)


class BaseScraper(ABC):
    source_name: str = ""
    country: str = ""
    base_url: str = ""

    def __init__(self, source_model=None, proxy_list: List[str] = None):
        self.source = source_model
        self.proxy_list = proxy_list or []
        self.logger = logging.getLogger(f"scraper.{self.source_name}")

    def _random_user_agent(self) -> str:
        return random.choice(USER_AGENTS)

    def _random_proxy(self) -> Optional[Dict]:
        if not self.proxy_list:
            return None
        return {"server": random.choice(self.proxy_list)}

    async def get_playwright_context(self, browser: Browser) -> BrowserContext:
        ctx = await browser.new_context(
            user_agent=self._random_user_agent(),
            proxy=self._random_proxy(),
            locale="en-US",
            timezone_id="America/New_York",
            viewport={"width": 1366, "height": 768},
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Upgrade-Insecure-Requests": "1",
            },
        )
        try:
            from playwright_stealth import stealth_async
            page = await ctx.new_page()
            await stealth_async(page)
            await page.close()
        except ImportError:
            pass
        await ctx.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US','en']});
            window.chrome = {runtime: {}};
        """)
        return ctx

    def get_httpx_client(self) -> httpx.AsyncClient:
        proxy = self._random_proxy()
        return httpx.AsyncClient(
            headers={"User-Agent": self._random_user_agent()},
            proxies=proxy["server"] if proxy else None,
            timeout=30,
            follow_redirects=True,
        )

    @abstractmethod
    async def fetch_listings(self) -> List[RawPropertyData]:
        pass

    @abstractmethod
    async def fetch_detail(self, url: str) -> Optional[RawPropertyData]:
        pass

    def _float_to_cents(self, value: Optional[float]) -> Optional[int]:
        if value is None:
            return None
        return int(round(value * 100))

    def _to_property_dict(self, raw: RawPropertyData) -> Dict:
        return {
            'external_id': raw.external_id,
            'source': self.source,
            'source_url': raw.source_url,
            'country': raw.country,
            'state_province': raw.state_province,
            'city': raw.city,
            'county': raw.county,
            'address': raw.address,
            'zip_code': raw.zip_code,
            'property_type': raw.property_type,
            'area_sqm': raw.area_sqm,
            'area_sqft': raw.area_sqft,
            'bedrooms': raw.bedrooms,
            'bathrooms': raw.bathrooms,
            'auction_type': raw.auction_type,
            'auction_date': raw.auction_date,
            'auction_number': raw.auction_number,
            'process_number': raw.process_number,
            'currency': raw.currency,
            'appraised_value_cents': self._float_to_cents(raw.appraised_value),
            'minimum_bid_cents': self._float_to_cents(raw.minimum_bid),
            'market_value_cents': self._float_to_cents(raw.market_value),
            'debt_type': raw.debt_type,
            'total_debt_cents': self._float_to_cents(raw.total_debt),
            'debt_details': raw.debt_details,
            'pdf_url': raw.pdf_url,
            'extra_data': raw.extra_data,
            'scraped_at': timezone.now(),
        }

    async def run(self) -> Dict[str, int]:
        from asgiref.sync import sync_to_async
        from apps.properties.models import Property
        from django.utils import timezone  # noqa: F811

        stats = {'created': 0, 'updated': 0, 'errors': 0}
        listings = await self.fetch_listings()
        self.logger.info(f"[{self.source_name}] Fetched {len(listings)} listings")

        for raw in listings:
            try:
                prop_dict = self._to_property_dict(raw)

                def _save():
                    from django.db import transaction
                    with transaction.atomic():
                        return Property.objects.update_or_create(
                            source=self.source,
                            external_id=raw.external_id,
                            defaults=prop_dict,
                        )

                obj, created = await sync_to_async(_save)()
                stats['created' if created else 'updated'] += 1

                if raw.pdf_url and not obj.pdf_processed:
                    from apps.scrapers.tasks import process_pdf_task
                    process_pdf_task.delay(str(obj.id), raw.pdf_url)

            except Exception as e:
                self.logger.error(f"Persist error {raw.external_id}: {e}", exc_info=True)
                stats['errors'] += 1

        if self.source:
            def _update_source():
                self.source.last_scraped_at = timezone.now()
                self.source.save(update_fields=['last_scraped_at'])
            await sync_to_async(_update_source)()

        return stats
