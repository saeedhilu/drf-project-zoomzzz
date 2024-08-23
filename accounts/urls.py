
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from .views import (
    GoogleSignInView,
    GenerateOTPView,
    VerifyOTPView,
    ResendOTPView,
    UserProfileEditAPIView,
    ChangePhoneNumberView,
    VerifyChangePhoneNumberView,
    AllRoomsView,
    RoomDetailAPIView,
    WishListAPIView,
    RoomListView,
    BookingCreate,
    BookingCancelAPIView,
    InitiatePaymentAPIView,
    RatingViewSet,
    TopRatedRoomListAPIView,
    UserCanceledRooms,
    UserConfirmedRooms,
    UserPendingRooms,
    SummaryStatisticsView
    # RatingListCreateAPIView,
    # RatingRetrieveUpdateDestroyAPIView,
)

urlpatterns = [
    # signin
    path('google/auth/', GoogleSignInView.as_view(), name='google-sign-in'),
    
    path('generate-ph-otp/', GenerateOTPView.as_view(), name='generate_phone_otp'),

    path('verify-ph-otp/', VerifyOTPView.as_view(), name='verify_phone_otp'),

    path('resend-otp/', ResendOTPView.as_view(), name='otp-resending'),

    # Search result
    path('room-search/', RoomListView.as_view(), name='Room-searching-or-filterign'),
    
    path('user/update/', UserProfileEditAPIView.as_view(), name='update-user'),

    path('phone-number/update/', ChangePhoneNumberView.as_view(), name='update-user'),

    path('verify-otp/update/', VerifyChangePhoneNumberView.as_view(), name='update-user'),

    path('all-rooms/', AllRoomsView.as_view(), name='all-rooms'),
    
    path('room-detail/<int:pk>/', RoomDetailAPIView.as_view(), name='room-detail'),

    # whishslist
    path('wishlists/', WishListAPIView.as_view()),
    path('wishlists/<int:pk>/', WishListAPIView.as_view()),

    # >>>>>>>>>>>>>>>>
    path('reservations/<int:room_id>/', BookingCreate.as_view(), name='create_reservation'),
    path('reservations/canellation/<int:pk>/', BookingCancelAPIView.as_view(), name='booking-cancel'),

    path('initiate_payment/', InitiatePaymentAPIView.as_view(), name='initiate_payment'),




    path('rooms/<int:room_id>/ratings/create/', RatingViewSet.as_view(), name='rating-create'),
    path('rooms/<int:room_id>/ratings/<int:pk>/', RatingViewSet.as_view(), name='rating-detail'),




    path('rooms/top-rated/', TopRatedRoomListAPIView.as_view(), name='top-rated-rooms'),

    path('canceled-rooms/', UserCanceledRooms.as_view(), name='user_canceled_rooms'),
    path('confirmed-rooms/', UserConfirmedRooms.as_view(), name='user_confirmed_rooms'),
    path('pending-rooms/', UserPendingRooms.as_view(), name='user_pending_rooms'),
    path('summary-statistics/', SummaryStatisticsView.as_view(), name='summary-statistics'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh')
 

]