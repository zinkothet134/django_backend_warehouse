from rest_framework import viewsets
from .models import Supplier, PurchaseOrder
from .serializers import SupplierSerializer, PurchaseOrderSerializer
from .pagination import SupplierPagination
from rest_framework import filters
from .pagination import SupplierPagination
from django_filters.rest_framework import DjangoFilterBackend

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all().order_by('-created_at')
    serializer_class = SupplierSerializer

    # Attach the custom pagination class here
    pagination_class = SupplierPagination
    # 2. Add these two lines to enable the search!
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'contact_name', 'email']

   

class PurchaseOrderViewSet(viewsets.ModelViewSet):
    # Added select_related and prefetch_related for massive performance boost
    queryset = PurchaseOrder.objects.select_related('supplier').prefetch_related('items').all().order_by('-order_date')
    serializer_class = PurchaseOrderSerializer

    # 1. Apply your pagination
    pagination_class = SupplierPagination
   
   # 2. Add both Filter and Search backends
    filter_backends = [ DjangoFilterBackend,filters.SearchFilter]

    # 3. Exact match filtering (e.g., ?status=DRAFT)
    filterset_fields = ['status']

    search_fields = ['id', 'supplier__name']