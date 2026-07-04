from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register your models here.

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Company Details', {'fields': ('role', 'phone_number')}),
    )

    list_display = ('username', 'email', 'first_name', 'last_name','role','is_staff')
    list_filter = ('role','is_staff', 'is_superuser')

admin.site.register(User, CustomUserAdmin)
