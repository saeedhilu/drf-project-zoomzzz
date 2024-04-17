import Levenshtein
from datetime import timedelta
from smtplib import SMTPException
from django.core.validators import RegexValidator
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth.hashers import check_password
from django.views.generic import View
from phonenumbers import parse as phonenumbers_parse, is_valid_number as phonenumbers_is_valid
from accounts.models import User
from accounts.utils import is_password_similar,validate_unique_email, validate_phone_number
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
"""
importing constant messages from constant file
"""
from accounts.constants import(
    PASSWORDS_DO_NOT_MATCH, 
    NEW_PASSWORD_SIMILAR_TO_OLD, 
    NEW_PASSWORD_CONFIRMATION_REQUIRED, 
    INVALID_EMAIL_OR_PASSWORD, 
    EMAIL_ALREADY_EXISTS
)

email_validator = RegexValidator(
    regex=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
    message='Enter a valid email address'
)


class GenerateEmailSerializer(serializers.Serializer):
    """
    Serializer for generating email OTP and user registration.
    """ 
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField(validators=[email_validator, validate_unique_email])
    phone_number = serializers.CharField(max_length=15, validators=[ validate_phone_number])
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, data):
        """
        Validate password and confirm_password fields.
        """
        password = data.get('password')
        confirm_password = data.pop('confirm_password', None)

        if password != confirm_password:
            raise serializers.ValidationError(PASSWORDS_DO_NOT_MATCH)

        return data

    def create(self, validated_data):
        """
        Create user instance using the email as username.
        """
        email = validated_data['email']
        username = email.split('@')[0]  # Extract username from email
        password = validated_data['password']
        phone_number = validated_data['phone_number']
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']

        # Create the user instance
        user = User.objects.create_user(
            username=username, 
            email=email,
            password=password,
            first_name=first_name, 
            last_name=last_name
            
            )

        return user

class VendorLoginSerializer(serializers.Serializer):
    """
    Serializer for vendor login.
    """
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate_email(self, value):
        # Custom validation for email, if needed
        return value

    def validate_password(self, value):
        # Custom validation for password, if needed
        return value


class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer for requesting password reset.
    """
    email = serializers.EmailField()


class ForgottPasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for changing user password.
    """

    new_password = serializers.CharField(
        max_length=128, 
        write_only=True
        )
    confirm_password = serializers.CharField(
        max_length=128, 
        write_only=True
        )

    def validate(self, data):
        """
        Validate old_password, new_password, and confirm_password fields.
        """

        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        # Check if new password and confirm password match
        if new_password != confirm_password:
            raise serializers.ValidationError(
                NEW_PASSWORD_CONFIRMATION_REQUIRED
                )

        # Run Django's built-in password validation checks on the new password
        try:
            validate_password(new_password)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

        return data


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing user password.
    """
    old_password = serializers.CharField(
        max_length=128, 
        write_only=True
        )
    new_password = serializers.CharField(
        max_length=128, 
        write_only=True
        )
    confirm_password = serializers.CharField(
        max_length=128, 
        write_only=True
        )

    def validate(self, data):
        """
        Validate old_password, new_password, and confirm_password fields.
        """
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        # Check if the new password is too similar to the old password
        if is_password_similar(old_password, new_password):
            raise serializers.ValidationError(
                NEW_PASSWORD_SIMILAR_TO_OLD
                )

        # Check if new password and confirm password match
        if new_password != confirm_password:
            raise serializers.ValidationError(
                NEW_PASSWORD_CONFIRMATION_REQUIRED
                )


        try:
            validate_password(new_password)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

        return data


class VendorProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(
        max_length=40, 
        required=False
        )
    last_name  = serializers.CharField(
        max_length=40, 
        required=False
        )
    image      = serializers.ImageField(
        required=False, 
        allow_null=True
        )

    class Meta:
        model = User
        fields = (
            'email', 
            'phone_number',
            'image', 
            'first_name', 
            'last_name'
                    )

    def validate_username(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError(
                {"username": "This username is already in use."}
                )
        return value

    def update(self, instance, validated_data):
        instance.username = validated_data.get(
            'username', 
            instance.username
            )
        instance.first_name = validated_data.get(
            'first_name', 
            instance.first_name
            )
        instance.last_name = validated_data.get(
            'last_name', 
            instance.last_name
            )
        if 'profile_photo' in validated_data:
            instance.profile_photo = validated_data['profile_photo']
        instance.save()
        return instance


class ChangeEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=500)

    class Meta:
        model = User
        fields = ['email']
