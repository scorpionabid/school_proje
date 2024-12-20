from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from ..models import Grade, Student, SchoolAdmin, Staff
from ..forms import GradeForm, GradeFilterForm

class GradeBaseView(LoginRequiredMixin, ListView):
    """
    Qiymətləndirmə üçün baza görünüş
    """
    model = Grade
    template_name = 'school/grades/grade_list.html'
    context_object_name = 'grades'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = Grade.objects.filter(
            student__school=self.request.user.school_admin.school,
            grade_type=self.grade_type
        ).select_related('student', 'teacher')
        
        # Filtrlərin tətbiqi
        form = GradeFilterForm(self.request.GET)
        if form.is_valid():
            filters = {}
            if form.cleaned_data['student']:
                filters['student'] = form.cleaned_data['student']
            if form.cleaned_data['subject']:
                filters['subject'] = form.cleaned_data['subject']
            if form.cleaned_data['start_date']:
                filters['date__gte'] = form.cleaned_data['start_date']
            if form.cleaned_data['end_date']:
                filters['date__lte'] = form.cleaned_data['end_date']
            queryset = queryset.filter(**filters)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'grade_type': self.grade_type,
            'grade_type_display': self.grade_type_display,
            'form': GradeForm(initial={'grade_type': self.grade_type}),
            'filter_form': GradeFilterForm(self.request.GET),
            'students': Student.objects.filter(
                school=self.request.user.school_admin.school,
                is_active=True
            ),
        })
        return context
    
    def post(self, request, *args, **kwargs):
        form = GradeForm(request.POST)
        if form.is_valid():
            grade = form.save(commit=False)
            grade.grade_type = self.grade_type
            grade.teacher = get_object_or_404(Staff, user=request.user)
            grade.save()
            messages.success(request, _('Qiymət əlavə edildi.'))
            return redirect(request.path)
        
        context = self.get_context_data()
        context['form'] = form
        return render(request, self.template_name, context)

class KSQGradeView(GradeBaseView):
    """
    KSQ (Kiçik Summativ Qiymətləndirmə) qiymətləri üçün görünüş
    """
    grade_type = 'KSQ'
    grade_type_display = _('Kiçik Summativ Qiymətləndirmə')

class BSQGradeView(GradeBaseView):
    """
    BSQ (Böyük Summativ Qiymətləndirmə) qiymətləri üçün görünüş
    """
    grade_type = 'BSQ'
    grade_type_display = _('Böyük Summativ Qiymətləndirmə')

class MonitoringGradeView(GradeBaseView):
    """
    Monitoring qiymətləri üçün görünüş
    """
    grade_type = 'MONITORING'
    grade_type_display = _('Monitoring')

class FinalGradeView(GradeBaseView):
    """
    Yekun qiymətlər üçün görünüş
    """
    grade_type = 'FINAL'
    grade_type_display = _('Yekun')
