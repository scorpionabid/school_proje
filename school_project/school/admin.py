from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import School, Student, ClassRoom, Attendance, Grade, SchoolAdmin

# School admin class adını dəyişirik
@admin.register(School)
class SchoolModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'utis_code', 'school_type', 'sector', 'principal', 'total_students', 'is_active')
    list_filter = ('school_type', 'sector', 'language', 'is_active')
    search_fields = ('name', 'utis_code', 'principal__username', 'sector__name')
    readonly_fields = ('created_at', 'updated_at', 'total_students', 'total_teachers', 'total_classes')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'utis_code', 'school_type', 'sector', 'principal')
        }),
        (_('Əlaqə məlumatları'), {
            'fields': ('address', 'phone', 'email', 'website')
        }),
        (_('Təhsil məlumatları'), {
            'fields': ('language', 'foundation_year', 'shift_count')
        }),
        (_('Statistika'), {
            'fields': ('total_students', 'total_teachers', 'total_classes')
        }),
        (_('Status'), {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'utis_id', 'school', 'class_room', 'gender', 'is_active')
    list_filter = ('school', 'gender', 'is_active', 'admission_date')
    search_fields = ('first_name', 'last_name', 'father_name', 'utis_id')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Şəxsi məlumatlar'), {
            'fields': (
                'first_name', 'last_name', 'father_name', 'birth_date',
                'gender', 'utis_id'
            )
        }),
        (_('Təhsil məlumatları'), {
            'fields': ('school', 'class_room', 'admission_date')
        }),
        (_('Əlaqə məlumatları'), {
            'fields': ('address', 'phone', 'email')
        }),
        (_('Valideyn məlumatları'), {
            'fields': ('parent_name', 'parent_phone', 'parent_email')
        }),
        (_('Status'), {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )

@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'school', 'grade', 'division', 'class_teacher', 'current_students')
    list_filter = ('school', 'grade', 'language')
    search_fields = ('school__name', 'class_teacher__username')
    readonly_fields = ('created_at', 'updated_at', 'current_students')
    
    fieldsets = (
        (None, {
            'fields': ('school', 'grade', 'division', 'language', 'capacity')
        }),
        (_('Rəhbərlik'), {
            'fields': ('class_teacher',)
        }),
        (_('Statistika'), {
            'fields': ('current_students',)
        }),
        (_('Status'), {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'is_present', 'absence_type', 'recorded_by')
    list_filter = ('is_present', 'absence_type', 'date')
    search_fields = ('student__first_name', 'student__last_name', 'note')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('student', 'date', 'is_present', 'absence_type')
        }),
        (_('Əlavə məlumat'), {
            'fields': ('note', 'recorded_by')
        }),
        (_('Tarixlər'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.recorded_by:
            obj.recorded_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'grade_type', 'grade', 'date', 'teacher')
    list_filter = ('grade_type', 'subject', 'date')
    search_fields = ('student__first_name', 'student__last_name', 'subject', 'note')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('student', 'subject', 'grade_type', 'grade', 'date')
        }),
        (_('Əlavə məlumat'), {
            'fields': ('teacher', 'note')
        }),
        (_('Tarixlər'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.teacher:
            obj.teacher = request.user
        super().save_model(request, obj, form, change)

@admin.register(SchoolAdmin)
class SchoolAdminModelAdmin(admin.ModelAdmin):
    list_display = ['user', 'school', 'phone', 'created_at']
    list_filter = ['school']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'school__name']
    raw_id_fields = ['user', 'school']
