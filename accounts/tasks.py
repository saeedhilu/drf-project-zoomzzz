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




