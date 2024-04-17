from rest_framework import serializers
from .models import Room, Category, RoomType, BedType, Amenity, Location, City


"""
<<<<< For Admin >>>>>
"""


class CategorySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()  # Added for image URL

    class Meta:
        model = Category
        fields = ('id', 'name', 'image', 'image_url', 'created_by', 'created_at')

    def get_image_url(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            return obj.image.url
        return None  # Return None if no image

class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = ('id', 'name')

class BedTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BedType
        fields = ('id', 'name')



"""
<<<<<<<< For Vendor >>>>>>>>
"""
from rest_framework import serializers
from .models import Room, Category, RoomType, BedType, Amenity, Location, City


"""
For Vendor
"""
from rest_framework import serializers

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'name')

class LocationSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(write_only=True)  # Write-only field for city name

    class Meta:
        model = Location
        fields = ('id', 'name', 'country', 'city_name')

    def create(self, validated_data):
        city_name = validated_data.pop('city_name')
        city, _ = City.objects.get_or_create(name=city_name)
        validated_data['city'] = city
        location = Location.objects.create(**validated_data)
        return location



class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ('id', 'name', 'image')


class RoomSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    room_type = serializers.PrimaryKeyRelatedField(queryset=RoomType.objects.all())
    bed_type = serializers.PrimaryKeyRelatedField(queryset=BedType.objects.all())
    amenities = serializers.PrimaryKeyRelatedField(queryset=Amenity.objects.all(), many=True)
    location = LocationSerializer()

    class Meta:
        model = Room
        fields = ('id', 'name', 'location', 'category', 'description', 'price_per_night',
                    'max_occupancy', 'image', 'availability', 'pet_allowed', 'room_type', 'bed_type',
                    'amenities', 'created_by', 'created_at')

    def create(self, validated_data):
        location_data = validated_data.pop('location')
        city_name = location_data.pop('city_name')
        
        # Get or create the city
        city, _ = City.objects.get_or_create(name=city_name)

        # Create the location and associate it with the city
        location = Location.objects.create(name=location_data['name'], country=location_data.get('country', ''), city=city)
        
        # Associate the location with the room
        validated_data['location'] = location

        # Create the room
        amenities_data = validated_data.pop('amenities', [])
        room = Room.objects.create(**validated_data)
        room.amenities.set(amenities_data)  # Use .set() for many-to-many relationships
        return room
