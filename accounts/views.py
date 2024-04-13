from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import timedelta
from django.utils import timezone
from .models import OTP, User
from .serializers import GenerateOTPSerializer, GoogleSignSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import send_otp_email, send_sms, generate_otp_code


class GoogleSignInView(APIView):
    """
    API endpoint for Google sign-in authentication.
    """
    serializer_class = GoogleSignSerializer

    def post(self, request):
        """
        Validate the Google access token and sign in the user.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        access_token = serializer.validated_data.get('access_token')
        return Response({'message': 'Email sign-in successful'}, status=status.HTTP_200_OK)


class GenerateOTPView(APIView):
    """
    API endpoint to generate and send OTP via SMS for user registration.
    """
    serializer_class = GenerateOTPSerializer

    def post(self, request):
        """
        Generate OTP and send it to the provided phone number.
        """
        serializer   = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['phone_number']

        try:
            existing_phone_number = request.session.get('phone_number')
            if existing_phone_number and existing_phone_number != phone_number:
                request.session['phone_number'] = phone_number

            otp_instance, created = OTP.objects.get_or_create(phone_number=phone_number)

            if not created and otp_instance.otp_expiry >= timezone.now():
                return Response({'error': 'OTP resend is not allowed until the previous OTP expires.'},
                                status=status.HTTP_400_BAD_REQUEST)

            otp_instance.otp_code    = generate_otp_code()
            otp_instance.otp_expiry  = timezone.now() + timezone.timedelta(minutes=5)  # Set expiry time, adjust as needed
            otp_instance.save()

            message  = f'Your OTP IS : {otp_instance.otp_code}'
            sms_sent = send_sms(message, phone_number)

            if sms_sent:
                return Response({'message': 'OTP generated and sent successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Failed to send OTP'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': f'Failed to generate/send OTP. Exception: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyOTPView(APIView):
    """
    API endpoint to verify OTP and authenticate user.
    """
    def post(self, request):
        """
        Verify OTP entered by the user and authenticate if valid.
        """
        phone_number = request.session.get('phone_number')
        otp_entered  = request.data.get('otp')

        try:
            otp_instance = OTP.objects.get(phone_number=phone_number)

            if otp_instance.otp_code == otp_entered and otp_instance.otp_expiry >= timezone.now():
                otp_instance.delete()
                user, _ = User.objects.get_or_create(phone_number=phone_number)
                access_token  = RefreshToken.for_user(user)
                refresh_token = RefreshToken.for_user(user)
                refresh_token_exp = timezone.now() + timedelta(days=7)
                return Response({
                    "access_token": str(access_token.access_token),
                    "refresh_token": str(refresh_token),
                    "refresh_token_expiry": refresh_token_exp.isoformat(),
                    "user": {
                        "id": user.id,
                        "phone_number": user.phone_number,
                    },
                    "message": "User Signup successfully",
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid OTP or OTP expired'}, status=status.HTTP_400_BAD_REQUEST)
        except OTP.DoesNotExist:
            return Response({'error': 'OTP entry not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResendOTPView(APIView):
    """
    API endpoint to resend OTP via SMS for user registration.
    """
    def post(self, request):
        """
        Resend OTP to the user's phone number.
        """
        phone_number = request.session.get('phone_number')

        try:
            otp_instance = OTP.objects.get(phone_number=phone_number)

            if otp_instance.phone_number != phone_number:
                return Response({'error': 'Provided phone number does not match the one associated with the OTP'},
                                status=status.HTTP_400_BAD_REQUEST)

            if otp_instance.otp_expiry >= timezone.now():
                return Response({'error': 'OTP resend is not allowed until the previous OTP expires.'},
                                status=status.HTTP_400_BAD_REQUEST)

            otp_instance.otp_code = generate_otp_code()
            otp_instance.otp_expiry = timezone.now() + timedelta(seconds=30)
            otp_instance.save()

            message  = f'Your OTP IS : {otp_instance.otp_code}'
            sms_sent = send_sms(message, phone_number)

            if sms_sent:
                return Response({'message': 'OTP resent successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Failed to resend OTP'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except OTP.DoesNotExist:
            return Response({'error': 'No OTP exists'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'Failed to resend OTP. Exception: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
