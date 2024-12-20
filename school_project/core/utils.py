import json
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from django.contrib import messages

def log_change_history(user, model_name, old_data, new_data):
    """
    Dəyişiklik tarixçəsini qeydə alır
    """
    from .models import ChangeHistory
    
    ChangeHistory.objects.create(
        user=user,
        model_name=model_name,
        old_data=json.dumps(old_data, cls=DjangoJSONEncoder) if old_data else None,
        new_data=json.dumps(new_data, cls=DjangoJSONEncoder) if new_data else None,
        timestamp=timezone.now()
    )

def add_success_message(request, message):
    """
    Uğurlu əməliyyat mesajı əlavə edir
    """
    messages.success(request, message)

def add_error_message(request, message):
    """
    Xəta mesajı əlavə edir
    """
    messages.error(request, message)

def get_client_ip(request):
    """
    İstifadəçinin IP adresini qaytarır
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def format_phone_number(number):
    """
    Telefon nömrəsini formatlaşdırır
    """
    if not number:
        return ""
    
    # Bütün boşluqları və xüsusi simvolları təmizlə
    number = ''.join(filter(str.isdigit, number))
    
    # Azərbaycan nömrə formatı: +994 XX XXX XX XX
    if len(number) == 9:  # Lokal format (XX XXX XX XX)
        return f"+994 {number[:2]} {number[2:5]} {number[5:7]} {number[7:]}"
    elif len(number) == 12 and number.startswith('994'):  # Tam format
        return f"+{number[:3]} {number[3:5]} {number[5:8]} {number[8:10]} {number[10:]}"
    
    return number

def validate_utis_code(code):
    """
    UTIS kodunu yoxlayır
    """
    if not code:
        return False
        
    # UTIS kodu 7 rəqəmdən ibarət olmalıdır
    if not len(code) == 7 or not code.isdigit():
        return False
        
    return True
