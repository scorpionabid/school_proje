import pytz
from django.utils import timezone
from django.conf import settings
from .utils import get_client_ip, log_change_history

class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Bakı saat qurşağını təyin et
        timezone.activate(pytz.timezone(settings.TIME_ZONE))
        return self.get_response(request)

class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Request məlumatlarını saxla
        request.client_ip = get_client_ip(request)
        
        response = self.get_response(request)
        
        # POST sorğularını qeydə al
        if request.method == 'POST' and request.user.is_authenticated:
            self._log_post_request(request)
            
        return response
    
    def _log_post_request(self, request):
        """
        POST sorğularını qeydə alır
        """
        # Şifrə sahələrini təmizlə
        post_data = request.POST.copy()
        for key in post_data:
            if 'password' in key.lower():
                post_data[key] = '********'
        
        log_change_history(
            user=request.user,
            model_name='HTTP_POST',
            old_data=None,
            new_data={
                'path': request.path,
                'data': dict(post_data),
                'ip': request.client_ip
            }
        )

class UserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # İstifadəçinin son aktivlik vaxtını yenilə
        if request.user.is_authenticated:
            request.user.last_login = timezone.now()
            request.user.save(update_fields=['last_login'])
            
        return response
