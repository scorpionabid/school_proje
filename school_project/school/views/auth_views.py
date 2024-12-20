from django.contrib.auth import login, logout
from django.contrib.auth.views import (
    LoginView, LogoutView,
    PasswordChangeView, PasswordChangeDoneView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

class SchoolLoginView(LoginView):
    """
    School login view
    """
    template_name = 'school/auth/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Login olduqdan sonra dashboard-a yönləndir"""
        return reverse_lazy('school:dashboard')
    
    def form_valid(self, form):
        """
        Login form valid olduqda istifadəçinin məktəb_admin olub olmadığını yoxla
        """
        user = form.get_user()
        if hasattr(user, 'school_admin'):
            login(self.request, user)
            return redirect(self.get_success_url())
        else:
            form.add_error(None, _('Bu hesab məktəb admin hesabı deyil'))
            return self.form_invalid(form)
            
    def dispatch(self, request, *args, **kwargs):
        """
        Əgər istifadəçi artıq login olubsa, dashboard-a yönləndir
        """
        if self.request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

class SchoolLogoutView(LogoutView):
    """
    School logout view
    """
    next_page = 'school:login'

class SchoolPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """
    School password change view
    """
    template_name = 'school/auth/password_change_form.html'
    success_url = reverse_lazy('school:password_change_done')

class SchoolPasswordChangeDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    """
    School password change done view
    """
    template_name = 'school/auth/password_change_done.html'
