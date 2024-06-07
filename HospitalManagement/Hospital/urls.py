from django.urls import path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from HealthPlus.views import GetAvailableTimesView, RescheduleAppointmentView, CancelAppointmentView, DownloadAppointmentPDFView, DownloadAppointmentExcelView, AppointmentDetailsView, AppointmentSuccessView, PatientEditView, DoctorEditView, GetDoctorsView, CustomLogoutView, BookAppointmentView, DoctorDashboardView, PatientDashboardView, WelcomePageView, PatientRegisterView, DoctorRegisterView, LoginView



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', WelcomePageView.as_view(), name='welcome'),
    path('patient/register/', PatientRegisterView.as_view(), name='patient_register'),
    path('doctor/register/', DoctorRegisterView.as_view(), name='doctor_register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('appointment_success/<int:appointment_id>/', AppointmentSuccessView.as_view(), name='appointment_success'),
    path('patient_dashboard/<int:pk>/', PatientDashboardView.as_view(), name='patient_dashboard'),
    path('doctor_dashboard/<int:pk>/', DoctorDashboardView.as_view(), name='doctor_dashboard'),
    path('book_appointment', BookAppointmentView.as_view(), name='book_appointment'),
    path('get-doctors/', GetDoctorsView.as_view(), name='get_doctors'),
    path('get-available-times/', GetAvailableTimesView.as_view(), name='get_available_times'),
    path('edit_patient/<int:pk>/', PatientEditView.as_view(), name='edit_patient'),
    path('edit_doctor/<int:pk>/', DoctorEditView.as_view(), name='edit_doctor'),
    path('appointment_details/<int:pk>/', AppointmentDetailsView.as_view(), name='appointment_details'),
    path('download_appointment_excel/<int:appointment_id>/', DownloadAppointmentExcelView.as_view(), name='download_appointment_excel'),
    path('download_appointment_pdf/<int:appointment_id>/', DownloadAppointmentPDFView.as_view(), name='download_appointment_pdf'),
    path('appointment/cancel/<int:pk>/', CancelAppointmentView.as_view(), name='cancel_appointment'),
    path('appointment/reschedule/<int:pk>/', RescheduleAppointmentView.as_view(), name='reschedule_appointment'),
    
    
    
    
    path('reset_password/', auth_views.PasswordResetView.as_view(
        template_name='password_reset_form.html',
        email_template_name='password_reset_email.html',
        subject_template_name='password_reset_subject.txt',
        success_url='/reset_password_done/'
    ), name='reset_password'),

    path('reset_password_done/', auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset_done.html'
    ), name='reset_password_done'),

    path('reset_password_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html',
        success_url='/reset_password_complete/'
    ), name='password_reset_confirm'),

    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html'
    ), name='password_reset_complete'),
]
