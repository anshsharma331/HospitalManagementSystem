# Generated by Django 5.0.4 on 2024-05-29 06:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HealthPlus', '0008_alter_doctor_user_alter_patient_user_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='doctor',
            name='email',
        ),
        migrations.RemoveField(
            model_name='patient',
            name='email',
        ),
        migrations.RemoveField(
            model_name='patient',
            name='password',
        ),
    ]
