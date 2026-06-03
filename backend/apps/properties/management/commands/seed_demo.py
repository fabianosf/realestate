from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.properties.models import Property, ScrapingSource
import uuid


DEMO = [
    {
        'country': 'US', 'state_province': 'FL', 'city': 'Miami',
        'county': 'Miami-Dade', 'address': '1234 Brickell Ave, Miami, FL 33131',
        'property_type': 'Residential', 'auction_type': 'tax_lien',
        'auction_date': timezone.now().replace(hour=10, minute=0) + timezone.timedelta(days=12),
        'currency': 'USD',
        'appraised_value_cents': 38000000,
        'minimum_bid_cents':     9500000,
        'market_value_cents':    35000000,
        'debt_type': 'property_tax',
        'total_debt_cents':      4200000,
        'debt_details': [{'type': 'Property Tax 2022', 'amount': 22000}, {'type': 'Property Tax 2023', 'amount': 20000}],
        'status': 'discovered',
        'pdf_url': 'https://www.w3.org/WAI/StructureNavigation/Demo/PDF/mobileOutage.pdf',
        'source_url': 'https://www.bid4assets.com/demo1',
    },
    {
        'country': 'US', 'state_province': 'FL', 'city': 'Orlando',
        'county': 'Orange', 'address': '890 International Dr, Orlando, FL 32819',
        'property_type': 'Commercial', 'auction_type': 'tax_deed',
        'auction_date': timezone.now().replace(hour=9, minute=0) + timezone.timedelta(days=5),
        'currency': 'USD',
        'appraised_value_cents': 52000000,
        'minimum_bid_cents':     18000000,
        'market_value_cents':    48000000,
        'debt_type': 'property_tax',
        'total_debt_cents':      8700000,
        'debt_details': [{'type': 'Property Tax 2021', 'amount': 31000}, {'type': 'HOA', 'amount': 56000}],
        'status': 'discovered',
        'pdf_url': 'https://www.w3.org/WAI/StructureNavigation/Demo/PDF/mobileOutage.pdf',
        'source_url': 'https://www.bid4assets.com/demo2',
    },
    {
        'country': 'US', 'state_province': 'TX', 'city': 'Houston',
        'county': 'Harris', 'address': '4500 Main St, Houston, TX 77002',
        'property_type': 'Residential', 'auction_type': 'foreclosure',
        'auction_date': timezone.now().replace(hour=11, minute=0) + timezone.timedelta(days=20),
        'currency': 'USD',
        'appraised_value_cents': 29000000,
        'minimum_bid_cents':     11000000,
        'market_value_cents':    27000000,
        'debt_type': 'mortgage',
        'total_debt_cents':      6500000,
        'debt_details': [{'type': 'Mortgage default', 'amount': 65000}],
        'status': 'discovered',
        'pdf_url': 'https://www.w3.org/WAI/StructureNavigation/Demo/PDF/mobileOutage.pdf',
        'source_url': 'https://www.bid4assets.com/demo3',
    },
    {
        'country': 'US', 'state_province': 'FL', 'city': 'Tampa',
        'county': 'Hillsborough', 'address': '220 Bayshore Blvd, Tampa, FL 33606',
        'property_type': 'Residential', 'auction_type': 'tax_lien',
        'auction_date': timezone.now().replace(hour=14, minute=0) + timezone.timedelta(days=8),
        'currency': 'USD',
        'appraised_value_cents': 44000000,
        'minimum_bid_cents':     7800000,
        'market_value_cents':    41000000,
        'debt_type': 'property_tax',
        'total_debt_cents':      3100000,
        'debt_details': [{'type': 'Property Tax 2022', 'amount': 15500}, {'type': 'Property Tax 2023', 'amount': 15500}],
        'status': 'opportunity',
        'source_url': 'https://www.bid4assets.com/demo4',
    },
    {
        'country': 'US', 'state_province': 'GA', 'city': 'Atlanta',
        'county': 'Fulton', 'address': '750 Peachtree St NE, Atlanta, GA 30308',
        'property_type': 'Residential', 'auction_type': 'tax_deed',
        'auction_date': timezone.now().replace(hour=10, minute=0) + timezone.timedelta(days=30),
        'currency': 'USD',
        'appraised_value_cents': 19500000,
        'minimum_bid_cents':     5200000,
        'market_value_cents':    18000000,
        'debt_type': 'property_tax',
        'total_debt_cents':      2800000,
        'debt_details': [{'type': 'Property Tax 2023', 'amount': 28000}],
        'status': 'analyzing',
        'source_url': 'https://www.bid4assets.com/demo5',
    },
    {
        'country': 'BR', 'state_province': 'SP', 'city': 'São Paulo',
        'county': '', 'address': 'Rua Augusta, 1200, Consolação, São Paulo - SP',
        'property_type': 'Apartamento', 'auction_type': 'judicial',
        'auction_date': timezone.now().replace(hour=10, minute=0) + timezone.timedelta(days=15),
        'currency': 'BRL',
        'appraised_value_cents': 85000000,
        'minimum_bid_cents':     56700000,
        'market_value_cents':    82000000,
        'debt_type': 'iptu',
        'total_debt_cents':      12400000,
        'debt_details': [{'type': 'IPTU atrasado', 'amount': 124000}],
        'status': 'discovered',
        'source_url': 'https://leilaovip.com.br/demo1',
    },
    {
        'country': 'BR', 'state_province': 'RJ', 'city': 'Rio de Janeiro',
        'county': '', 'address': 'Av. Atlântica, 3880, Copacabana, Rio de Janeiro - RJ',
        'property_type': 'Apartamento', 'auction_type': 'extrajudicial',
        'auction_date': timezone.now().replace(hour=14, minute=0) + timezone.timedelta(days=7),
        'currency': 'BRL',
        'appraised_value_cents': 149000000,
        'minimum_bid_cents':     99300000,
        'market_value_cents':    142000000,
        'debt_type': 'mortgage',
        'total_debt_cents':      31000000,
        'debt_details': [{'type': 'Financiamento', 'amount': 310000}],
        'status': 'opportunity',
        'source_url': 'https://leilaovip.com.br/demo2',
    },
    {
        'country': 'BR', 'state_province': 'MG', 'city': 'Belo Horizonte',
        'county': '', 'address': 'Rua da Bahia, 500, Centro, Belo Horizonte - MG',
        'property_type': 'Comercial', 'auction_type': 'judicial',
        'auction_date': timezone.now().replace(hour=9, minute=0) + timezone.timedelta(days=25),
        'currency': 'BRL',
        'appraised_value_cents': 42000000,
        'minimum_bid_cents':     28000000,
        'market_value_cents':    39000000,
        'debt_type': 'condominium',
        'total_debt_cents':      8900000,
        'debt_details': [{'type': 'Condomínio atrasado', 'amount': 45000}, {'type': 'IPTU', 'amount': 44000}],
        'status': 'discovered',
        'source_url': 'https://leilaovip.com.br/demo3',
    },
]


class Command(BaseCommand):
    help = 'Cria imóveis de demonstração'

    def handle(self, *args, **kwargs):
        source = ScrapingSource.objects.first()
        created = 0
        for d in DEMO:
            external_id = f"demo-{uuid.uuid4().hex[:8]}"
            p = Property.objects.create(
                source=source,
                external_id=external_id,
                scraped_at=timezone.now(),
                **d,
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f'{created} imóveis de demonstração criados!'))
