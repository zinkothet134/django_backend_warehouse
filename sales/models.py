from django.db import models
from django.conf import settings

class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Order(models.Model):

    ORDER_TYPE_CHOICES = [

        ("RETAIL", "Retail"),

        ("WHOLESALE", "Wholesale"),

    ]

    customer = models.ForeignKey(

        Customer,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

    )

    customer_name = models.CharField(max_length=255, blank=True, null=True)

    order_type = models.CharField(

        max_length=20,

        choices=ORDER_TYPE_CHOICES,

        default="RETAIL",

        db_index=True,

    )

    payment_method = models.CharField(max_length=50, default="CASH")

    status = models.CharField(max_length=50, default="COMPLETED")

    total_amount = models.DecimalField(

        max_digits=10,

        decimal_places=2,

        default=0,

    )

    cashier = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:

        ordering = ["-created_at"]

        indexes = [

            models.Index(fields=["created_at", "order_type"]),

            models.Index(fields=["status"]),

        ]

    def __str__(self):

        return f"Order #{self.id} - {self.get_order_type_display()}"

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE,
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.SET_NULL,
        null=True,
    )
    quantity = models.IntegerField(default=1)
    price_at_sale = models.DecimalField(max_digits=10, decimal_places=2)
    # Copy of variant.cost_price at checkout time

    cost_at_sale = models.DecimalField(

        max_digits=10,

        decimal_places=2,

        default=0,

    )

    @property
    def line_total(self):
        return self.quantity * self.price_at_sale
    
    @property

    def cost_total(self):

        return self.quantity * self.cost_at_sale

    @property

    def profit_total(self):

        return self.line_total - self.cost_total

    def __str__(self):
        return f"{self.quantity}x for Order #{self.order_id}"