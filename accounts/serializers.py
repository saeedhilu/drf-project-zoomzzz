from django.forms import ValidationError
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.validators import UniqueTogetherValidator

from .models import OTP, User
from .utils import GoogleAuthenticator, register_social_user
from django.contrib.auth import authenticate

# Validators


class GoogleSignSerializer(serializers.Serializer):
    access_token = serializers.CharField(min_length=5)

    def validate_access_token(self, access_token):
        google_user_data = GoogleAuthenticator.validate(access_token)
        try:
            userid = google_user_data['sub']
        except Exception as e:
            raise serializers.ValidationError('This token is expired')
        if google_user_data['aud'] != settings.GOOGLE_CLIENT_ID:
            raise AuthenticationFailed(detail="could not verify user")
        email = google_user_data['email']
        username = email.split('@')
        provider = 'google'
        return register_social_user(provider, email, username)


class GenerateOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)

    def validate_phone_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only numeric digits.")
        if len(value) != 10:
            raise serializers.ValidationError("Phone number must have exactly 10 digits.")
        return value









# class OTPSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = OTP
#         fields = ['phone_number', 'otp_code', 'otp_expiry']
#         read_only_fields = ['otp_code', 'otp_expiry']
#         validators = [
#             UniqueTogetherValidator(
#                 queryset=OTP.objects.all(),
#                 fields=['phone_number'],
#                 message='An OTP already exists for this phone number.'
#             )
#         ]



# from django.forms import ValidationError
# from rest_framework import serializers
# from django.contrib.auth.password_validation import validate_password
# from django.conf import settings
# from rest_framework.exceptions import AuthenticationFailed
# from rest_framework.validators import UniqueTogetherValidator
# from django.core.validators import RegexValidator, EmailValidator
# from .models import OTP, User
# from .utils import GoogleAuthenticator, register_social_user
# from django.contrib.auth import authenticate

# # Validators
# email_validator = EmailValidator()
# phone_regex = RegexValidator(
#     regex=r'^\d{10}$',
#     message='Phone number must be 10 digits only',
# )
# username_validator = RegexValidator(
#     regex=r'^[\w.@+-]+$',
#     message='Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters.',
# )


# class VenderRegisterSerializer(serializers.Serializer):
#     password = serializers.CharField(write_only=True, style={'input_type': 'password'})
#     confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

#     class Meta:
#         model = User
#         fields = ['email', 'first_name', 'last_name', 'phone_number', 'password', 'confirm_password']

#     def validate(self, data):
#         password = data.get('password')
#         confirm_password = data.pop('confirm_password', None)

#         if password != confirm_password:
#             raise ValidationError("Passwords do not match")

#         return data

#     def create(self, validated_data):
#         user = User.objects.create_user(
#             email=validated_data['email'],
#             first_name=validated_data.get('first_name'),
#             last_name=validated_data.get('last_name'),
#             phone_number=validated_data.get('phone_number'),
#         )
#         return user


# class GoogleSignSerializer(serializers.Serializer):
#     access_token = serializers.CharField(min_length=5)

#     def validate_access_token(self, access_token):
#         google_user_data = GoogleAuthenticator.validate(access_token)
#         try:
#             userid = google_user_data['sub']
#         except Exception as e:
#             raise serializers.ValidationError('This token is expired')
#         if google_user_data['aud'] != settings.GOOGLE_CLIENT_ID:
#             raise AuthenticationFailed(detail="could not verify user")
#         email = google_user_data['email']
#         username = email.split('@')
#         provider = 'google'
#         return register_social_user(provider, email, username)


# class GenerateOTPSerializer(serializers.Serializer):
#     phone_number = serializers.CharField(max_length=20)

#     def validate_phone_number(self, value):
#         if not value.isdigit():
#             raise serializers.ValidationError("Phone number must contain only numeric digits.")
#         if len(value) != 10:
#             raise serializers.ValidationError("Phone number must have exactly 10 digits.")
#         return value


# class OTPSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = OTP
#         fields = ['phone_number', 'otp_code', 'otp_expiry']
#         read_only_fields = ['otp_code', 'otp_expiry']
#         validators = [
#             UniqueTogetherValidator(
#                 queryset=OTP.objects.all(),
#                 fields=['phone_number'],
#                 message='An OTP already exists for this phone number.'
#             )
#         ]


# class GenerateEmailSerializer(serializers.Serializer):
#     first_name = serializers.CharField(max_length=100)
#     last_name = serializers.CharField(max_length=100)
#     email = serializers.EmailField(validators=[email_validator])
#     phone_number = serializers.CharField(max_length=10, validators=[phone_regex])
#     password = serializers.CharField(write_only=True, style={'input_type': 'password'})
#     confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

#     def validate_password(self, value):
#         validate_password(value)
#         return value

#     def validate(self, data):
#         password = data.get('password')
#         confirm_password = data.pop('confirm_password', None)

#         if password != confirm_password:
#             raise ValidationError("Passwords do not match")

#         return data


# class LoginSerializer(serializers.Serializer):
#     email = serializers.EmailField(validators=[email_validator])
#     password = serializers.CharField(write_only=True, style={'input_type': 'password'})
#     access_token = serializers.CharField(min_length=10)
#     refresh_token = serializers.CharField(min_length=10)

#     def validate(self, attrs):
#         email = attrs.get('email')
#         password = attrs.get('password')
#         request = self.context.get('request')
#         user = authenticate(request, email=email, password=password)
#         if not user:
#             raise AuthenticationFailed('Invalid credentials')
#         if not user.is_verified:
#             raise AuthenticationFailed('Email is not verified')
#         token = user.token
#         return {
#             'email': user.email,
#             'full_name': user.get_full_name(),
#             'access_token': str(token.get('access')),
#             'refresh_token': str(token.get('refresh'))
#         }
