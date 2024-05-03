# management/commands/check_reservation_status.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import Reservation

class Command(BaseCommand):
    help = 'Checks reservation status and updates if checkout date has passed'

    def handle(self, *args, **options):

        # Get reservations with checkout date in the past and status not already "Canceled"
        overdue_reservations = Reservation.objects.filter(
            check_out__lt=timezone.now().date(),
            reservation_status__in=[Reservation.PENDING, Reservation.CONFIRMED]
        )

        for reservation in overdue_reservations:
            reservation.reservation_status = Reservation.CONFIRMED
            reservation.save()

        self.stdout.write(self.style.SUCCESS('Reservation statuses updated successfully'))
