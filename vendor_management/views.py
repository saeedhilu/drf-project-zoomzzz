
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode
from datetime import timedelta, datetime
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


from accounts.models import OTP, User
from accounts.utils import (
    forgot_password_link,
    generate_otp_code,
    send_otp_email,
    create_otp
)
from .serializers import (
    ChangeEmailSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ForgottPasswordChangeSerializer,
    GenerateEmailSerializer,
    VendorLoginSerializer,
    VendorProfileSerializer,
)
from accounts.constants import *

class VendorSignupView(APIView):
    """
    API endpoint to generate and send OTP via email for user registration.
    """
    serializer_class = GenerateEmailSerializer

    def post(self, request):
        """
        Generate OTP and send it to the provided email address.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            email          = validated_data['email']
            phone_number   = validated_data.get('phone_number')
            password       = validated_data.get('password')
            first_name     = validated_data.get('first_name')
            last_name      = validated_data.get('last_name')
            # username is the first part of the email address
            username       = email.split('@')[0]

            try:
                otp_instance = OTP.objects.get(email=email)
                if otp_instance.otp_expiry >= timezone.now():
                    return Response({'message': OTP_ALREADY_EXISTS},
                                    status=status.HTTP_400_BAD_REQUEST)
            except OTP.DoesNotExist:
                pass

            try:
                otp, otp_instance, _ = create_otp(email, password)

                send_otp_email(email, otp, validated_data['first_name'])

                request.session['username']     = username
                request.session['email']        = email
                request.session['phone_number'] = phone_number
                request.session['first_name']   = first_name
                request.session['last_name']    = last_name

                return Response({'message': GENERATE_OTP_MESSAGE},
                                status=status.HTTP_200_OK)

            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                                )
        else:
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
                )


class VenodrVerifyView(APIView):
    """
    API endpoint to verify email OTP and authenticate user as a vendor.
    """
    def post(self, request):
        
        email        = request.session.get('email')
        otp_entered  = request.data.get('otp')
       
        print(email)
        print(otp_entered)
        
        # Get the data from session

        first_name   = request.session.get('first_name')
        last_name    = request.session.get('last_name')
        phone_number = request.session.get('phone_number')
        username     = request.session.get('username')

        try:
            otp_instance = OTP.objects.get(email=email)
            password = otp_instance.password

            if otp_instance.otp_code == otp_entered and otp_instance.otp_expiry >= timezone.now():
                otp_instance.delete()

                user = User.objects.create_user(
                    email       =email,
                    username    =username,
                    password    =password,
                    first_name  =first_name,
                    last_name   =last_name,
                    phone_number=phone_number,
                    is_vendor   =True,
                    is_active   =True
                )

                access_token    = RefreshToken.for_user(user)
                refresh_token   = RefreshToken.for_user(user)
                refresh_token_exp= timezone.now() + timedelta(days=7)

                return Response({
                    "access_token": str(access_token.access_token),
                    "refresh_token": str(refresh_token),
                    "refresh_token_expiry": refresh_token_exp.isoformat(),
                    "user": {
                        'username': user.username,
                        "id": user.id,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "phone_number": user.phone_number
                    },
                    "message": "User signed up successfully as a vendor",
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid OTP or OTP expired'},
                                status=status.HTTP_400_BAD_REQUEST)
        except OTP.DoesNotExist:
            return Response({'error': 'OTP entry not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )


class ResendEmailOTPView(APIView):
    """
    API endpoint to resend OTP via email.
    """
    def post(self, request):
        email = request.data.get('email')
        try:
            otp_instance = OTP.objects.get(email=email)

            if otp_instance.otp_expiry < timezone.now():
                otp = generate_otp_code()
                otp_expiry = timezone.now() + timedelta(seconds=40)
                otp_instance.otp_code = otp
                otp_instance.otp_expiry = otp_expiry
                otp_instance.save()

                send_otp_email(email, otp_instance.otp_code)

                return Response({'message': 'OTP resent successfully'},
                                status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': OTP_ALREADY_EXISTS},
                                status=status.HTTP_400_BAD_REQUEST)
        except OTP.DoesNotExist:
            return Response(
                {'error': 'OTP entry not found'},
                status=status.HTTP_404_NOT_FOUND)


class VendorLoginView(APIView):
    """
    This endpoint for login for vendor
    """
    def post(self, request):
        serializer   = VendorLoginSerializer(data=request.data)
        if serializer.is_valid():
            email    = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(
                    {'error': 'User not found'},
                        status=status.HTTP_404_NOT_FOUND
                        )

            if not user.check_password(password):
                return Response(
                    {'error': 'Incorrect password'},
                        status=status.HTTP_401_UNAUTHORIZED
                                )

            refresh = RefreshToken.for_user(user)

            vendor_data = {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                "phone_number": user.phone_number
            }

            return Response({
                'tokens': {
                    
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                },
                'vendor': vendor_data,
            }, status=status.HTTP_200_OK)

        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordEmailView(APIView):
    """
    This for sending email for forgot password option
    """
    EXPIRY_TIMEDELTA = timedelta(minutes=15)

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(
                    {'error': EMAIL_NOT_EXIST},
                        status=status.HTTP_404_NOT_FOUND
                        )

            forgot_password_link(user, email)
            return Response(
                {'success': 'Password reset email sent'},
                status=status.HTTP_200_OK
                )
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
            )


class ForgottPasswordResetView(APIView):
    """
    This end point for forgot password
    """
    TOKEN_EXPIRATION_DURATION = timedelta(minutes=15)

    def patch(self, request, uidb64=None, token=None):
        uidb64 = request.data.get('uidb64', uidb64)
        token  = request.data.get('token', token)

        if uidb64 and token:
            return self.handle_password_reset(
                request, 
                uidb64, 
                token
                )
        else:
            return Response(
                {'error': 'Invalid request'},
                    status=status.HTTP_400_BAD_REQUEST
                    )

    def handle_password_reset(
            self, 
            request, 
            uidb64, 
            token
            ):
        try:
            uid  = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (
            TypeError, 
            ValueError, 
            OverflowError, 
            User.DoesNotExist
            ):
            return Response(
                {'error': 'Invalid user or token'},
                    status=status.HTTP_400_BAD_REQUEST
                    )

        if default_token_generator.check_token(user, token):
            token_expiry_time = datetime.now() + self.TOKEN_EXPIRATION_DURATION

            if token_expiry_time < datetime.now():  
                return Response({'error': 'Reset token has expired'},
                                status=status.HTTP_400_BAD_REQUEST)

            serializer = ForgottPasswordChangeSerializer(
                data=request.data, context={'user': user}
                )
            if serializer.is_valid():
                new_password = serializer.validated_data['new_password']
                user.set_password(new_password)
                user.save()
                return Response({'success': PASSWORD_SUCCESS},
                                status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Invalid reset token'},
                            status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    
    """
    This end point for changing password
    """
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user  # Access the authenticated user

        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            old_password = serializer.validated_data.get('old_password')
            new_password = serializer.validated_data.get('new_password')

            if not user.check_password(old_password):
                return Response("Incorrect old password", status=400)

            user.set_password(new_password)
            user.save()
            return Response({'success': PASSWORD_SUCCESS}, 
                            status=200)
        else:
            return Response(serializer.errors, status=400)


class VendorProfileAPIView(APIView):
    """
    View for retrieving and updating user profile information.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Retrieve the profile information of the authenticated user.
        """
        serializer = VendorProfileSerializer(
            request.user, context={'request': request})
        return Response(serializer.data)

    def put(self, request):
        """
        Update the profile information of the authenticated user.
        """
        if request.user.is_authenticated:
            serializer = VendorProfileSerializer(
                request.user, data=request.data, 
                context={'request': request}
                )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, 
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Authentication failed'},
                            status=status.HTTP_401_UNAUTHORIZED)


class ChangeEmailView(APIView):
    """
    This for making option for changing email for vendors
    """
    serializer_class = ChangeEmailSerializer

    def post(self, request):
        """
        Generate OTP and send it to the provided email address.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            email  = validated_data['email']

            try:
                otp_instance = OTP.objects.get(email=email)
                if otp_instance.otp_expiry >= timezone.now():
                    return Response(
                        {'message': OTP_ALREADY_EXISTS},
                            status=status.HTTP_400_BAD_REQUEST
                            )
            except OTP.DoesNotExist:
                pass

            try:
                otp, otp_instance, _ = create_otp(email)

                send_otp_email(email, otp)

                request.session['email'] = email

                return Response({'message': GENERATE_OTP_MESSAGE},
                                status=status.HTTP_200_OK)

            except Exception as e:
                return Response(
                    {'error': str(e)}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
        else:
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
                )


class VerifyEmailChangeView(APIView):
    """
    Verify otp with email
    """
    def post(self, request):
        email = request.session.get('email')
        otp_entered = request.data.get('otp')
        user = request.user

        try:
            otp_instance = OTP.objects.get(email=email)

            if (otp_instance.otp_code == otp_entered and 
                    otp_instance.otp_expiry >= timezone.now()):

                otp_instance.delete()

                user.email = email
                user.save()

                return Response({'message': 'Email updated successfully'},
                                status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid OTP or OTP expired'},
                                status=status.HTTP_400_BAD_REQUEST)
        except OTP.DoesNotExist:
            return Response({'error': 'OTP entry not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)








from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from datetime import timedelta
from accounts.models import Reservation
from accounts.serializers import ReservationSerializer
from accounts.utils import get_vendor_summary_statistics

class DashboardView(APIView):
    """
    API view to provide recent bookings and summary statistics for the admin dashboard.
    """

    def get(self, request):
        user = request.user
        print('user',user)
        # Calculate recent bookings from the past 7 days
        
        summary = get_vendor_summary_statistics(request.user)
        
        recent_bookings = Reservation.objects.filter(room__created_by=user).select_related('user', 'room').order_by('-created_at')
        print('recent booking ',recent_bookings)

        
        # Serialize recent bookings
        booking_serializer = ReservationSerializer(recent_bookings, many=True)

        # Return the response with recent bookings
        return Response({
            'recent_bookings': booking_serializer.data,
            'summary': summary
        })





from rest_framework import generics
from accounts.models import User
from accounts.serializers import UserProfileEditSerializer
from accounts.permission import IsSuperUser
from rest_framework import generics
from accounts.models import User
from accounts.serializers import UserProfileEditSerializer
from accounts.permission import IsVendor
# from rooms.models import Reservation

class UserDetailaView(generics.ListAPIView):
    """
    This view lists all users who have booked rooms 
    """
    serializer_class = UserProfileEditSerializer
    permission_classes = [IsVendor]  

    def get_queryset(self):
        # Get the requesting user (vendor)
        vendor = self.request.user

        # Get the list of rooms created by the vendor
        vendor_rooms = vendor.created_rooms.all()

        # Get the reservations for the vendor's rooms
        reservations = Reservation.objects.filter(room__in=vendor_rooms)

        # Get the user IDs of the users who made the reservations
        user_ids = reservations.values_list('user', flat=True)

        # Filter the queryset to include only users who have booked the vendor's rooms
        queryset = User.objects.filter(id__in=user_ids)

        return queryset
