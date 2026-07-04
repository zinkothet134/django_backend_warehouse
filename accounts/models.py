from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Define the role choices
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('WAREHOUSE', 'Warehouse Staff'),
        ('CASHIER', 'Cashier'),
        ('SALES', 'Sales Staff'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='SALES')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"
