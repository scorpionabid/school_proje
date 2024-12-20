from django.contrib.auth.mixins import UserPassesTestMixin
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.user_type == 'ADMIN':
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view

def region_admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.user_type in ['ADMIN', 'REGION_ADMIN']:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view

def sector_admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.user_type in ['ADMIN', 'REGION_ADMIN', 'SECTOR_ADMIN']:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view

def school_admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.user_type in ['ADMIN', 'REGION_ADMIN', 'SECTOR_ADMIN', 'SCHOOL_ADMIN']:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.user_type == 'ADMIN'

class RegionAdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.user_type in ['ADMIN', 'REGION_ADMIN']

class SectorAdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.user_type in ['ADMIN', 'REGION_ADMIN', 'SECTOR_ADMIN']

class SchoolAdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.user_type in ['ADMIN', 'REGION_ADMIN', 'SECTOR_ADMIN', 'SCHOOL_ADMIN']
