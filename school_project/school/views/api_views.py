from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg
from django_filters.rest_framework import DjangoFilterBackend

from ..models import School, Student, ClassRoom, Attendance, Grade
from ..serializers import (
    SchoolSerializer, StudentSerializer, ClassRoomSerializer,
    AttendanceSerializer, GradeSerializer
)

class SchoolViewSet(viewsets.ModelViewSet):
    """
    Məktəb API endpoint
    """
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['school_type', 'sector', 'language', 'is_active']
    search_fields = ['name', 'utis_code', 'principal__username']
    ordering_fields = ['name', 'total_students', 'created_at']
    
    @action(detail=True)
    def statistics(self, request, pk=None):
        """
        Məktəb statistikası
        """
        school = self.get_object()
        
        # Sinif statistikası
        class_stats = school.classes.values('grade').annotate(
            total_students=Count('students', filter=models.Q(students__is_active=True)),
            avg_attendance=Avg('students__attendances__is_present'),
            avg_grade=Avg('students__grades__grade')
        ).order_by('grade')
        
        # Davamiyyət statistikası
        attendance_stats = Attendance.objects.filter(
            student__school=school,
            student__is_active=True
        ).values('date').annotate(
            present=Count('id', filter=models.Q(is_present=True)),
            absent=Count('id', filter=models.Q(is_present=False))
        ).order_by('-date')[:30]
        
        # Qiymət statistikası
        grade_stats = Grade.objects.filter(
            student__school=school,
            student__is_active=True
        ).values('grade_type').annotate(
            avg_grade=Avg('grade'),
            total_grades=Count('id')
        )
        
        return Response({
            'total_students': school.total_students,
            'total_teachers': school.total_teachers,
            'total_classes': school.total_classes,
            'class_stats': class_stats,
            'attendance_stats': attendance_stats,
            'grade_stats': grade_stats,
        })

class StudentViewSet(viewsets.ModelViewSet):
    """
    Şagird API endpoint
    """
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['school', 'class_room', 'gender', 'is_active']
    search_fields = ['first_name', 'last_name', 'father_name', 'utis_id']
    ordering_fields = ['last_name', 'first_name', 'created_at']
    
    @action(detail=True)
    def attendance(self, request, pk=None):
        """
        Şagird davamiyyəti
        """
        student = self.get_object()
        attendances = student.attendances.all().order_by('-date')
        serializer = AttendanceSerializer(attendances, many=True)
        return Response(serializer.data)
    
    @action(detail=True)
    def grades(self, request, pk=None):
        """
        Şagird qiymətləri
        """
        student = self.get_object()
        grades = student.grades.all().order_by('-date')
        serializer = GradeSerializer(grades, many=True)
        return Response(serializer.data)

class ClassRoomViewSet(viewsets.ModelViewSet):
    """
    Sinif API endpoint
    """
    queryset = ClassRoom.objects.all()
    serializer_class = ClassRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['school', 'grade', 'language', 'is_active']
    search_fields = ['school__name', 'class_teacher__username']
    ordering_fields = ['grade', 'division', 'current_students']
    
    @action(detail=True)
    def students(self, request, pk=None):
        """
        Sinif şagirdləri
        """
        classroom = self.get_object()
        students = classroom.students.filter(is_active=True)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)
    
    @action(detail=True)
    def attendance(self, request, pk=None):
        """
        Sinif davamiyyəti
        """
        classroom = self.get_object()
        date = request.query_params.get('date')
        
        attendances = Attendance.objects.filter(
            student__class_room=classroom,
            student__is_active=True
        )
        
        if date:
            attendances = attendances.filter(date=date)
        
        attendances = attendances.order_by('-date')
        serializer = AttendanceSerializer(attendances, many=True)
        return Response(serializer.data)
    
    @action(detail=True)
    def grades(self, request, pk=None):
        """
        Sinif qiymətləri
        """
        classroom = self.get_object()
        subject = request.query_params.get('subject')
        grade_type = request.query_params.get('grade_type')
        
        grades = Grade.objects.filter(
            student__class_room=classroom,
            student__is_active=True
        )
        
        if subject:
            grades = grades.filter(subject=subject)
        if grade_type:
            grades = grades.filter(grade_type=grade_type)
        
        grades = grades.order_by('-date')
        serializer = GradeSerializer(grades, many=True)
        return Response(serializer.data)

class AttendanceViewSet(viewsets.ModelViewSet):
    """
    Davamiyyət API endpoint
    """
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'date', 'is_present', 'absence_type']
    ordering_fields = ['date', 'created_at']
    
    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)

class GradeViewSet(viewsets.ModelViewSet):
    """
    Qiymət API endpoint
    """
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'subject', 'grade_type', 'date']
    ordering_fields = ['date', 'grade', 'created_at']
    
    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)
