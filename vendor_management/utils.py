from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.response import Response

def send_email_link(user, email):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    reset_url = f"http://127.0.0.1:8000/vendor/change-password/{uid}/{token}/"  # Change this to your actual domain
    send_mail(
        'Password Reset Request',
        f'Please click the following link to reset your password: {reset_url}',
        'from@example.com',  # Change this to your email address
        [email],
        fail_silently=False,
    )
    return Response({'success': 'Password reset email sent'}, status=status.HTTP_200_OK)
