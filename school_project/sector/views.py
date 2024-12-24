from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta

from .models import Sector, SectorDocument, SectorNews, SectorReport
from .forms import ReportForm
from documents.models import Document
from school.models import School, Student, Staff, Attendance, Grade

@login_required
def sector_list(request):
    """
    Sektorların siyahısı
    """
    sectors = Sector.objects.filter(is_active=True)
    
    # Region filtri
    region_id = request.GET.get('region')
    if region_id:
        sectors = sectors.filter(region_id=region_id)
    
    # Pagination
    paginator = Paginator(sectors, 10)
    page = request.GET.get('page')
    sectors = paginator.get_page(page)
    
    context = {
        'sectors': sectors,
        'total_sectors': Sector.objects.count(),
        'active_sectors': Sector.objects.filter(is_active=True).count(),
    }
    return render(request, 'sector/sector_list.html', context)

@login_required
def sector_detail(request, pk):
    """
    Sektor detalları
    """
    sector = get_object_or_404(Sector, pk=pk)
    context = {
        'sector': sector,
        'recent_documents': sector.documents.all()[:5],
        'recent_news': sector.news.filter(is_active=True)[:5],
        'recent_reports': sector.reports.all()[:5],
    }
    return render(request, 'sector/sector_detail.html', context)

@login_required
def sector_documents(request, pk):
    """
    Sektor sənədləri
    """
    sector = get_object_or_404(Sector, pk=pk)
    documents = sector.documents.all()
    
    # Filter by document type
    doc_type = request.GET.get('type')
    if doc_type:
        documents = documents.filter(document_type=doc_type)
    
    # Pagination
    paginator = Paginator(documents, 20)
    page = request.GET.get('page')
    documents = paginator.get_page(page)
    
    context = {
        'sector': sector,
        'documents': documents,
        'document_types': SectorDocument.DOCUMENT_TYPES,
    }
    return render(request, 'sector/sector_documents.html', context)

@login_required
def sector_news(request, pk):
    """
    Sektor xəbərləri
    """
    sector = get_object_or_404(Sector, pk=pk)
    news = sector.news.filter(is_active=True)
    
    # Pagination
    paginator = Paginator(news, 10)
    page = request.GET.get('page')
    news = paginator.get_page(page)
    
    context = {
        'sector': sector,
        'news': news,
    }
    return render(request, 'sector/sector_news.html', context)

@login_required
def sector_statistics(request, pk):
    """
    Sektor statistikası
    """
    sector = get_object_or_404(Sector, pk=pk)
    
    # Update statistics before showing
    sector.update_statistics()
    
    context = {
        'sector': sector,
        'total_schools': sector.total_schools,
        'total_students': sector.total_students,
        'total_teachers': sector.total_teachers,
    }
    return render(request, 'sector/sector_statistics.html', context)

@login_required
def sector_reports(request, pk):
    """
    Sektor hesabatları
    """
    sector = get_object_or_404(Sector, pk=pk)
    reports = sector.reports.all()
    
    # Filters
    report_type = request.GET.get('type')
    status = request.GET.get('status')
    
    if report_type:
        reports = reports.filter(report_type=report_type)
    if status:
        reports = reports.filter(status=status)
    
    # Pagination
    paginator = Paginator(reports, 15)
    page = request.GET.get('page')
    reports = paginator.get_page(page)
    
    context = {
        'sector': sector,
        'reports': reports,
        'report_types': SectorReport.REPORT_TYPES,
        'report_statuses': SectorReport.REPORT_STATUS,
    }
    return render(request, 'sector/sector_reports.html', context)

@login_required
def report_create(request, pk):
    """
    Yeni hesabat yaratma
    """
    sector = get_object_or_404(Sector, pk=pk)
    
    if request.method == 'POST':
        # Form məlumatlarını al
        title = request.POST.get('title')
        report_type = request.POST.get('report_type')
        report_period = request.POST.get('report_period')
        content = request.POST.get('content')
        attachments = request.FILES.get('attachments')
        
        # Hesabatı yarat
        report = SectorReport.objects.create(
            sector=sector,
            title=title,
            report_type=report_type,
            report_period=report_period,
            content=content,
            attachments=attachments,
            submitted_by=request.user,
            status='PENDING'
        )
        
        messages.success(request, _('Hesabat uğurla yaradıldı.'))
        return redirect('sector:report_detail', report_pk=report.pk)
    
    context = {
        'sector': sector,
        'report_types': SectorReport.REPORT_TYPES,
    }
    return render(request, 'sector/report_form.html', context)

@login_required
def report_detail(request, report_pk):
    """
    Hesabat detalları
    """
    report = get_object_or_404(SectorReport, pk=report_pk)
    context = {
        'report': report,
    }
    return render(request, 'sector/report_detail.html', context)

@login_required
def report_edit(request, report_pk):
    """
    Hesabat redaktəsi
    """
    report = get_object_or_404(SectorReport, pk=report_pk)
    
    # Yalnız qaralama vəziyyətində olan hesabatları redaktə etməyə icazə ver
    if report.status != 'DRAFT':
        messages.error(request, _('Bu hesabatı redaktə etmək mümkün deyil.'))
        return redirect('sector:report_detail', report_pk=report.pk)
    
    if request.method == 'POST':
        # Form məlumatlarını al və yenilə
        report.title = request.POST.get('title')
        report.report_type = request.POST.get('report_type')
        report.report_period = request.POST.get('report_period')
        report.content = request.POST.get('content')
        
        if 'attachments' in request.FILES:
            report.attachments = request.FILES['attachments']
        
        report.save()
        messages.success(request, _('Hesabat uğurla yeniləndi.'))
        return redirect('sector:report_detail', report_pk=report.pk)
    
    context = {
        'report': report,
        'report_types': SectorReport.REPORT_TYPES,
    }
    return render(request, 'sector/report_form.html', context)

@login_required
def report_approve(request, report_pk):
    """
    Hesabatı təsdiqləmə
    """
    report = get_object_or_404(SectorReport, pk=report_pk)
    
    if request.method == 'POST':
        report.approve(approved_by=request.user)
        messages.success(request, _('Hesabat uğurla təsdiqləndi.'))
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error', 'message': _('Yanlış sorğu metodu.')})

@login_required
def report_reject(request, report_pk):
    """
    Hesabatı rədd etmə
    """
    report = get_object_or_404(SectorReport, pk=report_pk)
    
    if request.method == 'POST':
        reason = request.POST.get('reason')
        report.reject(reason=reason)
        messages.warning(request, _('Hesabat rədd edildi.'))
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error', 'message': _('Yanlış sorğu metodu.')})

@login_required
def news_create(request, pk):
    """
    Yeni xəbər yaratma
    """
    sector = get_object_or_404(Sector, pk=pk)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')
        is_active = request.POST.get('is_active') == 'on'
        
        news = SectorNews.objects.create(
            sector=sector,
            title=title,
            content=content,
            image=image,
            published_by=request.user,
            is_active=is_active
        )
        
        messages.success(request, _('Xəbər uğurla yaradıldı.'))
        return JsonResponse({'status': 'success', 'message': _('Xəbər uğurla yaradıldı.')})
    
    return JsonResponse({'status': 'error', 'message': _('Yanlış sorğu metodu.')})

@login_required
def news_edit(request, news_pk):
    """
    Xəbər redaktəsi
    """
    news = get_object_or_404(SectorNews, pk=news_pk)
    
    if request.method == 'POST':
        news.title = request.POST.get('title')
        news.content = request.POST.get('content')
        
        if 'image' in request.FILES:
            news.image = request.FILES['image']
            
        news.is_active = request.POST.get('is_active') == 'on'
        news.save()
        
        messages.success(request, _('Xəbər uğurla yeniləndi.'))
        return JsonResponse({'status': 'success', 'message': _('Xəbər uğurla yeniləndi.')})
    
    return JsonResponse({'status': 'error', 'message': _('Yanlış sorğu metodu.')})

@login_required
def news_delete(request, news_pk):
    """
    Xəbər silmə
    """
    news = get_object_or_404(SectorNews, pk=news_pk)
    
    if request.method == 'POST':
        news.delete()
        messages.success(request, _('Xəbər uğurla silindi.'))
        return JsonResponse({'status': 'success', 'message': _('Xəbər uğurla silindi.')})
    
    return JsonResponse({'status': 'error', 'message': _('Yanlış sorğu metodu.')})

@login_required
def news_toggle_status(request, news_pk):
    """
    Xəbərin statusunu dəyişmə
    """
    news = get_object_or_404(SectorNews, pk=news_pk)
    
    if request.method == 'POST':
        news.is_active = not news.is_active
        news.save()
        
        status_message = _('aktivləşdirildi') if news.is_active else _('deaktiv edildi')
        messages.success(request, _(f'Xəbər uğurla {status_message}.'))
        return JsonResponse({'status': 'success', 'message': _(f'Xəbər uğurla {status_message}.')})
    
    return JsonResponse({'status': 'error', 'message': _('Yanlış sorğu metodu.')})

@login_required
def news_details(request, news_pk):
    """
    Xəbər detalları
    """
    news = get_object_or_404(SectorNews, pk=news_pk)
    
    data = {
        'status': 'success',
        'title': news.title,
        'content': news.content,
        'image': news.image.url if news.image else None,
        'published_by': news.published_by.get_full_name(),
        'published_at': news.published_at.strftime('%d.%m.%Y %H:%M')
    }
    
    return JsonResponse(data)

@login_required
def document_upload(request, pk):
    """
    Sənəd yükləmə
    """
    sector = get_object_or_404(Sector, pk=pk)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        document_type = request.POST.get('document_type')
        description = request.POST.get('description')
        file = request.FILES.get('file')
        
        if not file:
            return JsonResponse({
                'status': 'error',
                'message': _('Zəhmət olmasa fayl seçin.')
            })
        
        document = SectorDocument.objects.create(
            sector=sector,
            title=title,
            document_type=document_type,
            description=description,
            file=file,
            uploaded_by=request.user
        )
        
        messages.success(request, _('Sənəd uğurla yükləndi.'))
        return JsonResponse({'status': 'success', 'message': _('Sənəd uğurla yükləndi.')})
    
    return JsonResponse({'status': 'error', 'message': _('Yanlış sorğu metodu.')})

@login_required
def document_delete(request, doc_pk):
    """
    Sənəd silmə
    """
    document = get_object_or_404(SectorDocument, pk=doc_pk)
    
    if request.method == 'POST':
        document.delete()
        messages.success(request, _('Sənəd uğurla silindi.'))
        return JsonResponse({'status': 'success', 'message': _('Sənəd uğurla silindi.')})
    
    return JsonResponse({'status': 'error', 'message': _('Yanlış sorğu metodu.')})

@login_required
def document_details(request, doc_pk):
    """
    Sənəd detalları
    """
    document = get_object_or_404(SectorDocument, pk=doc_pk)
    
    data = {
        'status': 'success',
        'title': document.title,
        'document_type': document.get_document_type_display(),
        'description': document.description,
        'file_url': document.file.url,
        'uploaded_by': document.uploaded_by.get_full_name(),
        'uploaded_at': document.uploaded_at.strftime('%d.%m.%Y %H:%M'),
        'file_size': document.file.size
    }
    
    return JsonResponse(data)

@login_required
def sector_reports(request, sector_id):
    sector = get_object_or_404(Sector, id=sector_id)
    reports = sector.documents.filter(document_type='REPORT').order_by('-created_at')
    return render(request, 'sector/reports.html', {'sector': sector, 'reports': reports})

@login_required
def create_report(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.created_by = request.user
            report.save()
            messages.success(request, _('Hesabat uğurla yaradıldı.'))
            return redirect('sector:reports', sector_id=report.sector.id)
    else:
        form = ReportForm()
    return render(request, 'sector/report_form.html', {'form': form})

@login_required
def approve_report(request, report_id):
    report = get_object_or_404(Document, id=report_id, document_type='REPORT')
    report.status = 'APPROVED'
    report.save()
    messages.success(request, _('Hesabat təsdiqləndi.'))
    return redirect('sector:reports', sector_id=report.sector.id)

@login_required
def reject_report(request, report_id):
    report = get_object_or_404(Document, id=report_id, document_type='REPORT')
    report.status = 'REJECTED'
    report.save()
    messages.success(request, _('Hesabat rədd edildi.'))
    return redirect('sector:reports', sector_id=report.sector.id)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from core.models import CustomUser
from django.db.models import Count, Avg
from school.models import School, Student, Staff, Attendance

@login_required
def sector_dashboard(request):
    """
    Sector admin dashboard görünüşü
    """
    if request.user.user_type != CustomUser.UserType.SECTOR_ADMIN:
        raise PermissionDenied
        
    sector = request.user.sector
    total_students = Student.objects.filter(school__sector=sector).count()
    total_teachers = Staff.objects.filter(school__sector=sector, staff_type='TEACHER').count()
    avg_attendance = Attendance.objects.filter(student__school__sector=sector).aggregate(avg=Avg('is_present'))['avg']
    
    context = {
        'user': request.user,
        'sector': sector,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'avg_attendance': round(avg_attendance * 100 if avg_attendance else 0, 2)
    }
    return render(request, 'sector/sector_dashboard.html', context)

class SectorDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'sector/sector_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sector = self.request.user.directed_sector
        
        if not sector:
            return context
            
        # Sektor statistikasını yenilə
        sector.update_statistics()
        
        # Kontekst məlumatlarını hazırla
        context['sector'] = sector
        
        # Son 30 günlük davamiyyət trendi
        thirty_days_ago = timezone.now() - timedelta(days=30)
        attendance_trend = Attendance.objects.filter(
            student__school__sector=sector,
            date__gte=thirty_days_ago
        ).values('date').annotate(
            attendance_rate=Avg('is_present')
        ).order_by('date')
        
        context['attendance_trend'] = attendance_trend
        
        # Problemli məktəblər (aşağı davamiyyət və ya qiymət)
        problem_schools = School.objects.filter(
            sector=sector
        ).annotate(
            avg_attendance=Avg('students__attendances__is_present'),
            avg_grade=Avg('students__grades__grade')
        ).filter(
            Q(avg_attendance__lt=0.8) | Q(avg_grade__lt=6)
        )
        
        context['problem_schools'] = problem_schools
        
        # Məktəb statistikası
        schools = School.objects.filter(sector=sector).annotate(
            student_count=Count('students', distinct=True),
            teacher_count=Count('staff', filter=Q(staff__staff_type='TEACHER'), distinct=True),
            avg_attendance=Avg('students__attendances__is_present'),
            avg_grade=Avg('students__grades__grade')
        )
        
        context['schools'] = schools
        
        # Son hesabatlar
        context['recent_reports'] = sector.documents.filter(
            document_type='REPORT'
        ).order_by('-uploaded_at')[:5]
        
        # Gözləyən hesabatlar
        context['pending_reports'] = SectorReport.objects.filter(
            sector=sector,
            status='PENDING'
        ).order_by('-created_at')[:5]
        
        # Təsdiqlənmiş hesabatlar
        context['approved_reports'] = SectorReport.objects.filter(
            sector=sector,
            status='APPROVED'
        ).order_by('-approval_date')[:5]
        
        return context
