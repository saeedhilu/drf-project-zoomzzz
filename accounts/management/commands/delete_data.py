from django.core.management.base import BaseCommand
from accounts.models import OTP
from django.utils import timezone
import logging

class Command(BaseCommand):
    help = 'Deletes expired OTP records from the OTP model'

    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        logger.info('Deleting expired OTP records from the OTP model...')

        # Get current time
        current_time = timezone.now()

        # Filter expired OTP records
        expired_otps = OTP.objects.filter(otp_expiry__lt=current_time)

        # Delete expired OTP records
        num_deleted = expired_otps.delete()[0]
        
        logger.info(f'Deleted {num_deleted} expired OTP records from the OTP model.')
