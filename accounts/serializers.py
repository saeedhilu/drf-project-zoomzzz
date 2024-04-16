from django.forms import ValidationError
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.validators import UniqueTogetherValidator

from .models import OTP, User
from .utils import GoogleAuthenticator, register_social_user
from django.contrib.auth import authenticate
from phonenumbers import parse as phonenumbers_parse, is_valid_number as phonenumbers_is_valid
from .utils import phone_regex



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
        
        email    = google_user_data['email']
        username = email.split('@')
        provider = 'google'
        return register_social_user(provider, email, username)




class GenerateOTPSerializer(serializers.Serializer):
    """
    This serializer for generating otp given phone number
    """


    phone_number = serializers.CharField(max_length =20)

    def validate_phone_number(self, value):
        try:
            parsed_number = phonenumbers_parse(value, None)
            if not phonenumbers_is_valid(parsed_number):
                raise serializers.ValidationError("Invalid phone number format")
        except Exception as e:
            raise serializers.ValidationError("Invalid phone number format")
        
        return phonenumbers_parse(value, None).national_number

class UserProfileSerializer(serializers.ModelSerializer):

    username = serializers.CharField(required=True)
    image = serializers.ImageField(required=False, allow_null=True)


    class Meta:
        model = User
        fields = ('username', 'email','phone_number','image')

    def validate_username(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError({"username": "This username is already in use."})
        return value

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        if 'profile_photo' in validated_data:
            instance.profile_photo = validated_data['profile_photo']
        instance.save()
        return instance