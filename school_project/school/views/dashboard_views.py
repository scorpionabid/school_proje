from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
import json

from ..models import School, Student, Staff, Attendance, Grade

class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Məktəb dashboard view
    """
    template_name = 'school/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        school = self.request.user.school_admin.school
        today = timezone.now().date()
        
        # Statistika kartları üçün məlumatlar
        context['total_students'] = Student.objects.filter(
            school=school, 
            is_active=True
        ).count()
        
        context['total_teachers'] = Staff.objects.filter(
            school=school,
            staff_type='TEACHER',
            is_active=True
        ).count()
        
        # Bu günkü davamiyyət faizi
        today_attendance = Attendance.objects.filter(
            student__school=school,
            date=today
        ).aggregate(
            total=Count('id'),
            present=Count('id', filter=Q(is_present=True))
        )
        
        if today_attendance['total'] > 0:
            context['today_attendance_percent'] = round(
                (today_attendance['present'] / today_attendance['total']) * 100
            )
        else:
            context['today_attendance_percent'] = 0
        
        # Orta qiymət
        context['average_grade'] = round(Grade.objects.filter(
            student__school=school,
            student__is_active=True
        ).aggregate(avg=Avg('grade'))['avg'] or 0, 1)
        
        # Son 7 günün davamiyyət statistikası
        last_7_days = []
        attendance_data = []
        
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            last_7_days.append(date.strftime('%d.%m'))
            
            daily_attendance = Attendance.objects.filter(
                student__school=school,
                date=date
            ).aggregate(
                total=Count('id'),
                present=Count('id', filter=Q(is_present=True))
            )
            
            if daily_attendance['total'] > 0:
                percentage = round(
                    (daily_attendance['present'] / daily_attendance['total']) * 100
                )
            else:
                percentage = 0
                
            attendance_data.append(percentage)
        
        context['last_7_days'] = json.dumps(last_7_days)
        context['attendance_data'] = json.dumps(attendance_data)

        # Son davamiyyətlər
        context['recent_attendances'] = Attendance.objects.filter(
            student__school=school
        ).select_related('student').order_by('-date')[:10]

        # Son qiymətlər
        context['recent_grades'] = Grade.objects.filter(
            student__school=school
        ).select_related('student').order_by('-date')[:10]
        
        return context


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Avg, Q
from core.models import CustomUser
from ..models import School, ClassRoom, Student, Staff, Grade, Attendance

@login_required
def school_dashboard(request):
    """
    Məktəb admin dashboard görünüşü
    """
    if request.user.user_type != CustomUser.UserType.SCHOOL_ADMIN:
        raise PermissionDenied
        
    school = request.user.school
    today = timezone.now().date()
    
    # Əsas statistika
    total_students = Student.objects.filter(school=school).count()
    total_teachers = Staff.objects.filter(school=school, staff_type='TEACHER').count()
    total_classrooms = ClassRoom.objects.filter(school=school).count()
    
    # Son 7 günün davamiyyət trendi
    attendance_trend = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        daily_attendance = Attendance.objects.filter(
            student__school=school,
            date=date
        ).aggregate(
            total=Count('id'),
            present=Count('id', filter=Q(is_present=True))
        )
        
        attendance_rate = 0
        if daily_attendance['total'] > 0:
            attendance_rate = (daily_attendance['present'] / daily_attendance['total']) * 100
            
        attendance_trend.append({
            'date': date,
            'attendance_rate': attendance_rate
        })
    
    # Qiymət statistikası
    grade_stats = []
    for grade in range(1, 13):  # 1-dən 12-yə qədər siniflər
        count = Grade.objects.filter(
            student__school=school,
            grade=grade
        ).count()
        grade_stats.append({
            'grade': str(grade),
            'count': count
        })
    
    context = {
        'school': school,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_classrooms': total_classrooms,
        'attendance_trend': attendance_trend,
        'grade_stats': grade_stats,
        'pending_reports': []  # Gələcəkdə əlavə ediləcək
    }
    
    return render(request, 'school/school_dashboard.html', context)
