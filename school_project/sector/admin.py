from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Sector, SectorDocument, SectorNews, SectorReport

@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'utis_code', 'director', 'total_schools', 'is_active')
    list_filter = ('region', 'is_active', 'created_at')
    search_fields = ('name', 'utis_code', 'director__username', 'region__name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'region', 'utis_code', 'director')
        }),
        (_('Əlaqə məlumatları'), {
            'fields': ('phone_number', 'email', 'address')
        }),
        (_('Statistika'), {
            'fields': ('total_schools', 'total_students', 'total_teachers')
        }),
        (_('Status'), {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )

@admin.register(SectorDocument)
class SectorDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'sector', 'document_type', 'uploaded_by', 'uploaded_at')
    list_filter = ('document_type', 'sector', 'uploaded_at')
    search_fields = ('title', 'description', 'sector__name')
    readonly_fields = ('uploaded_by', 'uploaded_at')
    
    def save_model(self, request, obj, form, change):
        if not obj.uploaded_by:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(SectorNews)
class SectorNewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'sector', 'published_by', 'published_at', 'is_active')
    list_filter = ('sector', 'is_active', 'published_at')
    search_fields = ('title', 'content', 'sector__name')
    readonly_fields = ('published_by', 'published_at')
    
    def save_model(self, request, obj, form, change):
        if not obj.published_by:
            obj.published_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(SectorReport)
class SectorReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'sector', 'report_type', 'report_period', 'status', 'submitted_by')
    list_filter = ('sector', 'report_type', 'status', 'report_period')
    search_fields = ('title', 'content', 'sector__name')
    readonly_fields = ('created_at', 'updated_at', 'submitted_by', 'approved_by', 'approval_date')
    
    fieldsets = (
        (None, {
            'fields': ('sector', 'title', 'report_type', 'report_period')
        }),
        (_('Hesabat məzmunu'), {
            'fields': ('content', 'attachments')
        }),
        (_('Status'), {
            'fields': ('status', 'submitted_by', 'approved_by', 'approval_date', 'rejection_reason')
        }),
        (_('Tarixlər'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.submitted_by:
            obj.submitted_by = request.user
        super().save_model(request, obj, form, change)
