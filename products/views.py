# products/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import isWarehouseStaff 
from .pagination import ProductPagination
from rest_framework import filters
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce

from .models import Category, Brand, Product, ProductVariant, Attribute, AttributeValue
from .serializers import (
    CategorySerializer, 
    BrandSerializer, 
    ProductSerializer, 
    ProductVariantSerializer,
    AttributeSerializer,
    AttributeValueSerializer
)

class DynamicPermissionViewSet(viewsets.ModelViewSet):
    """
    A custom ViewSet that allows anyone logged in to view data,
    but restricts creating, updating, and deleting to Warehouse/Admin staff.
    """
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [isWarehouseStaff]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

class AttributeViewSet(DynamicPermissionViewSet):
    """Allows tenants to define parameters like 'Size', 'Color', 'Width'."""
    queryset = Attribute.objects.all().prefetch_related('values').order_by('name')
    # Assuming standard ModelSerializers are mapped in your serializers file
    serializer_class = AttributeSerializer
    permission_classes = [IsAuthenticated] # Ensure this matches
    
    

class AttributeValueViewSet(DynamicPermissionViewSet):
    """Allows tenants to manage the specific choices under each attribute category."""
    queryset = AttributeValue.objects.all().select_related('attribute').order_by('value')
    serializer_class = AttributeValueSerializer
    permission_classes = [IsAuthenticated] # Ensure this matches

class CategoryViewSet(DynamicPermissionViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer

class BrandViewSet(DynamicPermissionViewSet):
    queryset = Brand.objects.all().order_by('name')
    serializer_class = BrandSerializer

class ProductViewSet(DynamicPermissionViewSet):
    serializer_class = ProductSerializer
    pagination_class = ProductPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'brand__name', 'category__name']

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related(
            'category', 'brand'
        ).prefetch_related(
            'variants__attribute_values__attribute'
        ).order_by('-id')
    
    def destroy(self, request, *args, **kwargs):
        # Grab the product the user is trying to delete
        product = self.get_object()
        
        # Soft Delete it by archiving it!
        product.is_active = False
        product.save()
        
        # Return a 204 No Content success response (which is what React expects for a deletion)
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProductVariantViewSet(DynamicPermissionViewSet):
    serializer_class = ProductVariantSerializer
    pagination_class = ProductPagination
    filter_backends = [filters.SearchFilter]

    search_fields = [
        'sku', 
        'barcode', 
        'attribute_values__value',  # 🔥 Replaces 'color' and 'size' to scan all custom choices instantly
        'product__name', 
        'product__brand__name'
    ]

    def get_queryset(self):
    # 🌟 Only return variants if their parent product is ACTIVE
        return ProductVariant.objects.filter(
            product__is_active=True
        ).select_related(
            'product'
        ).prefetch_related(
            'attribute_values__attribute'
        ).annotate(
            stock=Coalesce(Sum('stock_levels__quantity_on_hand'), Value(0))
        ).order_by('-id')


