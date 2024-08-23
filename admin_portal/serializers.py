from rest_framework import serializers
from .models import Banner
from rest_framework import serializers
from accounts.models import User

from django.contrib.auth import authenticate


class SuperAdminLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        print('user')
        if user is None or not user.is_superuser:
            raise serializers.ValidationError('Invalid credentials')
        data['user'] = user
        # print('image is :',self.profile_images)
        return data




"""
<<<<< For Admin >>>>>
"""
from rooms.models import *
from rooms.serializers import *
# from django.contrib.auth import authenticate

# serializers.py

class CategorySerializer(serializers.ModelSerializer):
    """
    This Serializer  for Catogary management 
    """
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            'id', 
            'name', 
            'image', 
            'image_url', 
            'created_by', 
            'created_at'
        )
    
    def get_image_url(self, obj):
        localhost = "http://127.0.0.1:8000/"

        if obj.image and hasattr(obj.image, 'url'):
            return localhost+obj.image.url
        return None

    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError("Name cannot be empty.")
        

        if value != 'undefined' and  Category.objects.filter(name=value).exists() :
            raise serializers.ValidationError("Category with this name already exists.")
        return value


class AmenitySerializer(serializers.ModelSerializer):
    """
    This Serializer  for Amenity management 
    """
    image_url = serializers.SerializerMethodField()
    

    class Meta:
        model = Amenity
        fields = ('id', 'name', 'image', 'image_url')

    def get_image_url(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            return obj.image.url
        return None

    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError("Name cannot be empty.")

        if Amenity.objects.filter(name=value).exists():
            raise serializers.ValidationError("Amenity with this name already exists.")

        return value



class RoomTypeSerializer(serializers.ModelSerializer):
    """
    This Serializer  for RoomType management 
    """
    class Meta:
        model = RoomType
        fields = ('id', 'name')
    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError(
                "Name cannot be empty."
                )
        
        # Check if a category with the same name already exists
        if RoomType.objects.filter(name=value).exists():
            raise serializers.ValidationError(
                "Room Type with this name already exists."
                )
        
        return value
class BedTypeSerializer(serializers.ModelSerializer):
    """
    This Serializer  for BedType management 
    """
    class Meta:
        model = BedType
        fields = ('id', 'name')
    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError(
                "Name cannot be empty."
                )
        
        # Check if a category with the same name already exists
        if BedType.objects.filter(name=value).exists():
            raise serializers.ValidationError(
                "Bed Type with this name already exists."
                )
        
        return value

class CitySerializer(serializers.ModelSerializer):
    """
    This Serializer  for City management 
    """
    class Meta:
        model = City
        fields = ('id', 'name')

class CountrySerializer(serializers.ModelSerializer):
    """
    This Serializer  for Country management 
    """
    class Meta:
        model  = Country
        fields = ('id', 'name') 
class LocationSerializer(serializers.ModelSerializer):
    """
    This Serializer  for LocationSerializer management 
    """
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())

    class Meta:
        model = Location
        fields = ('id', 'name', 'country', 'city')

    def validate_city(self, value):
        
        # Check if the city exists
        if not City.objects.filter(name=value).exists():
            raise serializers.ValidationError("City does not exist.")
        return value

    def create(self, validated_data):
        city_name = validated_data.pop('city')
        country = validated_data.pop('country')
        city, _ = City.objects.get_or_create(name=city_name)
        location = Location.objects.create(city=city, country=country, **validated_data)
        return location




class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'






class UserBlockUnblockSerializer(serializers.ModelSerializer):
    """
    This Serializer  for User management 
    """
    class Meta:
        model = User
        fields = ['id', 'is_active']

    def update(self, instance, validated_data):
        # Update the user's is_active status based on the provided value
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()
        return instance



class TOPVendorSerializer(serializers.ModelSerializer):
    total_bookings = serializers.IntegerField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'email', 'image_url', 'total_bookings']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url)
        return None