from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "role", "department", "is_active")
    list_filter = ("role", "is_active", "is_staff", "department")
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Role & Contact", {"fields": ("role", "phone", "department")}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("Role & Contact", {"fields": ("role", "phone", "department", "email")}),
    )
    search_fields = ("username", "email", "first_name", "last_name")
