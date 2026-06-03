from django.contrib import admin
from .models import Property, ScrapingSource


@admin.register(ScrapingSource)
class ScrapingSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'owner', 'is_active', 'last_scraped_at', 'scraper_class']
    list_filter = ['country', 'is_active', 'owner']
    search_fields = ['name', 'url']
    raw_id_fields = ['owner']


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['address', 'city', 'state_province', 'country', 'auction_type',
                    'minimum_bid_cents', 'estimated_profit_pct', 'status', 'pdf_processed']
    list_filter = ['country', 'auction_type', 'debt_type', 'status', 'pdf_processed']
    search_fields = ['address', 'city', 'external_id', 'process_number']
    readonly_fields = ['id', 'estimated_profit_pct', 'created_at', 'updated_at']
    ordering = ['-created_at']
