# school/models.py
# school/models.py

# Django core imports
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

# Third-party imports
# (hal-hazırda yoxdur)

# Local imports
from core.models import CustomUser
from sector.models import Sector

# Configure logging
import logging
logger = logging.getLogger(__name__)


# Bütün sabitləri faylın əvvəlində birləşdirmək:
# Constants
SCHOOL_TYPES = [
    ('PUBLIC', _('Dövlət')),
    ('PRIVATE', _('Özəl')),
]

STAFF_TYPES = [
    ('TEACHER', _('Müəllim')),
    ('ADMIN', _('İnzibati işçi')),
    ('SUPPORT', _('Texniki işçi')),
]

GENDER_CHOICES = [
    ('M', _('Oğlan')),
    ('F', _('Qız')),
]

LANGUAGES = [
    ('AZ', _('Azərbaycan')),
    ('RU', _('Rus')),
    ('EN', _('İngilis')),
]

EDUCATION_LEVELS = [
    ('BACHELOR', _('Bakalavr')),
    ('MASTER', _('Magistr')),
    ('PHD', _('Doktorantura')),
    ('OTHER', _('Digər')),
]

ABSENCE_TYPES = [
    ('PRESENT', _('Dərsdə')),
    ('EXCUSE', _('Üzrlü')),
    ('UNEXCUSE', _('Üzrsüz')),
]


STAFF_TYPE_CHOICES = [
    ('TEACHER', _('Müəllim')),
    ('ADMIN', _('İnzibati işçi')),
    ('SUPPORT', _('Texniki işçi')),
]

class School(models.Model):
    """
    Məktəb modeli.

    Attributes:
        name (str): Məktəbin adı
        utis_code (str): UTIS kodu
        school_type (str): Məktəbin növü (dövlət/özəl)
        language (str): Tədris dili
        sector (Sector): Aid olduğu sektor
        address (str): Məktəbin ünvanı
        phone (str): Əlaqə nömrəsi
        email (str): E-poçt ünvanı
    """
    name = models.CharField(_('Məktəbin adı'), max_length=200)
    utis_code = models.CharField(_('UTIS kodu'), max_length=20, unique=True)
    school_type = models.CharField(_('Məktəbin növü'), max_length=10, choices=SCHOOL_TYPES)
    language = models.CharField(_('Tədris dili'), max_length=2, choices=LANGUAGES)
    sector = models.ForeignKey(
        Sector,
        on_delete=models.PROTECT,
        verbose_name=_('Sektor')
    )
    address = models.TextField(_('Ünvan'))
    phone = models.CharField(_('Telefon'), max_length=20)
    email = models.EmailField(_('E-poçt'))
    
    # Statistika sahələri
    student_count = models.PositiveIntegerField(
        _('Şagird sayı'),
        default=0,
        validators=[MinValueValidator(0)]
    )
    staff_count = models.PositiveIntegerField(
        _('İşçi sayı'),
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Tarix sahələri
    created_at = models.DateTimeField(_('Yaradılma tarixi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Yenilənmə tarixi'), auto_now=True)

    class Meta:
        verbose_name = _('Məktəb')
        verbose_name_plural = _('Məktəblər')
        ordering = ['name']
        indexes = [
            models.Index(fields=['utis_code']),
            models.Index(fields=['school_type']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_school_type_display()})"

    def clean(self):
        """Validate model fields."""
        if self.student_count < 0:
            raise ValidationError(_('Şagird sayı mənfi ola bilməz'))
        if self.staff_count < 0:
            raise ValidationError(_('İşçi sayı mənfi ola bilməz'))

    def save(self, *args, **kwargs):
        """Override save method to perform additional operations."""
        self.full_clean()
        super().save(*args, **kwargs)
        logger.info(f"School saved: {self.name} (ID: {self.id})")

    def update_statistics(self):
        """Update school statistics."""
        self.student_count = self.students.count()
        self.staff_count = self.staff_members.count()
        self.save()
        logger.info(f"Statistics updated for school: {self.name}")  # düzəldilmiş sətir

class Staff(models.Model):
    first_name = models.CharField(max_length=100, verbose_name='Ad')
    last_name = models.CharField(max_length=100, verbose_name='Soyad')
    email = models.EmailField(verbose_name='E-poçt')
    phone = models.CharField(max_length=20, verbose_name='Telefon')
    position = models.CharField(max_length=100, verbose_name='Vəzifə')
    staff_type = models.CharField(max_length=20, choices=STAFF_TYPE_CHOICES, verbose_name='İşçi növü')
    school = models.ForeignKey(School, on_delete=models.CASCADE, verbose_name='Məktəb')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'İşçi'
        verbose_name_plural = 'İşçilər'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class ClassRoom(models.Model):
    """
    Sinif modeli
    """
    GRADE_CHOICES = [(i, str(i)) for i in range(1, 13)]
    
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='classes',
        verbose_name=_('Məktəb')
    )
    grade = models.PositiveIntegerField(
        _('Sinif'),
        choices=GRADE_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    division = models.CharField(_('Bölmə'), max_length=1)
    language = models.CharField(_('Tədris dili'), max_length=2, choices=LANGUAGES)  # School.LANGUAGES -> LANGUAGES
    capacity = models.PositiveIntegerField(
        _('Tutum'),
        validators=[MinValueValidator(1), MaxValueValidator(40)]
    )
    current_students = models.PositiveIntegerField(
        _('Cari şagird sayı'),
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(40)]
    )
    class_teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_class',
        verbose_name=_('Sinif rəhbəri')
    )
    is_active = models.BooleanField(_('Aktivdir'), default=True)
    created_at = models.DateTimeField(_('Yaradılma tarixi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Yenilənmə tarixi'), auto_now=True)

    class Meta:
        verbose_name = _('Sinif')
        verbose_name_plural = _('Siniflər')
        ordering = ['grade', 'division']
        unique_together = ['school', 'grade', 'division']

    def __str__(self):
        return f"{self.grade}-{self.division}"

    def get_full_name(self):
        """
        Sinifin tam adını qaytarır
        """
        return f"{self.grade}-{self.division}"

    def update_statistics(self):
        """
        Sinif statistikasını yeniləyir
        """
        self.current_students = self.students.filter(is_active=True).count()
        self.save()

    def save(self, *args, **kwargs):
        # Validate current_students against capacity
        if self.current_students > self.capacity:
            raise ValidationError(_('Cari şagird sayı tutumdan çox ola bilməz'))
        super().save(*args, **kwargs)
        # Update school statistics
        self.school.update_statistics()


class Student(models.Model):
    """
    Şagird modeli
    """
    GENDER_CHOICES = [
        ('M', _('Oğlan')),
        ('F', _('Qız')),
    ]
    
    # Şəxsi məlumatlar
    first_name = models.CharField(_('Ad'), max_length=50)
    last_name = models.CharField(_('Soyad'), max_length=50)
    father_name = models.CharField(_('Ata adı'), max_length=50)
    birth_date = models.DateField(_('Doğum tarixi'))
    gender = models.CharField(_('Cins'), max_length=1, choices=GENDER_CHOICES)
    utis_id = models.CharField(_('UTIS ID'), max_length=20, unique=True)
    
    # Təhsil məlumatları
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='students',
        verbose_name=_('Məktəb')
    )
    class_room = models.ForeignKey(
        'ClassRoom',
        on_delete=models.SET_NULL,
        null=True,
        related_name='students',
        verbose_name=_('Sinif')
    )
    admission_date = models.DateField(_('Qəbul tarixi'))
    
    # Əlaqə məlumatları
    address = models.TextField(_('Ünvan'))
    phone = models.CharField(_('Telefon'), max_length=20, blank=True)
    email = models.EmailField(_('E-poçt'), blank=True)
    
    # Valideyn məlumatları
    parent_name = models.CharField(_('Valideynin adı'), max_length=100)
    parent_phone = models.CharField(_('Valideynin telefonu'), max_length=20)
    parent_email = models.EmailField(_('Valideynin e-poçtu'), blank=True)
    
    # Status
    is_active = models.BooleanField(_('Aktivdir'), default=True)
    created_at = models.DateTimeField(_('Yaradılma tarixi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Yenilənmə tarixi'), auto_now=True)

    class Meta:
        verbose_name = _('Şagird')
        verbose_name_plural = _('Şagirdlər')
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.father_name}"
    
    def get_full_name(self):
        return f"{self.last_name} {self.first_name} {self.father_name}"
    
    def get_short_name(self):
        return f"{self.last_name} {self.first_name}"


class Attendance(models.Model):
    """
    Davamiyyət modeli
    """
    ABSENCE_TYPES = [
        ('SICK', _('Xəstə')),
        ('EXCUSED', _('Üzrlü')),
        ('UNEXCUSED', _('Üzrsüz')),
    ]
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name=_('Şagird')
    )
    date = models.DateField(_('Tarix'))
    lesson_number = models.PositiveIntegerField(
        _('Dərs nömrəsi'),
        validators=[MinValueValidator(1), MaxValueValidator(8)],
        default=1
    )
    is_present = models.BooleanField(_('İştirak edir'), default=True)
    absence_type = models.CharField(
        _('Qayıb növü'),
        max_length=10,
        choices=ABSENCE_TYPES,
        blank=True,
        null=True
    )
    note = models.TextField(_('Qeyd'), blank=True)
    recorded_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_attendances',
        verbose_name=_('Qeyd edən')
    )
    created_at = models.DateTimeField(_('Yaradılma tarixi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Yenilənmə tarixi'), auto_now=True)

    class Meta:
        verbose_name = _('Davamiyyət')
        verbose_name_plural = _('Davamiyyət')
        ordering = ['-date']
        unique_together = ['student', 'date', 'lesson_number']

    def __str__(self):
        return f"{self.student} - {self.date} - Dərs {self.lesson_number}"


class Grade(models.Model):
    """
    Qiymət modeli
    """
    GRADE_TYPES = [
        ('DAILY', _('Gündəlik')),
        ('KSQ', _('Kiçik Summativ')),
        ('BSQ', _('Böyük Summativ')),
        ('MONITORING', _('Monitoring')),
        ('FINAL', _('Yekun')),
    ]
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='grades',
        verbose_name=_('Şagird')
    )
    subject = models.CharField(_('Fənn'), max_length=100)
    grade_type = models.CharField(_('Qiymət növü'), max_length=20, choices=GRADE_TYPES)
    grade = models.PositiveIntegerField(
        _('Qiymət'),
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    date = models.DateField(_('Tarix'))
    teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='given_grades',
        verbose_name=_('Müəllim')
    )
    note = models.TextField(_('Qeyd'), blank=True)
    created_at = models.DateTimeField(_('Yaradılma tarixi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Yenilənmə tarixi'), auto_now=True)

    class Meta:
        verbose_name = _('Qiymət')
        verbose_name_plural = _('Qiymətlər')
        ordering = ['-date']

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.grade} ({self.get_grade_type_display()})"


class SchoolAdmin(models.Model):
    """
    Məktəb administratoru modeli
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='school_admin',
        verbose_name=_('İstifadəçi')
    )
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='admins',
        verbose_name=_('Məktəb')
    )
    phone = models.CharField(
        max_length=20,
        verbose_name=_('Telefon'),
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Yaradılma tarixi')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Yenilənmə tarixi')
    )

    class Meta:
        verbose_name = _('Məktəb administratoru')
        verbose_name_plural = _('Məktəb administratorları')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.school.name}"


class StaffAttendance(models.Model):
    """
    İşçi davamiyyət modeli
    """
    ABSENCE_TYPES = [
        ('SICK', _('Xəstə')),
        ('VACATION', _('Məzuniyyət')),
        ('PERSONAL', _('Şəxsi')),
        ('OTHER', _('Digər')),
    ]

    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name=_('İşçi')
    )
    date = models.DateField(_('Tarix'))
    is_present = models.BooleanField(_('İştirak edir'), default=True)
    check_in = models.TimeField(_('Gəlmə vaxtı'), null=True, blank=True)
    check_out = models.TimeField(_('Getmə vaxtı'), null=True, blank=True)
    absence_type = models.CharField(
        _('Qayıb növü'),
        max_length=10,
        choices=ABSENCE_TYPES,
        blank=True,
        null=True
    )
    note = models.TextField(_('Qeyd'), blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_staff_attendances',
        verbose_name=_('Qeyd edən')
    )

    class Meta:
        verbose_name = _('İşçi davamiyyəti')
        verbose_name_plural = _('İşçi davamiyyəti')
        ordering = ['-date']
        unique_together = ['staff', 'date']

    def __str__(self):
        return f"{self.staff.get_full_name()} - {self.date}"


@receiver(post_save, sender=ClassRoom)
def update_school_statistics(sender, instance, **kwargs):
    """
    Sinif məlumatları yeniləndikdə məktəb statistikasını yeniləyir
    """
    instance.school.update_statistics()
