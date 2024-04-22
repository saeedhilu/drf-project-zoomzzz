# serializers.py

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import User, OTP
from .utils import GoogleAuthenticator, register_social_user, send_sms
from .mixins import PhoneNumberMixin
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed

class GoogleSignSerializer(serializers.Serializer):
    access_token = serializers.CharField(min_length=5)

    def validate_access_token(self, access_token):
        user_data = GoogleAuthenticator.validate(access_token)
        
        
        try:
            user_data['sub']
        except:
            raise serializers.ValidationError(
                'The token is invalid or expired. Please login again.'
            )       
        if user_data['aud'] != settings.GOOGLE_CLIENT_ID:

            raise serializers.ValidationError('your are not google user')
        
        email = user_data['email']
        username = email.split('@')[0]
        # provider = 'google'
        return register_social_user( email, username)


class GenerateOTPSerializer(PhoneNumberMixin, serializers.Serializer):
    """
    Serializer for generating OTP given a phone number with country code.
    """
    phone_number = serializers.CharField(max_length=20)


class   UserProfileEditSerializer(serializers.ModelSerializer):
    """
    Serializer for editing user profile.
    """

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'image')

    def validate_username(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise ValidationError({"username": "This username is already in use."})
        return value

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        if 'image' in validated_data:
            instance.image = validated_data['image']
        instance.save()
        return instance


class ChangePhoneNumberSerializer(
    PhoneNumberMixin, 
    serializers.ModelSerializer
    ):
    """
    Serializer for changing phone number.
    """

    class Meta:
        model = User
        fields = ['phone_number']

    def validate_phone_number(self, value):
    
        if User.objects.filter(phone_number=value).exists():
            raise ValidationError("This phone number is already in use.")
        return value



from .models import WishList
from rooms.serializers import RoomSerializer   

class WishListSerializer(serializers.ModelSerializer):
    room = RoomSerializer(read_only=True)  # Nested serialization

    class Meta:
        model = WishList
        fields = '__all__'

