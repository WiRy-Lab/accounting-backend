"""
Django admin customization
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core import models

class UserAdmin(BaseUserAdmin):
    """Define the admin pages for user"""
    ordering = ['id']
    list_display = ['account', 'name']
    fieldsets = (
        (None, {'fields': ('account', 'name', 'password')}),
        (
            _('Permissions'),
            {
                'fields': ('is_active', 'is_staff', 'is_superuser')
            }
        ),
        (_('Important dates'), {'fields': ('last_login', )}),
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide', ),
                'fields': ('name', 'account', 'email', 'password1', 'password2','is_active', 'is_staff', 'is_superuser')
            }
        ),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Accounting)
admin.site.register(models.Category)
admin.site.register(models.MonthTarget)
admin.site.register(models.SaveMoneyTarget)