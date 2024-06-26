# Generated by Django 5.0.4 on 2024-06-05 08:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HealthPlus', '0010_alter_appointment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='bonus',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='doctor',
            name='deduction',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='doctor',
            name='salary',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.CreateModel(
            name='Shift',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shifts', to='HealthPlus.doctor')),
            ],
        ),
    ]
