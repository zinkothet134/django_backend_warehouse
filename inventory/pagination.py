# inventory/pagination.py
from rest_framework.pagination import PageNumberPagination

class InventoryPagination(PageNumberPagination):
    # Default records per page for inventory lists
    page_size = 25 
    
    # Allows the frontend to override size if displaying a dense layout (e.g., ?page_size=50)
    page_size_query_param = 'page_size' 
    
    # Safety cap to protect database performance
    max_page_size = 100