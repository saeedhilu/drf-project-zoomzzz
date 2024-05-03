from django.test import TestCase

# Create your tests here.
from celery import shared_task
from .models import Reservation

@shared_task
def update_reservation_status():
    reservations = Reservation.objects.filter(checkout_date__lte=datetime.date.today(), status__ne='cancel')
    for reservation in reservations:
        reservation.status = 'confirm'
        reservation.save()