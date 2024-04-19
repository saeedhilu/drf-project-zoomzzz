from rest_framework import serializers

class SuperAdminLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        return data





"""
<<<<< For Admin >>>>>
"""
from rooms.models import *
from rooms.serializers import *
# from django.contrib.auth.models import User
# from django.contrib.auth import authenticate

class CategorySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()  # Added for image URL

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
        if obj.image and hasattr(obj.image, 'url'):
            return obj.image.url
        return None  # Return None if no image
    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError(
                "Name cannot be empty."
                )
        
        # Check if a category with the same name already exists
        if Category.objects.filter(name=value).exists():
            raise serializers.ValidationError(
                "Category with this name already exists."
                )
        
        return value


class RoomTypeSerializer(serializers.ModelSerializer):
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
class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ('id', 'name', 'image')
    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError(
                "Name cannot be empty."
                )
        
        # Check if a category with the same name already exists
        if Amenity.objects.filter(name=value).exists():
            raise serializers.ValidationError(
                "Aminities with this name already exists."
                )
        
        return value


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'name')

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Country
        fields = ('id', 'name') 
class LocationSerializer(serializers.ModelSerializer):
    # country = serializers.CharField(write_only=True)
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