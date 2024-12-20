from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, ChangeHistory

# Register your models here.

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'father_name', 
                   'user_type', 'utis_code', 'is_active')
    list_filter = ('user_type', 'is_active', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'utis_code')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Şəxsi məlumatlar'), {'fields': ('first_name', 'last_name', 'father_name', 'email', 
                                           'utis_code', 'whatsapp_number')}),
        (_('İcazələr'), {'fields': ('user_type', 'is_active', 'is_staff', 'is_superuser',
                                   'groups', 'user_permissions')}),
        (_('Vacib tarixlər'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'user_type', 'first_name', 
                      'last_name', 'father_name', 'email', 'utis_code', 'whatsapp_number'),
        }),
    )

class ChangeHistoryAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'model_name')
    list_filter = ('model_name', 'timestamp', 'user')
    search_fields = ('model_name', 'user__username')
    readonly_fields = ('timestamp', 'user', 'model_name', 'old_data', 'new_data')
    ordering = ('-timestamp',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ChangeHistory, ChangeHistoryAdmin)
