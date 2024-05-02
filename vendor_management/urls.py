from django.urls import path
from .views import (
    VendorSignupView,
    VenodrVerifyView,
    VendorLoginView,
    ForgottPasswordResetView,
    ForgotPasswordEmailView ,
    ChangePasswordView,
    ResendEmailOTPView,
    VendorProfileAPIView,
    ChangeEmailView,
    VerifyEmailChangeView,
     DashboardView,
     UserDetailaView
    # ChangePasswordEmailView
)

urlpatterns = [
    path('signup-vendor/', VendorSignupView.as_view(), name='generate_email_otp'),
    path('login/', VendorLoginView.as_view(), name='login'),
    path('verify-email-otp/', VenodrVerifyView.as_view(), name='verify_email_otp'),
    path('resend-otp/', ResendEmailOTPView.as_view(), name='otp-resending'),
    path('forgot-password-email/', ForgotPasswordEmailView.as_view(), name='forgot_password_email'),
    path('forgot_password_change/<uidb64>/<token>/', ForgottPasswordResetView.as_view(), name='change_password_token'),  # URL for password change with reset token
    path('vendor/update/', VendorProfileAPIView.as_view(), name='update-vendor'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),  # URL for regular password change
    path('change-email/', ChangeEmailView.as_view(), name='change-email'),  # URL for regular password change
    
    path('verify-email/', VerifyEmailChangeView.as_view(), name='verify-email'),  # URL for regular password change
    # >>>>>>>>>>>>>>>>>>>>
    path('vendor-dashboard/', DashboardView.as_view(), name='admin_dashboard'),
    path('all-users/', UserDetailaView.as_view(), name='admin_dashboard'),

]
