from django.core.management.base import BaseCommand
from apps.properties.models import ScrapingSource

SOURCES = [
    # ── GovEase (Tax Lien — dados reais, sem proxy) ────────────────────────────
    {
        "name": "GovEase — Pike County AL (Tax Lien)",
        "url": "https://liveauctions.govease.com/al/alpike/1267/browse",
        "country": "US",
        "scraper_class": "apps.scrapers.sources.govease.GovEaseScraper",
        "is_active": True,
        "config": {"auction_path": "/al/alpike/1267/browse", "state": "AL", "county": "Pike County"},
    },

    # ── RealtyTrac Florida ─────────────────────────────────────────────────────
    {
        "name": "RealtyTrac — Florida (Geral)",
        "url": "https://www.realtytrac.com/foreclosures/fl/",
        "country": "US",
        "scraper_class": "apps.scrapers.sources.realtytrac.RealtyTracScraper",
        "is_active": True,
        "config": {"state": "fl", "county": "Florida", "path": "/foreclosures/fl/"},
    },
    {
        "name": "RealtyTrac — Miami-Dade FL",
        "url": "https://www.realtytrac.com/foreclosures/fl/miami-dade-county/",
        "country": "US",
        "scraper_class": "apps.scrapers.sources.realtytrac.RealtyTracScraper",
        "is_active": True,
        "config": {"state": "fl", "county": "Miami-Dade", "path": "/foreclosures/fl/miami-dade-county/"},
    },
    {
        "name": "RealtyTrac — Broward County FL (Fort Lauderdale)",
        "url": "https://www.realtytrac.com/foreclosures/fl/broward-county/",
        "country": "US",
        "scraper_class": "apps.scrapers.sources.realtytrac.RealtyTracScraper",
        "is_active": True,
        "config": {"state": "fl", "county": "Broward", "path": "/foreclosures/fl/broward-county/"},
    },
    {
        "name": "RealtyTrac — Hillsborough County FL (Tampa)",
        "url": "https://www.realtytrac.com/foreclosures/fl/hillsborough-county/",
        "country": "US",
        "scraper_class": "apps.scrapers.sources.realtytrac.RealtyTracScraper",
        "is_active": True,
        "config": {"state": "fl", "county": "Hillsborough", "path": "/foreclosures/fl/hillsborough-county/"},
    },
    {
        "name": "RealtyTrac — Orange County FL (Orlando)",
        "url": "https://www.realtytrac.com/foreclosures/fl/orange-county/",
        "country": "US",
        "scraper_class": "apps.scrapers.sources.realtytrac.RealtyTracScraper",
        "is_active": True,
        "config": {"state": "fl", "county": "Orange", "path": "/foreclosures/fl/orange-county/"},
    },
    {
        "name": "RealtyTrac — Palm Beach County FL",
        "url": "https://www.realtytrac.com/foreclosures/fl/palm-beach-county/",
        "country": "US",
        "scraper_class": "apps.scrapers.sources.realtytrac.RealtyTracScraper",
        "is_active": True,
        "config": {"state": "fl", "county": "Palm Beach", "path": "/foreclosures/fl/palm-beach-county/"},
    },
    {
        "name": "RealtyTrac — Pinellas County FL (St. Petersburg)",
        "url": "https://www.realtytrac.com/foreclosures/fl/pinellas-county/",
        "country": "US",
        "scraper_class": "apps.scrapers.sources.realtytrac.RealtyTracScraper",
        "is_active": True,
        "config": {"state": "fl", "county": "Pinellas", "path": "/foreclosures/fl/pinellas-county/"},
    },

    # ── RealtyTrac Texas ───────────────────────────────────────────────────────
    {
        "name": "RealtyTrac — Texas (Geral)",
        "url": "https://www.realtytrac.com/foreclosures/tx/",
        "country": "US",
        "scraper_class": "apps.scrapers.sources.realtytrac.RealtyTracScraper",
        "is_active": True,
        "config": {"state": "tx", "county": "Texas", "path": "/foreclosures/tx/"},
    },
    {
        "name": "RealtyTrac — Harris County TX (Houston)",
        "url": "https://www.realtytrac.com/foreclosures/tx/harris-county/",
        "country": "US",
        "scraper_class": "apps.scrapers.sources.realtytrac.RealtyTracScraper",
        "is_active": True,
        "config": {"state": "tx", "county": "Harris", "path": "/foreclosures/tx/harris-county/"},
    },
    {
        "name": "RealtyTrac — Dallas County TX",
        "url": "https://www.realtytrac.com/foreclosures/tx/dallas-county/",
        "country": "US",
        "scraper_class": "apps.scrapers.sources.realtytrac.RealtyTracScraper",
        "is_active": True,
        "config": {"state": "tx", "county": "Dallas", "path": "/foreclosures/tx/dallas-county/"},
    },
    {
        "name": "RealtyTrac — Tarrant County TX (Fort Worth)",
        "url": "https://www.realtytrac.com/foreclosures/tx/tarrant-county/",
        "country": "US",
        "scraper_class": "apps.scrapers.sources.realtytrac.RealtyTracScraper",
        "is_active": True,
        "config": {"state": "tx", "county": "Tarrant", "path": "/foreclosures/tx/tarrant-county/"},
    },

    # ── RealtyTrac Georgia ─────────────────────────────────────────────────────
    {
        "name": "RealtyTrac — Georgia (Geral)",
        "url": "https://www.realtytrac.com/foreclosures/ga/",
        "country": "US",
        "scraper_class": "apps.scrapers.sources.realtytrac.RealtyTracScraper",
        "is_active": True,
        "config": {"state": "ga", "county": "Georgia", "path": "/foreclosures/ga/"},
    },
    {
        "name": "RealtyTrac — Fulton County GA (Atlanta)",
        "url": "https://www.realtytrac.com/foreclosures/ga/fulton-county/",
        "country": "US",
        "scraper_class": "apps.scrapers.sources.realtytrac.RealtyTracScraper",
        "is_active": True,
        "config": {"state": "ga", "county": "Fulton", "path": "/foreclosures/ga/fulton-county/"},
    },
    {
        "name": "RealtyTrac — Gwinnett County GA",
        "url": "https://www.realtytrac.com/foreclosures/ga/gwinnett-county/",
        "country": "US",
        "scraper_class": "apps.scrapers.sources.realtytrac.RealtyTracScraper",
        "is_active": True,
        "config": {"state": "ga", "county": "Gwinnett", "path": "/foreclosures/ga/gwinnett-county/"},
    },

    # ── RealtyTrac Carolina do Norte ───────────────────────────────────────────
    {
        "name": "RealtyTrac — North Carolina (Geral)",
        "url": "https://www.realtytrac.com/foreclosures/nc/",
        "country": "US",
        "scraper_class": "apps.scrapers.sources.realtytrac.RealtyTracScraper",
        "is_active": True,
        "config": {"state": "nc", "county": "North Carolina", "path": "/foreclosures/nc/"},
    },
    {
        "name": "RealtyTrac — Mecklenburg County NC (Charlotte)",
        "url": "https://www.realtytrac.com/foreclosures/nc/mecklenburg-county/",
        "country": "US",
        "scraper_class": "apps.scrapers.sources.realtytrac.RealtyTracScraper",
        "is_active": True,
        "config": {"state": "nc", "county": "Mecklenburg", "path": "/foreclosures/nc/mecklenburg-county/"},
    },

    # ── RealtyTrac Arizona ─────────────────────────────────────────────────────
    {
        "name": "RealtyTrac — Arizona (Geral)",
        "url": "https://www.realtytrac.com/foreclosures/az/",
        "country": "US",
        "scraper_class": "apps.scrapers.sources.realtytrac.RealtyTracScraper",
        "is_active": True,
        "config": {"state": "az", "county": "Arizona", "path": "/foreclosures/az/"},
    },
    {
        "name": "RealtyTrac — Maricopa County AZ (Phoenix)",
        "url": "https://www.realtytrac.com/foreclosures/az/maricopa-county/",
        "country": "US",
        "scraper_class": "apps.scrapers.sources.realtytrac.RealtyTracScraper",
        "is_active": True,
        "config": {"state": "az", "county": "Maricopa", "path": "/foreclosures/az/maricopa-county/"},
    },

    # ── RealtyTrac Ohio ────────────────────────────────────────────────────────
    {
        "name": "RealtyTrac — Ohio (Geral)",
        "url": "https://www.realtytrac.com/foreclosures/oh/",
        "country": "US",
        "scraper_class": "apps.scrapers.sources.realtytrac.RealtyTracScraper",
        "is_active": True,
        "config": {"state": "oh", "county": "Ohio", "path": "/foreclosures/oh/"},
    },

    # ── RealtyTrac Illinois ────────────────────────────────────────────────────
    {
        "name": "RealtyTrac — Illinois (Geral)",
        "url": "https://www.realtytrac.com/foreclosures/il/",
        "country": "US",
        "scraper_class": "apps.scrapers.sources.realtytrac.RealtyTracScraper",
        "is_active": True,
        "config": {"state": "il", "county": "Illinois", "path": "/foreclosures/il/"},
    },
    {
        "name": "RealtyTrac — Cook County IL (Chicago)",
        "url": "https://www.realtytrac.com/foreclosures/il/cook-county/",
        "country": "US",
        "scraper_class": "apps.scrapers.sources.realtytrac.RealtyTracScraper",
        "is_active": True,
        "config": {"state": "il", "county": "Cook", "path": "/foreclosures/il/cook-county/"},
    },

    # ── RealtyTrac Michigan ────────────────────────────────────────────────────
    {
        "name": "RealtyTrac — Michigan (Geral)",
        "url": "https://www.realtytrac.com/foreclosures/mi/",
        "country": "US",
        "scraper_class": "apps.scrapers.sources.realtytrac.RealtyTracScraper",
        "is_active": True,
        "config": {"state": "mi", "county": "Michigan", "path": "/foreclosures/mi/"},
    },
]


class Command(BaseCommand):
    help = "Cadastra todas as fontes Nivel 1 no sistema"

    def handle(self, *args, **kwargs):
        created = updated = 0
        for data in SOURCES:
            config = data.pop("config")
            obj, is_new = ScrapingSource.objects.update_or_create(
                name=data["name"],
                defaults={**data, "config": config},
            )
            if is_new:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"Fontes cadastradas: {created} novas, {updated} atualizadas."
        ))
