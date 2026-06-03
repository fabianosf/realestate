import django_filters
from .models import Property


class PropertyFilter(django_filters.FilterSet):
    estimated_profit_pct__gte = django_filters.NumberFilter(
        field_name='estimated_profit_pct', lookup_expr='gte'
    )
    minimum_bid_cents__lte = django_filters.NumberFilter(
        field_name='minimum_bid_cents', lookup_expr='lte'
    )
    minimum_bid_cents__gte = django_filters.NumberFilter(
        field_name='minimum_bid_cents', lookup_expr='gte'
    )
    auction_date__gte = django_filters.DateTimeFilter(field_name='auction_date', lookup_expr='gte')
    auction_date__lte = django_filters.DateTimeFilter(field_name='auction_date', lookup_expr='lte')
    city = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Property
        fields = ['country', 'state_province', 'auction_type', 'debt_type', 'status', 'pdf_processed']
