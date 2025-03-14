# Generated by Django 4.2.17 on 2024-12-22 03:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sector', '0002_sector_average_attendance_sector_average_grade_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Başlıq')),
                ('description', models.TextField(blank=True, verbose_name='Təsvir')),
                ('file', models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name='Fayl')),
                ('document_type', models.CharField(choices=[('REPORT', 'Hesabat'), ('PLAN', 'Plan'), ('OTHER', 'Digər')], max_length=20, verbose_name='Sənəd növü')),
                ('status', models.CharField(choices=[('PENDING', 'Gözləyir'), ('SUBMITTED', 'Təqdim edilib'), ('APPROVED', 'Təsdiqlənib'), ('REJECTED', 'Rədd edilib')], default='PENDING', max_length=20, verbose_name='Status')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Yaradılma tarixi')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Yenilənmə tarixi')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_documents', to=settings.AUTH_USER_MODEL, verbose_name='Yaradan')),
                ('sector', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sector_documents', to='sector.sector', verbose_name='Sektor')),
            ],
            options={
                'verbose_name': 'Sənəd',
                'verbose_name_plural': 'Sənədlər',
                'ordering': ['-created_at'],
            },
        ),
    ]
