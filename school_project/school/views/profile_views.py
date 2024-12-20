from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from ..models import SchoolAdmin
from ..forms import SchoolAdminProfileForm

class ProfileView(LoginRequiredMixin, UpdateView):
    """
    Məktəb admin profil səhifəsi
    """
    model = SchoolAdmin
    form_class = SchoolAdminProfileForm
    template_name = 'school/profile.html'
    success_url = reverse_lazy('school:profile')
    
    def get_object(self, queryset=None):
        """Get current user's school admin profile"""
        return self.request.user.school_admin
    
    def form_valid(self, form):
        messages.success(self.request, _('Profil məlumatları yeniləndi'))
        return super().form_valid(form)
