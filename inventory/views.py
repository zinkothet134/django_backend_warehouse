# inventory/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from accounts.permissions import isWarehouseStaff # Pulling the security rule we built earlier
from .models import WarehouseLocation, Stock
from .serializers import WarehouseLocationSerializer, StockSerializer
from .pagination import InventoryPagination
from rest_framework import filters

class DynamicInventoryViewSet(viewsets.ModelViewSet):
    def get_permissions(self):
        # Only warehouse staff can add, edit, or delete stock
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [isWarehouseStaff]
        else:
            # Everyone logged in can view stock
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
class WarehouseLocationViewSet(DynamicInventoryViewSet):
    queryset = WarehouseLocation.objects.all().order_by('name')
    serializer_class = WarehouseLocationSerializer
    

class StockViewSet(DynamicInventoryViewSet):
    # 'select_related' fixes the "N+1 Query Problem", making your database lookups lightning fast
    queryset = Stock.objects.select_related('variant__product', 'location').all().order_by('-id')
    serializer_class = StockSerializer
    pagination_class = InventoryPagination

    # 1. Enable the search filter
    filter_backends = [filters.SearchFilter]
    
    # 2. Map the relationships for the search bar
    search_fields = [
        'variant__sku',            # Search by exact SKU
        'variant__color',          # Search by color
        'variant__product__name',  # Cross the relationships to search the parent Product name
        'location__name'           # Search by Warehouse/Store location name
    ]

    def get_queryset(self):
        # 🌟 select_related keeps it fast, filter() hides the deleted items!
        return Stock.objects.select_related('variant__product', 'location').filter(
            variant__product__is_active=True
        ).order_by('-id')

    # 🌟 ADD THE CUSTOM CREATE METHOD HERE:
    def create(self, request, *args, **kwargs):
        variant_id = request.data.get('variant')
        location_id = request.data.get('location')
        
        # Safely convert the incoming quantity to an integer
        try:
            qty_to_add = int(request.data.get('quantity_on_hand', 0))
        except (ValueError, TypeError):
            qty_to_add = 0

        # 1. Check if this shoe already exists at this warehouse location
        existing_stock = Stock.objects.filter(variant_id=variant_id, location_id=location_id).first()

        if existing_stock:
            # 2. IF IT EXISTS: Just add the new quantity to the old quantity!
            existing_stock.quantity_on_hand += qty_to_add
            existing_stock.save()
            
            # Return the updated data to the frontend
            serializer = self.get_serializer(existing_stock)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # 3. IF IT DOES NOT EXIST: Let Django create a brand new row normally
        return super().create(request, *args, **kwargs)
