# products/serializers.py
from rest_framework import serializers
from .models import Category, Brand, Product, ProductVariant

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'   

class ProductVariantSerializer(serializers.ModelSerializer):
    # 1. ADD THIS LINE: Reach into the parent 'product' and grab its 'name'
    product_name = serializers.ReadOnlyField(source='product.name')
    # 🌟 Explicitly add the annotated field as read-only
    stock = serializers.IntegerField(read_only=True)
    class Meta:
        model = ProductVariant
        fields = ['id', 'product', 'product_name','sku', 'color', 'size',"cost_price", 'wholesale_price', 'retail_price','stock']
        # ADD THIS LINE:
        read_only_fields = ['product'] 

    

class ProductSerializer(serializers.ModelSerializer):
    # This magically nests all child variants inside the parent product JSON
    variants = ProductVariantSerializer(many=True)
    
    # We also pull in the string names of the category and brand for the frontend
    category_name = serializers.ReadOnlyField(source='category.name')
    brand_name = serializers.ReadOnlyField(source='brand.name')

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 
            'category', 'category_name', 
            'brand', 'brand_name', 
            'variants', # The nested variants list
            'created_at', 'updated_at'
        ]
    # 2. Add this create method
    def create(self, validated_data):
        # Pop the variants out of the validated data
        variants_data = validated_data.pop('variants', [])
        
        # Create the Product
        product = Product.objects.create(**validated_data)
        
        # Create each Variant associated with the Product
        for variant_data in variants_data:
            ProductVariant.objects.create(product=product, **variant_data)
            
        return product