# from celery import shared_task
# from .models import Booking

# @shared_task
# def schedule_booking_deletion(booking_id):
#     # Wait for 2 minutes before deleting the booking
#     from time import sleep
#     sleep(120)

#     # Fetch the booking instance
#     try:
#         booking = Booking.objects.get(id=booking_id)
#         if booking.is_active:
#             # Mark booking as canceled
#             booking.payment_status = 'CANCELED'
#             booking.is_active = False
#             booking.save()
#     except Booking.DoesNotExist:
#         # Handle the case where the booking does not exist
#         pass
# from celery import shared_task
# from .models import Booking

# @shared_task
# def update_booking_status():
#     now = datetime.now().date()  # Current date

#     # Get all bookings that are still pending and their check-in date has passed
#     pending_bookings = Booking.objects.filter(status='pending', check_in__lt=now)

#     # Update the status to 'confirmed'
#     for booking in pending_bookings:
#         booking.status = 'confirmed'
#         booking.save()




from django.db.models.signals import post_save
from django.dispatch import receiver
from pytz import timezone
from .models import Reservation

@receiver(post_save, sender=Reservation)
def update_reservation_status(sender, instance, created, **kwargs):
    if not created:  # Only update on existing reservations
        today = timezone.now().date()
        if instance.checkout_date and instance.checkout_date <= today:
            instance.reservation_status = 'Confirmed'
            instance.save()

