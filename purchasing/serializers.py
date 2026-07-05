from rest_framework import serializers
from .models import Supplier, PurchaseOrder, PurchaseOrderItem
from django.db import transaction

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    variant_sku = serializers.CharField(source='product_variant.sku', read_only=True)

    class Meta:
        model = PurchaseOrderItem
        fields = ['id', 'product_variant', 'variant_sku', 'quantity', 'unit_cost']

class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = ['id', 'supplier', 'supplier_name', 'order_date', 'expected_delivery', 'status', 'notes', 'items']
        # read_only_fields = ['order_date'] 

    
    @transaction.atomic
    def create(self, validated_data):
        # Pop the nested items array out of the request data
        items_data = validated_data.pop('items', [])

        # Create the parent PurchaseOrder
        purchase_order = PurchaseOrder.objects.create(**validated_data)

        # Loop through the items and create them, linking them to the new purchase_order
        for item_data in items_data:
            PurchaseOrderItem.objects.create(
                purchase_order=purchase_order, 
                **item_data
            )
        

        return purchase_order
    
    @transaction.atomic
    def update(self, instance, validated_data):
        # 1. Pop the nested items data out (if provided)
        items_data = validated_data.pop('items', None)

        # 2. Update the parent PurchaseOrder fields on the existing instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 3. If new items were sent, update the line items
        if items_data is not None:
            # Delete the old items and recreate the new ones
            instance.items.all().delete()
            for item_data in items_data:
                item_data.pop("id", None)
                PurchaseOrderItem.objects.create(
                    purchase_order=instance, 
                    **item_data
                )

        return instance
        
