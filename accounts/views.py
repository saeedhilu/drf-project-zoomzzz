import datetime
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import timedelta
from django.utils import timezone
from .models import OTP, User
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter,OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .filters import RoomFilter  
from rooms.models import Room
from rooms.serializers import RoomSerializer
from .constants import OTP_STILL_VALID
from .models import WishList
from django.core.cache import cache
from rest_framework.generics import RetrieveAPIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Reservation, Room
from .permission import IsActiveUser

from django.utils import timezone
from django.shortcuts import get_object_or_404


from .serializers import (
    GenerateOTPSerializer,
    GoogleSignSerializer,
    UserProfileEditSerializer,
    ChangePhoneNumberSerializer,
    ReservationSerializer,
    WishListSerializer
    )
from .constants import *
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
    This view is used to generate and send OTP to the user
                (Phone number signup)
    """
    serializer_class = GenerateOTPSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['phone_number']
        print(phone_number)
        

        try:
            # existing_phone_number = request.session.get('phone_number')
            # if existing_phone_number and existing_phone_number != phone_number:
            request.session['phone_number'] = phone_number
            


            otp_instance, created = OTP.objects.get_or_create(
                            phone_number=phone_number
                            )

            if not created and otp_instance.otp_expiry >= timezone.now():
                return Response(
                    {'error': OTP_STILL_VALID},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            otp_instance.otp_code = generate_otp_code()
            otp_instance.otp_expiry = timezone.now() + timezone.timedelta(minutes=5)  
            otp_instance.save()

            message = f'Your OTP IS : {otp_instance.otp_code}'
            sms_sent = send_sms(message, phone_number)

            if sms_sent:
                return Response(
                    {'message': GENERATE_OTP_MESSAGE}, 
                    status=status.HTTP_200_OK
                    )
            else:
                return Response(
                    {'error': 'Failed to send OTP'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
        except Exception as e:
            return Response(
                {'error': f'Failed to generate/send OTP. Exception: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                            )


class VerifyOTPView(APIView):
    """
    This endpoint is used to verify the OTP sent to the user.(phone number otp)
    """
    def post(self, request):
        phone_number     = request.session.get('phone_number')
        otp_entered = request.data.get('otp')
        print('Phone number is ',phone_number)

        try:
            otp_instance = OTP.objects.get(phone_number=phone_number)

            if otp_instance.otp_code == otp_entered and otp_instance.otp_expiry >= timezone.now():
                otp_instance.delete()
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
                        "phone_number": user.phone_number,
                    },
                    "message": "User Signup successfully",
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'Invalid OTP or OTP expired'}, 
                    status=status.HTTP_400_BAD_REQUEST
                    )
        except OTP.DoesNotExist:
            return Response(
                {'error': 'OTP entry not found'},
                    status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )


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
            return Response({'message': message}, 
                            status=status.HTTP_200_OK
                            )
        else:
            return Response(
                {'error': message}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        


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
            request.session['phone_number'] = phone_number


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
            # get
            return Response({'message': PHONE_SUCCESS}, 
                            status=status.HTTP_200_OK)
        else:
            return Response({'error': message}, 
                            status=status.HTTP_400_BAD_REQUEST)

from .utils import cache_queryset

class AllRoomsView(APIView):
    """
    API endpoint to retrieve all room data.
    """
    
    def get(self, request):
        cache_key = 'all_rooms_view'
        
        # Use cache_queryset function
        rooms = cache_queryset(cache_key, Room.objects.prefetch_related(
            'location',
            'amenities'
        ), timeout=300)
        
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)

class RoomDetailAPIView(RetrieveAPIView):
    """
    API view for retrieving the details of a selected room.
    """
    queryset = Room.objects.select_related('room_type', 'location').prefetch_related('amenities')
    serializer_class = RoomSerializer

    def get(self, request, pk):
        # Define the cache key for this specific room
        cache_key = f'room_detail_{pk}'

        # Try to retrieve the serialized room data from the cache
        room_data = cache.get(cache_key)

        if room_data is None:
            # If the data is not in the cache, query the room from the database
            room = self.queryset.filter(pk=pk).first()
            
            if not room:
                # If the room does not exist, return a 404 Not Found response
                return Response(status=status.HTTP_404_NOT_FOUND)

            # Serialize the room data
            serializer = self.get_serializer(room)
            room_data = serializer.data

            # Cache the serialized room data
            cache.set(cache_key, room_data, timeout=300)

        # Return the cached or freshly serialized room data
        return Response(room_data, status=status.HTTP_200_OK)



class WishListAPIView(APIView):
    """
    This End point for listing all WishList(
        create,delete,get)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Adds a room_id to the user's wish list.
        """
        room_id = request.data.get('room_id')
        if not room_id:
            return Response(
                {'error': 'Missing room_id field'}, 
                status=status.HTTP_400_BAD_REQUEST
                )

        try:
            # Ensure room_id is converted to int
            room_id = int(room_id)
            # Check if the room exists
            room = Room.objects.get(pk=room_id)
        except (ValueError, Room.DoesNotExist):
            return Response(
                {'error': 'Invalid room_id'}, 
                status=status.HTTP_400_BAD_REQUEST
                )

        user = request.user
        # Check if the wishlist already contains the room
        existing_wishlist = WishList.objects.filter(
            user=user, 
            room_id=room_id
            )
        if existing_wishlist.exists():

            return Response(
                {'error': 'Room already in wishlist'}, 
                status=status.HTTP_400_BAD_REQUEST
                )

        # Create a new wishlist item
        wishlist = WishList(user=user, room_id=room_id)
        wishlist.save()
        return Response(
            WishListSerializer(wishlist).data,
                status=status.HTTP_201_CREATED
                )

    def delete(self, request, pk):
        """
        Deletes a wish list item.
        """
        try:
            wishlist = WishList.objects.get(pk=pk)
        except WishList.DoesNotExist:
            return Response(
                {'error': 'Wishlist not found'}, 
                status=status.HTTP_404_NOT_FOUND
                )
        
        

        wishlist.delete()
        return Response(
            {'message':SUCCESS_MESSAGE},
            status=status.HTTP_204_NO_CONTENT
            )

    def get(self, request):
        """
        Retrieves the authenticated user's wish list items.
        """
        user = request.user
        wishlists = WishList.objects.filter(user=user)
        serializer = WishListSerializer(wishlists, many=True)
        return Response(serializer.data)

from django.db.models import Prefetch















class RoomListView(ListAPIView):
    """
    View for searching and filtering rooms.
    """
    serializer_class = RoomSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_class = RoomFilter
    search_fields = ['location__city__name', 'location__country__name', 'location__name']
    pagination_class = None  # Add pagination class if necessary

    def get_queryset(self):
        search_query = self.request.GET.get('search', '')
        filter_params = self.request.query_params.dict()
        # Generate a cache key based on search and filter parameters
        cache_key = f"rooms_list_{search_query}_{filter_params}"

        # Check cache for existing queryset
        queryset = cache.get(cache_key)

        if queryset is None:
            # Get base queryset and apply select_related and prefetch_related for efficiency
            base_queryset =Room.objects.select_related(
                'location__city',
                'location__country',
                'category',
                'room_type',
                'bed_type'
            ).prefetch_related(
                'amenities'
            )
            # Filter the base queryset using the RoomFilter class
            filtered_queryset = self.filter_queryset(base_queryset)

            # Cache the filtered queryset with a timeout of 300 seconds (5 minutes)
            cache.set(cache_key, filtered_queryset, timeout=300)

            queryset = filtered_queryset

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # If no rooms found, return a custom 404 response
        if not queryset.exists():
            return Response({
                'detail': f"Your search '{request.GET.get('search', '')}' did not match any rooms.",
                'suggestions': [
                    "Make sure all words are spelled correctly.",
                    "Try different keywords.",
                    "Try more general keywords.",
                    "Try fewer keywords."
                ]
            }, status=status.HTTP_404_NOT_FOUND)

        # Use the default list handling for non-empty querysets
        return super().list(request, *args, **kwargs)
 



 

class ReservationCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsActiveUser]
    serializer_class = ReservationSerializer

    def perform_create(self, serializer):
        room_id = self.kwargs.get('room_id')
        room = get_object_or_404(Room, id=room_id)
        user = self.request.user
        print('request.user:', self.request.user)
        
        
        # Calculate total price
        total_days = (serializer.validated_data['check_out'] - serializer.validated_data['check_in']).days
        total_price = total_days * room.price_per_night * serializer.validated_data['total_guest']

        # Save the booking
        serializer.save(user=self.request.user ,room=room, amount=total_price)

    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Include the room instance in the serializer context
        room_id = self.kwargs.get('room_id')
        room = get_object_or_404(Room, id=room_id)
        context['room'] = room
        return context



class BookingCancelAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        # Fetch the booking
        booking = get_object_or_404(Reservation, pk=pk)
        
        # Ensure the user making the request is the owner of the booking
        if booking.user != request.user:
            return Response({'status': 'error', 'message': 'You do not have permission to cancel this booking.'}, status=403)
        
        # Calculate the time difference between the current time and booking creation time
        time_difference = timezone.now() - booking.created_at
        
        # Check if the 2-minute cancellation window has passed
        two_minutes_in_seconds = 2 * 60
        if time_difference.total_seconds() > two_minutes_in_seconds:
            return Response({'status': 'error', 'message': 'Booking cannot be canceled as the 2-minute cancellation window has passed.'}, status=400)
        
        # Attempt to cancel the booking
        booking.is_active = False
        booking.reservation_status = 'CANCELED'
        booking.save()
        
        return Response({'status': 'success', 'message': 'Booking canceled successfully.'})
