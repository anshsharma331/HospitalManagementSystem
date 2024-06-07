# Generated by Django 5.0.4 on 2024-05-28 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HealthPlus', '0002_doctor_address_doctor_password_doctor_phone_number_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctor',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$720000$e3Ng0Ul4HXqGdUoN6cyJ4o$qQS3ks7YactP6vQXzaRrhIOZF/ggVlt4xIou06UiJHg=', max_length=128),
        ),
        migrations.AlterField(
            model_name='patient',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$720000$VgNJjB5YebAOOcM7PBYEOY$TOIfQBgABhpDma/k2Nylg2QP8znE1nJEecHi0++UE/g=', max_length=128),
        ),
    ]