import random
from google.auth.transport import requests
from google.oauth2 import id_token
from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from accounts.models import User
from django.core.mail import send_mail
from requests.exceptions import RequestException
import requests

def generate_otp_code():
    """
    Generating OTP for all purpuse

    """
    return ''.join(random.choices('0123456789', k=6))



class GoogleAuthenticator:
    @staticmethod
    def validate(access_token):
        try:
            id_info = id_token.verify_oauth2_token(access_token, requests.Request())
            if "accounts.google.com" in id_info['iss']:
                return id_info
        except Exception as e:
            return "token is invalid or has expired "


def login_social_user(email,password):
    user = authenticate(email=email,password=password)
    if user:
        user_tokens = user.token
        return {
            'email': user.email,    
            'username': user.get_username(),
            'access_token': str(user_tokens.get('access')),
            'refresh_token': str(user_tokens.get('refresh'))
        }
    return None

def register_social_user(email, username):
    user=User.objects.filter(email=email)
    if user.exists():
        login_social_user(email, settings.CUSTOM_PASSWORD_FOR_AUTH)
    else:   
        new_user={
            'email':email,
            'username':username,
            'password':settings.CUSTOM_PASSWORD_FOR_AUTH
        }
        register_user=User.objects.create_user(**new_user)
        register_user.is_active=True
        register_user.save()
        login_social_user(email, settings.CUSTOM_PASSWORD_FOR_AUTH)


def send_otp_email(email, first_name, otp):
    subject = "Your OTP for Vendor Sign Up"
    message = f"Hi {first_name},\n\nYour OTP is: {otp}\n\nPlease use this OTP to complete your sign-up process.\n\nThank you."  
    sender = settings.EMAIL_HOST_USER  # Sender's email address
    recipient_list = [email]
    send_mail(subject, message, sender, recipient_list)




def send_sms(message, phone_number):
    try:
        message = f'Hello {message}, This is a test message from spring edge'
        mobileno = f'91{phone_number}'
        sender = 'SEDEMO'
        apikey = '621492a44a89m36c2209zs4l7e74672cj'

        baseurl = 'https://instantalerts.co/api/web/send/?apikey=' + apikey
        url = baseurl + '&sender=' + sender + '&to=' + mobileno + '&message=' + message + '&format=json'
        
        response = requests.get(url)
        
        if response.status_code == 200:
            return True  # SMS sent successfully
        else:
            return False  # Failed to send SMS
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return False  # Failed to send SMS due to exception
    



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









    # client = vonage.Client(key="73bb1e67", secret="VBE4FosOO0vnRj0Q")
    # sms = vonage.Sms(client)
    # Check for HTTP codes other than 200
    # if response.status_code != 200:
    #     print('Status:', response, 'Problem with the request.')
    # exit()

    
    # try:
    #     responseData = sms.send_message(
    #         {
    #             "from": "Vonage APIs",
    #             "to": phone_number,
    #             "text": message,
    #         }
    #     )

    #     if responseData["messages"][0]["status"] == "0":
    #         print("Message sent successfully")
    #         return True
    #     else:
    #         print(f"Failed to send message. Vonage response: {responseData}")
    #         return False
    # except Exception as e:
    #     print(f"An error occurred while sending message: {e}")
    #     return False