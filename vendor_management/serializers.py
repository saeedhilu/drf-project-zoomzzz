import Levenshtein
from rest_framework import serializers
from accounts.models import User
from django.core.validators import RegexValidator
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from rest_framework.response import Response
from rest_framework import status
from django.views.generic import View
from smtplib import SMTPException
from rest_framework import serializers

from django.contrib.auth.hashers import check_password
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from Levenshtein import distance

email_validator = RegexValidator(
    regex=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
    message='Enter a valid email address'
)

phone_regex = RegexValidator(
    regex=r'^\d{10}$',
    message='Phone number must be entered in the format: 1234567890.'
)

class GenerateEmailSerializer(serializers.Serializer):
    """
    Serializer for generating email OTP and user registration.
    """
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField(validators=[email_validator])
    phone_number = serializers.CharField(max_length=10, validators=[phone_regex])
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate_email(self, value):
        """
        Check if the email is already used by another user.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already Exist")
        return value

    

    def validate(self, data):
        """
        Validate password and confirm_password fields.
        """
        password = data.get('password')
        confirm_password = data.pop('confirm_password', None)

        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match")

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
        user = User.objects.create_user(username=username, email=email, password=password,
                                        first_name=first_name, last_name=last_name)

        return user
# from django.contrib.auth.password_validation import validate_password





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
    



# class EmailSerializer(serializers.Serializer):
#     email = serializers.EmailField()





class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for changing user password.
    """
    old_password = serializers.CharField(max_length=128, write_only=True)
    new_password = serializers.CharField(max_length=128, write_only=True)
    confirm_password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        """
        Validate old_password, new_password, and confirm_password fields.
        """
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        # Check if the new password is too similar to the old password
        if self.is_password_similar(old_password, new_password):
            raise serializers.ValidationError("New password is too similar to the old password")

        # Check if new password and confirm password match
        if new_password != confirm_password:
            raise serializers.ValidationError("New password and confirm password do not match")

        # Run Django's built-in password validation checks on the new password
        try:
            validate_password(new_password)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

        return data

    def is_password_similar(self, old_password, new_password):
        """
        Check if the new password is too similar to the old password.
        """
        # Calculate Levenshtein distance between old and new passwords
        lev_distance = distance(old_password, new_password)
        
        # Calculate similarity score as 1 - (distance / max_length)
        max_length = max(len(old_password), len(new_password))
        similarity_score = 1 - (lev_distance / max_length)
        
        # Adjust threshold as needed
        return similarity_score > 0.8

class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer for requesting password reset.
    """
    email = serializers.EmailField()

