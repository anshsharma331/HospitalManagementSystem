from django.core.management.base import BaseCommand
from django.utils import timezone
from HealthPlus.models import Appointment

class Command(BaseCommand):
    help = 'Update appointment statuses from pending to past or current'

    def handle(self, *args, **kwargs):
        now = timezone.now()

        # Update past appointments to 'past'
        past_appointments = Appointment.objects.filter(status='pending', date__lt=now.date())
        for appointment in past_appointments:
            appointment.status = 'past'
            appointment.save()

        # Update current appointments to 'current'
        current_appointments = Appointment.objects.filter(status='pending', date=now.date(), time__gte=now.time())
        for appointment in current_appointments:
            appointment.status = 'current'
            appointment.save()

        self.stdout.write(self.style.SUCCESS('Successfully updated appointment statuses'))