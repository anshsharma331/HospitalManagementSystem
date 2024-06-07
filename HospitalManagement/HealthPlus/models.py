from django.db import models
from django.contrib.auth.models import User


class Disease(models.Model):
    """Model representing a disease."""
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class Patient(models.Model):
    """Model representing a patient."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    diseases = models.ManyToManyField(Disease, related_name='patients')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Doctor(models.Model):
    """Model representing a doctor."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    speciality = models.CharField(max_length=100)
    diseases = models.ManyToManyField(Disease, related_name='doctors')
    experience = models.PositiveIntegerField()
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.speciality}"


class Staff(models.Model):
    """Model representing a staff member."""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    designation = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.designation}"


class Shift(models.Model):
    """Model representing a shift for a staff member."""
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='shifts', default=None)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"Shift for {self.staff.first_name} {self.staff.last_name} on {self.date} ({self.start_time} - {self.end_time})"


class Appointment(models.Model):
    """Model representing an appointment."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('current', 'Current'),
        ('past', 'Past'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Appointment on {self.date} with Dr. {self.doctor.last_name}"
