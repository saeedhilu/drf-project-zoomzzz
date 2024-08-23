
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode
from datetime import timedelta, datetime
from rest_framework import status
from accounts.permission import IsAuthenticatedUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics
from accounts.models import Rating, User
from accounts.serializers import UserProfileEditSerializer
from accounts.permission import IsSuperUser
from rest_framework import generics
from accounts.models import User
from accounts.permission import IsVendor
from datetime import timedelta
from accounts.models import Reservation
from accounts.serializers import ReservationSerializer
from accounts.utils import get_vendor_summary_statistics
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
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from accounts.views import StandardResultsSetPagination

class VendorSignupView(APIView):
    """
    API endpoint to generate and send OTP via email for user registration.
    """
    serializer_class = GenerateEmailSerializer

    def post(self, request):
        print('from request for vendor creating:',request.data)

        """
        Generate OTP and send it to the provided email address.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            email = validated_data['email']
            phone_number = validated_data.get('phone_number')
            print('phone number si :',phone_number)
            password = validated_data.get('password')
            first_name = validated_data.get('first_name')
            last_name = validated_data.get('last_name')
            username = email.split('@')[0]

            try:
                otp_instance = OTP.objects.get(email=email)
                if otp_instance.otp_expiry >= timezone.now():
                    return Response({'message': OTP_ALREADY_EXISTS},
                                    status=status.HTTP_400_BAD_REQUEST)
            except OTP.DoesNotExist:
                pass

            try:
                otp, otp_instance, _ = create_otp(email, password)
                print('otp is ssss:',otp)
                print('email is :',email)
                send_otp_email(email, otp, validated_data['first_name'])

                request.session.update({
                    'username': username,
                    'email': email,
                    'phone_number': phone_number,
                    'first_name': first_name,
                    'last_name': last_name
                })

                return Response({'message': GENERATE_OTP_MESSAGE},
                                status=status.HTTP_200_OK)

            except Exception as e:
                print('error is :',e)
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
        

        
import logging
logger = logging.getLogger(__name__)


class VendorVerifyView(APIView):
    """
    API endpoint to verify email OTP and authenticate user as a vendor.
    """
    def post(self, request):
        print('from request for vendor verifying:',request.data)
        email = request.data.get('email')
        otp_entered = request.data.get('otp')
        
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        phone_number = request.data.get('phone_number')
        username = email.split('@')[0]

        print('1',email,'2',otp_entered,'3',first_name,'4',last_name,'5',phone_number,'6',username)

        try:
            otp_instance = OTP.objects.get(email=email)
            print('otp isnts:',otp_instance)
            password = otp_instance.password
            print('password for instance:',password)

            if otp_instance.otp_code == otp_entered and otp_instance.otp_expiry >= timezone.now():
                otp_instance.delete()

                user = User.objects.create_user(
                    email=email,
                    username=username,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number,
                    is_vendor=True,
                    is_active=True
                )

                access_token = RefreshToken.for_user(user)
                refresh_token = RefreshToken.for_user(user)
                refresh_token_exp = timezone.now() + timedelta(days=7)

                # Send notification to admin
                # self.send_admin_notification(f'New vendor verified:')

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
                    "message": "Signup successful",
                }, status=200)
            else:
                return Response({'error': 'Invalid OTP or OTP expired'}, status=400)
        except OTP.DoesNotExist:
            return Response({'error': 'OTP entry not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
        



    # def send_admin_notification(self, message):
    #     print('message is :',message)
    #     channel_layer = get_channel_layer()
    #     async_to_sync(channel_layer.group_send)(
    #         'admin_notifications',
    #         {
    #             'type': 'send_notification',
    #             'message': message
    #         }
    #     )

# class VendorVerifyView(APIView):
#     """
#     API endpoint to verify email OTP and authenticate user as a vendor.
#     """
#     def post(self, request):
#         email = request.session.get('email')
#         otp_entered = request.data.get('otp')
        
#         first_name = request.session.get('first_name')
#         last_name = request.session.get('last_name')
#         phone_number = request.session.get('phone_number')
#         username = request.session.get('username')

#         try:
#             otp_instance = OTP.objects.get(email=email)
#             password = otp_instance.password

#             if otp_instance.otp_code == otp_entered and otp_instance.otp_expiry >= timezone.now():
#                 otp_instance.delete()

#                 user = User.objects.create_user(
#                     email=email,
#                     username=username,
#                     password=password,
#                     first_name=first_name,
#                     last_name=last_name,
#                     phone_number=phone_number,
#                     is_vendor=True,
#                     is_active=True
#                 )

              
#                 access_token = RefreshToken.for_user(user)
#                 refresh_token = RefreshToken.for_user(user)
#                 refresh_token_exp = timezone.now() + timedelta(days=7)
#                 channel_layer = get_channel_layer()
#                 message = f"New vendor verified: {first_name} {last_name} ({email})"
#                 async_to_sync(channel_layer.group_send)(
#                 'admin_notifications',
#                     {
#                         'type': 'send_notification',
#                         'message': message
#                     }
#                 )
#                 return Response({
#                     "access_token": str(access_token.access_token),
#                     "refresh_token": str(refresh_token),
#                     "refresh_token_expiry": refresh_token_exp.isoformat(),
#                     "user": {
#                         'username': user.username,
#                         "id": user.id,
#                         "email": user.email,
#                         "first_name": user.first_name,
#                         "last_name": user.last_name,
#                         "phone_number": user.phone_number
#                     },
#                     "message": SIGNUP_SUCCESS,
#                 }, status=status.HTTP_200_OK)
#             else:
#                 return Response({'error': 'Invalid OTP or OTP expired'},
#                                 status=status.HTTP_400_BAD_REQUEST)
#         except OTP.DoesNotExist:
#             return Response({'error': 'OTP entry not found'},
#                             status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response(
#                 {'error': str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

class ResendEmailOTPView(APIView):
    """
    API endpoint to resend OTP via email.
    """
    def post(self, request):
        print('request data is :',request.data)
        email = request.data.get('data')
        print('email for ressentign :',email)
        try:
            otp_instance = OTP.objects.get(email=email)

            if otp_instance.otp_expiry < timezone.now():
                otp = generate_otp_code()
                otp_expiry = timezone.now() + timedelta(seconds=40)
                otp_instance.otp_code = otp
                otp_instance.otp_expiry = otp_expiry
                otp_instance.save()
                print('otp is :',otp)
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
                "phone_number": user.phone_number,
                'is_vendor': user.is_vendor,
                
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
    permission_classes = [IsAuthenticatedUser]
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
    permission_classes = (IsAuthenticatedUser,)

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
        print('requesest data is :',request.data)
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
        email = request.data.get('email')
        otp_entered = request.data.get('otp')
        print('email is :',email)
        print('entered otp is :',otp_entered)
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






class DashboardView(APIView):
    """
    API view to provide recent bookings and summary statistics for the admin dashboard.
    """

    def get(self, request):
        user = request.user
        
        # Get summary statistics for the vendor
        summary = get_vendor_summary_statistics(user.id)
        print('summary is :', summary)
        
        # Get recent pending bookings for the vendor
        recent_bookings = Reservation.objects.filter(
            room__created_by=user.id, reservation_status=Reservation.PENDING
        ).select_related('user', 'room').order_by('-created_at')[:5]
        booking_serializer = ReservationSerializer(recent_bookings, many=True, context={'request': request})

        # Return the response with recent bookings and summary statistics
        return Response({
            'recent_bookings': booking_serializer.data,
            'summary': summary
        })


class VendorBookingsView(APIView):
    """
    API view to provide a list of all bookings for the vendor.
    """
    
    def get(self, request):
        user = request.user

        # Get all bookings for the vendor
        all_bookings = Reservation.objects.filter(
            room__created_by=user.id
        ).select_related('user', 'room').order_by('-created_at')

        # Instantiate the paginator and apply pagination
        paginator = StandardResultsSetPagination()
        paginated_bookings = paginator.paginate_queryset(all_bookings, request)

        # Serialize the paginated data
        booking_serializer = ReservationSerializer(paginated_bookings, many=True, context={'request': request})

        # Return the paginated response
        return paginator.get_paginated_response(booking_serializer.data)

class UserDetailaView(generics.ListAPIView):
    """
    This view lists all users who have booked rooms 
    """
    serializer_class = UserProfileEditSerializer
    permission_classes = [IsVendor]  

    def get_queryset(self):
        vendor = self.request.user
        print('vendro i s:',vendor)
        vendor_rooms = vendor.created_rooms.all()
        print('vendro room is :',vendor_rooms)

        reservations = Reservation.objects.filter(room__in=vendor_rooms)
        user_ids = reservations.values_list('user', flat=True)
        queryset = User.objects.filter(id__in=user_ids)
        return queryset




from .serializers import RoomRatingSerializer
from rooms.models import Room
from rest_framework import permissions
from django.db.models import Count, Avg

class VendorRoomsListView(generics.ListAPIView):
    serializer_class = RoomRatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_vendor:
            return Room.objects.none()  # Return no rooms if the user is not a vendor

        # Annotate and filter rooms with at least one rating
        return Room.objects.filter(
            created_by=user,
            ratings__isnull=False  # Ensure there is at least one rating
        ).annotate(
            average_rating=Avg('ratings__rating'),  # Calculate the average rating
            total_ratings=Count('ratings')           # Count the number of ratings
        ).distinct()  # Ensure unique rooms are returned
    



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from datetime import datetime
import calendar

class VendorReservationsByMonthView(APIView):
    """
    API view to get reservations by month, status, and vendor.
    """
    permission_classes = [IsVendor]

    def get(self, request):
        vendor_id = request.user.id
        month = request.query_params.get('month')
        year = request.query_params.get('year')

        if not month or not year:
            return Response({'error': 'Month and year are required parameters.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            month = int(month)
            year = int(year)
        except ValueError:
            return Response({'error': 'Month and year must be integers.'}, status=status.HTTP_400_BAD_REQUEST)

        if month < 1 or month > 12:
            return Response({'error': 'Month must be between 1 and 12.'}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate the start and end dates for the requested month
        start_date = datetime(year, month, 1).date()
        last_day = calendar.monthrange(year, month)[1]
        end_date = datetime(year, month, last_day).date()

        # Filter reservations by date range and vendor
        reservations = Reservation.objects.filter(
            check_in__range=[start_date, end_date],
            room__created_by_id=vendor_id
        )
        print('sentuing data  i s:',reservations)

        # Annotate reservations based on their status
        data = {
            'confirmed': reservations.filter(reservation_status='Confirmed').values('check_in').annotate(total=Count('id')).order_by('check_in'),
            'upcoming': reservations.filter(reservation_status='Pending').values('check_in').annotate(total=Count('id')).order_by('check_in'),
            'canceled': reservations.filter(reservation_status='Canceled').values('check_in').annotate(total=Count('id')).order_by('check_in'),
        }
        print('data is fornm  sentuing:',data)

        return Response(data, status=status.HTTP_200_OK)


from rooms.serializers import RoomSerializer
from django.db.models import Avg, Count

class VendorTopRoomsView(APIView):
    """
    API view to get the top rooms for the current vendor based on average ratings.
    """
    permission_classes = [IsVendor]

    def get(self, request):
        # Get the current vendor (assumes that the user is a vendor)
        vendor = request.user
        
        # Query to get the top rooms for the vendor based on average rating,
        # with secondary sorting by rating_count if averages are equal
        top_rooms = Room.objects.filter(created_by=vendor) \
            .annotate(
                average_rating=Avg('ratings__rating'),
                rating_count=Count('ratings')
            ) \
            .filter(rating_count__gt=0) \
            .order_by('-average_rating', '-rating_count')[:5]  # Top 5 rooms

        serializer = RoomSerializer(top_rooms, many=True, context={'request': request})
        
        return Response(serializer.data, status=200)
