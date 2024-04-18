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
class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ('id', 'name', 'image')