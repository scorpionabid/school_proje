from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Count
from django import forms
from django.db import models

from ..models import School, ClassRoom, Student, SchoolAdmin, Staff
from core.models import CustomUser
from ..forms import ClassRoomForm, StudentForm, SchoolForm, StaffForm

@login_required
def settings_view(request):
    """
    Settings view
    """
    school = request.user.school
    context = {
        'school': school,
        'staff_count': Staff.objects.filter(school=school).count(),
        'student_count': Student.objects.filter(school=school).count(),
        'classroom_count': ClassRoom.objects.filter(school=school).count(),
    }
    return render(request, 'school/settings/settings.html', context)

class SchoolUpdateView(LoginRequiredMixin, UpdateView):
    """
    School update view
    """
    model = School
    fields = ['name', 'address', 'phone', 'email']
    template_name = 'school/settings/school_form.html'
    success_url = reverse_lazy('school:settings')

    def get_object(self, queryset=None):
        return self.request.user.school

    def form_valid(self, form):
        messages.success(self.request, _('Məktəb məlumatları uğurla yeniləndi.'))
        return super().form_valid(form)

@login_required
def school_profile(request):
    """
    Məktəb profili səhifəsi
    """
    school = request.user.school_admin.school
    if request.method == 'POST':
        form = SchoolForm(request.POST, instance=school)
        if form.is_valid():
            form.save()
            messages.success(request, _('Məktəb məlumatları uğurla yeniləndi.'))
    else:
        form = SchoolForm(instance=school)
    
    context = {
        'form': form,
        'school': school
    }
    return render(request, 'school/settings/school_profile.html', context)

class StaffListView(LoginRequiredMixin, ListView):
    """
    İşçilərin siyahısı
    """
    model = Staff
    template_name = 'school/settings/staff_list.html'
    context_object_name = 'staff_list'
    paginate_by = 10

    def get_queryset(self):
        queryset = Staff.objects.filter(school=self.request.user.school_admin.school)
        
        # Axtarış
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(position__icontains=search_query) |
                Q(staff_type__icontains=search_query)
            )
        
        # Filtrlər
        staff_type = self.request.GET.get('staff_type')
        if staff_type:
            queryset = queryset.filter(staff_type=staff_type)
            
        is_active = self.request.GET.get('is_active')
        if is_active is not None:
            is_active = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active)
        
        # Sıralama
        order_by = self.request.GET.get('order_by', 'user__last_name')
        queryset = queryset.order_by(order_by)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['staff_types'] = Staff.STAFF_TYPES
        context['current_staff_type'] = self.request.GET.get('staff_type', '')
        context['current_is_active'] = self.request.GET.get('is_active', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context

class StaffCreateView(LoginRequiredMixin, CreateView):
    """
    Yeni işçi əlavə etmə
    """
    model = Staff
    form_class = StaffForm
    template_name = 'school/settings/staff_form.html'
    success_url = reverse_lazy('school:staff_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = self.request.user.school_admin.school
        return kwargs

    def form_valid(self, form):
        form.instance.school = self.request.user.school_admin.school
        response = super().form_valid(form)
        messages.success(self.request, _('İşçi uğurla əlavə edildi.'))
        return response

class StaffUpdateView(LoginRequiredMixin, UpdateView):
    """
    İşçi məlumatlarının yenilənməsi
    """
    model = Staff
    form_class = StaffForm
    template_name = 'school/settings/staff_form.html'
    success_url = reverse_lazy('school:staff_list')

    def get_queryset(self):
        return Staff.objects.filter(school=self.request.user.school_admin.school)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = self.request.user.school_admin.school
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('İşçi məlumatları uğurla yeniləndi.'))
        return response

class StaffDeleteView(LoginRequiredMixin, DeleteView):
    """
    İşçinin silinməsi
    """
    model = Staff
    template_name = 'school/settings/staff_confirm_delete.html'
    success_url = reverse_lazy('school:staff_list')

    def get_queryset(self):
        return Staff.objects.filter(school=self.request.user.school_admin.school)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('İşçi uğurla silindi.'))
        return super().delete(request, *args, **kwargs)

class ClassRoomListView(LoginRequiredMixin, ListView):
    """
    Siniflərin siyahısı
    """
    model = ClassRoom
    template_name = 'school/settings/classroom_list.html'
    context_object_name = 'classroom_list'
    paginate_by = 10

    def get_queryset(self):
        import logging
        logger = logging.getLogger(__name__)
        
        # Debug məlumatı - istifadəçi və məktəb
        logger.debug(f"User: {self.request.user}")
        logger.debug(f"Is school admin: {hasattr(self.request.user, 'school_admin')}")
        if hasattr(self.request.user, 'school_admin'):
            logger.debug(f"School: {self.request.user.school_admin.school}")
            logger.debug(f"School ID: {self.request.user.school_admin.school.id}")

        # Əsas sorğu
        queryset = ClassRoom.objects.select_related('class_teacher__user', 'school').filter(
            school=self.request.user.school_admin.school
        ).annotate(
            current_students=models.Count('students', filter=models.Q(students__is_active=True))
        )

        # Debug məlumatı - siniflər
        logger.debug(f"Found {queryset.count()} classrooms")
        for classroom in queryset:
            logger.debug(f"Classroom: {classroom.grade}-{classroom.division}, Teacher: {classroom.class_teacher}, School: {classroom.school}")

        # SQL sorğusunu göstər
        logger.debug(f"SQL Query: {str(queryset.query)}")
        
        # Axtarış
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                models.Q(grade__icontains=search_query) |
                models.Q(division__icontains=search_query) |
                models.Q(class_teacher__user__first_name__icontains=search_query) |
                models.Q(class_teacher__user__last_name__icontains=search_query)
            )
        
        # Filtrlər
        grade = self.request.GET.get('grade')
        if grade:
            queryset = queryset.filter(grade=grade)
            
        is_active = self.request.GET.get('is_active')
        if is_active is not None:
            is_active = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active)
        
        # Sıralama
        order_by = self.request.GET.get('order_by', 'grade')
        if order_by == 'class_teacher':
            queryset = queryset.order_by('class_teacher__user__last_name', 'class_teacher__user__first_name')
        else:
            queryset = queryset.order_by('grade', 'division')
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Sinif seçimləri üçün sözlük
        grades = [(str(i), str(i)) for i in range(1, 13)]
        context['grades'] = grades
        context['current_grade'] = self.request.GET.get('grade', '')
        context['current_is_active'] = self.request.GET.get('is_active', '')
        context['search_query'] = self.request.GET.get('search', '')
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
        response = super().form_valid(form)
        messages.success(self.request, _('Sinif uğurla əlavə edildi.'))
        return response

class ClassRoomUpdateView(LoginRequiredMixin, UpdateView):
    """
    Sinif məlumatlarının yenilənməsi
    """
    model = ClassRoom
    form_class = ClassRoomForm
    template_name = 'school/settings/classroom_form.html'
    success_url = reverse_lazy('school:classroom_list')

    def get_queryset(self):
        return ClassRoom.objects.filter(school=self.request.user.school_admin.school)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = self.request.user.school_admin.school
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        # Update school statistics after saving classroom
        self.object.school.update_statistics()
        messages.success(self.request, _('Sinif məlumatları uğurla yeniləndi.'))
        return response

class ClassRoomDeleteView(LoginRequiredMixin, DeleteView):
    """
    Sinifin silinməsi
    """
    model = ClassRoom
    template_name = 'school/settings/classroom_confirm_delete.html'
    success_url = reverse_lazy('school:classroom_list')

    def get_queryset(self):
        return ClassRoom.objects.filter(school=self.request.user.school_admin.school)

    def delete(self, request, *args, **kwargs):
        classroom = self.get_object()
        school = classroom.school
        response = super().delete(request, *args, **kwargs)
        # Məktəb statistikasını yenilə
        school.update_statistics()
        messages.success(request, _('Sinif uğurla silindi.'))
        return response
