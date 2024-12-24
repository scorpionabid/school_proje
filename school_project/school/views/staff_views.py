from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext as _
from django.db.models import Count
from django.db.models import Q
from django.core.exceptions import PermissionDenied

from core.models import CustomUser
from ..models import Staff
from ..forms import StaffForm

class SchoolStaffListView(LoginRequiredMixin, ListView):
    """
    Staff list view
    """
    model = Staff
    template_name = 'school/staff/staff_list.html'
    context_object_name = 'staff_list'
    paginate_by = 20

    def get_queryset(self):
        queryset = Staff.objects.filter(school=self.request.user.school)

        # Axtarış
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(position__icontains=search_query)
            )

        # Status filtri
        is_active = self.request.GET.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active == 'true')

        return queryset.order_by('user__last_name', 'user__first_name')

class StaffDetailView(LoginRequiredMixin, DetailView):
    """
    Staff detail view
    """
    model = Staff
    template_name = 'school/staff/staff_detail.html'
    context_object_name = 'staff'

    def get_queryset(self):
        return Staff.objects.filter(school=self.request.user.school)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        staff = self.object

        # Sinif rəhbərliyi
        context['classroom'] = staff.classroom_set.first()

        # Tədris etdiyi fənlər
        context['subjects'] = staff.subject_set.all()

        # Tədris etdiyi siniflər
        context['teaching_classes'] = staff.teaching_classes.all()

        return context

class StaffCreateView(LoginRequiredMixin, CreateView):
    """
    Staff create view
    """
    model = Staff
    form_class = StaffForm
    template_name = 'school/staff/staff_form.html'
    success_url = reverse_lazy('school:staff_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = self.request.user.school
        return kwargs

    def form_valid(self, form):
        form.instance.school = self.request.user.school
        messages.success(self.request, _('İşçi uğurla əlavə edildi.'))
        return super().form_valid(form)

class StaffUpdateView(LoginRequiredMixin, UpdateView):
    """
    Staff update view
    """
    model = Staff
    form_class = StaffForm
    template_name = 'school/staff/staff_form.html'

    def get_queryset(self):
        return Staff.objects.filter(school=self.request.user.school)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = self.request.user.school
        return kwargs

    def get_success_url(self):
        return reverse_lazy('school:staff_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, _('İşçi məlumatları uğurla yeniləndi.'))
        return super().form_valid(form)

class StaffDeleteView(LoginRequiredMixin, DeleteView):
    """
    Staff delete view
    """
    model = Staff
    template_name = 'school/staff/staff_confirm_delete.html'
    success_url = reverse_lazy('school:staff_list')

    def get_queryset(self):
        return Staff.objects.filter(school=self.request.user.school)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('İşçi uğurla silindi.'))
        return super().delete(request, *args, **kwargs)

class SettingsStaffListView(LoginRequiredMixin, ListView):
    """İşçilərin siyahısı (Ayarlar səhifəsi üçün)"""
    model = Staff
    template_name = 'school/settings/staff_list.html'
    context_object_name = 'staff_list'
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.user_type != CustomUser.UserType.SCHOOL_ADMIN:
            raise PermissionDenied
        return Staff.objects.filter(school=self.request.user.school)

class SettingsStaffCreateView(LoginRequiredMixin, CreateView):
    """Yeni işçi əlavə etmə (Ayarlar səhifəsi üçün)"""
    model = Staff
    template_name = 'school/settings/staff_form.html'
    form_class = StaffForm
    success_url = reverse_lazy('school:settings_staff_list')

    def form_valid(self, form):
        if self.request.user.user_type != CustomUser.UserType.SCHOOL_ADMIN:
            raise PermissionDenied
        form.instance.school = self.request.user.school
        messages.success(self.request, _('İşçi uğurla əlavə edildi'))
        return super().form_valid(form)

class SettingsStaffUpdateView(LoginRequiredMixin, UpdateView):
    """İşçi məlumatlarının yenilənməsi (Ayarlar səhifəsi üçün)"""
    model = Staff
    template_name = 'school/settings/staff_form.html'
    form_class = StaffForm
    success_url = reverse_lazy('school:settings_staff_list')

    def get_queryset(self):
        if self.request.user.user_type != CustomUser.UserType.SCHOOL_ADMIN:
            raise PermissionDenied
        return Staff.objects.filter(school=self.request.user.school)

    def form_valid(self, form):
        messages.success(self.request, _('İşçi məlumatları uğurla yeniləndi'))
        return super().form_valid(form)

class SettingsStaffDeleteView(LoginRequiredMixin, DeleteView):
    """İşçinin silinməsi (Ayarlar səhifəsi üçün)"""
    model = Staff
    template_name = 'school/settings/staff_confirm_delete.html'
    success_url = reverse_lazy('school:settings_staff_list')

    def get_queryset(self):
        if self.request.user.user_type != CustomUser.UserType.SCHOOL_ADMIN:
            raise PermissionDenied
        return Staff.objects.filter(school=self.request.user.school)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('İşçi uğurla silindi'))
        return super().delete(request, *args, **kwargs)
