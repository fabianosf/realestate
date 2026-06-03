from rest_framework import serializers
from .models import Property, ScrapingSource


class PropertyListSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source.name', read_only=True)
    pdf_file_url = serializers.SerializerMethodField()

    def get_pdf_file_url(self, obj):
        if not obj.pdf_file:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.pdf_file.url)
        return obj.pdf_file.url

    class Meta:
        model = Property
        fields = [
            'id', 'country', 'state_province', 'city', 'address',
            'property_type', 'area_sqm', 'area_sqft', 'bedrooms', 'bathrooms',
            'auction_type', 'auction_date', 'currency',
            'appraised_value_cents', 'minimum_bid_cents', 'market_value_cents',
            'debt_type', 'total_debt_cents',
            'status', 'estimated_profit_pct', 'roi_score',
            'source_url', 'pdf_url', 'pdf_file_url', 'pdf_processed',
            'source_name', 'scraped_at', 'created_at',
        ]


class PropertyDetailSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source.name', read_only=True)
    pdf_file_url = serializers.SerializerMethodField()

    def get_pdf_file_url(self, obj):
        if not obj.pdf_file:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.pdf_file.url)
        return obj.pdf_file.url

    class Meta:
        model = Property
        exclude = ['pdf_extracted_text']


class PropertyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ['status', 'notes', 'roi_score', 'market_value_cents']
