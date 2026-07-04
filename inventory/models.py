from django.db import models
from products.models import ProductVariant

# Create your models here.
class WarehouseLocation(models.Model):
    name = models.CharField(max_length=100, help_text="e.g., Main Warehouse, Storefront Backroom")
    zone = models.CharField(max_length=50, blank=True, help_text="e.g., Aisle 4, Shelf B")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        if self.zone:
            return f"{self.name} - {self.zone}"
        return self.name
    
class Stock(models.Model):
    # Link to the exact SKU (Size/Color) in the products app
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='stock_levels')
    
    # Link to where it is physically sitting
    location = models.ForeignKey(WarehouseLocation, on_delete=models.CASCADE, related_name='inventory')
    
    # The actual numbers
    quantity_on_hand = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5, help_text="Alert when stock drops below this number")
    
    # Tracking for timestamps
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        # A single SKU can only have ONE stock record per physical location
        unique_together = ('variant', 'location')
        verbose_name_plural = "Stock Levels"

    def __str__(self):
        return f"{self.variant.sku} | Qty: {self.quantity_on_hand} | Loc: {self.location.name}"

    @property
    def is_low_stock(self):
        return self.quantity_on_hand <= self.low_stock_threshold