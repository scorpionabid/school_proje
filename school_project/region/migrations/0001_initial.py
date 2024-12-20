# Generated by Django 4.2.17 on 2024-12-19 11:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Region adı')),
                ('utis_code', models.CharField(max_length=7, unique=True, verbose_name='UTIS kodu')),
                ('phone_number', models.CharField(max_length=20, verbose_name='Əlaqə nömrəsi')),
                ('address', models.TextField(verbose_name='Ünvan')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='Email')),
                ('website', models.URLField(blank=True, verbose_name='Vebsayt')),
                ('total_schools', models.PositiveIntegerField(default=0, verbose_name='Məktəb sayı')),
                ('total_students', models.PositiveIntegerField(default=0, verbose_name='Şagird sayı')),
                ('total_teachers', models.PositiveIntegerField(default=0, verbose_name='Müəllim sayı')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Yaradılma tarixi')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Yenilənmə tarixi')),
                ('is_active', models.BooleanField(default=True, verbose_name='Aktivdir')),
                ('director', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='directed_region', to=settings.AUTH_USER_MODEL, verbose_name='Region rəhbəri')),
            ],
            options={
                'verbose_name': 'Region',
                'verbose_name_plural': 'Regionlar',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='RegionNews',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Başlıq')),
                ('content', models.TextField(verbose_name='Məzmun')),
                ('image', models.ImageField(blank=True, upload_to='region_news/', verbose_name='Şəkil')),
                ('published_at', models.DateTimeField(auto_now_add=True, verbose_name='Dərc tarixi')),
                ('is_active', models.BooleanField(default=True, verbose_name='Aktivdir')),
                ('published_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Dərc edən')),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='news', to='region.region', verbose_name='Region')),
            ],
            options={
                'verbose_name': 'Region xəbəri',
                'verbose_name_plural': 'Region xəbərləri',
                'ordering': ['-published_at'],
            },
        ),
        migrations.CreateModel(
            name='RegionDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Başlıq')),
                ('document_type', models.CharField(choices=[('REPORT', 'Hesabat'), ('PLAN', 'Plan'), ('ORDER', 'Əmr'), ('OTHER', 'Digər')], max_length=10, verbose_name='Sənəd növü')),
                ('file', models.FileField(upload_to='region_documents/', verbose_name='Fayl')),
                ('description', models.TextField(blank=True, verbose_name='Açıqlama')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='Yüklənmə tarixi')),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='region.region', verbose_name='Region')),
                ('uploaded_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Yükləyən')),
            ],
            options={
                'verbose_name': 'Region sənədi',
                'verbose_name_plural': 'Region sənədləri',
                'ordering': ['-uploaded_at'],
            },
        ),
    ]
