# footwear_erp/urls_tenant.py

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView # 🌟 Import this

urlpatterns = [
    # The local admin panel where Store A manages their own database
    path('admin/', admin.site.urls),
    # 🌟 Explicitly add the refresh path here
    path('api/accounts/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # All of your isolated ERP business logic APIs
    path('api/accounts/', include('accounts.urls')),
    path('api/products/', include('products.urls')),
    path('api/inventory/', include('inventory.urls')), 
    path('api/sales/', include('sales.urls')),
    path('api/purchasing/', include('purchasing.urls')),
]
