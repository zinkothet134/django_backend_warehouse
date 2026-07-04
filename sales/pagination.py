# sales/pagination.py
from rest_framework.pagination import PageNumberPagination

class POSPagination(PageNumberPagination):
    # Default number of records per page
    page_size = 10 
    
    # Allows your React/React Native frontend to request a custom size (e.g., ?page_size=50)
    page_size_query_param = 'page_size' 
    
    # Absolute maximum to prevent a malicious or buggy client from requesting 10,000 records at once
    max_page_size = 50

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10 # Shows 10 customers per page (matches React frontend expectations)
    page_size_query_param = 'page_size'
    max_page_size = 100