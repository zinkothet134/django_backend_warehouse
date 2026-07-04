# inventory/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WarehouseLocationViewSet, StockViewSet

router = DefaultRouter()
router.register(r'locations', WarehouseLocationViewSet)
router.register(r'levels', StockViewSet)

urlpatterns = [
    path('', include(router.urls)),
]