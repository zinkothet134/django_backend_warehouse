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

from .models import Category, Brand, Product, ProductVariant
from .serializers import (
    CategorySerializer, 
    BrandSerializer, 
    ProductSerializer, 
    ProductVariantSerializer
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

class CategoryViewSet(DynamicPermissionViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer

class BrandViewSet(DynamicPermissionViewSet):
    queryset = Brand.objects.all().order_by('name')
    serializer_class = BrandSerializer

class ProductViewSet(DynamicPermissionViewSet):
    # 'prefetch_related' makes the database query incredibly fast when loading nested variants
    queryset = Product.objects.select_related('category', 'brand').prefetch_related('variants', 'category', 'brand').order_by('-id')
    serializer_class = ProductSerializer
    pagination_class = ProductPagination

    # Add these two lines to enable the search bar!
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'brand__name', 'category__name']

    def get_queryset(self):
        return Product.objects.filter(is_active=True).prefetch_related('variants').order_by('-id')
    
    def destroy(self, request, *args, **kwargs):
        # Grab the product the user is trying to delete
        product = self.get_object()
        
        # Soft Delete it by archiving it!
        product.is_active = False
        product.save()
        
        # Return a 204 No Content success response (which is what React expects for a deletion)
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProductVariantViewSet(DynamicPermissionViewSet):
    queryset = ProductVariant.objects.all().order_by('-id')
    serializer_class = ProductVariantSerializer

    pagination_class = ProductPagination
    # 1. This tells Django to listen for the ?search= parameter from React
    filter_backends = [filters.SearchFilter]

    search_fields = [
    'sku', # Searches ProductVariant.sku
    'barcode', # 🌟 Added here!
    'color', # Searches ProductVariant.color
    'size', # Searches ProductVariant.size
    'product__name', # Crosses the ForeignKey to search Product.name
    'product__brand__name' # Crosses two ForeignKeys to search Brand.name!
    ]

    def get_queryset(self):
    # 🌟 Only return variants if their parent product is ACTIVE
        return ProductVariant.objects.filter(product__is_active=True).annotate(
        stock=Coalesce(Sum('stock_levels__quantity_on_hand'), Value(0))
        ).order_by('-id') 


