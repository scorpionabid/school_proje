from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Count, Q, Avg
from django.utils import timezone
from django.db import transaction
from django.views.generic import (
    TemplateView, CreateView, UpdateView, DeleteView,
    DetailView, ListView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
import json
import datetime

from ..models import Attendance, Student, ClassRoom
from ..forms import AttendanceForm, AttendanceFilterForm

class AttendanceCreateView(LoginRequiredMixin, CreateView):
    """
    Davamiyyət yaratma
    """
    model = Attendance
    form_class = AttendanceForm
    template_name = 'school/attendance/attendance_form.html'

    def get_initial(self):
        initial = super().get_initial()
        student_id = self.request.GET.get('student')
        if student_id:
            student = get_object_or_404(Student, pk=student_id)
            initial['student'] = student
        return initial

    def form_valid(self, form):
        attendance = form.instance
        attendance.recorded_by = self.request.user
        
        # Eyni tarixdə təkrar qeyd yoxla
        existing = Attendance.objects.filter(
            student=attendance.student,
            date=attendance.date
        ).first()
        
        if existing:
            messages.error(self.request, _('Bu tarixdə artıq davamiyyət qeydi mövcuddur.'))
            return redirect('school:student_attendance', pk=attendance.student.pk)
        
        response = super().form_valid(form)
        messages.success(self.request, _('Davamiyyət qeydi əlavə edildi.'))
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        return response

    def get_success_url(self):
        return reverse_lazy('school:student_attendance', kwargs={'pk': self.object.student.pk})

    def get_template_names(self):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return ['school/includes/attendance_form.html']
        return [self.template_name]

class AttendanceUpdateView(LoginRequiredMixin, UpdateView):
    """
    Davamiyyət redaktəsi
    """
    model = Attendance
    form_class = AttendanceForm
    template_name = 'school/attendance/attendance_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Davamiyyət qeydi yeniləndi.'))
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        return response

    def get_success_url(self):
        return reverse_lazy('school:student_attendance', kwargs={'pk': self.object.student.pk})

    def get_template_names(self):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return ['school/includes/attendance_form.html']
        return [self.template_name]

class AttendanceDeleteView(LoginRequiredMixin, DeleteView):
    """
    Davamiyyət silmə
    """
    model = Attendance
    template_name = 'school/attendance/attendance_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, _('Davamiyyət qeydi silindi.'))
        return response

    def get_success_url(self):
        return reverse_lazy('school:student_attendance', kwargs={'pk': self.object.student.pk})

class AttendanceBulkCreateView(LoginRequiredMixin, TemplateView):
    """
    Toplu davamiyyət yaratma
    """
    template_name = 'school/attendance/bulk_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        school = self.request.user.school_admin.school
        classrooms = ClassRoom.objects.filter(
            school=school,
            is_active=True
        ).select_related('class_teacher')
        context['classrooms'] = classrooms
        return context

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            date = data.get('date')
            attendance_data = data.get('attendance', [])
            
            if not date:
                return JsonResponse({
                    'status': 'error',
                    'message': _('Tarix tələb olunur')
                })

            school = request.user.school_admin.school
            
            # Convert date string to date object
            date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
            
            # Create attendance records
            with transaction.atomic():
                # Delete existing records for this date and school
                Attendance.objects.filter(
                    student__class_room__school=school,
                    date=date
                ).delete()
                
                # Create new records
                for classroom_data in attendance_data:
                    classroom_id = classroom_data.get('classroom_id')
                    present = classroom_data.get('present', 0)
                    excused = classroom_data.get('excused', 0)
                    unexcused = classroom_data.get('unexcused', 0)
                    note = classroom_data.get('note', '')
                    
                    classroom = get_object_or_404(ClassRoom, pk=classroom_id, school=school)
                    students = Student.objects.filter(class_room=classroom, is_active=True)
                    
                    # Create present records
                    for student in students[:present]:
                        Attendance.objects.create(
                            student=student,
                            date=date,
                            is_present=True,
                            note=note,
                            recorded_by=request.user
                        )
                    
                    # Create excused absence records
                    for student in students[present:present+excused]:
                        Attendance.objects.create(
                            student=student,
                            date=date,
                            is_present=False,
                            absence_type='excused',
                            note=note,
                            recorded_by=request.user
                        )
                    
                    # Create unexcused absence records
                    for student in students[present+excused:present+excused+unexcused]:
                        Attendance.objects.create(
                            student=student,
                            date=date,
                            is_present=False,
                            absence_type='unexcused',
                            note=note,
                            recorded_by=request.user
                        )

            return JsonResponse({
                'status': 'success',
                'message': _('Davamiyyət uğurla qeyd edildi')
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

class GeneralAttendanceView(LoginRequiredMixin, TemplateView):
    template_name = 'school/attendance/general.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date = self.request.GET.get('date', timezone.now().date())
        if isinstance(date, str):
            date = datetime.datetime.strptime(date, '%Y-%m-%d').date()

        school = self.request.user.school_admin.school
        classrooms = ClassRoom.objects.filter(
            school=school,
            is_active=True
        ).select_related(
            'class_teacher'
        ).annotate(
            student_count=Count('students', filter=Q(students__is_active=True))
        )

        # Get attendance stats for each classroom
        for classroom in classrooms:
            attendance_stats = Attendance.objects.filter(
                student__class_room=classroom,
                date=date
            ).aggregate(
                present=Count('id', filter=Q(is_present=True)),
                excused=Count('id', filter=Q(is_present=False, absence_type='excused')),
                unexcused=Count('id', filter=Q(is_present=False, absence_type='unexcused')),
            )
            classroom.attendance_stats = attendance_stats

        context.update({
            'date': date,
            'classrooms': classrooms,
            'total_students': sum(c.current_students for c in classrooms),
            'total_present': sum(c.attendance_stats['present'] for c in classrooms),
            'total_excused': sum(c.attendance_stats['excused'] for c in classrooms),
            'total_unexcused': sum(c.attendance_stats['unexcused'] for c in classrooms),
        })
        return context

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            classroom_id = data.get('classroom_id')
            present = int(data.get('present', 0))
            excused = int(data.get('excused', 0))
            unexcused = int(data.get('unexcused', 0))
            note = data.get('note', '')
            date = data.get('date', timezone.now().date())

            if isinstance(date, str):
                date = datetime.datetime.strptime(date, '%Y-%m-%d').date()

            classroom = ClassRoom.objects.get(id=classroom_id, school=request.user.school_admin.school)
            
            # Validate total count
            if present + excused + unexcused > classroom.current_students:
                return JsonResponse({
                    'status': 'error',
                    'message': _('Toplam sayı sinif tutumundan çox ola bilməz')
                })

            # Update or create attendance records
            with transaction.atomic():
                # Reset all attendance records for the classroom on this date
                Attendance.objects.filter(
                    student__class_room=classroom,
                    date=date
                ).delete()

                # Create new attendance records
                students = classroom.students.filter(is_active=True)
                
                # Mark students as present
                present_students = students[:present]
                Attendance.objects.bulk_create([
                    Attendance(
                        student=student,
                        date=date,
                        is_present=True,
                        recorded_by=request.user
                    ) for student in present_students
                ])

                # Mark students as excused
                excused_students = students[present:present+excused]
                Attendance.objects.bulk_create([
                    Attendance(
                        student=student,
                        date=date,
                        is_present=False,
                        absence_type='excused',
                        note=note,
                        recorded_by=request.user
                    ) for student in excused_students
                ])

                # Mark students as unexcused
                unexcused_students = students[present+excused:present+excused+unexcused]
                Attendance.objects.bulk_create([
                    Attendance(
                        student=student,
                        date=date,
                        is_present=False,
                        absence_type='unexcused',
                        note=note,
                        recorded_by=request.user
                    ) for student in unexcused_students
                ])

            return JsonResponse({
                'status': 'success',
                'message': _('Davamiyyət uğurla yeniləndi')
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

class AttendanceDetailView(LoginRequiredMixin, DetailView):
    """
    Detallı davamiyyət səhifəsi
    """
    model = Student
    template_name = 'school/attendance/detail.html'
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.object
        
        # Get date range from request or use current month
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        if start_date and end_date:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            today = timezone.now().date()
            start_date = today.replace(day=1)
            end_date = today
        
        # Get attendance records
        attendance_records = Attendance.objects.filter(
            student=student,
            date__range=(start_date, end_date)
        ).select_related('recorded_by').order_by('-date')
        
        # Calculate statistics
        total_days = (end_date - start_date).days + 1
        present_days = attendance_records.filter(is_present=True).count()
        excused_days = attendance_records.filter(is_present=False, absence_type='excused').count()
        unexcused_days = attendance_records.filter(is_present=False, absence_type='unexcused').count()
        
        context.update({
            'start_date': start_date,
            'end_date': end_date,
            'attendance_records': attendance_records,
            'total_days': total_days,
            'present_days': present_days,
            'excused_days': excused_days,
            'unexcused_days': unexcused_days,
            'attendance_rate': round(present_days / total_days * 100, 1) if total_days > 0 else 0
        })
        return context

class AttendanceClassDetailView(LoginRequiredMixin, DetailView):
    """
    Sinif üzrə detallı davamiyyət məlumatları
    """
    model = ClassRoom
    template_name = 'school/attendance/class_detail.html'
    context_object_name = 'classroom'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        classroom = self.object
        
        # Get date from request or use today
        date = self.request.GET.get('date', timezone.now().date())
        if isinstance(date, str):
            date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        
        # Get all students in the classroom
        students = classroom.students.filter(is_active=True)
        
        # Get attendance records for the date
        attendance_records = Attendance.objects.filter(
            student__in=students,
            date=date
        ).select_related('student')
        
        # Create a dictionary for easy lookup
        attendance_dict = {record.student_id: record for record in attendance_records}
        
        # Prepare student list with attendance info
        student_list = []
        for student in students:
            attendance = attendance_dict.get(student.id)
            student_list.append({
                'student': student,
                'attendance': attendance,
                'is_present': attendance.is_present if attendance else None,
                'absence_type': attendance.absence_type if attendance and not attendance.is_present else None,
                'note': attendance.note if attendance else ''
            })
        
        # Calculate statistics
        total_students = len(students)
        present_count = sum(1 for record in attendance_records if record.is_present)
        excused_count = sum(1 for record in attendance_records if not record.is_present and record.absence_type == 'excused')
        unexcused_count = sum(1 for record in attendance_records if not record.is_present and record.absence_type == 'unexcused')
        
        context.update({
            'date': date,
            'student_list': student_list,
            'total_students': total_students,
            'present_count': present_count,
            'excused_count': excused_count,
            'unexcused_count': unexcused_count,
            'attendance_rate': round(present_count / total_students * 100, 1) if total_students > 0 else 0
        })
        return context
