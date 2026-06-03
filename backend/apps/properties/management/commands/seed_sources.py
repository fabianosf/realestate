from django.core.management.base import BaseCommand
from apps.properties.models import ScrapingSource

SOURCES = [
    {
        "name": "GovEase — Pike County AL (Tax Lien)",
        "url": "https://liveauctions.govease.com/al/alpike/1267/browse",
        "country": "US",
        "scraper_class": "apps.scrapers.sources.govease.GovEaseScraper",
        "is_active": True,
        "config": {
            "auction_path": "/al/alpike/1267/browse",
            "state": "AL",
            "county": "Pike County",
        },
    },
    {
        "name": "RealtyTrac — Florida Foreclosures",
        "url": "https://www.realtytrac.com/foreclosures/fl/",
        "country": "US",
        "scraper_class": "apps.scrapers.sources.realtytrac.RealtyTracScraper",
        "is_active": True,
        "config": {
            "state": "fl",
            "county": "Florida",
            "path": "/foreclosures/fl/",
        },
    },
    {
        "name": "RealtyTrac — Miami-Dade FL",
        "url": "https://www.realtytrac.com/foreclosures/fl/miami-dade-county/",
        "country": "US",
        "scraper_class": "apps.scrapers.sources.realtytrac.RealtyTracScraper",
        "is_active": True,
        "config": {
            "state": "fl",
            "county": "Miami-Dade",
            "path": "/foreclosures/fl/miami-dade-county/",
        },
    },
    {
        "name": "RealtyTrac — Broward County FL",
        "url": "https://www.realtytrac.com/foreclosures/fl/broward-county/",
        "country": "US",
        "scraper_class": "apps.scrapers.sources.realtytrac.RealtyTracScraper",
        "is_active": True,
        "config": {
            "state": "fl",
            "county": "Broward",
            "path": "/foreclosures/fl/broward-county/",
        },
    },
    {
        "name": "RealtyTrac — Hillsborough County FL (Tampa)",
        "url": "https://www.realtytrac.com/foreclosures/fl/hillsborough-county/",
        "country": "US",
        "scraper_class": "apps.scrapers.sources.realtytrac.RealtyTracScraper",
        "is_active": True,
        "config": {
            "state": "fl",
            "county": "Hillsborough",
            "path": "/foreclosures/fl/hillsborough-county/",
        },
    },
    {
        "name": "RealtyTrac — Orange County FL (Orlando)",
        "url": "https://www.realtytrac.com/foreclosures/fl/orange-county/",
        "country": "US",
        "scraper_class": "apps.scrapers.sources.realtytrac.RealtyTracScraper",
        "is_active": True,
        "config": {
            "state": "fl",
            "county": "Orange",
            "path": "/foreclosures/fl/orange-county/",
        },
    },
]


class Command(BaseCommand):
    help = "Cadastra todas as fontes Nível 1 no sistema"

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
