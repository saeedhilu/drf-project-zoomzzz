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



















from rest_framework import serializers
from datetime import date
from .models import Reservation, Room

class ReservationSerializer(serializers.ModelSerializer):
    check_in = serializers.DateField()
    check_out = serializers.DateField()
    total_guest = serializers.IntegerField()
    
    class Meta:
        model =  Reservation
        fields = ['check_in', 'check_out', 'total_guest']

    def validate(self, data):
        # Retrieve room from context
        room = self.context.get('room')
        
        # Retrieve check-in, check-out dates and total guests from data
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        total_guest = data.get('total_guest')

        # Check date validity: check-in date must be before check-out date
        if check_in >= check_out:
            raise serializers.ValidationError("Check-in date must be before check-out date.")

        # Check that check-in date is in the future
        if check_in < date.today():
            raise serializers.ValidationError("Check-in date must be in the future.")
        
        # Check guest count against room's max occupancy
        if room and total_guest > room.max_occupancy:
            raise serializers.ValidationError(
                f"The room can only accommodate up to {room.max_occupancy} guests, but you requested {total_guest} guests."
            )

        # Check for overlapping bookings
        overlapping_bookings = Reservation.objects.filter(
            room=room,
            check_in__lt=check_out,
            check_out__gt=check_in
        )

        # Exclude the current booking if editing an existing booking
        if self.instance:
            overlapping_bookings = overlapping_bookings.exclude(pk=self.instance.pk)
        
        # If overlapping bookings exist, raise a validation error
        if overlapping_bookings.exists():
            raise serializers.ValidationError("The room is already booked within the specified time range.")

        return data