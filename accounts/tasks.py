from celery import shared_task
from .models import Reservation
from datetime import datetime

@shared_task
def update_reservation_status():
    print('hello')
    reservations = Reservation.objects.filter(check_out__lte=datetime.today())
    for reservation in reservations:
        if reservation.reservation_status != Reservation.CONFIRMED :
            reservation.reservation_status = Reservation.CONFIRMED
            reservation.save(update_fields=['reservation_status'])