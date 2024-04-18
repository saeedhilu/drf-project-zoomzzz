
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

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'name')
class LocationSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(write_only=True)

    class Meta:
        model = Location
        fields = ('id', 'name', 'country', 'city_name')

    def create(self, validated_data):
        city_name = validated_data.pop('city_name')
        location, _ = Location.objects.get_or_create(name=validated_data['name'], country=validated_data.get('country', ''))
        city, _ = City.objects.get_or_create(name=city_name, location=location)
        return location

class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ('id', 'name', 'image')
from rest_framework import serializers
class RoomSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    room_type = serializers.PrimaryKeyRelatedField(queryset=RoomType.objects.all())
    bed_type = serializers.PrimaryKeyRelatedField(queryset=BedType.objects.all())
    amenities = serializers.PrimaryKeyRelatedField(queryset=Amenity.objects.all(), many=True)
    location = LocationSerializer()  # Set location as read-only

    # Change field types for availability and pet_allowed
    availability = serializers.BooleanField()
    pet_allowed = serializers.BooleanField()

    class Meta:
        model = Room
        fields = ('id', 'name', 'location', 'category', 'description', 'price_per_night',
                    'max_occupancy', 'image', 'availability', 'pet_allowed', 'room_type', 'bed_type',
                    'amenities', 'created_by', 'created_at')

    

    def create(self, validated_data):
        location_data = validated_data.pop('location')
        city_name = location_data.pop('city_name')

        # Check if a city with the provided name already exists
        city, _ = City.objects.get_or_create(name=city_name)

        # Create location with the existing or newly created city
        location, _ = Location.objects.get_or_create(name=location_data['name'], country=location_data.get('country', ''), city=city)

        validated_data['location'] = location

        amenities_data = validated_data.pop('amenities', [])
        room = Room.objects.create(**validated_data)

        # Set amenities using set() method
        room.amenities.set(amenities_data)

        return room
    def update(self, instance, validated_data):
        location_data = validated_data.pop('location', None)
        if location_data:
            location_serializer = LocationSerializer(instance.location, data=location_data)
            if location_serializer.is_valid():
                location_serializer.save()
            else:
                raise serializers.ValidationError(location_serializer.errors)

        instance.name = validated_data.get('name', instance.name)
        instance.category = validated_data.get('category', instance.category)
        instance.description = validated_data.get('description', instance.description)
        instance.price_per_night = validated_data.get('price_per_night', instance.price_per_night)
        instance.max_occupancy = validated_data.get('max_occupancy', instance.max_occupancy)
        instance.image = validated_data.get('image', instance.image)
        instance.availability = validated_data.get('availability', instance.availability)
        instance.pet_allowed = validated_data.get('pet_allowed', instance.pet_allowed)
        instance.room_type = validated_data.get('room_type', instance.room_type)
        instance.bed_type = validated_data.get('bed_type', instance.bed_type)

        # Update many-to-many relationship for amenities
        amenities_data = validated_data.get('amenities')
        if amenities_data is not None:
            instance.amenities.set(amenities_data)

        instance.save()
        return instance


# class RoomUpdateSerializer(serializers.ModelSerializer):
#     category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
#     room_type = serializers.PrimaryKeyRelatedField(queryset=RoomType.objects.all())
#     bed_type = serializers.PrimaryKeyRelatedField(queryset=BedType.objects.all())
#     amenities = serializers.PrimaryKeyRelatedField(queryset=Amenity.objects.all(), many=True)
#     location = LocationSerializer()

#     # Change field types for availability and pet_allowed
#     availability = serializers.BooleanField()
#     pet_allowed = serializers.BooleanField()

#     class Meta:
#         model = Room
#         fields = ('id', 'name', 'location', 'category', 'description', 'price_per_night',
#                     'max_occupancy', 'image', 'availability', 'pet_allowed', 'room_type', 'bed_type',
#                     'amenities', 'created_by', 'created_at')

    