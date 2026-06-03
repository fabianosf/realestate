import logging
from pathlib import Path

from celery import shared_task
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, queue='scraping')
def run_scraper_task(self, source_id: int):
    import asyncio
    import importlib
    from apps.properties.models import ScrapingSource

    try:
        source = ScrapingSource.objects.get(id=source_id, is_active=True)
        module_path, class_name = source.scraper_class.rsplit('.', 1)
        cls = getattr(importlib.import_module(module_path), class_name)
        scraper = cls(source_model=source, proxy_list=settings.PROXY_LIST)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        stats = loop.run_until_complete(scraper.run())
        loop.close()
        logger.info(f"[{source.name}] done: {stats}")
        return stats
    except Exception as exc:
        logger.error(f"Scraper failed source_id={source_id}: {exc}")
        raise self.retry(exc=exc, countdown=300)


@shared_task(bind=True, max_retries=2, queue='pdf_processing')
def process_pdf_task(self, property_id: str, pdf_url: str):
    from apps.properties.models import Property
    from apps.pdf_processor.extractor import PDFExtractor

    try:
        prop = Property.objects.get(id=property_id)
        pdf_dir = Path(settings.MEDIA_ROOT) / 'pdfs' / property_id[:2]
        pdf_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = pdf_dir / f"{property_id}.pdf"

        extractor = PDFExtractor()
        if not extractor.download_pdf(pdf_url, pdf_path):
            raise Exception(f"Download failed: {pdf_url}")

        result = extractor.process(pdf_path, currency=prop.currency)

        relative_path = f"pdfs/{property_id[:2]}/{property_id}.pdf"
        prop.pdf_file = relative_path
        prop.pdf_extracted_text = result['raw_text']
        prop.pdf_processed = True
        extra = prop.extra_data or {}
        extra['pdf_extraction'] = {
            'language': result['language'],
            'key_values': result['key_values'],
            'debt_mentions_count': len(result['debt_mentions']),
        }
        prop.extra_data = extra

        kv = result['key_values']
        if not prop.minimum_bid_cents:
            bid_key = 'lance_minimo' if result['language'] == 'pt' else 'minimum_bid'
            if bid_key in kv:
                prop.minimum_bid_cents = extractor.parse_to_cents(kv[bid_key], prop.currency)

        prop.save()
        return {'status': 'success', 'language': result['language'], 'keys': list(kv.keys())}

    except Exception as exc:
        logger.error(f"PDF processing failed property_id={property_id}: {exc}")
        raise self.retry(exc=exc, countdown=120)


@shared_task(queue='scraping')
def schedule_active_scrapers():
    from apps.properties.models import ScrapingSource
    sources = ScrapingSource.objects.filter(is_active=True)
    for source in sources:
        run_scraper_task.delay(source.id)
    return f"Scheduled {sources.count()} scrapers"
