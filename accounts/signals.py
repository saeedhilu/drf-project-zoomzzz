# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.utils import timezone
# from .models import Reservation

# @receiver(post_save, sender=Reservation)
# def update_reservation_status(sender, instance, created, **kwargs):
#     if not created:  # Only execute for updates, not new reservations
#         if instance.reservation_status == 'Pending' and instance.check_out <= timezone.now().date():
#             instance.reservation_status = 'Confirmed'
#             instance.save(update_fields=['reservation_status'])
