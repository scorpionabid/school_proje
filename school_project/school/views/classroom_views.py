from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.db.models import Count, Avg

from ..models import ClassRoom, Student, Attendance, Grade
from ..forms import ClassRoomForm

class ClassRoomListView(LoginRequiredMixin, ListView):
    """
    Siniflərin siyahısı
    """
    model = ClassRoom
    template_name = 'school/settings/classroom_list.html'
    context_object_name = 'classrooms'
    paginate_by = 10

    def get_queryset(self):
        return ClassRoom.objects.filter(school=self.request.user.school_admin.school)

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
        messages.success(self.request, _('Sinif uğurla əlavə edildi.'))
        return super().form_valid(form)

class ClassRoomDetailView(LoginRequiredMixin, DetailView):
    """
    Sinif detalları
    """
    model = ClassRoom
    template_name = 'school/settings/classroom_detail.html'
    context_object_name = 'classroom'

    def get_queryset(self):
        return ClassRoom.objects.filter(school=self.request.user.school_admin.school)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        classroom = self.object

        # Şagird statistikası
        context['total_students'] = classroom.students.filter(is_active=True).count()
        
        # Davamiyyət statistikası
        context['attendance_stats'] = Attendance.objects.filter(
            student__classroom=classroom,
            student__is_active=True
        ).values('date').annotate(
            present=Count('id', filter=models.Q(is_present=True)),
            absent=Count('id', filter=models.Q(is_present=False))
        ).order_by('-date')[:30]

        # Qiymət statistikası
        context['grade_stats'] = Grade.objects.filter(
            student__classroom=classroom,
            student__is_active=True
        ).values('grade_type').annotate(
            avg_grade=Avg('grade'),
            total_grades=Count('id')
        )

        # Şagird siyahısı
        context['students'] = classroom.students.filter(is_active=True).order_by('last_name', 'first_name')

        return context

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
        messages.success(self.request, _('Sinif məlumatları uğurla yeniləndi.'))
        return super().form_valid(form)

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
        messages.success(self.request, _('Sinif uğurla silindi.'))
        return super().delete(request, *args, **kwargs)
