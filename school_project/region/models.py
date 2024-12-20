from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import CustomUser
from core.utils import format_phone_number

class Region(models.Model):
    """
    Region modeli
    """
    name = models.CharField(_('Region adı'), max_length=100)
    utis_code = models.CharField(_('UTIS kodu'), max_length=7, unique=True)
    phone_number = models.CharField(_('Əlaqə nömrəsi'), max_length=20)
    address = models.TextField(_('Ünvan'))
    email = models.EmailField(_('Email'), blank=True)
    website = models.URLField(_('Vebsayt'), blank=True)
    
    # Region rəhbərliyi
    director = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='directed_region',
        verbose_name=_('Region rəhbəri')
    )
    
    # Statistik məlumatlar
    total_schools = models.PositiveIntegerField(_('Məktəb sayı'), default=0)
    total_students = models.PositiveIntegerField(_('Şagird sayı'), default=0)
    total_teachers = models.PositiveIntegerField(_('Müəllim sayı'), default=0)
    
    # Metadata
    created_at = models.DateTimeField(_('Yaradılma tarixi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Yenilənmə tarixi'), auto_now=True)
    is_active = models.BooleanField(_('Aktivdir'), default=True)

    class Meta:
        verbose_name = _('Region')
        verbose_name_plural = _('Regionlar')
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Telefon nömrəsini format et
        if self.phone_number:
            self.phone_number = format_phone_number(self.phone_number)
        super().save(*args, **kwargs)

    def update_statistics(self):
        """
        Region statistikasını yeniləyir
        """
        # Bu metod daha sonra sektor və məktəb app-ləri yaradıldıqdan sonra
        # real məlumatlarla doldurulacaq
        pass

class RegionDocument(models.Model):
    """
    Region sənədləri
    """
    DOCUMENT_TYPES = [
        ('REPORT', _('Hesabat')),
        ('PLAN', _('Plan')),
        ('ORDER', _('Əmr')),
        ('OTHER', _('Digər')),
    ]

    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name=_('Region')
    )
    title = models.CharField(_('Başlıq'), max_length=200)
    document_type = models.CharField(
        _('Sənəd növü'),
        max_length=10,
        choices=DOCUMENT_TYPES
    )
    file = models.FileField(_('Fayl'), upload_to='region_documents/')
    description = models.TextField(_('Açıqlama'), blank=True)
    uploaded_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Yükləyən')
    )
    uploaded_at = models.DateTimeField(_('Yüklənmə tarixi'), auto_now_add=True)

    class Meta:
        verbose_name = _('Region sənədi')
        verbose_name_plural = _('Region sənədləri')
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.region.name} - {self.title}"

class RegionNews(models.Model):
    """
    Region xəbərləri
    """
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name='news',
        verbose_name=_('Region')
    )
    title = models.CharField(_('Başlıq'), max_length=200)
    content = models.TextField(_('Məzmun'))
    image = models.ImageField(_('Şəkil'), upload_to='region_news/', blank=True)
    published_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Dərc edən')
    )
    published_at = models.DateTimeField(_('Dərc tarixi'), auto_now_add=True)
    is_active = models.BooleanField(_('Aktivdir'), default=True)

    class Meta:
        verbose_name = _('Region xəbəri')
        verbose_name_plural = _('Region xəbərləri')
        ordering = ['-published_at']

    def __str__(self):
        return f"{self.region.name} - {self.title}"
