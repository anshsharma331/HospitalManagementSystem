from django.urls import reverse,reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import FormView, TemplateView, View, DetailView
from django.http import JsonResponse, HttpResponse, Http404, HttpResponseRedirect
from django.core.mail import send_mail

from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LogoutView
from django.contrib.auth import authenticate, login
from django.contrib import messages

from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_time

from datetime import datetime, timedelta, time
import pandas as pd
from weasyprint import HTML
from icalendar import Calendar, Event

from .models import Patient, Doctor, Appointment, Disease
from .forms import RescheduleAppointmentForm, DoctorEditForm ,PatientEditForm, PatientRegistrationForm, DoctorRegistrationForm, LoginForm, AppointmentForm


class WelcomePageView(TemplateView):
    """Displays the welcome page."""
    template_name = 'welcome.html'


class CustomLogoutView(LogoutView):
    """Custom logout view."""
    next_page = reverse_lazy('welcome')


class PatientRegisterView(SuccessMessageMixin, FormView):
    """Handles patient registration."""
    template_name = 'patient_registration.html'
    form_class = PatientRegistrationForm
    success_url = '/login/'
    success_message = "Patient registered successfully!"

    def form_valid(self, form):
        try:
            form.save()
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f"An error occurred: {str(e)}")
            return HttpResponseRedirect(reverse('patient_register'))


class DoctorRegisterView(SuccessMessageMixin, FormView):
    """Handles doctor registration."""
    template_name = 'doctor_registration.html'
    form_class = DoctorRegistrationForm
    success_url = '/login/'
    success_message = "Doctor registered successfully!"

    def form_valid(self, form):
        try:
            form.save()
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f"An error occurred: {str(e)}")
            return HttpResponseRedirect(reverse('doctor_register'))


class CustomSuccessMessageMixin(SuccessMessageMixin):
    """Custom success message mixin."""
    def get_success_url(self):
        user = self.request.user
        if hasattr(user, 'doctor'):
            return reverse('doctor_dashboard', args=[user.doctor.pk])
        elif hasattr(user, 'patient'):
            return reverse('patient_dashboard', args=[user.patient.pk])
        else:
            return reverse('welcome')


class LoginView(CustomSuccessMessageMixin, FormView):
    """Handles user login."""
    template_name = 'login.html'
    form_class = LoginForm
    success_message = "Login successful!"

    def form_valid(self, form):
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        print(f"Attempting to authenticate user with email: {email}")
        user = authenticate(self.request, username=email, password=password)
        print(f"Authenticated user: {user}")
        if user is not None:
            login(self.request, user)
            return super().form_valid(form)
        else:
            messages.error(self.request, "Invalid login credentials.")
            return self.form_invalid(form)

    def form_invalid(self, form):
        print(f"Form invalid with errors: {form.errors}")
        return super().form_invalid(form)


class PatientDashboardView(TemplateView):
    """Displays the patient dashboard."""
    template_name = 'patient_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = Patient.objects.get(user=self.request.user)
        current_appointments = Appointment.objects.filter(patient=patient, status='current')
        past_appointments = Appointment.objects.filter(patient=patient, status='past')
        pending_appointments = Appointment.objects.filter(patient=patient, status='pending')

        context['patient'] = patient
        context['current_appointments'] = current_appointments
        context['past_appointments'] = past_appointments
        context['pending_appointments'] = pending_appointments

        return context


class DoctorDashboardView(View):
    """Displays the doctor dashboard."""
    def get(self, request, pk):
        doctor = get_object_or_404(Doctor, pk=pk)
        total_patients_with_appointments = Appointment.objects.filter(doctor=doctor).count()
        todays_appointments = Appointment.objects.filter(doctor=doctor, date=timezone.now().date()).count()
        pending_appointments = Appointment.objects.filter(doctor=doctor, status='pending')
        past_appointments = Appointment.objects.filter(doctor=doctor, status='past')

        context = {
            'doctor': doctor,
            'total_patients_with_appointments': total_patients_with_appointments,
            'todays_appointments': todays_appointments,
            'pending_appointments': pending_appointments,
            'past_appointments': past_appointments,
        }
        return render(request, 'doctor_dashboard.html', context)



class BookAppointmentView(TemplateView):
    """Handles booking appointments."""
    template_name = 'book_appointment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.request.user.patient
        diseases = patient.diseases.all()

        # Generating time slots from 10:00 AM to 6:00 PM with 30-minute intervals
        time_slots = []
        start_time = datetime.strptime('10:00', '%H:%M')
        end_time = datetime.strptime('18:00', '%H:%M')
        while start_time < end_time:
            time_slots.append(start_time.strftime('%H:%M'))
            start_time += timedelta(minutes=30)

        context['patient'] = patient
        context['diseases'] = diseases
        context['time_slots'] = time_slots
        context['today'] = datetime.today().strftime('%Y-%m-%d')
        return context

    def generate_icalendar(self, appointment):
        """Generates iCalendar (.ics) file for the appointment."""
        cal = Calendar()
        event = Event()
        event.add('summary', f'Appointment with Dr. {appointment.doctor.first_name} {appointment.doctor.last_name}')
        
        start_datetime = datetime.combine(appointment.date, appointment.time)
        end_datetime = start_datetime + timedelta(minutes=30)

        event.add('dtstart', start_datetime)
        event.add('dtend', end_datetime)
        event.add('dtstamp', datetime.now())
        event['uid'] = f'{appointment.id}@yourdomain.com'
        event.add('priority', 5)

        cal.add_component(event)
        return cal.to_ical()

    def post(self, request, *args, **kwargs):
        disease_id = request.POST.get('disease')
        doctor_id = request.POST.get('doctor')
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')

        if disease_id and doctor_id and date_str and time_str:
            patient = request.user.patient

            try:
                doctor = Doctor.objects.get(pk=doctor_id)
            except Doctor.DoesNotExist:
                raise Http404("Doctor does not exist")

            date = parse_date(date_str)
            time = parse_time(time_str)

            if date is None or time is None:
                return self.get(request, *args, **kwargs)

            appointment = Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                date=date,
                time=time,
                status='pending'
            )

            subject = 'Appointment Confirmation'
            message = f'Dear {patient.first_name},\n\nYour appointment with Dr. {doctor.first_name} {doctor.last_name} has been scheduled for {date} at {time}.\n\nThank you for booking with us.\n\nBest regards,\nHealthPlus'
            from_email = 'anshsharma.as331@gmail.com'
            recipient_list = [patient.user.email]

            try:
                send_mail(subject, message, from_email, recipient_list)
                print("Email sent successfully")
            except Exception as e:
                print("Error sending email:", e)

            ical_data = self.generate_icalendar(appointment)
            response = HttpResponse(ical_data, content_type='text/calendar')
            response['Content-Disposition'] = f'attachment; filename=appointment_{appointment.id}.ics'

            return redirect(reverse('appointment_success', kwargs={'appointment_id': appointment.id}))

        return self.get(request, *args, **kwargs)


class GetDoctorsView(View):
    """Retrieves list of doctors based on disease."""
    def get(self, request, *args, **kwargs):
        disease_id = request.GET.get('disease')
        if disease_id:
            try:
                # Ensure that the disease_id is valid
                disease = Disease.objects.get(id=disease_id)
            except Disease.DoesNotExist:
                return JsonResponse({'error': 'Invalid disease ID'}, status=400)
            
            # Filter doctors based on the disease
            doctors = Doctor.objects.filter(diseases__id=disease_id).values('user_id', 'first_name', 'last_name')
            doctors_list = list(doctors)
            return JsonResponse(doctors_list, safe=False)
        return JsonResponse({'error': 'Disease ID not provided'}, status=400)


class GetAvailableTimesView(View):
    """Provides available time slots for a doctor on a given date."""

    def get(self, request, *args, **kwargs):
        doctor_id = request.GET.get('doctor_id')
        date_str = request.GET.get('date')

        if not doctor_id or doctor_id == 'undefined' or not date_str:
            return JsonResponse({'error': 'Doctor ID and Date are required'}, status=400)

        try:
            doctor_id = int(doctor_id)
        except ValueError:
            return JsonResponse({'error': 'Invalid Doctor ID'}, status=400)

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()  # Explicit date format parsing
        except ValueError:
            return JsonResponse({'error': 'Invalid Date format. Use YYYY-MM-DD'}, status=400)

        # Fetch booked times for the doctor on the given date
        booked_appointments = Appointment.objects.filter(doctor_id=doctor_id, date=date).values_list('time', flat=True)
        booked_times = list(booked_appointments)

        # Generate all possible time slots from 10:00 AM to 6:00 PM with 30-minute intervals
        all_time_slots = []
        start_time = time(hour=10, minute=0)  # Create time object directly
        end_time = time(hour=18, minute=0)
        current_time = datetime.combine(date, start_time)
        end_datetime = datetime.combine(date, end_time)

        while current_time < end_datetime:
            all_time_slots.append(current_time.time().strftime('%H:%M'))
            current_time += timedelta(minutes=30)

        # Filter out booked time slots
        available_time_slots = [slot for slot in all_time_slots if slot not in booked_times]

        return JsonResponse(available_time_slots, safe=False)


class AppointmentSuccessView(TemplateView):
    """Displays the appointment success page."""
    template_name = 'appointment_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        appointment_id = self.kwargs['appointment_id']
        appointment = get_object_or_404(Appointment, id=appointment_id)
        context['appointment'] = appointment
        return context


class PatientEditView(SuccessMessageMixin, View):
    """Handles editing patient profile."""
    template_name = 'edit_patient.html'
    success_message = "Patient profile updated successfully!"

    def get(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk)
        form = PatientEditForm(instance=patient)
        return render(request, self.template_name, {'form': form})

    def post(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk)
        form = PatientEditForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('patient_dashboard', args=[pk]))
        return render(request, self.template_name, {'form': form})


class DoctorEditView(SuccessMessageMixin, View):
    """Handles editing doctor profile."""
    template_name = 'edit_doctor.html'
    success_message = "Doctor profile updated successfully!"

    def get(self, request, pk):
        doctor = get_object_or_404(Doctor, pk=pk)
        form = DoctorEditForm(instance=doctor)
        return render(request, self.template_name, {'form': form})

    def post(self, request, pk):
        doctor = get_object_or_404(Doctor, pk=pk)
        form = DoctorEditForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            return redirect(reverse('doctor_dashboard', kwargs={'pk': doctor.pk}))
        return render(request, self.template_name, {'form': form})
    

class AppointmentDetailsView(DetailView):
    model = Appointment
    template_name = 'appointment_details.html'
    context_object_name = 'appointment'

    def get(self, request, *args, **kwargs):
        appointment = get_object_or_404(Appointment, pk=kwargs['pk'])
        context = {
            'appointment': appointment,
            'patient_info': {
                'Name': appointment.patient.first_name + ' ' + appointment.patient.last_name,
                'Date of Birth': appointment.patient.date_of_birth,
                'Phone Number': appointment.patient.phone_number,
                'Address': appointment.patient.address,
            },
            'doctor_info': {
                'Name': appointment.doctor.first_name + ' ' + appointment.doctor.last_name,
                'Speciality': appointment.doctor.speciality,
                'Experience': appointment.doctor.experience,
            },
            'diseases': appointment.doctor.diseases.all(),
            'appointment_details': {
                'Date': appointment.date,
                'Time': appointment.time,
            }
        }
        format = request.GET.get('format')
        if format == 'pdf':
            return self.render_to_pdf_response(context, 'appointment_details.pdf')
        elif format == 'excel':
            return self.render_to_excel_response(context, 'appointment_details.xlsx')
        else:
            return self.render_to_response(context)
    

class DownloadAppointmentExcelView(View):
    """Handles downloading appointment details as an Excel file."""
    def get(self, request, *args, **kwargs):
        appointment_id = kwargs.get('appointment_id')
        appointment = Appointment.objects.get(pk=appointment_id)

        # Create a DataFrame with appointment details
        appointment_data = {
            'Date': [appointment.date],
            'Time': [appointment.time],
            'Patient Name': [f"{appointment.patient.first_name} {appointment.patient.last_name}"],
            'Doctor Name': [f"{appointment.doctor.first_name} {appointment.doctor.last_name}"],
            'Doctor Speciality': [appointment.doctor.speciality],
            'Doctor Experience': [appointment.doctor.experience],
        }
        df = pd.DataFrame(appointment_data)

        # Write DataFrame to an Excel file
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=appointment_details.xlsx'
        with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Appointment Details')
        return response

class DownloadAppointmentPDFView(View):
    """Handles downloading appointment details as a PDF file."""
    def get(self, request, *args, **kwargs):
        appointment_id = kwargs.get('appointment_id')
        appointment = Appointment.objects.get(pk=appointment_id)

        # Prepare context data for the template
        context = {
            'appointment': appointment
        }

        # Render appointment details template to HTML string
        html_string = render_to_string('appointment_details_pdf.html', context)

        # Generate PDF from HTML string
        pdf_file = HTML(string=html_string).write_pdf()

        # Serve PDF file as response
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=appointment_details.pdf'
        return response

class CancelAppointmentView(View):
    """Handles canceling an appointment."""
    def get(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        return render(request, 'cancel_appointment.html', {'object': appointment})

    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        patient_pk = appointment.patient.pk  # Get the patient's pk before deleting the appointment
        appointment.delete()
        return redirect('patient_dashboard', pk=patient_pk)

class RescheduleAppointmentView(View):
    """Handles rescheduling an appointment."""
    def get(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        form = RescheduleAppointmentForm(instance=appointment)
        return render(request, 'reschedule_appointment.html', {'form': form, 'appointment': appointment})

    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        form = RescheduleAppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            return redirect('patient_dashboard', pk=appointment.patient.pk)
        return render(request, 'reschedule_appointment.html', {'form': form, 'appointment': appointment})