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
    
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    # SKU (Stock Keeping Unit) - The most important field for warehouse tracking
    sku = models.CharField(max_length=50, unique=True)
    # 🌟 ADD THIS: A dedicated string field for the scanner
    barcode = models.CharField(max_length=100, unique=True, null=True, blank=True)
    # Footwear Specifics
    size = models.CharField(max_length=20) # e.g., "US 10", "EU 42", "UK 9"
    color = models.CharField(max_length=50)
    # Pricing for your two business models

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

    class Meta:
    # Ensures you don't accidentally create duplicate variants for the exact same shoe
        unique_together = ('product', 'size', 'color')

    def __str__(self):
        return f"{self.product.name} - {self.color} - Size {self.size} ({self.sku})" 
