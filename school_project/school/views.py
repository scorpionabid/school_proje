from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext as _
from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
)

from core.models import CustomUser
from .models import School, Staff, ClassRoom, Student, Attendance, Grade
from .forms import (
    SchoolForm, StaffForm, ClassRoomForm, StudentForm,
    AttendanceBulkForm, GradeForm
)

# Auth Views
class SchoolLoginView(LoginView):
    template_name = 'school/login.html'
    
    def get_success_url(self):
        return reverse_lazy('school:dashboard')

class SchoolLogoutView(LogoutView):
    next_page = reverse_lazy('school:login')

class SchoolPasswordChangeView(PasswordChangeView):
    template_name = 'school/password_change.html'
    success_url = reverse_lazy('school:password_change_done')

class SchoolPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'school/password_change_done.html'

# Dashboard Views
@login_required
def school_dashboard(request):
    if request.user.user_type != CustomUser.UserType.SCHOOL_ADMIN:
        raise PermissionDenied
    
    school = request.user.school_admin.school
    context = {
        'school': school,
        'class_attendance': [],  # Sinif davamiyyətləri
        'problem_students': [],  # Problem olan şagirdlər
        'recent_grades': [],     # Son qiymətlər
        'attendance_trend': [],  # Davamiyyət trendi
        'grade_stats': []        # Qiymət statistikası
    }
    return render(request, 'school/school_dashboard.html', context)

# Settings Views
@login_required
def school_settings(request):
    if request.user.user_type != CustomUser.UserType.SCHOOL_ADMIN:
        raise PermissionDenied
    
    school = request.user.school_admin.school
    return render(request, 'school/settings/settings.html', {'school': school})

@login_required
def school_profile(request):
    if request.user.user_type != CustomUser.UserType.SCHOOL_ADMIN:
        raise PermissionDenied
    
    school = request.user.school_admin.school
    return render(request, 'school/settings/profile.html', {'school': school})

# Staff Views
class StaffListView(ListView):
    model = Staff
    template_name = 'school/staff_list.html'
    context_object_name = 'staff_list'

    def get_queryset(self):
        return Staff.objects.filter(school=self.request.user.schooladmin.school)
class StaffCreateView(LoginRequiredMixin, CreateView):
    model = Staff
    form_class = StaffForm
    template_name = 'school/staff/form.html'
    success_url = reverse_lazy('school:staff_list')
    
    def form_valid(self, form):
        form.instance.school = self.request.user.school_admin.school
        return super().form_valid(form)

class StaffDetailView(LoginRequiredMixin, DetailView):
    model = Staff
    template_name = 'school/staff/detail.html'
    context_object_name = 'staff'

class StaffUpdateView(LoginRequiredMixin, UpdateView):
    model = Staff
    form_class = StaffForm
    template_name = 'school/staff/form.html'
    success_url = reverse_lazy('school:staff_list')

class StaffDeleteView(LoginRequiredMixin, DeleteView):
    model = Staff
    template_name = 'school/staff/delete.html'
    success_url = reverse_lazy('school:staff_list')

# Settings Staff Views
class SettingsStaffListView(LoginRequiredMixin, ListView):
    model = Staff
    template_name = 'school/settings/staff/list.html'
    context_object_name = 'staff_list'
    
    def get_queryset(self):
        return Staff.objects.filter(school=self.request.user.school_admin.school)

class SettingsStaffCreateView(LoginRequiredMixin, CreateView):
    model = Staff
    form_class = StaffForm
    template_name = 'school/settings/staff/form.html'
    success_url = reverse_lazy('school:settings_staff_list')
    
    def form_valid(self, form):
        form.instance.school = self.request.user.school_admin.school
        return super().form_valid(form)

class SettingsStaffUpdateView(LoginRequiredMixin, UpdateView):
    model = Staff
    form_class = StaffForm
    template_name = 'school/settings/staff/form.html'
    success_url = reverse_lazy('school:settings_staff_list')

class SettingsStaffDeleteView(LoginRequiredMixin, DeleteView):
    model = Staff
    template_name = 'school/settings/staff/delete.html'
    success_url = reverse_lazy('school:settings_staff_list')

# ClassRoom Views
class ClassRoomListView(LoginRequiredMixin, ListView):
    model = ClassRoom
    template_name = 'school/classroom/list.html'
    context_object_name = 'classroom_list'
    
    def get_queryset(self):
        return ClassRoom.objects.filter(school=self.request.user.school_admin.school)

class ClassRoomCreateView(LoginRequiredMixin, CreateView):
    model = ClassRoom
    form_class = ClassRoomForm
    template_name = 'school/classroom/form.html'
    success_url = reverse_lazy('school:classroom_list')
    
    def form_valid(self, form):
        form.instance.school = self.request.user.school_admin.school
        return super().form_valid(form)

class ClassRoomDetailView(LoginRequiredMixin, DetailView):
    model = ClassRoom
    template_name = 'school/classroom/detail.html'
    context_object_name = 'classroom'

class ClassRoomUpdateView(LoginRequiredMixin, UpdateView):
    model = ClassRoom
    form_class = ClassRoomForm
    template_name = 'school/classroom/form.html'
    success_url = reverse_lazy('school:classroom_list')

class ClassRoomDeleteView(LoginRequiredMixin, DeleteView):
    model = ClassRoom
    template_name = 'school/classroom/delete.html'
    success_url = reverse_lazy('school:classroom_list')

class ClassStudentsView(LoginRequiredMixin, DetailView):
    model = ClassRoom
    template_name = 'school/classroom/students.html'
    context_object_name = 'classroom'

# Student Views
class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'school/student/list.html'
    context_object_name = 'student_list'
    
    def get_queryset(self):
        return Student.objects.filter(school=self.request.user.school_admin.school)

class StudentCreateView(LoginRequiredMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'school/student/form.html'
    success_url = reverse_lazy('school:student_list')
    
    def form_valid(self, form):
        form.instance.school = self.request.user.school_admin.school
        return super().form_valid(form)

class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'school/student/detail.html'
    context_object_name = 'student'

class StudentUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'school/student/form.html'
    success_url = reverse_lazy('school:student_list')

class StudentDeleteView(LoginRequiredMixin, DeleteView):
    model = Student
    template_name = 'school/student/delete.html'
    success_url = reverse_lazy('school:student_list')

# Attendance Views
class AttendanceListView(LoginRequiredMixin, ListView):
    model = Attendance
    template_name = 'school/attendance/list.html'
    context_object_name = 'attendance_list'
    
    def get_queryset(self):
        return Attendance.objects.filter(student__school=self.request.user.school_admin.school)

class AttendanceBulkCreateView(LoginRequiredMixin, CreateView):
    model = Attendance
    form_class = AttendanceBulkForm
    template_name = 'school/attendance/bulk_form.html'
    success_url = reverse_lazy('school:attendance_list')

# Grade Views
class GradeKSQView(LoginRequiredMixin, ListView):
    model = Grade
    template_name = 'school/grade/ksq.html'
    context_object_name = 'grade_list'
    
    def get_queryset(self):
        return Grade.objects.filter(
            student__school=self.request.user.school_admin.school,
            grade_type='KSQ'
        )

class GradeBSQView(LoginRequiredMixin, ListView):
    model = Grade
    template_name = 'school/grade/bsq.html'
    context_object_name = 'grade_list'
    
    def get_queryset(self):
        return Grade.objects.filter(
            student__school=self.request.user.school_admin.school,
            grade_type='BSQ'
        )

class GradeMonitoringView(LoginRequiredMixin, ListView):
    model = Grade
    template_name = 'school/grade/monitoring.html'
    context_object_name = 'grade_list'
    
    def get_queryset(self):
        return Grade.objects.filter(
            student__school=self.request.user.school_admin.school,
            grade_type='MONITORING'
        )

class GradeFinalView(LoginRequiredMixin, ListView):
    model = Grade
    template_name = 'school/grade/final.html'
    context_object_name = 'grade_list'
    
    def get_queryset(self):
        return Grade.objects.filter(
            student__school=self.request.user.school_admin.school,
            grade_type='FINAL'
        )
