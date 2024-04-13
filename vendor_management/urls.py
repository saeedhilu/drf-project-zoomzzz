from django.urls import path
from .views import (
    GenerateEmailView,
    VerifyEmailView,
    VendorLoginView,
    PasswordChangeView,
    ForgotPasswordEmailView 
)

urlpatterns = [
    path('generate-email-otp/', GenerateEmailView.as_view(), name='generate_email_otp'),
    path('login/', VendorLoginView.as_view(), name='login'),
    path('verify-email-otp/', VerifyEmailView.as_view(), name='verify_email_otp'),
    path('forgot-password-email/', ForgotPasswordEmailView.as_view(), name='forgot_password_email'),
    path('change-password/', PasswordChangeView.as_view(), name='change-password'),  # URL for regular password change
    path('change-password/<uidb64>/<token>/', PasswordChangeView.as_view(), name='change_password_token'),  # URL for password change with reset token
]
