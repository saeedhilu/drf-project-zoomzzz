
from django.urls import path
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
    ReservationCreateAPIView
)

urlpatterns = [
    path('google/auth', GoogleSignInView.as_view(), name='google-sign-in'),
    path('room-search/', RoomListView.as_view(), name='google-sign-in'),
    path('generate-ph-otp/', GenerateOTPView.as_view(), name='generate_phone_otp'),
    path('verify-ph-otp/', VerifyOTPView.as_view(), name='verify_phone_otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='otp-resending'),
    path('user/update/', UserProfileEditAPIView.as_view(), name='update-user'),
    path('phone-number/update/', ChangePhoneNumberView.as_view(), name='update-user'),
    path('verify-otp/update/', VerifyChangePhoneNumberView.as_view(), name='update-user'),
    path('all-rooms/', AllRoomsView.as_view(), name='all-rooms'),
    path('room-detail/<int:pk>/', RoomDetailAPIView.as_view(), name='room-detail'),
    path('wishlists/', WishListAPIView.as_view()),
    path('wishlists/<int:pk>/', WishListAPIView.as_view()),
    path('reservations/<int:room_id>/', ReservationCreateAPIView.as_view(), name='create_reservation'),
    
    
#     # path('login/', LoginUserView.as_view(), name='login'),
#     path('verify-email-otp/', VerifyEmailView.as_view(), name='verify_email_otp'),
]
