from rest_framework import serializers
from .models import Room, Category, RoomType, BedType, Amenity, Location, City, Country

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'name')

from rest_framework import serializers
from .models import Location

class LocationSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city.name', read_only=True)
    country_name = serializers.CharField(source='country.name', read_only=True)

    class Meta:
        model = Location
        fields = ['name','city_name', 'country_name']


class CategorySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    class Meta:
        model = Category
        fields = ('id', 'name', 'image')  

class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = ('id', 'name')

class BedTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BedType
        fields = ('id', 'name')

class AmenitySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)

    class Meta:
        model = Amenity
        fields = ('id', 'name', 'image')


# class RoomSerializer(serializers.ModelSerializer):
#     category = CategorySerializer()
#     room_type = serializers.StringRelatedField()
#     created_by = serializers.StringRelatedField()
#     bed_type = serializers.StringRelatedField()
#     amenities = AmenitySerializer(many=True)
#     location = LocationSerializer()
#     average_rating = serializers.FloatField(read_only=True)
#     rating_count = serializers.IntegerField(read_only=True) 
#     class Meta:
#         model = Room
#         fields = (
#             'id', 'name', 'location', 'category', 'description', 'price_per_night',
#             'max_occupancy', 'image','image2','image3','image4','image5', 'availability', 'pet_allowed', 'room_type', 'bed_type',
#             'amenities', 'created_by', 'created_at', 'average_rating', 'rating_count','google_map_url',
#         )
#     def create(self, validated_data):
#         location_data = validated_data.pop('location')
#         city_obj = location_data.get('city')
#         country_obj = location_data.get('country')
        
#         if country_obj:
#             location_data['country'] = country_obj.id
        
#         if city_obj:
#             location_data['city'] = city_obj.id
        
#         location_serializer = LocationSerializer(data=location_data)
#         if location_serializer.is_valid():
#             location = location_serializer.save()
#         else:
#             raise serializers.ValidationError(location_serializer.errors)
        
#         validated_data['location'] = location
        
#         amenities_data = validated_data.pop('amenities', [])
#         room = Room.objects.create(**validated_data)
#         room.amenities.set(amenities_data)
        
#         return room

#     def update(self, instance, validated_data):
#         location_data = validated_data.pop('location', None)
        
#         if location_data:
#             location_serializer = LocationSerializer(instance.location, data=location_data, partial=True)
#             if location_serializer.is_valid():
#                 location_serializer.save()
#             else:
#                 raise serializers.ValidationError(location_serializer.errors)

#         instance.name           = validated_data.get('name', instance.name)
#         instance.category       = validated_data.get('category', instance.category)
#         instance.description    = validated_data.get('description', instance.description)
#         instance.price_per_night= validated_data.get('price_per_night', instance.price_per_night)
#         instance.max_occupancy  = validated_data.get('max_occupancy', instance.max_occupancy)
#         instance.image          = validated_data.get('image', instance.image)
#         instance.availability   = validated_data.get('availability', instance.availability)
#         instance.pet_allowed    = validated_data.get('pet_allowed', instance.pet_allowed)
#         instance.room_type      = validated_data.get('room_type', instance.room_type)
#         instance.bed_type       = validated_data.get('bed_type', instance.bed_type)
#         amenities_data          = validated_data.get('amenities')
#         if amenities_data:
#             instance.amenities.set(amenities_data)
        
#         instance.save()

#         return instance



class RoomSerializer(serializers.ModelSerializer):
    # category = serializers.SlugRelatedField(slug_field='name', queryset=Category.objects.all())
    category = CategorySerializer()
    print('catogary is :',category)
    room_type = serializers.SlugRelatedField(slug_field='name', queryset=RoomType.objects.all())
    bed_type = serializers.SlugRelatedField(slug_field='name', queryset=BedType.objects.all())
    # amenities = serializers.SlugRelatedField(slug_field='name', queryset=Amenity.objects.all(), many=True)
    amenities = AmenitySerializer(many=True)
    location = LocationSerializer()
    created_by = serializers.StringRelatedField()
    average_rating = serializers.FloatField(read_only=True)
    rating_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Room
        fields = (
            'id', 'name', 'location', 'category', 'description', 'price_per_night',
            'max_occupancy', 'image', 'image2', 'image3', 'image4', 'image5', 
            'availability', 'pet_allowed', 'room_type', 'bed_type', 'amenities', 
            'created_by', 'created_at', 'average_rating', 'rating_count', 'google_map_url',
        )

   

    def create(self, validated_data):
        # Handle location creation
        location_data = validated_data.pop('location', {})

        # Check if 'city' and 'country' are dictionaries or objects
        city_data = location_data.get('city', None)
        country_data = location_data.get('country', None)

        if isinstance(city_data, dict):
            city_name = city_data.get('name', None)
            city, created = City.objects.get_or_create(name=city_name)
        elif isinstance(city_data, City):
            city = city_data
        else:
            raise serializers.ValidationError("City must be provided as a dictionary or City instance")

        if isinstance(country_data, dict):
            country_name = country_data.get('name', None)
            country, created = Country.objects.get_or_create(name=country_name)
        elif isinstance(country_data, Country):
            country = country_data
        else:
            raise serializers.ValidationError("Country must be provided as a dictionary or Country instance")

        location_data['city'] = city
        location_data['country'] = country

        location = Location.objects.create(**location_data)
        validated_data['location'] = location

        # Handle related fields
        amenities_names = validated_data.pop('amenities', [])
        amenities = Amenity.objects.filter(name__in=amenities_names)

        room = Room.objects.create(**validated_data)
        room.amenities.set(amenities)

        return room

    def update(self, instance, validated_data): 
        print('validate data from instasnd ',validated_data,instance)
        location_data = validated_data.pop('location', None)
        print('locati9oon data is :',location_data)
        # Handle nested location update
        if location_data:
            city_name = location_data.get('city', {}).get('name', None)
            country_name = location_data.get('country', {}).get('name', None)

            if city_name and country_name:
                city, created = City.objects.get_or_create(name=city_name)
                country, created = Country.objects.get_or_create(name=country_name)

                location_data['city'] = city
                location_data['country'] = country

                location_serializer = LocationSerializer(instance.location, data=location_data, partial=True)
                if location_serializer.is_valid():
                    location_serializer.save()
                else:
                    raise serializers.ValidationError(location_serializer.errors)
            else:
                raise serializers.ValidationError("City and country are required")

        # Update related fields
        if 'category' in validated_data:
            instance.category = Category.objects.get(name=validated_data.pop('category'))

        if 'room_type' in validated_data:
            instance.room_type = RoomType.objects.get(name=validated_data.pop('room_type'))

        if 'bed_type' in validated_data:
            instance.bed_type = BedType.objects.get(name=validated_data.pop('bed_type'))

        if 'amenities' in validated_data:
            amenities_names = validated_data.pop('amenities')
            amenities = Amenity.objects.filter(name__in=amenities_names)
            instance.amenities.set(amenities)

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()

        return instance
