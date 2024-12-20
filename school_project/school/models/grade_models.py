from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Grade(models.Model):
    GRADE_TYPES = [
        ('KSQ', _('Kiçik Summativ Qiymətləndirmə')),
        ('BSQ', _('Böyük Summativ Qiymətləndirmə')),
        ('MON', _('Monitoring')),
        ('FIN', _('Yekun')),
    ]

    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='grades',
                              verbose_name=_('Şagird'))
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE, related_name='grades',
                             verbose_name=_('Fənn'))
    teacher = models.ForeignKey('Staff', on_delete=models.SET_NULL, null=True, related_name='given_grades',
                              verbose_name=_('Müəllim'))
    grade_type = models.CharField(max_length=3, choices=GRADE_TYPES, verbose_name=_('Qiymət növü'))
    grade = models.DecimalField(max_digits=4, decimal_places=2,
                              validators=[MinValueValidator(2), MaxValueValidator(10)],
                              verbose_name=_('Qiymət'))
    date = models.DateField(default=timezone.now, verbose_name=_('Tarix'))
    semester = models.IntegerField(choices=[(1, '1'), (2, '2')], verbose_name=_('Yarımil'))
    academic_year = models.CharField(max_length=9, verbose_name=_('Tədris ili'))  # Format: 2023-2024
    note = models.TextField(blank=True, verbose_name=_('Qeyd'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Qiymət')
        verbose_name_plural = _('Qiymətlər')
        ordering = ['-date', 'student']
        indexes = [
            models.Index(fields=['student', 'subject', 'grade_type', 'semester']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.get_grade_type_display()} - {self.grade}"

class Subject(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Ad'))
    code = models.CharField(max_length=10, unique=True, verbose_name=_('Kod'))
    is_active = models.BooleanField(default=True, verbose_name=_('Aktiv'))

    class Meta:
        verbose_name = _('Fənn')
        verbose_name_plural = _('Fənlər')
        ordering = ['name']

    def __str__(self):
        return self.name
