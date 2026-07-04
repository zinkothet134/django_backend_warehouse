# inventory/serializers.py
from rest_framework import serializers
from .models import WarehouseLocation, Stock


class WarehouseLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarehouseLocation
        fields = '__all__'

class StockSerializer(serializers.ModelSerializer):
    # 🌟 Pro-Tip: Pulling read-only nested data so React doesn't have to do extra work!
    sku = serializers.CharField(source='variant.sku', read_only=True)
    product_name = serializers.CharField(source='variant.product.name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)

    class Meta:
        model = Stock
        fields = [
            'id', 'variant', 'sku', 'product_name', 
            'location', 'location_name', 
            'quantity_on_hand', 'low_stock_threshold', 
            'is_low_stock', 'last_updated'
        ]