from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Avg, Q

from .models import Property
from .serializers import PropertyListSerializer, PropertyDetailSerializer, PropertyUpdateSerializer

ALLOWED_ORDERINGS = {
    'roi_score', '-roi_score',
    'estimated_profit_pct', '-estimated_profit_pct',
    'minimum_bid_cents', '-minimum_bid_cents',
    'auction_date', '-auction_date',
    'created_at', '-created_at',
}


class PropertyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ('update', 'partial_update'):
            return PropertyUpdateSerializer
        if self.action == 'retrieve':
            return PropertyDetailSerializer
        return PropertyListSerializer

    def get_queryset(self):
        qs = Property.objects.select_related('source')

        # Superuser vê tudo; usuário comum só vê fontes próprias ou compartilhadas
        user = self.request.user
        if not user.is_superuser:
            qs = qs.filter(
                Q(source__owner=user) | Q(source__owner=None)
            )

        p = self.request.query_params

        if p.get('country'):
            qs = qs.filter(country=p['country'])
        if p.get('auction_type'):
            qs = qs.filter(auction_type=p['auction_type'])
        if p.get('debt_type'):
            qs = qs.filter(debt_type=p['debt_type'])
        if p.get('status'):
            qs = qs.filter(status=p['status'])

        try:
            if p.get('estimated_profit_pct__gte') not in (None, '', '0'):
                qs = qs.filter(estimated_profit_pct__gte=float(p['estimated_profit_pct__gte']))
        except (ValueError, TypeError):
            pass

        try:
            if p.get('minimum_bid_cents__lte'):
                qs = qs.filter(minimum_bid_cents__lte=int(p['minimum_bid_cents__lte']))
        except (ValueError, TypeError):
            pass

        ordering = p.get('ordering', '-created_at')
        if ordering not in ALLOWED_ORDERINGS:
            ordering = '-created_at'

        return qs.order_by(ordering)

    @action(detail=False, methods=['GET'])
    def stats(self, request):
        qs = Property.objects.all()
        by_country = dict(qs.values_list('country').annotate(c=Count('id')).values_list('country', 'c'))
        by_status = dict(qs.values_list('status').annotate(c=Count('id')).values_list('status', 'c'))
        avg_roi = qs.filter(estimated_profit_pct__isnull=False).aggregate(v=Avg('estimated_profit_pct'))['v']
        return Response({
            'total_properties': qs.count(),
            'opportunities': by_status.get('opportunity', 0),
            'analyzing': by_status.get('analyzing', 0),
            'avg_roi': float(avg_roi) if avg_roi else None,
            'by_country': by_country,
            'by_status': by_status,
        })

    @action(detail=True, methods=['POST'])
    def trigger_pdf(self, request, pk=None):
        prop = self.get_object()
        if not prop.pdf_url:
            return Response({'error': 'No PDF URL'}, status=status.HTTP_400_BAD_REQUEST)
        from apps.scrapers.tasks import process_pdf_task
        process_pdf_task.delay(str(prop.id), prop.pdf_url)
        return Response({'status': 'queued'})
