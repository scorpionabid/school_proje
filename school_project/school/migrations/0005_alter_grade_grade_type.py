# Generated by Django 4.2.17 on 2024-12-20 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0004_alter_classroom_class_teacher_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grade',
            name='grade_type',
            field=models.CharField(choices=[('DAILY', 'Gündəlik'), ('KSQ', 'Kiçik Summativ'), ('BSQ', 'Böyük Summativ'), ('MONITORING', 'Monitoring'), ('FINAL', 'Yekun')], max_length=20, verbose_name='Qiymət növü'),
        ),
    ]
