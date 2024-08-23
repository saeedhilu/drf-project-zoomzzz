from django.contrib import admin
from .models import *


class LocationAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'country', 'display_city')

    def display_city(self, obj):
        return obj.city.name if obj.city else None
    # Display both name and formatted city in the list view


class CityAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name',  # Include all fields you want to display
    ]


class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name', 'image', 'created_by', 'created_at',  # Include all fields you want to display
    ]


class RoomTypeAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name',  # Include all fields you want to display
    ]


class BedTypeAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name',  # Include all fields you want to display
    ]


class AmenityAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name', 'image',  # Include all fields you want to display
    ]
def get_amenities_list(self, obj):
    return ', '.join([str(amenity) for amenity in obj.amenities.all()])


class RoomAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name', 'location', 'get_city_name', 'get_country_name',
        'description', 'price_per_night', 'max_occupancy', 'availability',
        'pet_allowed', 'room_type', 'bed_type', 'created_by', 'created_at',
        'get_amenities_list',  
    ]

    def get_amenities_list(self, obj):
        return ', '.join([str(amenity) for amenity in obj.amenities.all()])

    def get_city_name(self, obj):
        return obj.location.city.name if obj.location else None

    def get_country_name(self, obj):
        return obj.location.country if obj.location else None
class CountryAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name',  # Include all fields you want to display 
    ]
admin.site.register(Country,CountryAdmin)
# Register models with custom admin panels
admin.site.register(Location, LocationAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(RoomType, RoomTypeAdmin)
admin.site.register(BedType, BedTypeAdmin)
admin.site.register(Amenity, AmenityAdmin)
admin.site.register(Room, RoomAdmin)
