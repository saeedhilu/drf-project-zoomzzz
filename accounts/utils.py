import random
from google.auth.transport import requests as GoogleRequest
from google.oauth2 import id_token
from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from django.core.mail import send_mail
from requests.exceptions import RequestException
import requests
from django.core.validators import RegexValidator
from .models import User,OTP
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework import status
from datetime import timedelta
from django.utils import timezone
from Levenshtein import distance
from django.http import HttpResponse
from django.core.validators import RegexValidator
from phonenumbers import parse as phonenumbers_parse, is_valid_number as phonenumbers_is_valid
from rest_framework import serializers
from .constants import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
User = get_user_model()

def generate_otp_code():
    """
    Generating OTP for all purpuse

    """
    return ''.join(random.choices('0123456789', k=6))

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.conf import settings

class Google_signin():
    """
    Class for Google Sign-In authentication.
    """

    @staticmethod
    def validate(access_token):
        """
        Validate Google access token.

        :param access_token: The access token received from Google.
        :return: User data if validation is successful, otherwise None.
        """
        try:
            id_info = id_token.verify_oauth2_token(access_token, google_requests.Request(), settings.GOOGLE_CLIENT_ID)
            if 'accounts.google.com' in id_info['iss']:
                return id_info
        except Exception as e:
            print('Error:', e)
            return None


def login_google_user(email):
    """
    Authenticate and login a user using Google credentials.

    Returns User information along with access and refresh tokens.
    """
    user = User.objects.filter(email=email).first()
    print('user i s:',user)
    print(user)
    print(email)
    if not user:
        raise AuthenticationFailed("Invalid login credentials")
    

    user_tokens = user.tokens
    user_data = {
        'email': user.email,
        'username': user.username,
        'access_token': user_tokens['access'],
        'refresh_token': user_tokens['refresh'],
        "id":user.id,
        "phone_number": user.phone_number,
        "is_vendor": user.is_vendor,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }
    if user.image:
        user_data['image'] = str(user.image)
    return {
       "user":user_data
                    
    }



def register_google_user(email, username):
    """
    Register a new user with Google credentials.

    Returns User information along with access and refresh tokens.
    """
    user = User.objects.filter(email=email)
    if user.exists():
        return login_google_user(email)
    else:
        new_user = {
            'email': email,
            'username': username,
            'password': settings.CUSTOM_PASSWORD_FOR_AUTH
        }
        register_user = User.objects.create_user(**new_user)
        register_user.is_active = True
        register_user.save()
        return login_google_user(email)



def send_otp_email(email,otp , first_name=None):
    print('entered in sent otp:')
    subject = "Your OTP for Vendor Sign Up"
    message = f"Hi {first_name},\n\nYour OTP is: {otp}\n\nPlease use this OTP to complete your sign-up process.\n\nThank you."  
    sender = settings.EMAIL_HOST_USER  # Sender's email address
    recipient_list = [email]
    send_mail(subject, message, sender, recipient_list)

def forgot_password_link(user, email):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    reset_url = f"http://127.0.0.1:8000/vendor/forgot_password_change/{uid}/{token}/"  # Change this to your actual domain
    send_mail(
        'Password Reset Request',
        f'Please click the following link to reset your password: {reset_url}',
        'from@example.com',  # Change this to your email address
        [email],
        fail_silently=False,
    )
    return HttpResponse({'success': 'Password reset email sent'}, status=status.HTTP_200_OK)

import requests

def send_sms(message, phone_number):
    try:
        message = f'Hello {message}, This is a test message from spring edge'
        mobileno = f'{phone_number}'
        sender = 'SEDEMO'
        apikey = '621492a44a89m36c2209zs4l7e74672cj'

        baseurl = 'https://instantalerts.co/api/web/send/?apikey=' + apikey
        url = baseurl + '&sender=' + sender + '&to=' + mobileno + '&message=' + message + '&format=json'
        
        response = requests.get(url)
        
        if response.status_code == 200:
            return True 
        else:
            print(f"Failed to send SMS. Status code: {response.status_code}")
            return False  
    except requests.exceptions.RequestException as e:
        print(f"Error sending SMS: {e}")
        return False   
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False




def generate_otp_code(length=6):
    """
    Generate a random OTP code of specified length.
    
    Args:
        length (int): Length of the OTP code (default is 6).
    
    Returns:
        str: Generated OTP code.
    """
    # Define the characters to choose from
    characters = '0123456789'
    
    # Generate the OTP code by selecting random characters
    otp_code = ''.join(random.choice(characters) for _ in range(length))
    
    return otp_code



def phone_regex(value):
    phone_regex = RegexValidator(
    regex=r'^\d{15}$',
    message='Phone number must be 10 digits only',
    )
    return phone_regex


def create_otp(email, password=None):
    """
    Create or update OTP for the given email and password.
    """
    otp = generate_otp_code()
    otp_expiry = timezone.now() + timedelta(seconds=40)
    
    defaults = {'otp_code': otp, 'otp_expiry': otp_expiry}
    if password:
        defaults['password'] = password
    
    otp_instance, created = OTP.objects.update_or_create(
        email=email,
        defaults=defaults
    )
    return otp, otp_instance, created





def is_password_similar(old_password, new_password):
    """
    Check if the new password is too similar to the old password.
    """
    lev_distance = distance(old_password, new_password)
    max_length = max(len(old_password), len(new_password))
    similarity_score = 1 - (lev_distance / max_length)
    return similarity_score > 0.8


def generate_and_send_otp(phone_number):
    """
    Generate OTP and send it via SMS.
    """
    otp_instance, created = OTP.objects.get_or_create(phone_number=phone_number)

    
    otp_instance.otp_code = generate_otp_code()
    otp_instance.otp_expiry = timezone.now() + timedelta(minutes=5)  # Set expiry time, adjust as needed
    otp_instance.save()

    message = f'Your OTP IS : {otp_instance.otp_code}'
    sms_sent = send_sms(message, phone_number)

    if sms_sent:
        return otp_instance, GENERATE_OTP_MESSAGE
    else:
        return None, "Failed to send OTP"
    



def resend_otp(phone_number):
    """
    Resend OTP to the provided phone number.
    Returns the OTP instance and a message indicating success or failure.
    """
    try:
        otp_instance = OTP.objects.get(phone_number=phone_number)

        

        otp_instance.otp_code = generate_otp_code()
        otp_instance.otp_expiry = timezone.now() + timedelta(seconds=30)
        otp_instance.save()

        message = f'Your OTP is: {otp_instance.otp_code}'
        sms_sent = send_sms(message, phone_number)

        if sms_sent:
            return otp_instance, 'OTP resent successfully'
        else:
            return None, 'Failed to resend OTP'
    except OTP.DoesNotExist:
        return None, 'No OTP exists'
    except Exception as e:
        return None, f'Failed to resend OTP. Exception: {str(e)}'
    


def verify_otp(phone_number, otp_entered):
    print('hpne number ',phone_number)
    print('entered otp ',otp_entered)
    """
    Verify the OTP entered by the user.
    Returns a tuple containing a boolean indicating whether the OTP is valid and a message.
    """
    try:
        otp_instance = OTP.objects.get(phone_number=phone_number)
        print(otp_instance)
        if otp_instance.otp_code == otp_entered and otp_instance.otp_expiry >= timezone.now():
            otp_instance.delete()
            return True, "OTP verification successful"
        else:
            return False, "Invalid OTP or OTP expired"
    except OTP.DoesNotExist:
        return False, "OTP entry not found Does not "
    except Exception as e:
        return False, f"Failed to verify OTP. Exception: {str(e)}"





    
def validate_phone_number(value):
    """
    Validate phone number format and uniqueness.
    """
    
        
    if User.objects.filter(phone_number=value).exists():
        raise serializers.ValidationError("Phone number is already in usedd")
        
    
def validate_unique_email(value):
    """
    Validate email uniqueness.
    """
    if User.objects.filter(email=value).exists():
        raise serializers.ValidationError("Email is already in use.")
    return value


def validate_name(value):
    """
    Check Username validator
    """
    if not value:
            raise serializers.ValidationError("Name cannot be empty.")
    return value 

def generate_otp(phone_number):

    """
    Generate a new OTP for the given phone number.
    
    Args:
        phone_number (str): The phone number to generate OTP for.
    
    Returns:
        OTP: The generated OTP instance.
    """
    otp_code = generate_otp_code()  # Assuming this function exists
    otp_expiry = timezone.now() + timedelta(minutes=5)

    otp_instance, created = OTP.objects.get_or_create(
        phone_number=phone_number,
        defaults={'otp_code': otp_code, 'otp_expiry': otp_expiry}
    )

    if not created:
        # Update existing OTP instance
        otp_instance.otp_code = otp_code
        otp_instance.otp_expiry = otp_expiry
        otp_instance.save()

    return otp_instance




from django.contrib.auth.tokens import PasswordResetTokenGenerator

def get_random_secret_key():
    """Generates a cryptographically secure random string suitable for use as a cancellation token."""
    generator = PasswordResetTokenGenerator()
    return generator.make_token()




from django.core.cache import cache

def cache_queryset(key, queryset, timeout=300):
    result = cache.get(key)
    print('from cache')
    if not result:
        print('form db')
        result = queryset
        cache.set(key, result, timeout)
    return result





from rooms.models import Room
from django.utils import timezone
from datetime import timedelta
from .models import Reservation, User
from django.db.models import Q
def get_summary_statistics():

    """
    Total summary statics
    """
    # Find the total booking count
    total_bookings = Reservation.objects.count()
    total_rooms    = Room.objects.count()
    # find total venodrs count
    total_vendors = User.objects.filter(is_vendor=True).count()
    total_users = User.objects.filter(is_vendor=False,is_superuser=False).count()
    
    # find total check in count( pending means user checkin)
    total_check_ins = Reservation.objects.filter(
        Q(reservation_status='Pending') | Q(reservation_status='PENDING')
    ).count()
    
    # find the total checkout (Confimed means User checkouted)
    total_check_outs = Reservation.objects.filter(
        Q(reservation_status='CONFIRMED') | Q(reservation_status='Confirmed')
    ).count()
    
    return {
        'total_bookings': total_bookings,
        'total_vendors': total_vendors,
        'total_check_ins': total_check_ins,
        'total_check_outs': total_check_outs,
        'total_rooms': total_rooms,
        'total_users':total_users,

    }


from django.db.models import Sum


def get_vendor_summary_statistics(user_id):
    """
    Vendor summary statistics
    """
    try:
        # Get total bookings, total check-ins, and total check-outs for the vendor
        
        total_bookings = Reservation.objects.filter(
            room__created_by=user_id).count()
        total_check_ins = Reservation.objects.filter(
            room__created_by=user_id, reservation_status=Reservation.PENDING).count()
        total_check_outs = Reservation.objects.filter(
            room__created_by=user_id, reservation_status=Reservation.CONFIRMED).count()

        total_earnings = Reservation.objects.filter(
            room__created_by=user_id).aggregate(total_earnings=Sum('amount'))['total_earnings'] or 0

        return {
            'total_bookings': total_bookings,
            'total_check_ins': total_check_ins,
            'total_check_outs': total_check_outs,
            'total_earnings': total_earnings,
        }
    except Exception as e:
        # Handle exceptions, such as invalid user_id or database errors
        return {'error': str(e)}


# # utils.py

# from django.core.exceptions import ValidationError
# from .models import Reservation

# def validate_unique_booking(room, check_in, check_out, instance=None):
#     overlapping_bookings = Reservation.objects.filter(
#         room=room,
#         check_in__lt=check_out,
#         check_out__gt=check_in
#     ).exclude(reservation_status='Canceled')

#     if instance:
#         overlapping_bookings = overlapping_bookings.exclude(pk=instance.pk)

#     if overlapping_bookings.exists():
#         raise ValidationError('Room is already booked for the selected dates.')
