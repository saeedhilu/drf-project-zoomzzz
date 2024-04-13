from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import timedelta
from django.utils import timezone
from accounts.models import User
from .serializers import GenerateEmailSerializer, VendorLoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from accounts.utils import send_otp_email,generate_otp_code
from accounts.models import OTP
from django.core.validators import RegexValidator, EmailValidator
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ForgotPasswordSerializer, PasswordChangeSerializer
from accounts.models import User
from datetime import timedelta
from .utils import send_email_link


class GenerateEmailView(APIView):
    """
    API endpoint to generate and send OTP via email for user registration.
    """
    serializer_class = GenerateEmailSerializer

    def create_otp(self, email):
        """
        Create or update OTP for the given email.
        """
        otp = generate_otp_code()
        otp_expiry = timezone.now() + timedelta(seconds=40)
        otp_instance, created = OTP.objects.update_or_create(
            email=email,
            defaults={'otp_code': otp, 'otp_expiry': otp_expiry}
        )
        return otp, otp_instance, created

    def post(self, request):
        """
        Generate OTP and send it to the provided email address.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            email = validated_data['email']
            phone_number = validated_data.get('phone_number')  # Extract phone number from validated data

            # Store email in session
            request.session['email'] = email

            try:
                # Check if there's an existing valid OTP for the email
                otp_instance = OTP.objects.get(email=email)
                if otp_instance.otp_expiry >= timezone.now():
                    # If the OTP is still valid, notify the user and return
                    return Response({'message': 'A valid OTP already exists for this email address.'}, status=status.HTTP_400_BAD_REQUEST)
            except OTP.DoesNotExist:
                pass

            try:
                # Create user
                user = User.objects.create_user(
                    email=email,
                    username=email,
                    password=make_password(validated_data['password']),
                    first_name=validated_data['first_name'],
                    last_name=validated_data['last_name'],
                    phone_number=phone_number  # Save phone number to the user object
                )

                # Set is_vendor to True
                user.is_vendor = True
                user.save()

                # Create or update OTP
                otp, otp_instance, _ = self.create_otp(email)

                # Send OTP email with the generated OTP
                send_otp_email(email, validated_data['first_name'], otp)

                # Return success response
                return Response({'message': 'OTP generated and sent successfully'}, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class VerifyEmailView(APIView):
    """
    API endpoint to verify email OTP and authenticate user as a vendor.
    """
    def post(self, request):
        # Retrieve email and OTP entered by the user
        email = request.session.get('email')
        otp_entered = request.data.get('otp')

        try:
            # Retrieve OTP instance from the database
            otp_instance = OTP.objects.get(email=email)

            # Check if OTP is valid and not expired
            if otp_instance.otp_code == otp_entered and otp_instance.otp_expiry >= timezone.now():
                # Delete the OTP instance as it's no longer needed
                otp_instance.delete()

                # Create or retrieve user by email
                user, created = User.objects.get_or_create(email=email)

                # Set the user password and other details
                # user.set_password(make_password(request.data.get('password')))
                # user.first_name = request.data.get('first_name')
                # user.last_name = request.data.get('last_name')
                # user.phone_number = request.data.get('phone_number')  

                # Debugging: Print user details before saving
                print("User before saving:", user.__dict__)

                user.is_vendor = True
                user.save()

                # Generate tokens for authentication
                access_token = RefreshToken.for_user(user)
                refresh_token = RefreshToken.for_user(user)
                refresh_token_exp = timezone.now() + timedelta(days=7)

                # Return success response with tokens and user information
                print("User after saving:", user.__dict__)
                return Response({
                    "access_token": str(access_token.access_token),
                    "refresh_token": str(refresh_token),
                    "refresh_token_expiry": refresh_token_exp.isoformat(),
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "phone_number": user.phone_number  
                    },
                    "message": "User signed up successfully as a vendor",
                }, status=status.HTTP_200_OK)
            else:
                # If OTP is invalid or expired, return error response
                return Response({'error': 'Invalid OTP or OTP expired'}, status=status.HTTP_400_BAD_REQUEST)
        except OTP.DoesNotExist:
            # If OTP entry is not found, return error response
            return Response({'error': 'OTP entry not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # If any other exception occurs, return generic error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ResendEmailOTPView(APIView):
    """ 
    API endpoint to resend OTP via email.
    """
    def post(self, request):
        email = request.data.get('email')
        try:
            otp_instance = OTP.objects.get(email=email)

            if otp_instance.otp_expiry < timezone.now():
                # If OTP is expired, generate a new OTP and update the expiry time
                otp = generate_otp_code()
                otp_expiry = timezone.now() + timedelta(seconds=40)
                otp_instance.otp_code = otp
                otp_instance.otp_expiry = otp_expiry
                otp_instance.save()

                # Resend OTP email
                send_otp_email(email, otp_instance.otp_code)  # Assuming send_otp_email is defined elsewhere

                return Response({'message': 'OTP resent successfully'}, status=status.HTTP_200_OK)
            else:
                # If OTP is not expired, return error indicating OTP resend is not allowed
                return Response({'error': 'OTP resend is not allowed until the previous OTP expires.'}, status=status.HTTP_400_BAD_REQUEST)
        except OTP.DoesNotExist:
            # If OTP entry does not exist, return error
            return Response({'error': 'OTP entry not found'}, status=status.HTTP_404_NOT_FOUND)



class VendorLoginView(APIView):
    def post(self, request):
        serializer = VendorLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')

            # Get the user
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # Check if the provided password matches the actual password
            if   user.check_password(password) == False:
                print(password,user.check_password(password))
                return Response({'error': 'Incorrect password'}, status=status.HTTP_401_UNAUTHORIZED)

            # Proceed with successful login
            # Generate tokens
            refresh = RefreshToken.for_user(user)

            # Additional vendor data
            vendor_data = {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                "phone_number":user.phone_number
            }

            # Return tokens and vendor data to the client
            return Response({
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                'vendor': vendor_data,
            }, status=status.HTTP_200_OK)
            
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        




class ForgotPasswordEmailView(APIView):
    EXPIRY_TIMEDELTA = timedelta(minutes=15)  # Adjust expiry duration as needed

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

            
            send_email_link(user,email)
            return Response({'success': 'Password reset email sent'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.models import User
from .serializers import PasswordChangeSerializer
from datetime import timedelta,datetime


class PasswordChangeView(APIView):
    TOKEN_EXPIRATION_DURATION = timedelta(minutes=15)  # Adjust expiry duration as needed

    def patch(self, request, uidb64=None, token=None):
        uidb64 = request.data.get('uidb64', uidb64)
        token = request.data.get('token', token)

        print(token)
        print(uidb64)

        if uidb64 and token:
            return self.handle_password_reset(request, uidb64, token)
        else:
            return self.handle_regular_password_change(request)

    def handle_password_reset(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid user or token'}, status=status.HTTP_400_BAD_REQUEST)

        # Verify the token
        if default_token_generator.check_token(user, token):
            # current_time  = datetime.now() + self.TOKEN_EXPIRATION_DURATION 
            token_expiry_time = datetime.now() +  self.TOKEN_EXPIRATION_DURATION
            

            # Check if the token has expired
            if token_expiry_time < datetime.now():
                return Response({'error': 'Reset token has expired'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = PasswordChangeSerializer(data=request.data, context={'user': user})
            if serializer.is_valid():
                new_password = serializer.validated_data['new_password']
                user.set_password(new_password)
                user.save()
                return Response({'success': 'Password changed successfully'}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Invalid reset token'}, status=status.HTTP_400_BAD_REQUEST)

    def handle_regular_password_change(self, request):
        if not isinstance(request.user, AnonymousUser):
            serializer = PasswordChangeSerializer(data=request.data, context={'user': request.user})
            if serializer.is_valid():
                old_password = serializer.validated_data.get('old_password')
                new_password = serializer.validated_data['new_password']
                confirm_password = serializer.validated_data['confirm_password']

                # Check if the old password matches the user's current password
                if not request.user.check_password(old_password):
                    return Response({'error': 'Incorrect password'}, status=status.HTTP_400_BAD_REQUEST)

                # Set the new password
                request.user.set_password(new_password)
                request.user.save()
                return Response({'success': 'Password changed successfully'}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)



# views.py

# from accounts.models import User
# from django.contrib.auth.tokens import default_token_generator
# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.utils.encoding import force_bytes, force_str

# from django.core.mail import send_mail
# from django.shortcuts import redirect
# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from .serializers import EmailSerializer, PasswordChangeSerializer
# from django.contrib.auth.tokens import default_token_generator
# from .utils import send_email_link

# from datetime import datetime, timedelta
# from django.utils import timezone
# from django.utils import timezone

# class ForgotPasswordEmailView(APIView):
#     EXPIRY_TIMEDELTA = timedelta(minutes=1)  # Adjust expiry duration as needed

#     def post(self, request):
#         serializer = EmailSerializer(data=request.data)
#         if serializer.is_valid():
#             email = serializer.validated_data['email']
#             try:
#                 user = User.objects.get(email=email)
#             except User.DoesNotExist:
#                 return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)
            
#             token = default_token_generator.make_token(user)

#             # Calculate expiry time
#             expiry_time = timezone.now() + self.EXPIRY_TIMEDELTA

#             # Send email with reset link and expiry time
#             send_email_link(user, email)
#             return Response({'success': 'Password reset email sent'}, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    










# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from django.contrib.auth.models import User
# from django.contrib.auth.tokens import default_token_generator
# from django.utils.encoding import force_bytes, force_str
# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.core.mail import send_mail
# from django.conf import settings
# from datetime import datetime, timedelta

# class ForgotPasswordView(APIView):
#     def post(self, request):
#         email = request.data.get('email')
#         if not email:
#             return Response({'error': 'Please provide an email address'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

#         # Generate token and encode user ID
#         uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
#         token = default_token_generator.make_token(user)

#         # Build password reset link
#         reset_url = f"{settings.FRONTEND_URL}/reset-password/{uidb64}/{token}/"
        
#         # Send password reset link to user's email
#         send_mail(
#             'Password Reset',
#             f'Click the link below to reset your password:\n{reset_url}',
#             settings.EMAIL_HOST_USER,
#             [email],
#             fail_silently=False,
#         )

#         return Response({'success': 'Password reset link sent'}, status=status.HTTP_200_OK)

# class PasswordChangeView(APIView):
#     def patch(self, request, uidb64, token):
#         new_password = request.data.get('new_password')

#         if not new_password:
#             return Response({'error': 'Please provide a new password'}, status=status.HTTP_400_BAD_REQUEST)

#         # Decode user ID from base64
#         uid = force_str(urlsafe_base64_decode(uidb64))

#         try:
#             user = User.objects.get(pk=uid)
#         except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#             return Response({'error': 'Invalid user or token'}, status=status.HTTP_400_BAD_REQUEST)

#         # Verify the token
#         if not default_token_generator.check_token(user, token):
#             return Response({'error': 'Invalid reset token'}, status=status.HTTP_400_BAD_REQUEST)

#         # Update user's password
#         user.set_password(new_password)
#         user.save()

#         return Response({'success': 'Password changed successfully'}, status=status.HTTP_200_OK)






# class OTPVerificationView(APIView):
#     def post(self, request):
#         serializer = OTPVerificationSerializer(data=request.data)
#         if serializer.is_valid():
#             otp = serializer.validated_data['otp']
#             if request.session.get('otp') == otp:
#                 return Response({'success': 'OTP verified successfully'}, status=status.HTTP_200_OK)
#             else:
#                 return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# views.py





# # views.py

# from django.contrib.auth.models import User
# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from .serializers import PasswordChangeSerializer

# class PasswordChangeView(APIView):
#     def post(self, request):
#         serializer = PasswordChangeSerializer(data=request.data)
#         if serializer.is_valid():
#             user = request.user
#             old_password = serializer.validated_data['old_password']
#             new_password = serializer.validated_data['new_password']

#             if not user.check_password(old_password):
#                 return Response({'error': 'Invalid old password'}, status=status.HTTP_400_BAD_REQUEST)

#             if old_password == new_password:
#                 return Response({'error': 'New password must be different from old password'}, status=status.HTTP_400_BAD_REQUEST)

#             user.set_password(new_password)
#             user.save()

#             return Response({'success': 'Password changed successfully'}, status=status.HTTP_200_OK)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




















# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from accounts.models import User
# from django.contrib.auth.tokens import default_token_generator
# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.utils.encoding import force_bytes, force_str
# from django.core.mail import send_mail
# from .serializers import PasswordResetRequestSerializer, PasswordResetConfirmSerializer

# class PasswordResetRequestView(APIView):
#     def post(self, request):
#         serializer = PasswordResetRequestSerializer(data=request.data)
#         if serializer.is_valid():
#             email = serializer.validated_data['email']
#             try:
#                 user = User.objects.get(email=email)
#             except User.DoesNotExist:
#                 return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)
#             token = default_token_generator.make_token(user)
#             uid = urlsafe_base64_encode(force_bytes(user.pk))
#             reset_url = f"http://127.0.0.1:8000/vendor/{uid}/{token}/"


#             send_mail(
#                 'Password Reset Request',
#                 f'Please click the following link to reset your password: {reset_url}',
#                 'from@example.com',
#                 [email],
#                 fail_silently=False,
#             )
#             return Response({'success': 'Password reset email sent'}, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class PasswordResetConfirmView(APIView):
#     def post(self, request, uidb64, token):
#         try:
#             uid = force_str(urlsafe_base64_decode(uidb64))
#             user = User.objects.get(pk=uid)
#         except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#             user = None
#         if user is not None and default_token_generator.check_token(user, token):
#             serializer = PasswordResetConfirmSerializer(data=request.data)
#             if serializer.is_valid():
#                 new_password = serializer.validated_data['new_password']
#                 user.set_password(new_password)
#                 user.save()
#                 return Response({'success': 'Password reset successful'}, status=status.HTTP_200_OK)
#             else:
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         return Response({'error': 'Invalid token or user'}, status=status.HTTP_400_BAD_REQUEST)

