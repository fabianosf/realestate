import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('real_estate_mining')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.task_routes = {
    'apps.scrapers.tasks.run_scraper_task': {'queue': 'scraping'},
    'apps.scrapers.tasks.process_pdf_task': {'queue': 'pdf_processing'},
}

app.conf.beat_schedule = {
    'schedule-active-scrapers': {
        'task': 'apps.scrapers.tasks.schedule_active_scrapers',
        'schedule': crontab(hour=6, minute=0),
    },
}
