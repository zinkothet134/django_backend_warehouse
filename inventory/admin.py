# inventory/admin.py
from django.contrib import admin
from .models import WarehouseLocation, Stock

@admin.register(WarehouseLocation)
class WarehouseLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'zone', 'is_active')
    list_filter = ('is_active',)

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('variant', 'location', 'quantity_on_hand', 'low_stock_threshold', 'is_low_stock', 'last_updated')
    list_filter = ('location',)
    search_fields = ('variant__sku', 'variant__product__name')