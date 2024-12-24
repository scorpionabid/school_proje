from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, ChangeHistory

# Register your models here.

class CustomUserAdmin(UserAdmin):
    """
    Xüsusi istifadəçi admin paneli
    """
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'utis_code')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'father_name', 'email', 'utis_code', 'whatsapp_number')
        }),
        (_('User Type and Relationships'), {
            'fields': ('user_type', 'region', 'sector', 'school')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )

    readonly_fields = ('created_at', 'updated_at')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'father_name', 'email', 'utis_code', 'whatsapp_number')
        }),
        (_('User Type and Relationships'), {
            'fields': ('user_type', 'region', 'sector', 'school')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
    )

    def save_model(self, request, obj, form, change):
        """
        İstifadəçi məlumatlarını yadda saxlayarkən əlavə yoxlamalar
        """
        if obj.user_type == CustomUser.UserType.REGION_ADMIN:
            obj.sector = None
            obj.school = None
        elif obj.user_type == CustomUser.UserType.SECTOR_ADMIN:
            obj.school = None
            
        super().save_model(request, obj, form, change)

class ChangeHistoryAdmin(admin.ModelAdmin):
    """
    Dəyişiklik tarixçəsi admin paneli
    """
    list_display = ('user', 'model_name', 'timestamp')
    list_filter = ('model_name', 'timestamp')
    search_fields = ('user__username', 'model_name')
    readonly_fields = ('user', 'model_name', 'timestamp', 'old_data', 'new_data')
    ordering = ('-timestamp',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ChangeHistory, ChangeHistoryAdmin)
