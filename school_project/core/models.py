from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class CustomUser(AbstractUser):
    """
    Xüsusi istifadəçi modeli
    """
    class UserType(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        REGION_ADMIN = 'REGION_ADMIN', _('Region Admin')
        SECTOR_ADMIN = 'SECTOR_ADMIN', _('Sektor Admin')
        SCHOOL_ADMIN = 'SCHOOL_ADMIN', _('Məktəb Admin')

    user_type = models.CharField(
        _('İstifadəçi tipi'),
        max_length=20,
        choices=UserType.choices,
        default=UserType.SCHOOL_ADMIN,
    )
    
    father_name = models.CharField(_('Ata adı'), max_length=150, blank=True)
    utis_code = models.CharField(_('UTIS kodu'), max_length=7, unique=True, null=True, blank=True)
    whatsapp_number = models.CharField(_('WhatsApp nömrəsi'), max_length=20, blank=True)
    
    # Məktəb əlaqəsi
    school = models.ForeignKey(
        'school.School',
        on_delete=models.CASCADE,
        related_name='users',
        verbose_name=_('Məktəb'),
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('İstifadəçi')
        verbose_name_plural = _('İstifadəçilər')

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_user_type_display()})"

    def get_full_name(self):
        """
        İstifadəçinin tam adını qaytarır: Ad, Soyad, Ata adı
        """
        full_name = super().get_full_name()
        if self.father_name:
            full_name = f"{full_name} {self.father_name}"
        return full_name.strip()

class ChangeHistory(models.Model):
    """
    Sistem dəyişikliklərinin tarixçəsi
    """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('İstifadəçi')
    )
    timestamp = models.DateTimeField(_('Tarix'), default=timezone.now)
    model_name = models.CharField(_('Model'), max_length=100)
    old_data = models.JSONField(_('Köhnə data'), null=True, blank=True)
    new_data = models.JSONField(_('Yeni data'), null=True, blank=True)

    class Meta:
        verbose_name = _('Dəyişiklik tarixçəsi')
        verbose_name_plural = _('Dəyişiklik tarixçəsi')
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} - {self.model_name} - {self.timestamp}"
