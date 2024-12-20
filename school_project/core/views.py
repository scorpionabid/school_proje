from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.db.models import Count
from .permissions import (
    admin_required, 
    region_admin_required, 
    sector_admin_required, 
    school_admin_required
)
from .models import CustomUser

# Create your views here.

class CustomLoginView(LoginView):
    template_name = 'core/login.html'
    redirect_authenticated_user = True

@login_required
def dashboard(request):
    user = request.user
    context = {
        'user_type': user.get_user_type_display(),
        'can_view_admin': user.user_type == 'ADMIN',
        'can_view_region': user.user_type in ['ADMIN', 'REGION_ADMIN'],
        'can_view_sector': user.user_type in ['ADMIN', 'REGION_ADMIN', 'SECTOR_ADMIN'],
        'can_view_school': True,
    }

    # Statistika məlumatlarını əlavə et
    if user.user_type == 'ADMIN':
        context.update({
            'total_users': CustomUser.objects.count(),
            'admin_count': CustomUser.objects.filter(user_type='ADMIN').count(),
            'region_admin_count': CustomUser.objects.filter(user_type='REGION_ADMIN').count(),
            'sector_admin_count': CustomUser.objects.filter(user_type='SECTOR_ADMIN').count(),
            'school_admin_count': CustomUser.objects.filter(user_type='SCHOOL_ADMIN').count(),
            'dashboard_type': 'admin'
        })
    
    elif user.user_type == 'REGION_ADMIN':
        context.update({
            'sector_admin_count': CustomUser.objects.filter(
                user_type='SECTOR_ADMIN'
            ).count(),
            'school_admin_count': CustomUser.objects.filter(
                user_type='SCHOOL_ADMIN'
            ).count(),
            'dashboard_type': 'region'
        })
    
    elif user.user_type == 'SECTOR_ADMIN':
        context.update({
            'school_admin_count': CustomUser.objects.filter(
                user_type='SCHOOL_ADMIN'
            ).count(),
            'dashboard_type': 'sector'
        })
    
    else:  # SCHOOL_ADMIN
        context.update({
            'dashboard_type': 'school'
        })

    return render(request, 'core/dashboard.html', context)

def custom_permission_denied(request, exception):
    return render(request, 'core/403.html', status=403)

# Test views for different permission levels
@admin_required
def admin_only_view(request):
    return render(request, 'core/dashboard.html', {'message': 'Bu səhifəni yalnız Admin görə bilər'})

@region_admin_required
def region_admin_view(request):
    return render(request, 'core/dashboard.html', {'message': 'Bu səhifəni Region Admin və ya yuxarı səviyyə görə bilər'})

@sector_admin_required
def sector_admin_view(request):
    return render(request, 'core/dashboard.html', {'message': 'Bu səhifəni Sektor Admin və ya yuxarı səviyyə görə bilər'})

@school_admin_required
def school_admin_view(request):
    return render(request, 'core/dashboard.html', {'message': 'Bu səhifəni Məktəb Admin və ya yuxarı səviyyə görə bilər'})
