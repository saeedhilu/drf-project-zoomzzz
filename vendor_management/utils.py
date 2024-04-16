from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.response import Response



# def change_password_link(user, email):
#     token = default_token_generator.make_token(user)
#     uid = urlsafe_base64_encode(force_bytes(user.pk))
#     reset_url = f"http://127.0.0.1:8000/vendor/change-password/{uid}/{token}/"  # Change this to your actual domain
#     send_mail(
#         'Password Reset Request',
#         f'Please click the following link to reset your password: {reset_url}',
#         'from@example.com',  # Change this to your email address
#         [email],
#         fail_silently=False,
#     )
#     return Response({'success': 'Password reset email sent'}, status=status.HTTP_200_OK)

from Levenshtein import distance

def is_password_similar(old_password, new_password):
    """
    Check if the new password is too similar to the old password.
    """
    lev_distance = distance(old_password, new_password)
    max_length = max(len(old_password), len(new_password))
    similarity_score = 1 - (lev_distance / max_length)
    return similarity_score > 0.8
