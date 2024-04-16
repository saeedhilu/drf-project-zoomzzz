from django.urls import path
from .views import (
    GoogleSignInView,
    GenerateOTPView,
    VerifyOTPView,
    ResendOTPView,
    UserProfileEditAPIView,
    ChangePhoneNumberView,
    VerifyChangePhoneNumberView
)

urlpatterns = [
    path('google/auth', GoogleSignInView.as_view(), name='google-sign-in'),
    path('generate-ph-otp/', GenerateOTPView.as_view(), name='generate_phone_otp'),
    path('verify-ph-otp/', VerifyOTPView.as_view(), name='verify_phone_otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='otp-resending'),
    path('user/update/', UserProfileEditAPIView.as_view(), name='update-user'),
    path('phone-number/update/', ChangePhoneNumberView.as_view(), name='update-user'),
    path('verify-otp/update/', VerifyChangePhoneNumberView.as_view(), name='update-user'),
#     # path('login/', LoginUserView.as_view(), name='login'),
#     path('verify-email-otp/', VerifyEmailView.as_view(), name='verify_email_otp'),
]
