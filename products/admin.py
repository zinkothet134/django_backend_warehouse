# products/admin.py
from django.contrib import admin
from .models import Category, Brand, Product, ProductVariant

# A clean way to show variants inside the parent product page
class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category')
    inlines = [ProductVariantInline]

admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Product, ProductAdmin)