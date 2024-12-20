from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Region, RegionDocument, RegionNews

# Register your models here.

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'utis_code', 'director', 'total_schools', 'total_students', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'utis_code', 'director__username')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'utis_code', 'director')
        }),
        (_('Əlaqə məlumatları'), {
            'fields': ('phone_number', 'email', 'website', 'address')
        }),
        (_('Statistika'), {
            'fields': ('total_schools', 'total_students', 'total_teachers')
        }),
        (_('Status'), {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )

@admin.register(RegionDocument)
class RegionDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'region', 'document_type', 'uploaded_by', 'uploaded_at')
    list_filter = ('document_type', 'region', 'uploaded_at')
    search_fields = ('title', 'description', 'region__name')
    readonly_fields = ('uploaded_by', 'uploaded_at')
    
    def save_model(self, request, obj, form, change):
        if not obj.uploaded_by:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(RegionNews)
class RegionNewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'region', 'published_by', 'published_at', 'is_active')
    list_filter = ('region', 'is_active', 'published_at')
    search_fields = ('title', 'content', 'region__name')
    readonly_fields = ('published_by', 'published_at')
    
    def save_model(self, request, obj, form, change):
        if not obj.published_by:
            obj.published_by = request.user
        super().save_model(request, obj, form, change)
