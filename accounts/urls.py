from django.urls import path
from .views import GoogleSignInView,GenerateOTPView,VerifyOTPView,ResendOTPView

urlpatterns = [
    path('google/auth', GoogleSignInView.as_view(), name='google-sign-in'),
    path('generate-ph-otp/', GenerateOTPView.as_view(), name='generate_phone_otp'),
    path('verify-ph-otp/', VerifyOTPView.as_view(), name='verify_phone_otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='otp-resending'),
#     # path('login/', LoginUserView.as_view(), name='login'),
#     path('verify-email-otp/', VerifyEmailView.as_view(), name='verify_email_otp'),
]
