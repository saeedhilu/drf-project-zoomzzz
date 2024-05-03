from datetime import datetime, timedelta
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.db.models import Avg, Count
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import (
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    RetrieveModelMixin
)
from .permission import IsActiveUser
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    OTP,
    User,
    WishList,
    Reservation,
    Room,
    Rating
)
from .filters import RoomFilter
from .constants import *
from .serializers import (
    GenerateOTPSerializer,
    GoogleSignSerializer,
    UserProfileEditSerializer,
    ChangePhoneNumberSerializer,
    ReservationSerializer,
    WishListSerializer,
    TopRatedSerializer,
    RatingSerializer
)
from rooms.serializers import RoomSerializer
from .utils import (
    send_otp_email,
    send_sms,
    generate_otp_code,
    generate_and_send_otp,
    resend_otp,
    verify_otp,
    cache_queryset
)
import razorpay



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
        return Response({MESSAGE: EMAIL_SIGNIN_SUCCESSGULLY},
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
                    {ERROR_MESSAGE: OTP_STILL_VALID},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            otp_instance.otp_code = generate_otp_code()
            otp_instance.otp_expiry = timezone.now() + timezone.timedelta(minutes=5)  
            otp_instance.save()

            message = f'Your OTP IS : {otp_instance.otp_code}'
            sms_sent = send_sms(message, phone_number)

            if sms_sent:
                return Response(
                    {MESSAGE: GENERATE_OTP_MESSAGE}, 
                    status=status.HTTP_200_OK
                    )
            else:
                return Response(
                    {ERROR_MESSAGE: FAILED_TO_SENTOTP}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
        except Exception as e:
            return Response(
                {ERROR_MESSAGE: f'FAIL_GENERATE: {str(e)}'},
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
                    MESSAGE: EMAIL_SIGNIN_SUCCESSGULLY,
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {ERROR_MESSAGE: INVALID_OTP}, 
                    status=status.HTTP_400_BAD_REQUEST
                    )
        except OTP.DoesNotExist:
            return Response(
                {ERROR_MESSAGE: ENTERY_NOT_FOUND},
                    status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {ERROR_MESSAGE: str(e)}, 
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
            return Response({MESSAGE: message}, 
                            status=status.HTTP_200_OK
                            )
        else:
            return Response(
                {ERROR_MESSAGE: message}, 
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
            return Response({ERROR_MESSAGE: AUTHENTICATION_FAILED}, 
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
                return Response({MESSAGE: message}, 
                                status=status.HTTP_200_OK)
            else:
                return Response({ERROR_MESSAGE: message}, 
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, 
                            status=status.HTTP_400_BAD_REQUEST)






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
            return Response({ERROR_MESSAGE: AUTHENTICATION_FAILED}, 
                            status=status.HTTP_401_UNAUTHORIZED)

        is_valid, message = verify_otp(phone_number, otp_entered)

        if is_valid:
            user.phone_number = phone_number
            user.save(update_field='phone_number')
        
            return Response({MESSAGE: PHONE_SUCCESS}, 
                            status=status.HTTP_200_OK)
        else:
            return Response({ERROR_MESSAGE: message}, 
                            status=status.HTTP_400_BAD_REQUEST)


class AllRoomsView(APIView):
    """
    API endpoint to retrieve all room data with average ratings.
    """

    @staticmethod
    def get_average_rating(room):
        """
        Calculates and returns the average rating for the given room.

        Args:
            room (Room): The room object for which to calculate the average rating.

        Returns:
            float: The average rating of the room, or None if no ratings exist.
        """

        average_rating = Rating.objects.filter(room=room).aggregate(average=Avg('rating'))
        return average_rating.get('average', None)  # Return None if no results

    def get(self, request):
        cache_key = 'all_rooms_view'

        rooms = Room.objects.prefetch_related(
            'location',
            'amenities',
        ).annotate(average_rating=Avg('rating__rating'))

        rooms_with_ratings = [
            RoomSerializer(room).data | {'average_rating': room.average_rating}
            for room in rooms
        ]

        return Response(rooms_with_ratings)




class RoomDetailAPIView(RetrieveAPIView):
    """
    API view for retrieving the details of a selected room.
    """
    queryset = Room.objects.select_related(
        'room_type', 
        'location'
        ).prefetch_related(
            'amenities'
            )
    serializer_class = RoomSerializer

    def get_average_rating(self, room):
    
        average_rating = Rating.objects.filter(
            room=room
            ).aggregate(
                average=Avg('rating'))
        return average_rating['average']

    def get_user_feedbacks(self, room):
        ratings = Rating.objects.filter(room=room).select_related('user').values(
        'user__username', 
        'rating',
        'feedback',
        'created_at'
        )
        return list(ratings)

    def get(self, request, pk):  
        
        cache_key = ROOM_DETAIL    
        room_data = cache.get(cache_key)
        if room_data is None:
            room = self.queryset.filter(pk=pk).first()
            if not room:
                return Response(status=status.HTTP_404_NOT_FOUND)
            average_rating = self.get_average_rating(room)

            user_feedbacks = self.get_user_feedbacks(room)
            serializer = self.get_serializer(room)
            room_data = serializer.data
            room_data['average_rating'] = average_rating
            room_data['user_feedbacks'] = user_feedbacks
            cache.set(cache_key, room_data, timeout=300)

        return Response(room_data, status=status.HTTP_200_OK)





class TopRatedRoomListAPIView(generics.ListAPIView):
    """
    This View For  top rated rooms
    """
    serializer_class = TopRatedSerializer

    def get_queryset(self):
        cache_key = TOP_RATED_ROOMS_CACHE_KEY

        queryset = cache.get(cache_key)
        
        if queryset is None:
            
            queryset = Room.objects.annotate(
                average_rating=Avg('rating__rating')
            ).filter(
                average_rating__isnull=False
            ).order_by('-average_rating')[:5]
            
            queryset = queryset.select_related('location').only(
                'id',
                'name',
                'price_per_night',
                'image',
                'location__name',
                'location__city',
                'location__country'
            )
            
            cache_queryset(cache_key, queryset,timeout=300)  # Cache for 15 minutes (900 seconds)
        
        return queryset





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
                {ERROR_MESSAGE: MISSING_ROOM_ID}, 
                status=status.HTTP_400_BAD_REQUEST
                )

        try:
            room_id = int(room_id)
            room = Room.objects.get(pk=room_id)
        except (ValueError, Room.DoesNotExist):
            return Response(
                {ERROR_MESSAGE:INVALID_ROOM}, 
                status=status.HTTP_400_BAD_REQUEST
                )

        user = request.user
        existing_wishlist = WishList.objects.filter(
            user=user, 
            room_id=room_id
            )
        if existing_wishlist.exists():

            return Response(
                {ERROR_MESSAGE: WHISHLIST_ALREADY_EXCIST}, 
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
                {ERROR_MESSAGE: WHISHLIST_NOT_FOUND}, 
                status=status.HTTP_404_NOT_FOUND
                )
        
        

        wishlist.delete()
        return Response(
            {MESSAGE:SUCCESS_MESSAGE},
            status=status.HTTP_204_NO_CONTENT
            )

    def get(self, request):
        """
        Retrieves the authenticated user's wish list items.
        """
        user = request.user

        
        cache_key = USER_WHISHLIST
    
        cached_wishlists = cache_queryset(
            cache_key, WishList.objects.select_related(
                'room',
                'room__location'
                ).filter(
                    user=user
                    ))

        serializer = WishListSerializer(cached_wishlists, many=True)
        
        return Response(serializer.data)







class RoomListView(ListAPIView):
    """
    View for searching and filtering rooms.
    """
    serializer_class = RoomSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_class = RoomFilter
    search_fields = [
        'location__city__name', 
        'location__country__name', 
        'location__name'
        ]
    pagination_class = None  # Add pagination class if necessary

    def get_queryset(self):
        search_query = self.request.GET.get('search', '')
        filter_params = self.request.query_params.dict()
        cache_key = ROOM_LIST

        queryset = cache.get(cache_key)

        if queryset is None:
            base_queryset =Room.objects.select_related(
                'location__city',
                'location__country',
                'category',
                'room_type',
                'bed_type',
                

            ).prefetch_related(
                'amenities'
                
            )
            filtered_queryset = self.filter_queryset(base_queryset)

            cache.set(cache_key, filtered_queryset, timeout=300)

            queryset = filtered_queryset
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # If no rooms found, return a custom 404 response
        if not queryset.exists():
            return Response({
                'detail': f"Your search '{request.GET.get('search', '')}' did not match any rooms.",
                'suggestions':SUGGESTION

            }, status=status.HTTP_404_NOT_FOUND)

        # Use the default list handling for non-empty querysets
        return super().list(request, *args, **kwargs)







# ##################

class BookingCreate(generics.CreateAPIView):
    """
    This view for Booking
    """
    permission_classes = [IsActiveUser]
    serializer_class = ReservationSerializer

    def perform_create(self, serializer):
        room_id = self.kwargs.get('room_id')
        room = get_object_or_404(Room, id=room_id)
        user = self.request.user

        total_days = (serializer.validated_data['check_out'] - serializer.validated_data['check_in']).days
        total_price = total_days * room.price_per_night * serializer.validated_data['total_guest']

        serializer.save(user=user, room=room, amount=total_price)

    def get_serializer_context(self):

        """For taking room for checking already excist"""
        context = super().get_serializer_context()

        room_id = self.kwargs.get('room_id')
        room = get_object_or_404(Room, id=room_id)
        context['room'] = room
        return context
        

    
class BookingCancelAPIView(APIView):
    """
    This View for Cancel Booking with in two minutes
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        
        booking = Reservation.objects.select_related('user').get(pk=pk)
        
        
        time_difference = timezone.now() - booking.created_at
        
        two_minutes_in_seconds = 2 * 60
        if time_difference.total_seconds() > two_minutes_in_seconds:
            return Response(
                {ERROR_MESSAGE: BOOKING_NOT_CANCEL}, 
                status=400
            )
        
        
        booking.is_active = False
        booking.reservation_status = Reservation.CANCELED

        booking.save()
        room = booking.room
        room.availability = True  
        room.save(update_fields=['availability'])
        
        return Response(
            {SUCCESS_MESSAGE: BOOKING_CANCEL}, 
            status=200
        )


class InitiatePaymentAPIView(APIView):
    
    def post(self, request):
        # Retrieve payment details from POST request data
        amount = int(request.data.get('amount', 0))  # Amount in paisa (₹500.00)
        currency = CURRENCY

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # Create Razorpay order
        order_data = {
            'amount': amount,
            'currency': currency,
            'payment_capture': '1'
        }
        razorpay_order = client.order.create(data=order_data)
        return Response({
            'order_id': razorpay_order['id'],
            'amount': razorpay_order['amount'],
            'currency': razorpay_order['currency'],
            'key_id': settings.RAZORPAY_KEY_ID,
        })

    def get(self, request):
        return Response(
            {ERROR_MESSAGE: METHOD_NOT_ALLOWED}, 
            status=status.HTTP_405_METHOD_NOT_ALLOWED
            )



class RatingViewSet(
    generics.GenericAPIView, 
    CreateModelMixin,
    RetrieveModelMixin, 
    UpdateModelMixin, 
    DestroyModelMixin
    ):
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]
    queryset = Rating.objects.all()

    def perform_create(self, serializer):
        room_id = self.kwargs.get('room_id')
        user = self.request.user
        room = get_object_or_404(Room, id=room_id)
        cache.delete('top_rated_rooms_list')
        serializer.save(user=user, room=room)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
    
        new_rating = request.data.get('rating')
        new_feedback = request.data.get('feedback')
        
        # Update only the specified fields
        if new_rating is not None:
            instance.rating = new_rating
        if new_feedback is not None:
            instance.feedback = new_feedback 
        
        instance.save()
        return Response(self.get_serializer(instance).data)
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)







class UserCanceledRooms(generics.ListAPIView):
    """
    This view returns all canceled rooms for the authenticated user.
    """
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user, reservation_status=Reservation.CANCELED).prefetch_related('user')


class UserConfirmedRooms(generics.ListAPIView):
    """
    This view returns all confirmed rooms for the authenticated user.
    """
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user, reservation_status=Reservation.CONFIRMED).prefetch_related('user')



class UserPendingRooms(generics.ListAPIView):
    """
    This view returns all pending rooms for the authenticated user.
    """
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user, reservation_status=Reservation.PENDING).prefetch_related('user')

