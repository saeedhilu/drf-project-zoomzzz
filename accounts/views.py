import datetime
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import timedelta
from django.utils import timezone
from .models import OTP, User
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .filters import RoomFilter  
from rooms.models import Room
from rooms.serializers import RoomSerializer
from .constants import OTP_STILL_VALID
from .models import WishList
from .serializers import WishListSerializer
from django.core.cache import cache



from .serializers import (
    GenerateOTPSerializer,
    GoogleSignSerializer,
    UserProfileEditSerializer,
    ChangePhoneNumberSerializer
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


class AllRoomsView(APIView):
    """
    API endpoint to retrieve all room data.
    """
    
    def get(self, request):
        cache_key = 'all_rooms_view'
        rooms = cache.get(cache_key)
        
        if rooms is None:
            rooms = Room.objects.prefetch_related(
                'location',
                'amenities'
                )
            cache.set(cache_key, rooms, timeout=300)  
        
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)    
    



class RoomDetailAPIView(APIView):
    """
    This End point for listing selected Room
    """

    def get(self, request, pk):
        try:
            # Reduce redundant location queries and avoid unnecessary data fetching
            room = Room.objects.select_related('room_type', 'location').prefetch_related('amenities').get(pk=pk)

            serializer = RoomSerializer(room)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Room.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)




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
        

        
        # # TODO Add permission classes
        # if wishlist.user != request.user:
        #     return Response(
        #         {'error': 'Permission denied'}, 
        #         status=status.HTTP_403_FORBIDDEN
                # )

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
    

class RoomListView(ListAPIView):
    """
    This view is used to search and filter rooms
    """
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    
    # Specify filter backends
    filter_backends = [SearchFilter, DjangoFilterBackend]
    
    # Specify filter set class
    filterset_class = RoomFilter
    
    # Define searchable fields
    search_fields = [
        'location__city__name',
        'location__country__name', 
        'location__name'
        ]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # Retrieve the search query from the request
        search_query = request.GET.get('search', '')

        # Check if there are any results in the queryset
        if not queryset.exists():
            # Return a custom message and HTTP 404 status if no results are found
            return Response({
                'detail': f"Your search '{search_query}' did not match any rooms.",
                'suggestions': [
                    "Make sure that all words are spelled correctly.",
                    "Try different keywords.",
                    "Try more general keywords.",
                    "Try fewer keywords."
                ]
            }, status=status.HTTP_404_NOT_FOUND)

        # If results are found, return the standard list response
        return super().list(request, *args, **kwargs)

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Booking, Room
from .serializers import ReservationSerializer

class ReservationCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReservationSerializer

    def perform_create(self, serializer):
        # Retrieve the room from the URL using the 'room_id' parameter
        room_id = self.kwargs.get('room_id')
        room = get_object_or_404(Room, id=room_id)

        # Calculate the total price for the booking
        total_days = (serializer.validated_data['check_out'] - serializer.validated_data['check_in']).days
        total_price = total_days * room.price_per_night * serializer.validated_data['total_guest']

        # Save the booking with the current user, the room instance, and the calculated total price
        serializer.save(user=self.request.user, room=room, amount=total_price)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Include the room instance in the serializer context
        room_id = self.kwargs.get('room_id')
        room = get_object_or_404(Room, id=room_id)
        context['room'] = room
        return context
