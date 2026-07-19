
from django.db import models
from django_tenants.models import TenantMixin, DomainMixin

class Client(TenantMixin):
    # The 'schema_name' field is automatically provided by TenantMixin
    name = models.CharField(max_length=100)
    paid_until = models.DateField(null=True, blank=True)
    on_trial = models.BooleanField(default=True)
    created_on = models.DateField(auto_now_add=True)

    # Automatically drop schema if the tenant is deleted (optional but helpful in dev)
    auto_drop_schema = True 
    auto_create_schema = True

    def __str__(self):
        return self.name

class Domain(DomainMixin):
    # The 'domain' and 'is_primary' fields are automatically provided by DomainMixin
    # The 'tenant' foreign key is also automatically provided
    pass