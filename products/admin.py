# products/admin.py
from django.contrib import admin
from .models import Category, Brand, Product, ProductVariant, Attribute, AttributeValue

# --- 1. Basic Models ---
admin.site.register(Category)
admin.site.register(Brand)

# --- 2. Dynamic Attribute Management ---
class AttributeValueInline(admin.TabularInline):
    """Allows adding values (e.g., 'Red', 'Blue') directly inside the Attribute ('Color') screen."""
    model = AttributeValue
    extra = 1

@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [AttributeValueInline]

@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ('attribute', 'value')
    list_filter = ('attribute',)
    # search_fields is strictly required here for 'autocomplete_fields' to work in ProductVariantInline
    search_fields = ('value',) 

# --- 3. Product & Variant Management ---
class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    # Replaces the clunky default ManyToMany UI with a sleek, searchable dropdown
    autocomplete_fields = ['attribute_values']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category')
    search_fields = ('name',)
    list_filter = ('brand', 'category')
    inlines = [ProductVariantInline]

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    """
    Providing a dedicated variant view is highly recommended. It allows store managers 
    to filter, search, and update prices for specific SKUs without opening the parent product.
    """
    list_display = ('sku', 'product', 'display_attributes', 'cost_price', 'wholesale_price', 'retail_price', 'is_active')
    list_filter = ('is_active', 'product__category')
    search_fields = ('sku', 'barcode', 'product__name')
    
    # Creates a side-by-side selection box when editing a variant directly
    filter_horizontal = ('attribute_values',) 

    def display_attributes(self, obj):
        # Extracts all assigned attribute values to display them neatly in the admin list view
        return ", ".join([av.value for av in obj.attribute_values.all()])
    
    display_attributes.short_description = 'Attributes'