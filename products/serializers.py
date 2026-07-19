# products/serializers.py
from rest_framework import serializers
from .models import Category, Brand, Product, ProductVariant,Attribute, AttributeValue

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'   
class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = '__all__'

# --- 1. ADD THESE SERIALIZERS FOR ATTRIBUTES ---
class AttributeValueReadSerializer(serializers.ModelSerializer):
    """Used strictly for reading data to give the frontend clean, displayable names."""
    attribute_name = serializers.ReadOnlyField(source='attribute.name')
    
    class Meta:
        model = AttributeValue
        fields = ['id', 'attribute_name', 'value']

class AttributeValueSerializer(serializers.ModelSerializer):
        class Meta:
            model = AttributeValue
            fields = '__all__'

class ProductVariantSerializer(serializers.ModelSerializer):
    # 1. ADD THIS LINE: Reach into the parent 'product' and grab its 'name'
    product_name = serializers.ReadOnlyField(source='product.name')
    # 🌟 Explicitly add the annotated field as read-only
    stock = serializers.IntegerField(read_only=True)

    # 🌟 READ ONLY: Provides structured JSON for the UI (e.g., [{"attribute_name": "Color", "value": "Red"}])
    attributes_details = AttributeValueReadSerializer(source='attribute_values', many=True, read_only=True)

    attribute_value_ids = serializers.PrimaryKeyRelatedField(
        source='attribute_values',
        queryset=AttributeValue.objects.all(),
        many=True,
        write_only=True,
        required=False
    )
    class Meta:
        model = ProductVariant
        fields = [
            'id', 'product', 'product_name', 'sku', 'barcode', 
            'cost_price', 'wholesale_price', 'retail_price', 
            'stock', 'attributes_details', 'attribute_value_ids'
        ]
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
            # 🌟 MUST POP M2M FIELDS BEFORE CREATING THE INSTANCE
            attribute_values = variant_data.pop('attribute_values', [])
            # Create the physical variant database row
            variant = ProductVariant.objects.create(product=product, **variant_data)
            # 🌟 ATTACH THE M2M ATTRIBUTES AFTER CREATION
            if attribute_values:
                variant.attribute_values.set(attribute_values)
            
        return product