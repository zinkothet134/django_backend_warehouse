# footwear_erp/urls_public.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # The master admin panel where YOU manage the businesses/tenants
    path('admin/', admin.site.urls),
    
    # 🌟 Later, you will add your SaaS endpoints here:
    # path('api/billing/', include('billing.urls')),
    # path('api/register/', include('customers.urls')), 
]