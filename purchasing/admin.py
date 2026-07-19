from django.contrib import admin
from .models import Supplier, PurchaseOrder,PurchaseOrderItem
# Register your models here.

admin.site.register(Supplier)
admin.site.register(PurchaseOrder)
admin.site.register(PurchaseOrderItem)