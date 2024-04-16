from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import timedelta
from django.utils import timezone
from .models import OTP, User
from .serializers import (
    GenerateOTPSerializer,
    GoogleSignSerializer,
    UserProfileEditSerializer,
    ChangePhoneNumberSerializer
    )
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .utils import (
    send_otp_email,
    send_sms,
    generate_otp_code,
    generate_and_send_otp,
    resend_otp,
    verify_otp
    )   

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
        return Response({'message': 'Email sign-in successful'},
                        status=status.HTTP_200_OK)




class GenerateOTPView(APIView):
    """
    API endpoint to generate and send OTP via SMS for user registration.
    """
    serializer_class = GenerateOTPSerializer

    def post(self, request):
        """
        Generate OTP and send it to the provided phone number.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['phone_number']

        otp_instance, message = generate_and_send_otp(phone_number)

        if otp_instance:
            return Response({'message': message}, status=status.HTTP_200_OK)
        else:
            return Response({'error': message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyOTPView(APIView):
    """
    API endpoint to verify OTP and authenticate user.
    """
    def post(self, request):
        """
        Verify OTP entered by the user and authenticate if valid.
        """
        phone_number = request.session.get('phone_number')
        otp_entered = request.data.get('otp')

        is_valid, message = verify_otp(phone_number, otp_entered)

        if is_valid:
            user, _ = User.objects.get_or_create(phone_number=phone_number)
            access_token = RefreshToken.for_user(user)
            refresh_token = RefreshToken.for_user(user)
            refresh_token_exp = timezone.now() + timedelta(days=7)
            return Response({
                "access_token": str(access_token.access_token),
                "refresh_token": str(refresh_token),
                "refresh_token_expiry": refresh_token_exp.isoformat(),
                "user": {
                    "id": user.id,
                    "phone_number": phone_number,
                },
                "message": "User Signup successfully",
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
        


class ResendOTPView(APIView):
    """
    API endpoint to resend OTP via SMS for user registration.
    """
    def post(self, request):
        """
        Resend OTP to the user's phone number.
        """
        phone_number = request.session.get('phone_number')

        otp_instance, message = resend_otp(phone_number)

        if otp_instance:
            return Response({'message': message}, status=status.HTTP_200_OK)
        else:
            return Response({'error': message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class UserProfileEditAPIView(APIView):
    """
    View for retrieving and updating user profile information.
    """
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        """
        Retrieve the profile information of the authenticated user.
        """
    
        serializer = UserProfileEditSerializer(
            request.user, context={'request': request})
        return Response(serializer.data)
        


    def put(self, request):
        """
        Update the profile information of the authenticated user.
        """
        if request.user.is_authenticated:
            serializer = UserProfileEditSerializer(
                request.user, data=request.data, 
                    context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, 
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Authentication failed'}, 
                            status=status.HTTP_401_UNAUTHORIZED)

class ChangePhoneNumberView(APIView):
    """
    API endpoint for changing phone number.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePhoneNumberSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']

            otp_instance, message = generate_and_send_otp(phone_number)

            if otp_instance:
                return Response({'message': message}, 
                                status=status.HTTP_200_OK)
            else:
                return Response({'error': message}, 
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, 
                            status=status.HTTP_400_BAD_REQUEST)


# views.py

class VerifyChangePhoneNumberView(APIView):
    """
    API endpoint for verifying OTP and updating phone number.
    """
    def post(self, request):
        phone_number = request.session.get('phone_number')
        otp_entered = request.data.get('otp')
        user = request.user
        from django.contrib.auth.models import AnonymousUser
        if not user or isinstance(user, AnonymousUser):
            return Response({'error': 'User authentication required'}, 
                            status=status.HTTP_401_UNAUTHORIZED)

        is_valid, message = verify_otp(phone_number, otp_entered)

        if is_valid:
            user.phone_number = phone_number
            user.save()
            return Response({'message': 'Phone number updated successfully'}, 
                            status=status.HTTP_200_OK)
        else:
            return Response({'error': message}, 
                            status=status.HTTP_400_BAD_REQUEST)
