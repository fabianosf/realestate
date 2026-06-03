import asyncio
import re
from datetime import datetime
from typing import List, Optional

from bs4 import BeautifulSoup

from ..base import BaseScraper, RawPropertyData


class BRLeiloeiroScraper(BaseScraper):
    """
    Scraper para leiloeiros judiciais brasileiros.
    Adapte os seletores CSS conforme o site-alvo.
    """
    source_name = "br_leiloeiro"
    country = "BR"
    base_url = "https://exemplo-leiloeiro.com.br"

    async def fetch_listings(self) -> List[RawPropertyData]:
        listings = []
        page = 1
        async with self.get_httpx_client() as client:
            while page <= 50:
                try:
                    r = await client.get(
                        f"{self.base_url}/leiloes/imoveis",
                        params={"pagina": page, "tipo": "judicial"},
                    )
                    r.raise_for_status()
                    soup = BeautifulSoup(r.text, 'html.parser')
                    cards = soup.select('.imovel-card')
                    if not cards:
                        break
                    for card in cards:
                        link = card.select_one('a')
                        if link and link.get('href'):
                            detail = await self.fetch_detail(self.base_url + link['href'])
                            if detail:
                                listings.append(detail)
                        await asyncio.sleep(2)
                    page += 1
                except Exception as e:
                    self.logger.error(f"Page {page}: {e}")
                    break
        return listings

    async def fetch_detail(self, url: str) -> Optional[RawPropertyData]:
        try:
            async with self.get_httpx_client() as client:
                r = await client.get(url)
                r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')

            def txt(sel):
                el = soup.select_one(sel)
                return el.get_text(strip=True) if el else ''

            localizacao = txt('.localizacao').split(',')
            city = localizacao[0].strip() if localizacao else ''
            state = localizacao[-1].strip()[-2:] if len(localizacao) > 1 else ''

            auction_date = None
            date_text = txt('.data-leilao')
            for fmt in ('%d/%m/%Y %H:%M', '%d/%m/%Y'):
                try:
                    auction_date = datetime.strptime(date_text, fmt)
                    break
                except ValueError:
                    continue

            pdf_link = soup.select_one('a[href$=".pdf"]')

            return RawPropertyData(
                external_id=url.rstrip('/').split('/')[-1],
                source_url=url,
                country='BR',
                state_province=state,
                city=city,
                address=txt('.endereco-imovel'),
                auction_type='judicial',
                auction_date=auction_date,
                currency='BRL',
                minimum_bid=self._parse_brl(txt('.lance-minimo')),
                appraised_value=self._parse_brl(txt('.valor-avaliacao')),
                total_debt=self._parse_brl(txt('.divida-total')),
                debt_type='iptu',
                pdf_url=self.base_url + pdf_link['href'] if pdf_link else '',
            )
        except Exception as e:
            self.logger.error(f"Detail failed {url}: {e}")
            return None

    def _parse_brl(self, text: str) -> Optional[float]:
        cleaned = re.sub(r'[^\d,]', '', text).replace(',', '.')
        try:
            return float(cleaned) if cleaned else None
        except ValueError:
            return None
