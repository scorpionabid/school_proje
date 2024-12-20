from rest_framework import serializers
from .models import School, Student, ClassRoom, Attendance, Grade

class SchoolSerializer(serializers.ModelSerializer):
    sector_name = serializers.CharField(source='sector.name', read_only=True)
    principal_name = serializers.CharField(source='principal.get_full_name', read_only=True)
    school_type_display = serializers.CharField(source='get_school_type_display', read_only=True)
    language_display = serializers.CharField(source='get_language_display', read_only=True)
    
    class Meta:
        model = School
        fields = [
            'id', 'name', 'utis_code', 'school_type', 'school_type_display',
            'sector', 'sector_name', 'address', 'phone', 'email', 'website',
            'language', 'language_display', 'foundation_year', 'shift_count',
            'principal', 'principal_name', 'total_students', 'total_teachers',
            'total_classes', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['total_students', 'total_teachers', 'total_classes']

class StudentSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name', read_only=True)
    class_name = serializers.CharField(source='class_room.__str__', read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'id', 'first_name', 'last_name', 'father_name', 'full_name',
            'birth_date', 'gender', 'gender_display', 'utis_id',
            'school', 'school_name', 'class_room', 'class_name',
            'admission_date', 'address', 'phone', 'email',
            'parent_name', 'parent_phone', 'parent_email',
            'is_active', 'created_at', 'updated_at'
        ]

class ClassRoomSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name', read_only=True)
    teacher_name = serializers.CharField(source='class_teacher.get_full_name', read_only=True)
    language_display = serializers.CharField(source='get_language_display', read_only=True)
    
    class Meta:
        model = ClassRoom
        fields = [
            'id', 'school', 'school_name', 'grade', 'division',
            'language', 'language_display', 'capacity',
            'class_teacher', 'teacher_name', 'current_students',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['current_students']

class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.get_full_name', read_only=True)
    absence_type_display = serializers.CharField(source='get_absence_type_display', read_only=True)
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'student', 'student_name', 'date', 'is_present',
            'absence_type', 'absence_type_display', 'note',
            'recorded_by', 'recorded_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['recorded_by']

class GradeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    grade_type_display = serializers.CharField(source='get_grade_type_display', read_only=True)
    
    class Meta:
        model = Grade
        fields = [
            'id', 'student', 'student_name', 'subject', 'grade_type',
            'grade_type_display', 'grade', 'date', 'teacher',
            'teacher_name', 'note', 'created_at', 'updated_at'
        ]
        read_only_fields = ['teacher']
