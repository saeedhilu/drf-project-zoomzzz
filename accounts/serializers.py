# serializers.py

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import User, OTP
from .utils import GoogleAuthenticator, register_social_user, send_sms
from .mixins import PhoneNumberMixin
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from .constants import *
from rest_framework import serializers
from datetime import date
from .models import Reservation, User, Room





from rest_framework import serializers
from .models import Rating, Reservation
from rooms.models import Room
from django.core.exceptions import MultipleObjectsReturned
from rest_framework import serializers
from .models import Rating, Reservation
from rooms.models import Room
from django.core.exceptions import MultipleObjectsReturned
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
    is_active = serializers.BooleanField(read_only=True)
    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'image','is_active')
        

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





# from email_validator import validate_email, EmailNotValidError
# import phonenumbers
from rest_framework import serializers
from django.utils import timezone
from .models import Reservation
from email_validator import validate_email, EmailNotValidError
import phonenumbers



from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import Reservation
from email_validator import validate_email, EmailNotValidError
import phonenumbers
from django.utils import timezone

class ReservationSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)
    check_in = serializers.DateField()
    check_out = serializers.DateField()
    total_guest = serializers.IntegerField()
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    email = serializers.EmailField()
    contact_number = serializers.CharField(max_length=15)
    
    class Meta:
        model = Reservation
        fields = [
            'id',
            'check_in', 
            'check_out', 
            'total_guest',
            'user_name', 
            'room_name',
            'first_name',
            'last_name',
            'email',
            'contact_number',
        ] 
    
    def validate(self, data):
        room = self.context.get('room')
        
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        total_guest = data.get('total_guest')
        email = data.get('email')
        contact_number = data.get('contact_number')

        # Check date validity: check-in date must be before check-out date
        if check_in >= check_out:
            raise serializers.ValidationError('Check-in date must be before check-out date.')

        # Check that check-in date is in the future
        if check_in < timezone.now().date():
            raise serializers.ValidationError('Check-in date must be in the future.')

        # Check guest count against room's max occupancy
        if room and total_guest > room.max_occupancy:
            raise serializers.ValidationError(
                f"The room can only accommodate up to {room.max_occupancy} guests, but you requested {total_guest} guests."
            )

        # Validate email address
        try:
            validate_email(email)
        except EmailNotValidError:
            raise serializers.ValidationError('Invalid email address.')

        # Validate contact number
        try:
            parsed_number = phonenumbers.parse(contact_number, None)
            if not phonenumbers.is_valid_number(parsed_number):
                raise serializers.ValidationError('Invalid phone number.')
        except phonenumbers.phonenumberutil.NumberParseException:
            raise serializers.ValidationError('Invalid phone number.')
        print('room is ',room)
        print('check_in date is ',check_in)

        # Check for overlapping bookings
        overlapping_bookings = Reservation.objects.filter(
            room=room,
            check_in__lte=check_out,
            check_out__gte=check_in
        ).exclude(reservation_status='Canceled')
        print(overlapping_bookings)

        if self.instance:
            overlapping_bookings = overlapping_bookings.exclude(pk=self.instance.pk)

        if overlapping_bookings.exists():
            raise serializers.ValidationError('Room is already booked for the selected dates.')

        return data




class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'user', 'room', 'rating', 'feedback', 'created_at']
        read_only_fields = ['user', 'room', 'created_at']

    def validate(self, data):
        user = self.context['request'].user
        room_id = self.context['view'].kwargs.get('room_id')
        
        # Fetch the room instance
        room = Room.objects.get(id=room_id)
        instance = self.instance
        existing_rating = Rating.objects.filter(user=user, room=room).first()
    
        if existing_rating:
            if instance and instance == existing_rating:
                pass
            else:
                raise serializers.ValidationError("You have already rated this room.")
        try:
            reservation = Reservation.objects.get(room=room, user=user, reservation_status='Confirmed')
        except Reservation.DoesNotExist:
            raise serializers.ValidationError("No confirmed reservation found for this user and room.")
        except MultipleObjectsReturned:
            raise serializers.ValidationError("Multiple reservations found for the same user and room.")

        return data

        







class TopRatedSerializer(serializers.ModelSerializer):
    # Fields to hold the average rating and count of ratings
    average_rating = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Room
        fields = [
            'id', 'name', 'location', 'average_rating', 'price_per_night', 'image'
        ]
        depth = 1  # This setting enables nested serialization for related fields

from .models import WishList
from rooms.serializers import RoomSerializer   

class WishListSerializer(serializers.ModelSerializer):
    room = TopRatedSerializer(read_only=True)  # Nested serialization

    class Meta:
        model = WishList
        fields = '__all__'



class BlockAndUnblockSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ['is_active']