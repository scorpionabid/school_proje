from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Avg, Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from ..models import School, Student, ClassRoom, Attendance, Grade
from ..forms import ClassRoomForm

class ClassRoomListView(LoginRequiredMixin, ListView):
    """
    Siniflərin siyahısı
    """
    model = ClassRoom
    template_name = 'school/settings/classroom_list.html'
    context_object_name = 'classes'
    paginate_by = 20

    def get_queryset(self):
        queryset = ClassRoom.objects.filter(school=self.request.user.school_admin.school)
        
        # Filtrlər
        grade = self.request.GET.get('grade')
        language = self.request.GET.get('language')
        
        if grade:
            queryset = queryset.filter(grade=grade)
        if language:
            queryset = queryset.filter(language=language)
        
        # Statistika əlavə et
        queryset = queryset.annotate(
            student_count=Count('students', filter=Q(students__is_active=True))
        )
        
        # Sıralama
        order_by = self.request.GET.get('order_by', 'grade')
        return queryset.order_by(order_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['school'] = self.request.user.school_admin.school
        return context

class ClassRoomDetailView(LoginRequiredMixin, DetailView):
    """
    Sinif detalları
    """
    model = ClassRoom
    template_name = 'school/class_detail.html'
    context_object_name = 'classroom'

    def get_queryset(self):
        return ClassRoom.objects.filter(school=self.request.user.school_admin.school)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        classroom = self.object

        # Şagird statistikası
        context['student_stats'] = {
            'total': classroom.students.filter(is_active=True).count(),
            'male': classroom.students.filter(is_active=True, gender='M').count(),
            'female': classroom.students.filter(is_active=True, gender='F').count(),
        }

        # Davamiyyət statistikası
        context['attendance_stats'] = Attendance.objects.filter(
            student__class_room=classroom,
            student__is_active=True
        ).values('date').annotate(
            present=Count('id', filter=Q(is_present=True)),
            absent=Count('id', filter=Q(is_present=False))
        ).order_by('-date')[:30]

        # Qiymət statistikası
        context['grade_stats'] = Grade.objects.filter(
            student__class_room=classroom,
            student__is_active=True
        ).values('subject').annotate(
            avg_grade=Avg('grade')
        )

        return context

class ClassRoomCreateView(LoginRequiredMixin, CreateView):
    """
    Yeni sinif əlavə etmə
    """
    model = ClassRoom
    form_class = ClassRoomForm
    template_name = 'school/settings/classroom_form.html'
    success_url = reverse_lazy('school:classroom_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = self.request.user.school_admin.school
        return kwargs

    def form_valid(self, form):
        form.instance.school = self.request.user.school_admin.school
        return super().form_valid(form)

class ClassRoomUpdateView(LoginRequiredMixin, UpdateView):
    """
    Sinif məlumatlarının yenilənməsi
    """
    model = ClassRoom
    form_class = ClassRoomForm
    template_name = 'school/settings/classroom_form.html'

    def get_queryset(self):
        return ClassRoom.objects.filter(school=self.request.user.school_admin.school)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = self.request.user.school_admin.school
        return kwargs

    def get_success_url(self):
        return reverse_lazy('school:class_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, _('Sinif məlumatları uğurla yeniləndi.'))
        return super().form_valid(form)

class ClassRoomDeleteView(LoginRequiredMixin, DeleteView):
    """
    Sinifin silinməsi
    """
    model = ClassRoom
    template_name = 'school/class_confirm_delete.html'
    success_url = reverse_lazy('school:classroom_list')

    def get_queryset(self):
        return ClassRoom.objects.filter(school=self.request.user.school_admin.school)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('Sinif uğurla silindi.'))
        return super().delete(request, *args, **kwargs)

class ClassStudentsView(LoginRequiredMixin, ListView):
    """
    Sinif şagirdləri
    """
    model = Student
    template_name = 'school/class_students.html'
    context_object_name = 'students'
    paginate_by = 20

    def get_queryset(self):
        classroom = get_object_or_404(ClassRoom, pk=self.kwargs['pk'])
        return classroom.students.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classroom'] = get_object_or_404(ClassRoom, pk=self.kwargs['pk'])
        return context

class ClassAttendanceView(LoginRequiredMixin, ListView):
    """
    Sinif davamiyyəti
    """
    model = Attendance
    template_name = 'school/class_attendance.html'
    context_object_name = 'attendances'
    paginate_by = 20

    def get_queryset(self):
        classroom = get_object_or_404(ClassRoom, pk=self.kwargs['pk'])
        date = self.request.GET.get('date')
        if date:
            return Attendance.objects.filter(student__class_room=classroom, date=date)
        return Attendance.objects.filter(student__class_room=classroom)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classroom'] = get_object_or_404(ClassRoom, pk=self.kwargs['pk'])
        context['date'] = self.request.GET.get('date')
        return context

class ClassGradesView(LoginRequiredMixin, ListView):
    """
    Sinif qiymətləri
    """
    model = Grade
    template_name = 'school/class_grades.html'
    context_object_name = 'grades'
    paginate_by = 20

    def get_queryset(self):
        classroom = get_object_or_404(ClassRoom, pk=self.kwargs['pk'])
        subject = self.request.GET.get('subject')
        grade_type = self.request.GET.get('grade_type')
        grades = Grade.objects.filter(student__class_room=classroom)
        if subject:
            grades = grades.filter(subject=subject)
        if grade_type:
            grades = grades.filter(grade_type=grade_type)
        return grades

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classroom'] = get_object_or_404(ClassRoom, pk=self.kwargs['pk'])
        return context
