from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.db.models import Q, Count, Avg
import pandas as pd

from ..models import Student, Attendance, Grade
from ..forms import StudentForm

class StudentListView(LoginRequiredMixin, ListView):
    """
    Student list view
    """
    model = Student
    template_name = 'school/student/student_list.html'
    context_object_name = 'students'
    paginate_by = 20

    def get_queryset(self):
        queryset = Student.objects.filter(school=self.request.user.school_admin.school)
        
        # Axtarış
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(father_name__icontains=search_query) |
                Q(utis_id__icontains=search_query)
            )
        
        # Sinif filtri
        classroom = self.request.GET.get('classroom')
        if classroom:
            queryset = queryset.filter(classroom_id=classroom)
        
        # Status filtri
        is_active = self.request.GET.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active == 'true')
        
        return queryset.order_by('last_name', 'first_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classrooms'] = self.request.user.school_admin.school.classes.all()
        return context

class StudentDetailView(LoginRequiredMixin, DetailView):
    """
    Student detail view
    """
    model = Student
    template_name = 'school/student/student_detail.html'
    context_object_name = 'student'

    def get_queryset(self):
        return Student.objects.filter(school=self.request.user.school_admin.school)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.object

        # Davamiyyət statistikası
        context['attendance_stats'] = Attendance.objects.filter(
            student=student
        ).values('date').annotate(
            present=Count('id', filter=Q(is_present=True)),
            absent=Count('id', filter=Q(is_present=False))
        ).order_by('-date')[:30]

        # Qiymət statistikası
        context['grade_stats'] = Grade.objects.filter(
            student=student
        ).values('grade_type').annotate(
            avg_grade=Avg('grade'),
            total_grades=Count('id')
        )

        # Son qiymətlər
        context['recent_grades'] = Grade.objects.filter(
            student=student
        ).select_related('subject').order_by('-date')[:10]

        return context

class StudentCreateView(LoginRequiredMixin, CreateView):
    """
    Student create view
    """
    model = Student
    form_class = StudentForm
    template_name = 'school/student/student_form.html'
    success_url = reverse_lazy('school:student_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = self.request.user.school_admin.school
        return kwargs

    def form_valid(self, form):
        form.instance.school = self.request.user.school_admin.school
        messages.success(self.request, _('Şagird uğurla əlavə edildi.'))
        return super().form_valid(form)

class StudentUpdateView(LoginRequiredMixin, UpdateView):
    """
    Student update view
    """
    model = Student
    form_class = StudentForm
    template_name = 'school/student/student_form.html'

    def get_queryset(self):
        return Student.objects.filter(school=self.request.user.school_admin.school)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = self.request.user.school_admin.school
        return kwargs

    def get_success_url(self):
        return reverse_lazy('school:student_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, _('Şagird məlumatları uğurla yeniləndi.'))
        return super().form_valid(form)

class StudentDeleteView(LoginRequiredMixin, DeleteView):
    """
    Student delete view
    """
    model = Student
    template_name = 'school/student/student_confirm_delete.html'
    success_url = reverse_lazy('school:student_list')

    def get_queryset(self):
        return Student.objects.filter(school=self.request.user.school_admin.school)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('Şagird uğurla silindi.'))
        return super().delete(request, *args, **kwargs)

@login_required
def export_students_excel(request):
    """
    Export students to excel
    """
    # TODO: Implement excel export
    messages.warning(request, _('Bu funksiya hələ hazır deyil.'))
    return render(request, 'school/student/student_list.html')

@login_required
def import_students_excel(request):
    """
    Excel faylından şagirdləri idxal edir
    """
    if request.method == 'POST' and request.FILES.get('excel_file'):
        try:
            # Excel faylını oxu
            excel_file = request.FILES['excel_file']
            df = pd.read_excel(excel_file)
            
            # Məlumatları yoxla və əlavə et
            success_count = 0
            error_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # Məcburi sahələri yoxla
                    if not all([row['first_name'], row['last_name'], row['father_name']]):
                        raise ValueError(_('Ad, soyad və ata adı məcburidir'))
                    
                    # Şagirdi əlavə et
                    student = Student(
                        school=request.user.school_admin.school,
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        father_name=row['father_name'],
                        gender=row.get('gender', 'M'),
                        birth_date=row.get('birth_date'),
                        utis_id=row.get('utis_id'),
                        classroom_id=row.get('classroom_id'),
                        is_active=True
                    )
                    student.save()
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    errors.append(f"Sətir {index + 2}: {str(e)}")
            
            # Nəticəni göstər
            if success_count > 0:
                messages.success(request, _(f'{success_count} şagird uğurla əlavə edildi'))
            if error_count > 0:
                messages.error(request, _(f'{error_count} şagird əlavə edilə bilmədi'))
                for error in errors:
                    messages.error(request, error)
                    
        except Exception as e:
            messages.error(request, str(e))
    
    return redirect('school:student_list')
