# Generated by Django 4.2.17 on 2024-12-19 15:16

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('school', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('staff_type', models.CharField(choices=[('TEACHER', 'Müəllim'), ('ADMIN', 'İnzibati işçi'), ('SUPPORT', 'Texniki işçi')], max_length=20, verbose_name='İşçi növü')),
                ('position', models.CharField(max_length=100, verbose_name='Vəzifə')),
                ('phone', models.CharField(max_length=20, verbose_name='Telefon')),
                ('emergency_contact', models.CharField(max_length=20, verbose_name='Təcili əlaqə nömrəsi')),
                ('address', models.TextField(verbose_name='Ünvan')),
                ('education_level', models.CharField(choices=[('BACHELOR', 'Bakalavr'), ('MASTER', 'Magistr'), ('PHD', 'Doktorantura'), ('OTHER', 'Digər')], max_length=20, verbose_name='Təhsil səviyyəsi')),
                ('specialization', models.CharField(max_length=100, verbose_name='İxtisas')),
                ('experience_years', models.PositiveIntegerField(verbose_name='İş təcrübəsi (il)')),
                ('start_date', models.DateField(verbose_name='İşə başlama tarixi')),
                ('teaching_subjects', models.CharField(blank=True, help_text='Vergüllə ayıraraq daxil edin', max_length=200, verbose_name='Tədris fənləri')),
                ('weekly_hours', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(40)], verbose_name='Həftəlik saat')),
                ('is_active', models.BooleanField(default=True, verbose_name='Aktivdir')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Yaradılma tarixi')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Yenilənmə tarixi')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='staff_members', to='school.school', verbose_name='Məktəb')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='staff_profile', to=settings.AUTH_USER_MODEL, verbose_name='İstifadəçi')),
            ],
            options={
                'verbose_name': 'İşçi',
                'verbose_name_plural': 'İşçilər',
                'ordering': ['user__last_name', 'user__first_name'],
            },
        ),
        migrations.CreateModel(
            name='StaffAttendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Tarix')),
                ('is_present', models.BooleanField(default=True, verbose_name='İştirak edir')),
                ('check_in', models.TimeField(blank=True, null=True, verbose_name='Gəlmə vaxtı')),
                ('check_out', models.TimeField(blank=True, null=True, verbose_name='Getmə vaxtı')),
                ('absence_type', models.CharField(blank=True, choices=[('SICK', 'Xəstə'), ('VACATION', 'Məzuniyyət'), ('PERSONAL', 'Şəxsi'), ('OTHER', 'Digər')], max_length=10, null=True, verbose_name='Qayıb növü')),
                ('note', models.TextField(blank=True, verbose_name='Qeyd')),
                ('recorded_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recorded_staff_attendances', to=settings.AUTH_USER_MODEL, verbose_name='Qeyd edən')),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendances', to='school.staff', verbose_name='İşçi')),
            ],
            options={
                'verbose_name': 'İşçi davamiyyəti',
                'verbose_name_plural': 'İşçi davamiyyəti',
                'ordering': ['-date'],
                'unique_together': {('staff', 'date')},
            },
        ),
    ]
