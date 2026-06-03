import uuid
from django.conf import settings
from django.db import models


class Country(models.TextChoices):
    BRAZIL = 'BR', 'Brasil'
    USA = 'US', 'Estados Unidos'


class AuctionType(models.TextChoices):
    JUDICIAL = 'judicial', 'Judicial'
    EXTRAJUDICIAL = 'extrajudicial', 'Extrajudicial'
    FORECLOSURE = 'foreclosure', 'Foreclosure'
    TAX_LIEN = 'tax_lien', 'Tax Lien'
    TAX_DEED = 'tax_deed', 'Tax Deed'


class DebtType(models.TextChoices):
    IPTU = 'iptu', 'IPTU'
    CONDOMINIUM = 'condominium', 'Condomínio'
    MORTGAGE = 'mortgage', 'Hipoteca/Financiamento'
    PROPERTY_TAX = 'property_tax', 'Property Tax'
    HOA = 'hoa', 'HOA'
    OTHER = 'other', 'Outro'


class PropertyStatus(models.TextChoices):
    DISCOVERED = 'discovered', 'Descoberto'
    ANALYZING = 'analyzing', 'Em Análise'
    OPPORTUNITY = 'opportunity', 'Oportunidade'
    DISCARDED = 'discarded', 'Descartado'
    ACQUIRED = 'acquired', 'Adquirido'


class ScrapingSource(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField()
    country = models.CharField(max_length=2, choices=Country.choices)
    scraper_class = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    last_scraped_at = models.DateTimeField(null=True, blank=True)
    schedule_cron = models.CharField(max_length=100, default='0 6 * * *')
    config = models.JSONField(default=dict, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='scraping_sources',
        help_text='Deixe vazio para fonte compartilhada (visível a todos)',
    )

    class Meta:
        db_table = 'scraping_sources'

    def __str__(self):
        return f"{self.name} ({self.country})"


class Property(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    source = models.ForeignKey(ScrapingSource, on_delete=models.SET_NULL, null=True)
    external_id = models.CharField(max_length=255, blank=True)
    source_url = models.URLField(max_length=2000, blank=True)

    country = models.CharField(max_length=2, choices=Country.choices)
    state_province = models.CharField(max_length=100)
    city = models.CharField(max_length=255)
    county = models.CharField(max_length=255, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    property_type = models.CharField(max_length=100, blank=True)
    area_sqm = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    area_sqft = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    bedrooms = models.PositiveSmallIntegerField(null=True, blank=True)
    bathrooms = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)

    auction_type = models.CharField(max_length=50, choices=AuctionType.choices)
    auction_date = models.DateTimeField(null=True, blank=True)
    auction_number = models.CharField(max_length=255, blank=True)
    process_number = models.CharField(max_length=255, blank=True)

    currency = models.CharField(max_length=3, default='BRL')
    appraised_value_cents = models.BigIntegerField(null=True, blank=True)
    minimum_bid_cents = models.BigIntegerField(null=True, blank=True)
    market_value_cents = models.BigIntegerField(null=True, blank=True)

    debt_type = models.CharField(max_length=50, choices=DebtType.choices, blank=True)
    total_debt_cents = models.BigIntegerField(null=True, blank=True)
    debt_details = models.JSONField(default=list, blank=True)

    status = models.CharField(
        max_length=50, choices=PropertyStatus.choices, default=PropertyStatus.DISCOVERED
    )
    estimated_profit_pct = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    roi_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)

    extra_data = models.JSONField(default=dict, blank=True)

    pdf_url = models.URLField(max_length=2000, blank=True)
    pdf_file = models.FileField(upload_to='pdfs/%Y/%m/', blank=True)
    pdf_extracted_text = models.TextField(blank=True)
    pdf_processed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    scraped_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'properties'
        unique_together = [('source', 'external_id')]
        indexes = [
            models.Index(fields=['country', 'state_province', 'city']),
            models.Index(fields=['auction_type', 'auction_date']),
            models.Index(fields=['status', 'roi_score']),
            models.Index(fields=['currency', 'minimum_bid_cents']),
        ]

    def _calculate_roi(self):
        if not self.market_value_cents or not self.total_debt_cents or self.total_debt_cents <= 0:
            return None
        return ((self.market_value_cents - self.total_debt_cents) / self.total_debt_cents) * 100

    def save(self, *args, **kwargs):
        self.estimated_profit_pct = self._calculate_roi()
        if (
            self.estimated_profit_pct is not None
            and self.estimated_profit_pct >= 100
            and self.status == PropertyStatus.DISCOVERED
        ):
            self.status = PropertyStatus.OPPORTUNITY
        # Garante que campos computados sejam incluídos mesmo quando update_fields é passado
        update_fields = kwargs.get('update_fields')
        if update_fields is not None:
            kwargs['update_fields'] = set(update_fields) | {'estimated_profit_pct', 'status'}
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.address or self.external_id} ({self.country})"
