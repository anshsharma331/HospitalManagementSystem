from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from HealthPlus.models import Patient, Doctor, Appointment, Disease


class LoginForm(forms.Form):
    """Form for user login."""
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")


class CustomPasswordResetForm(PasswordResetForm):
    """Custom password reset form."""
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'class': 'form-control'})
    )


class PatientRegistrationForm(forms.ModelForm):
    """Form for patient registration."""
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'date_of_birth', 'phone_number', 'address', 'diseases']
        widgets = {
            'diseases': forms.CheckboxSelectMultiple()
        }

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['email'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        patient = super().save(commit=False)
        patient.user = user
        if commit:
            self.save_m2m()  # Save many-to-many relationships
            patient.save()
        return patient


class DoctorRegistrationForm(forms.ModelForm):
    """Form for doctor registration."""
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Doctor
        fields = ['first_name', 'last_name', 'date_of_birth', 'speciality', 'experience', 'diseases']
        widgets = {
            'diseases': forms.CheckboxSelectMultiple()
        }

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['email'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        doctor = super().save(commit=False)
        doctor.user = user
        if commit:
            doctor.save()
        return doctor


class AppointmentForm(forms.ModelForm):
    """Form for scheduling an appointment."""
    disease = forms.ModelChoiceField(queryset=Disease.objects.all(), label="Disease")
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.none(), label="Doctor")
    date = forms.DateField(widget=forms.SelectDateWidget)
    time = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))

    class Meta:
        model = Appointment
        fields = ['disease', 'doctor', 'date', 'time']

    def __init__(self, *args, **kwargs):
        patient = kwargs.pop('patient', None)
        super().__init__(*args, **kwargs)
        
        if patient:
            self.fields['disease'].queryset = patient.diseases.all()
            self.fields['doctor'].queryset = Doctor.objects.filter(diseases__in=patient.diseases.all()).distinct()


class PatientEditForm(forms.ModelForm):
    """Form for editing patient information."""
    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'date_of_birth', 'phone_number', 'address', 'diseases']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter your first name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter your last name'
        self.fields['date_of_birth'].widget.attrs['placeholder'] = 'YYYY-MM-DD'


class DoctorEditForm(forms.ModelForm):
    """Form for editing doctor information."""
    class Meta:
        model = Doctor
        fields = ['first_name', 'last_name', 'date_of_birth', 'phone_number', 'address', 'speciality', 'diseases', 'experience']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter your first name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter your last name'
        self.fields['date_of_birth'].widget.attrs['placeholder'] = 'YYYY-MM-DD'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter your phone number'
        self.fields['address'].widget.attrs['placeholder'] = 'Enter your address'
        self.fields['speciality'].widget.attrs['placeholder'] = 'Enter your speciality'
        self.fields['experience'].widget.attrs['placeholder'] = 'Enter your experience in years'


class RescheduleAppointmentForm(forms.ModelForm):
    """Form for rescheduling an appointment."""
    class Meta:
        model = Appointment
        fields = ['date', 'time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }
