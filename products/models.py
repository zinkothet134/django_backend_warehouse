import re
from django.db import models
from django.utils.text import slugify

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True,help_text="A Short label for urls")

    class Meta: 
        verbose_name_plural = 'Categories'
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Brand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # 🌟 ADD THIS LINE:
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.brand.name} {self.name}"
    
class Attribute(models.Model):
    """
    Allows tenants to define their own custom variant options.
    Examples: "Size", "Color", "Material", "Width"
    """
    name = models.CharField(max_length=100)  # e.g., "Size" or "Color"

    def __str__(self):
        return self.name

class AttributeValue(models.Model):
    """
    The specific options belonging to an attribute.
    Examples: Under "Size" -> "EU 42", "US 10". Under "Color" -> "Black", "Crimson Red"
    """
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=100)  # e.g., "EU 42"

    class Meta:
        unique_together = ('attribute', 'value')

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"
    
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    # SKU (Stock Keeping Unit) - The most important field for warehouse tracking
    sku = models.CharField(max_length=50, unique=True)
    # 🌟 ADD THIS: A dedicated string field for the scanner
    barcode = models.CharField(max_length=100, unique=True, null=True, blank=True)
    # # Footwear Specifics
    # size = models.CharField(max_length=20) # e.g., "US 10", "EU 42", "UK 9"
    # color = models.CharField(max_length=50)
    # # Pricing for your two business models
    attribute_values = models.ManyToManyField(AttributeValue, related_name='variants')

     # Purchase / supplier cost per unit

    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Supplier purchase cost per unit, used for profit reporting.",

    )
    wholesale_price = models.DecimalField(max_digits=10, decimal_places=2)
    retail_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        attr_string = ", ".join([str(av.value) for av in self.attribute_values.all()])
        return f"{self.product.name} ({attr_string or 'No Variants'}) - {self.sku}"
