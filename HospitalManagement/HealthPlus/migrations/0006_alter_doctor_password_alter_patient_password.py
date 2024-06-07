# Generated by Django 5.0.4 on 2024-05-28 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HealthPlus', '0005_alter_doctor_password_alter_patient_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctor',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$720000$L19KLEG5Qx6YgBv4NM9VCf$moaeto58W535dllUQ/qFRXVOpY+jjRLTD97kPWhmcUU=', max_length=128),
        ),
        migrations.AlterField(
            model_name='patient',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$720000$MKJacekUKmwHRvW2gtzCvs$gUW0LdAwIocnBMdUmvmdS0asS+Rrc9wdWCkrd4cZi4Q=', max_length=128),
        ),
    ]
