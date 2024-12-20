from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from core.models import CustomUser
from region.models import Region
from core.utils import format_phone_number

class Sector(models.Model):
    """
    Sektor modeli
    """
    name = models.CharField(_('Sektor adı'), max_length=100)
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name='sectors',
        verbose_name=_('Region')
    )
    utis_code = models.CharField(_('UTIS kodu'), max_length=7, unique=True)
    phone_number = models.CharField(_('Əlaqə nömrəsi'), max_length=20)
    address = models.TextField(_('Ünvan'))
    email = models.EmailField(_('Email'), blank=True)
    
    # Sektor rəhbərliyi
    director = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='directed_sector',
        verbose_name=_('Sektor rəhbəri')
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
        verbose_name = _('Sektor')
        verbose_name_plural = _('Sektorlar')
        ordering = ['region', 'name']
        unique_together = ['region', 'name']

    def __str__(self):
        return f"{self.region.name} - {self.name}"

    def save(self, *args, **kwargs):
        # Telefon nömrəsini format et
        if self.phone_number:
            self.phone_number = format_phone_number(self.phone_number)
        super().save(*args, **kwargs)

    def update_statistics(self):
        """
        Sektor statistikasını yeniləyir
        """
        # Bu metod daha sonra məktəb app-i yaradıldıqdan sonra
        # real məlumatlarla doldurulacaq
        pass

class SectorDocument(models.Model):
    """
    Sektor sənədləri
    """
    DOCUMENT_TYPES = [
        ('REPORT', _('Hesabat')),
        ('PLAN', _('Plan')),
        ('ORDER', _('Əmr')),
        ('OTHER', _('Digər')),
    ]

    sector = models.ForeignKey(
        Sector,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name=_('Sektor')
    )
    title = models.CharField(_('Başlıq'), max_length=200)
    document_type = models.CharField(
        _('Sənəd növü'),
        max_length=10,
        choices=DOCUMENT_TYPES
    )
    file = models.FileField(_('Fayl'), upload_to='sector_documents/')
    description = models.TextField(_('Açıqlama'), blank=True)
    uploaded_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Yükləyən')
    )
    uploaded_at = models.DateTimeField(_('Yüklənmə tarixi'), auto_now_add=True)

    class Meta:
        verbose_name = _('Sektor sənədi')
        verbose_name_plural = _('Sektor sənədləri')
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.sector} - {self.title}"

class SectorNews(models.Model):
    """
    Sektor xəbərləri
    """
    sector = models.ForeignKey(
        Sector,
        on_delete=models.CASCADE,
        related_name='news',
        verbose_name=_('Sektor')
    )
    title = models.CharField(_('Başlıq'), max_length=200)
    content = models.TextField(_('Məzmun'))
    image = models.ImageField(_('Şəkil'), upload_to='sector_news/', blank=True)
    published_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Dərc edən')
    )
    published_at = models.DateTimeField(_('Dərc tarixi'), auto_now_add=True)
    is_active = models.BooleanField(_('Aktivdir'), default=True)

    class Meta:
        verbose_name = _('Sektor xəbəri')
        verbose_name_plural = _('Sektor xəbərləri')
        ordering = ['-published_at']

    def __str__(self):
        return f"{self.sector} - {self.title}"

class SectorReport(models.Model):
    """
    Sektor hesabatları
    """
    REPORT_TYPES = [
        ('MONTHLY', _('Aylıq')),
        ('QUARTERLY', _('Rüblük')),
        ('YEARLY', _('İllik')),
        ('SPECIAL', _('Xüsusi')),
    ]

    REPORT_STATUS = [
        ('DRAFT', _('Qaralama')),
        ('PENDING', _('Təsdiq gözləyir')),
        ('APPROVED', _('Təsdiqlənib')),
        ('REJECTED', _('Rədd edilib')),
    ]

    sector = models.ForeignKey(
        Sector,
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name=_('Sektor')
    )
    title = models.CharField(_('Başlıq'), max_length=200)
    report_type = models.CharField(
        _('Hesabat növü'),
        max_length=10,
        choices=REPORT_TYPES
    )
    report_period = models.DateField(_('Hesabat dövrü'))
    content = models.TextField(_('Məzmun'))
    status = models.CharField(
        _('Status'),
        max_length=10,
        choices=REPORT_STATUS,
        default='DRAFT'
    )
    
    # Əlavə fayllar
    attachments = models.FileField(
        _('Əlavə fayllar'),
        upload_to='sector_reports/',
        blank=True
    )
    
    # Təsdiq prosesi
    submitted_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='submitted_reports',
        verbose_name=_('Təqdim edən')
    )
    approved_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_reports',
        verbose_name=_('Təsdiq edən')
    )
    approval_date = models.DateTimeField(_('Təsdiq tarixi'), null=True, blank=True)
    rejection_reason = models.TextField(_('Rədd səbəbi'), blank=True)
    
    # Metadata
    created_at = models.DateTimeField(_('Yaradılma tarixi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Yenilənmə tarixi'), auto_now=True)

    class Meta:
        verbose_name = _('Sektor hesabatı')
        verbose_name_plural = _('Sektor hesabatları')
        ordering = ['-report_period', '-created_at']

    def __str__(self):
        return f"{self.sector} - {self.title} ({self.get_report_type_display()})"

    def approve(self, approved_by):
        """
        Hesabatı təsdiqləyir
        """
        self.status = 'APPROVED'
        self.approved_by = approved_by
        self.approval_date = timezone.now()
        self.save()

    def reject(self, reason):
        """
        Hesabatı rədd edir
        """
        self.status = 'REJECTED'
        self.rejection_reason = reason
        self.save()
