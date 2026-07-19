# products/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, BrandViewSet, ProductViewSet, ProductVariantViewSet, AttributeViewSet, AttributeValueViewSet

# The router automatically generates standard RESTful URLs for our viewsets
router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'brands', BrandViewSet)
router.register(r'catalog', ProductViewSet, basename='catalog')
router.register(r'variants', ProductVariantViewSet, basename='variants')

# 🌟 Register the new attribute endpoints
router.register(r'attributes', AttributeViewSet)
router.register(r'attribute-values', AttributeValueViewSet)

urlpatterns = [
    path('', include(router.urls)),
]