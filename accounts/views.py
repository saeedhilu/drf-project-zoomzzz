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
from rest_framework.pagination import PageNumberPagination
from rest_framework.mixins import (
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    RetrieveModelMixin
)

from rest_framework.permissions import AllowAny

from .permission import IsActiveUser,IsAuthenticatedUser
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



class StandardResultsSetPagination(PageNumberPagination):
    page_size = 7
    page_size_query_param = 'page_size'
    max_page_size = 100




class GoogleSignInView(APIView):
    serializer_class=GoogleSignSerializer

    def post(self, request):
        print(request.data)
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data=((serializer.validated_data)['access_token'])
        return Response(data, status=status.HTTP_200_OK) 






















class GenerateOTPView(APIView):
    serializer_class = GenerateOTPSerializer


    def post(self, request):

        print('request is :',request)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['phone_number']
        print('Phone number from input:', phone_number)

        try:
            request.session['phone_number'] = phone_number
            request.session.modified = True  
            phone = request.session.get('phone_number')
            

            otp_instance, created = OTP.objects.get_or_create(phone_number=phone_number)
            otp_instance.otp_code = generate_otp_code()
            print('Generated OTP:', otp_instance.otp_code)
            otp_instance.otp_expiry = timezone.now() + timezone.timedelta(minutes=5)
            otp_instance.save()

            message = f'Your OTP is: {otp_instance.otp_code}'
            sms_sent = send_sms(message, phone_number)

            if sms_sent:
                return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"error_message": "Failed to send OTP"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error_message": f'Failed to generate OTP: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyOTPView(APIView):

    def post(self, request):
        phone = request.data.get('phone_number')
        print('Phone number from session during verification:', phone)
        otp_entered = request.data.get('otp')
        print('OTP entered:', otp_entered)

        if not phone:
            return Response({"error_message": "Phone number not found in session."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            otp_instance = OTP.objects.get(phone_number=phone)

            if otp_instance.otp_code == otp_entered and otp_instance.otp_expiry >= timezone.now():
                otp_instance.delete()
                user, _ = User.objects.get_or_create(phone_number=phone)
                access_token = RefreshToken.for_user(user).access_token
                refresh_token = RefreshToken.for_user(user)
                refresh_token_exp = timezone.now() + timedelta(days=7)
                user_data ={
                    "id":user.id,
                    "phone_number": user.phone_number,
                    "is_vendor": user.is_vendor,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                }
                if user.username:
                    user_data['username'] = user.username
                if user.image:
                    user_data['image'] = str(user.image)
                print('user data is :',user_data)
                return Response({
                    "access_token": str(access_token),
                    "refresh_token": str(refresh_token),
                    "refresh_token_expiry": refresh_token_exp.isoformat(),
                    "user": user_data,
                    "message": "OTP verified successfully........",

                }, status=status.HTTP_200_OK)
            else:
                return Response({"error_message": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
        except OTP.DoesNotExist:
            return Response({"error_message": "OTP entry not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error_message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






class ResendOTPView(APIView):
    """
    API endpoint to resend OTP via SMS for user registration.
    """
    def post(self, request):
        """
        Resend OTP to the user's phone number.
        """
        phone_number = request.data.get('data')
        print('resent ot p phn is ',phone_number)

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
    permission_classes = [IsAuthenticated]


    def get(self, request):
        
        """
        Retrieve the profile information of the authenticated user.
        """
        serializer = UserProfileEditSerializer(
            request.user, context={'request': request}
        )
        return Response(serializer.data)

    def put(self, request):
        print('reqeust is :',request.data)
        """
        Update the profile information of the authenticated user.
        """
        serializer = UserProfileEditSerializer(
            request.user, data=request.data, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)








class   ChangePhoneNumberView(APIView):
    """
    API endpoint for changing phone number.
    """
    # permission_classes = [IsAuthenticated]
    serializer_class = ChangePhoneNumberSerializer

    def post(self, request):
        print('request from change  ph number L.....', request)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            
            otp_instance, message = generate_and_send_otp(phone_number)
            print('otp i s:',otp_instance,message)

            if otp_instance:
                return Response({"success": True}, status=status.HTTP_200_OK)
            else:
                return Response({ERROR_MESSAGE: message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class VerifyChangePhoneNumberView(APIView):
    """
    API endpoint for verifying OTP and updating phone number.
    """
    def post(self, request):
        phone_number = request.data.get('phone_number')
        print('from view', phone_number)
        otp_entered = request.data.get('otp')
        print('otp entering:', otp_entered)
        user = request.user

        if not user.is_authenticated:
            return Response({ERROR_MESSAGE: AUTHENTICATION_FAILED}, status=status.HTTP_401_UNAUTHORIZED)

        is_valid, message = verify_otp(phone_number, otp_entered)

        if is_valid:
            user.phone_number = phone_number
            user.save(update_fields=['phone_number'])
        
            return Response({MESSAGE: PHONE_SUCCESS}, status=status.HTTP_200_OK)
        else:
            return Response({ERROR_MESSAGE: message}, status=status.HTTP_400_BAD_REQUEST)

        





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
        'user__image', 
        'rating',
        'feedback',
        'created_at'
        )
        return list(ratings)

    def get(self, request, pk):  
        
        # cache_key = ROOM_DETAIL    
        # room_data = cache.get(cache_key)
        # if room_data is None:
        room = self.queryset.filter(pk=pk).first()
        print('room is :....',room)
        if not room:
            return Response(status=status.HTTP_404_NOT_FOUND)
        average_rating = self.get_average_rating(room)
        user_feedbacks = self.get_user_feedbacks(room)
        serializer = self.get_serializer(room)
        room_data = serializer.data
        room_data['average_rating'] = average_rating
        room_data['user_feedbacks'] = user_feedbacks
        # cache.set(cache_key, room_data, timeout=300)

        return Response(room_data, status=status.HTTP_200_OK)





class TopRatedRoomListAPIView(generics.ListAPIView):

    """
    This View For  top rated rooms
    """
    serializer_class = TopRatedSerializer
    permission_classes  = [AllowAny]

    def get_queryset(self):
        cache_key = TOP_RATED_ROOMS_CACHE_KEY

        queryset = cache.get(cache_key)
        
        if queryset is None:
            
            queryset = Room.objects.annotate(
                average_rating=Avg('ratings__rating')
            ).filter(
                average_rating__isnull=False
            ).order_by('-average_rating')[:4]
            
            queryset = queryset.select_related('location').only(
                'id',
                'name',
                'price_per_night',
                'image',
                'location__name',
                'location__city',
                'location__country'
            )
            
            cache_queryset(cache_key, queryset,timeout=300) 
            print('from top rated room', queryset)
        
        return queryset





# class WishListAPIView(APIView):
#     """
#     This End point for listing all WishList(
#         create,delete,get)
#     """
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         """
#         Adds a room_id to the user's wish list.
#         """
#         room_id = request.data.get('room_id')
#         if not room_id:
#             return Response(
#                 {ERROR_MESSAGE: MISSING_ROOM_ID}, 
#                 status=status.HTTP_400_BAD_REQUEST
#                 )

#         try:
#             room_id = int(room_id)
#             room = Room.objects.get(pk=room_id)
#         except (ValueError, Room.DoesNotExist):
#             return Response(
#                 {ERROR_MESSAGE:INVALID_ROOM}, 
#                 status=status.HTTP_400_BAD_REQUEST
#                 )

#         user = request.user
#         existing_wishlist = WishList.objects.filter(
#             user=user, 
#             room_id=room_id
#             )
#         if existing_wishlist.exists():

#             return Response(
#                 {ERROR_MESSAGE: WHISHLIST_ALREADY_EXCIST}, 
#                 status=status.HTTP_400_BAD_REQUEST
#                 )

#         # Create a new wishlist item
#         wishlist = WishList(user=user, room_id=room_id)
#         wishlist.save()
#         return Response(
#             WishListSerializer(wishlist).data,
#                 status=status.HTTP_201_CREATED
#                 )

#     def delete(self, request, pk):
#         """
#         Deletes a wish list item.
#         """
#         try:
#             wishlist = WishList.objects.get(pk=pk)
#         except WishList.DoesNotExist:
#             return Response(
#                 {ERROR_MESSAGE: WHISHLIST_NOT_FOUND}, 
#                 status=status.HTTP_404_NOT_FOUND
#                 )
        
        

#         wishlist.delete()
#         return Response(
#             {MESSAGE:SUCCESS_MESSAGE},
#             status=status.HTTP_204_NO_CONTENT
#             )

#     def get(self, request):
#         """
#         Retrieves the authenticated user's wish list items.
#         """
#         user = request.user

        
#         cache_key = USER_WHISHLIST
    
#         cached_wishlists = cache_queryset(
#             cache_key, WishList.objects.select_related(
#                 'room',
#                 'room__location'
#                 ).filter(
#                     user=user
#                     ))

#         serializer = WishListSerializer(cached_wishlists, many=True)
        
#         return Response(serializer.data)
    

class WishListAPIView(APIView):
    """
    This End point for listing all WishList (create, delete, get)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Adds a room_id to the user's wish list.
        """
        print('request ois :',request)
        print('request get method for whishlit',request.data)
        room_id = request.data.get('room_id')
        print('room_id',room_id)
        if not room_id:
            print('no rooom')
            return Response(
                {ERROR_MESSAGE: MISSING_ROOM_ID}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            room_id = int(room_id)
            print('room ida ',room_id)
            room = Room.objects.get(pk=room_id)
            print('room is :....',room)
        except (ValueError, Room.DoesNotExist):
            return Response(
                {ERROR_MESSAGE: INVALID_ROOM}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user
        print('user is whishi',user)
        existing_wishlist = WishList.objects.filter(user=user, room_id=room_id)
        if existing_wishlist.exists():
            return Response(
                {ERROR_MESSAGE: WHISHLIST_ALREADY_EXCIST}, 
                status=status.HTTP_409
            )

        # Create a new wishlist item
        wishlist = WishList(user=user, room_id=room_id)
        wishlist.save()

        # Invalidate or refresh cache after adding an item
        cache_key = f"user_{user.id}_wishlist"
        cache.delete(cache_key)  # Invalidate cache

        return Response(
            WishListSerializer(wishlist).data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, pk):
        """
        Deletes a wish list item.
        """

        print('from delete option ',pk)
        try:
            wishlist = WishList.objects.get(pk=pk)
        except WishList.DoesNotExist:
            return Response(
                {ERROR_MESSAGE: WHISHLIST_NOT_FOUND}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        user = wishlist.user
        wishlist.delete()

        
        cache_key = f"user_{user.id}_wishlist"
        cache.delete(cache_key)  

        return Response(
            {MESSAGE: SUCCESS_MESSAGE},
            status=status.HTTP_204_NO_CONTENT
        )

    def get(self, request):
        """
        Retrieves the authenticated user's wish list items.
        """
        
        user = request.user
        cache_key = f"user_{user.id}_wishlist"

        # Fetch data from cache or database
        cached_wishlists = cache.get(cache_key)
        if cached_wishlists is None:
            cached_wishlists = list(WishList.objects.select_related(
                'room',
                'room__location'
            ).filter(
                user=user
            ))
            cache.set(cache_key, cached_wishlists)

        serializer = WishListSerializer(cached_wishlists, many=True)
        
        return Response(serializer.data)

import json





class RoomListView(ListAPIView):
    serializer_class = RoomSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_class = RoomFilter
    search_fields = [
        'location__city__name', 
        'location__country__name', 
        'location__name'
    ]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        base_queryset = Room.objects.select_related(
            'location__city',
            'location__country',
            'category',
            'room_type',
            'bed_type',
            
        ).prefetch_related(
            'amenities'
        ).annotate(
            average_rating=Avg('ratings__rating'),  
            rating_count=Count('ratings')  
        )
        queryset = self.filter_queryset(base_queryset)
        return queryset

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()

            if not queryset.exists():
                search_value = request.GET.get('search')
                return Response({
                    'detail': f"{search_value}did not match any rooms.",
                    'suggestions': []
                }, status=status.HTTP_404_NOT_FOUND)

            return super().list(request, *args, **kwargs)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ##################


class BookingCreate(generics.CreateAPIView):
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
        context = super().get_serializer_context()
        room_id = self.kwargs.get('room_id')
        room = get_object_or_404(Room, id=room_id)
        context['room'] = room
        return context



# class BookingCreate(generics.CreateAPIView):
#     permission_classes = [IsActiveUser]
#     serializer_class = ReservationSerializer

#     def perform_create(self, serializer):
#         room_id = self.kwargs.get('room_id')
#         room = get_object_or_404(Room, id=room_id)
#         user = self.request.user

#         total_days = (serializer.validated_data['check_out'] - serializer.validated_data['check_in']).days
#         total_price = total_days * room.price_per_night * serializer.validated_data['total_guest']
        
#         # Convert Decimal to string or float before storing in session
#         self.request.session['booking_data'] = {
#             'user_id': user.id,
#             'room_id': room.id,
#             'check_in': serializer.validated_data['check_in'].strftime('%Y-%m-%d'),
#             'check_out': serializer.validated_data['check_out'].strftime('%Y-%m-%d'),
#             'total_guest': serializer.validated_data['total_guest'],
#             'amount': str(total_price)  # Convert Decimal to string or float
#         }



class  BookingCancelAPIView(APIView):
    """
        Cancel a booking.
    """
    permission_classes = [IsAuthenticatedUser]

    def post(self, request, pk):
        user= request.user
        print('user ios :',user)
        print('pk ios :',pk)
        booking = Reservation.objects.get(pk=pk)
        time_difference = timezone.now() - booking.created_at
        two_minutes_in_seconds = 2 * 60

        if time_difference.total_seconds() > two_minutes_in_seconds:
            return Response({ERROR_MESSAGE: BOOKING_NOT_CANCEL}, status=400)

        booking.is_active = False
        booking.reservation_status = Reservation.CANCELED
        booking.save()
        room = booking.room
        room.availability = True
        room.save(update_fields=['availability'])

        return Response({SUCCESS_MESSAGE: BOOKING_CANCEL}, status=200)
    

from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
import razorpay

class InitiatePaymentAPIView(APIView):
    def post(self, request):
        amount = int(request.data.get('amount', 0))
        currency = 'INR'
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        order_data = {
            'amount': amount,
            'currency': currency,
            'payment_capture': '1'
        }
        try:
            razorpay_order = client.order.create(data=order_data)
            print('Razorpay order created:', razorpay_order)  # Debugging statement

            return Response({
                'order_id': razorpay_order['id'],
                'amount': razorpay_order['amount'],
                'currency': razorpay_order['currency'],
                'key_id': settings.RAZORPAY_KEY_ID,
            })
        except Exception as e:
            print('Error creating Razorpay order:', str(e))  # Debugging statement
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        return Response({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)



        
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


# @method_decorator(csrf_exempt, name='dispatch')
# class RazorpayWebhook(APIView):
#     def post(self, request):
#         try:
#             data = json.loads(request.body)
#             print('webhook data is ')
#             payload = data['payload']
#             event = data['event']

#             client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
#             webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
#             signature = request.headers.get('X-Razorpay-Signature')
#             client.utility.verify_webhook_signature(request.body, signature, webhook_secret)

#             if event == 'payment.captured':
#                 self.handle_payment_captured(payload)
#             elif event == 'payment.failed':
#                 self.handle_payment_failed(payload)

#             return Response({'status': 'success'}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

#     def handle_payment_captured(self, payload):
#         payment_id = payload['payment']['entity']['id']
#         order_id = payload['payment']['entity']['order_id']
#         amount = payload['payment']['entity']['amount']

#         try:
#             reservation = Reservation.objects.get(order_id=order_id)
#             reservation.is_paid = True
#             reservation.payment_id = payment_id
#             reservation.amount_paid = amount / 100
#             reservation.save()
#         except Reservation.DoesNotExist:
#             pass

#     def handle_payment_failed(self, payload):
#         pass

from decimal import Decimal

class RazorpayWebhook(APIView):
    @method_decorator(csrf_exempt, name='dispatch')
    def post(self, request):
        try:
            data = json.loads(request.body)
            print('Webhook data received:', data)  # Debugging statement
            payload = data.get('payload', {})
            event = data.get('event', '')
            print('Event received:', event)  # Debugging statement

            # Initialize Razorpay client
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            # Verify webhook signature
            webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
            signature = request.headers.get('X-Razorpay-Signature')
            client.utility.verify_webhook_signature(request.body, signature, webhook_secret)

            # Handle different events
            if event == 'payment.captured':
                print('Payment captured event detected')  # Debugging statement
                self.handle_payment_captured(payload)
            elif event == 'payment.failed':
                print('Payment failed event detected')  # Debugging statement
                self.handle_payment_failed(payload)
            else:
                print('Unhandled event:', event)  # Debugging statement
                return Response({'status': 'event not handled'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        except Exception as e:
            print('Error handling webhook:', str(e))  # Debugging statement
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def handle_payment_captured(self, payload):
        order_id = payload['payment']['entity']['order_id']
        payment_id = payload['payment']['entity']['id']
        amount = Decimal(payload['payment']['entity']['amount']) / 100  # Amount is in paise/cents
        print('Payment captured details:', {'order_id': order_id, 'payment_id': payment_id, 'amount': amount})  # Debugging statement
        
        # Retrieve booking data from session
        booking_data = self.request.session.get('booking_data')
        if booking_data:
            try:
                user = User.objects.get(id=booking_data['user_id'])
                room = Room.objects.get(id=booking_data['room_id'])
                print('Creating reservation with data:', booking_data)  # Debugging statement

                # Create the reservation
                Reservation.objects.create(
                    user=user,
                    room=room,
                    check_in=booking_data['check_in'],
                    check_out=booking_data['check_out'],
                    total_guest=booking_data['total_guest'],
                    amount=amount,
                    is_paid=True,
                    payment_id=payment_id
                )
                self.request.session.pop('booking_data')
            except User.DoesNotExist:
                print('User does not exist')  # Debugging statement
            except Room.DoesNotExist:
                print('Room does not exist')  # Debugging statement

    def handle_payment_failed(self, payload):
        print('Handling payment failed event:', payload)  # Debugging statement
        # Handle failed payment logic here
        pass


class RatingViewSet(
    generics.GenericAPIView, 
    CreateModelMixin,
    RetrieveModelMixin, 
    UpdateModelMixin, 
    DestroyModelMixin
    ):
    """
    API endpoint for managing room ratings.
    """
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticatedUser]
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

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user, reservation_status=Reservation.CANCELED).prefetch_related('user')


class UserConfirmedRooms(generics.ListAPIView):
    """
    This view returns all confirmed rooms for the authenticated user.
    """
    serializer_class = ReservationSerializer

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user, reservation_status=Reservation.CONFIRMED).prefetch_related('user')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class UserPendingRooms(generics.ListAPIView):
    """
    This view returns all pending rooms for the authenticated user.
    """
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticatedUser]

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user, reservation_status=Reservation.PENDING).prefetch_related('user')



from .utils import get_summary_statistics
class SummaryStatisticsView(APIView):
    """
    This view returns summary statistics for the hotel.
    """
    def get(self, request):
        summary_statistics = get_summary_statistics()
        return Response(summary_statistics)