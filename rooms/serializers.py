
from rest_framework import serializers
from .models import Room, Category, RoomType, BedType, Amenity, Location, City,Country

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'name')
class LocationSerializer(serializers.ModelSerializer):
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())
    country = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all())

    class Meta:
        model = Location
        fields = ('id', 'name', 'country', 'city')


class RoomSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    room_type = serializers.PrimaryKeyRelatedField(queryset=RoomType.objects.all())
    bed_type = serializers.PrimaryKeyRelatedField(queryset=BedType.objects.all())
    amenities = serializers.PrimaryKeyRelatedField(queryset=Amenity.objects.all(), many=True)
    
    # Use LocationSerializer for better handling of location, city, and country data
    location = LocationSerializer()

    class Meta:
        model = Room
        fields = ('id', 'name', 'location', 'category', 'description', 'price_per_night',
                    'max_occupancy', 'image', 'availability', 'pet_allowed', 'room_type', 'bed_type',
                    'amenities', 'created_by', 'created_at')

    def create(self, validated_data):
        location_data = validated_data.pop('location')
        
        
        city_obj = location_data.get('city')
        country_obj = location_data.get('country')
        if country_obj is not None:
            country_id = country_obj.id
            location_data['country'] = country_id
        
        
        if city_obj is not None:
            
            city_id = city_obj.id
            
            
            location_data['city'] = city_id
        
        # Create the Location object with the modified location_data
        location_serializer = LocationSerializer(data=location_data)
        if location_serializer.is_valid():
            location = location_serializer.save()
        else:
            raise serializers.ValidationError(location_serializer.errors)
        
        validated_data['location'] = location
        
        amenities_data = validated_data.pop('amenities', [])
        room = Room.objects.create(**validated_data)
        
        # Set amenities using set() method
        room.amenities.set(amenities_data)
        
        return room

    def update(self, instance, validated_data):
    # Check if `location` data is present in validated_data
        location_data = validated_data.pop('location', None)
        
        if location_data:
        
            location_serializer = LocationSerializer(instance.location, data=location_data, partial=True)
            if location_serializer.is_valid():
                location_serializer.save()
            else:
                raise serializers.ValidationError(location_serializer.errors)

        # Update other fields in the instance
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
        
        # Update amenities if provided
        amenities_data = validated_data.get('amenities')
        if amenities_data:
            instance.amenities.set(amenities_data)
            
        # Save the updated instance
        instance.save()

        # Return the updated instance
        return instance
