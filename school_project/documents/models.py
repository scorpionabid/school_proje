from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

# Create your models here.

class Document(models.Model):
    """
    Sənəd modeli
    """
    DOCUMENT_TYPES = (
        ('REPORT', _('Hesabat')),
        ('PLAN', _('Plan')),
        ('OTHER', _('Digər')),
    )
    
    STATUS_CHOICES = (
        ('PENDING', _('Gözləyir')),
        ('SUBMITTED', _('Təqdim edilib')),
        ('APPROVED', _('Təsdiqlənib')),
        ('REJECTED', _('Rədd edilib')),
    )
    
    title = models.CharField(_('Başlıq'), max_length=200)
    description = models.TextField(_('Təsvir'), blank=True)
    file = models.FileField(_('Fayl'), upload_to='documents/%Y/%m/%d/')
    document_type = models.CharField(_('Sənəd növü'), max_length=20, choices=DOCUMENT_TYPES)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Əlaqələr
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_documents',
        verbose_name=_('Yaradan')
    )
    sector = models.ForeignKey(
        'sector.Sector',
        on_delete=models.CASCADE,
        related_name='sector_documents',
        verbose_name=_('Sektor')
    )
    
    # Metadata
    created_at = models.DateTimeField(_('Yaradılma tarixi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Yenilənmə tarixi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Sənəd')
        verbose_name_plural = _('Sənədlər')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
