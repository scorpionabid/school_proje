from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from .forms import LoginForm
from .models import CustomUser

def login_view(request):
    """
    Login view
    """
    if request.user.is_authenticated:
        return redirect('core:dashboard')
        
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, _('Uğurla daxil oldunuz!'))
                return redirect('core:dashboard')
            else:
                messages.error(request, _('İstifadəçi adı və ya şifrə yanlışdır!'))
    else:
        form = LoginForm()
    
    return render(request, 'core/login.html', {'form': form})

@login_required
def dashboard(request):
    """
    Dashboard view that redirects users to their respective dashboards
    based on their user type
    """
    user = request.user
    
    if user.user_type == CustomUser.UserType.REGION_ADMIN:
        return redirect('region:dashboard')
    elif user.user_type == CustomUser.UserType.SECTOR_ADMIN:
        return redirect('sector:dashboard')
    elif user.user_type == CustomUser.UserType.SCHOOL_ADMIN:
        return redirect('school:dashboard')
    else:
        messages.error(request, _('Sizin istifadəçi növünüz düzgün təyin edilməyib!'))
        return redirect('core:login')

@login_required
def logout_view(request):
    """
    Logout view
    """
    logout(request)
    messages.success(request, _('Uğurla çıxış etdiniz!'))
    return redirect('core:login')
