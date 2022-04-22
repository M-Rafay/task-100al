from django.contrib import admin
from rest_framework.authtoken.models import Token
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models.usermodel import User

class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'full_name', 'name', 'role', 'is_active', 'is_staff')
    list_filter = ('is_superuser', 'is_staff', 'is_active')
    fieldsets = (
        (None, {
            'fields': ('password', 'last_login', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'first_name', 'name', 'last_name', 'full_name', 'email', 'phone_no', 'is_active', 'role'),
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_active', 'role'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)

admin.site.register(User, UserAdmin)
# admin.site.unregister(Token)
