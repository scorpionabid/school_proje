from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Avg
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from ..models import School, Student, ClassRoom, Attendance, Grade
from ..forms import SchoolForm

class SchoolListView(LoginRequiredMixin, ListView):
    """
    Məktəblərin siyahısı
    """
    model = School
    template_name = 'school/school_list.html'
    context_object_name = 'schools'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = School.objects.all()
        
        # Filtrlər
        school_type = self.request.GET.get('school_type')
        sector = self.request.GET.get('sector')
        is_active = self.request.GET.get('is_active')
        search = self.request.GET.get('search')
        
        if school_type:
            queryset = queryset.filter(school_type=school_type)
        if sector:
            queryset = queryset.filter(sector_id=sector)
        if is_active:
            queryset = queryset.filter(is_active=is_active == 'true')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        # Sıralama
        order_by = self.request.GET.get('order_by', 'name')
        return queryset.order_by(order_by)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['school_types'] = School.SCHOOL_TYPES
        return context

class SchoolCreateView(LoginRequiredMixin, CreateView):
    """
    Məktəb yaratma
    """
    model = School
    form_class = SchoolForm
    template_name = 'school/school_form.html'
    success_url = reverse_lazy('school:school_list')
    
    def form_valid(self, form):
        messages.success(self.request, _('Məktəb yaradıldı.'))
        return super().form_valid(form)

class SchoolDetailView(LoginRequiredMixin, DetailView):
    """
    Məktəb detalları
    """
    model = School
    template_name = 'school/school_detail.html'
    context_object_name = 'school'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        school = self.object
        
        # Statistika
        context.update({
            'total_students': school.students.filter(is_active=True).count(),
            'total_teachers': school.teachers.filter(is_active=True).count(),
            'total_classes': school.classes.count(),
            'class_stats': school.classes.values('grade').annotate(
                total=Count('students')
            ).order_by('grade'),
            'attendance_stats': Attendance.objects.filter(
                student__school=school,
                student__is_active=True
            ).values('is_present').annotate(
                total=Count('id')
            ),
            'grade_stats': Grade.objects.filter(
                student__school=school,
                student__is_active=True
            ).aggregate(
                avg_grade=Avg('grade')
            ),
        })
        
        return context

class SchoolUpdateView(LoginRequiredMixin, UpdateView):
    """
    Məktəb redaktəsi
    """
    model = School
    form_class = SchoolForm
    template_name = 'school/school_form.html'
    
    def get_success_url(self):
        return reverse_lazy('school:school_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, _('Məktəb məlumatları yeniləndi.'))
        return super().form_valid(form)

class SchoolDeleteView(LoginRequiredMixin, DeleteView):
    """
    Məktəb silmə
    """
    model = School
    template_name = 'school/school_confirm_delete.html'
    success_url = reverse_lazy('school:school_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Məktəb silindi.'))
        return super().delete(request, *args, **kwargs)

class SchoolDashboardView(LoginRequiredMixin, DetailView):
    """
    Məktəb dashboard
    """
    model = School
    template_name = 'school/school_dashboard.html'
    context_object_name = 'school'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        school = self.object
        
        # Son əlavə edilən şagirdlər
        context['recent_students'] = school.students.order_by('-created_at')[:5]
        
        # Son davamiyyət
        context['recent_attendance'] = Attendance.objects.filter(
            student__school=school
        ).select_related('student').order_by('-date')[:10]
        
        # Son qiymətlər
        context['recent_grades'] = Grade.objects.filter(
            student__school=school
        ).select_related('student').order_by('-date')[:10]
        
        # Sinif statistikası
        context['class_stats'] = school.classes.values('grade').annotate(
            total_students=Count('students')
        ).order_by('grade')
        
        return context

class SchoolStatisticsView(LoginRequiredMixin, DetailView):
    """
    Məktəb statistikaları
    """
    model = School
    template_name = 'school/school_statistics.html'
    context_object_name = 'school'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        school = self.object
        
        # Ümumi statistika
        context['total_students'] = school.students.filter(is_active=True).count()
        context['total_teachers'] = school.teachers.filter(is_active=True).count()
        context['total_classes'] = school.classes.count()
        
        # Sinif statistikası
        context['class_stats'] = school.classes.values('grade').annotate(
            total_students=Count('students', filter=models.Q(students__is_active=True)),
            avg_attendance=Avg('students__attendances__is_present', filter=models.Q(students__is_active=True)),
            avg_grade=Avg('students__grades__grade', filter=models.Q(students__is_active=True))
        ).order_by('grade')
        
        # Davamiyyət statistikası
        context['attendance_stats'] = Attendance.objects.filter(
            student__school=school,
            student__is_active=True
        ).values('date').annotate(
            present=Count('id', filter=models.Q(is_present=True)),
            absent=Count('id', filter=models.Q(is_present=False))
        ).order_by('-date')[:30]
        
        # Qiymət statistikası
        context['grade_stats'] = Grade.objects.filter(
            student__school=school,
            student__is_active=True
        ).values('grade_type').annotate(
            avg_grade=Avg('grade'),
            total_grades=Count('id')
        )
        
        return context
