from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.core.paginator import Paginator
from .models import School, ClassRoom, Student, SchoolAdmin, Staff, CustomUser
from .forms import ClassRoomForm, StudentForm, SchoolForm, StaffForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from django import forms

@login_required
def school_settings(request):
    """
    Məktəb ayarları səhifəsi
    """
    if not hasattr(request.user, 'school_admin'):
        messages.error(request, _('Bu səhifəyə yalnız məktəb administratorları daxil ola bilər'))
        return redirect('dashboard')
    
    school = request.user.school_admin.school
    classes = ClassRoom.objects.filter(school=school).order_by('grade', 'division')
    students = Student.objects.filter(school=school).order_by('last_name', 'first_name')
    
    context = {
        'school': school,
        'total_students': school.students.count(),
        'total_teachers': school.staff_members.filter(staff_type='TEACHER').count(),
        'total_classes': school.classes.count(),
        'classes': classes,
        'students': students,
    }
    return render(request, 'school/settings/dashboard.html', context)

@login_required
def school_profile(request):
    """
    Məktəb profili səhifəsi
    """
    if not hasattr(request.user, 'school_admin'):
        messages.error(request, _('Bu səhifəyə yalnız məktəb administratorları daxil ola bilər'))
        return redirect('dashboard')
    
    school = request.user.school_admin.school
    if request.method == 'POST':
        form = SchoolForm(request.POST, instance=school)
        if form.is_valid():
            form.save()
            messages.success(request, _('Məktəb məlumatları uğurla yeniləndi'))
            return redirect('school:settings')
    else:
        form = SchoolForm(instance=school)
    
    context = {
        'form': form,
        'school': school,
    }
    return render(request, 'school/settings/school_profile.html', context)

class ClassRoomListView(LoginRequiredMixin, ListView):
    model = ClassRoom
    template_name = 'school/settings/classroom_list.html'
    context_object_name = 'classes'
    paginate_by = 10

    def get_queryset(self):
        return ClassRoom.objects.filter(school=self.request.user.school_admin.school)

class ClassRoomCreateView(LoginRequiredMixin, CreateView):
    model = ClassRoom
    form_class = ClassRoomForm
    template_name = 'school/settings/classroom_form.html'
    success_url = reverse_lazy('school:classroom_list')

    def form_valid(self, form):
        form.instance.school = self.request.user.school_admin.school
        messages.success(self.request, _('Sinif uğurla yaradıldı'))
        return super().form_valid(form)

class ClassRoomUpdateView(LoginRequiredMixin, UpdateView):
    model = ClassRoom
    form_class = ClassRoomForm
    template_name = 'school/settings/classroom_form.html'
    success_url = reverse_lazy('school:classroom_list')

    def get_queryset(self):
        return ClassRoom.objects.filter(school=self.request.user.school_admin.school)

    def form_valid(self, form):
        messages.success(self.request, _('Sinif uğurla yeniləndi'))
        return super().form_valid(form)

class ClassRoomDeleteView(LoginRequiredMixin, DeleteView):
    model = ClassRoom
    template_name = 'school/settings/classroom_confirm_delete.html'
    success_url = reverse_lazy('school:classroom_list')

    def get_queryset(self):
        return ClassRoom.objects.filter(school=self.request.user.school_admin.school)

    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Sinif uğurla silindi'))
        return super().delete(request, *args, **kwargs)

# Student Views
class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'school/settings/student_list.html'
    context_object_name = 'students'
    paginate_by = 20

    def get_queryset(self):
        return Student.objects.filter(school=self.request.user.school_admin.school)

class StudentCreateView(LoginRequiredMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'school/settings/student_form.html'
    success_url = reverse_lazy('school:student_list')

    def form_valid(self, form):
        form.instance.school = self.request.user.school_admin.school
        messages.success(self.request, _('Şagird uğurla əlavə edildi'))
        return super().form_valid(form)

class StudentUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'school/settings/student_form.html'
    success_url = reverse_lazy('school:student_list')

    def get_queryset(self):
        return Student.objects.filter(school=self.request.user.school_admin.school)

    def form_valid(self, form):
        messages.success(self.request, _('Şagird məlumatları uğurla yeniləndi'))
        return super().form_valid(form)

class StudentDeleteView(LoginRequiredMixin, DeleteView):
    model = Student
    template_name = 'school/settings/student_confirm_delete.html'
    success_url = reverse_lazy('school:student_list')

    def get_queryset(self):
        return Student.objects.filter(school=self.request.user.school_admin.school)

    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Şagird uğurla silindi'))
        return super().delete(request, *args, **kwargs)

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
    template_name = 'school/settings/staff_form.html'
    form_class = StaffForm
    success_url = reverse_lazy('school:staff_list')

    def form_valid(self, form):
        # İstifadəçi yaratma
        user = CustomUser.objects.create(
            username=form.cleaned_data['email'],
            email=form.cleaned_data['email'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            is_staff=True
        )
        user.set_password(form.cleaned_data['password'])
        user.save()
        
        # İşçi yaratma
        staff = form.save(commit=False)
        staff.user = user
        staff.school = self.request.user.school_admin.school
        staff.save()
        
        messages.success(self.request, _('İşçi uğurla əlavə edildi.'))
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['email'] = forms.EmailField(label=_('E-poçt'))
        form.fields['first_name'] = forms.CharField(label=_('Ad'))
        form.fields['last_name'] = forms.CharField(label=_('Soyad'))
        form.fields['password'] = forms.CharField(
            label=_('Şifrə'),
            widget=forms.PasswordInput
        )
        return form

class StaffUpdateView(LoginRequiredMixin, UpdateView):
    """
    İşçi məlumatlarının yenilənməsi
    """
    model = Staff
    template_name = 'school/settings/staff_form.html'
    form_class = StaffForm
    success_url = reverse_lazy('school:staff_list')

    def get_queryset(self):
        return Staff.objects.filter(school=self.request.user.school_admin.school)

    def form_valid(self, form):
        messages.success(self.request, _('İşçi məlumatları uğurla yeniləndi.'))
        return super().form_valid(form)

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
