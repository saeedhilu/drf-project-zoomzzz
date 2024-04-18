from django.contrib import admin
from .models import Location, City, Category, RoomType, BedType, Amenity, Room


class LocationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name', 'country', 'city',  # Include all fields you want to display
    ]


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

class RoomAdmin(admin.ModelAdmin):
    list_display = [
    'id', 'name','location', 'get_city_name', 'get_country_name',
    'description', 'price_per_night', 'max_occupancy', 'availability',
    'pet_allowed', 'room_type', 'bed_type', 'created_by', 'created_at',
        ]

    def get_city_name(self, obj):
        return obj.location.city.name if obj.location else None

    def get_country_name(self, obj):
        return obj.location.country if obj.location else None
    def get_amenities(self, obj):
        return ', '.join([amenity.name for amenity in obj.amenities.all()])



# Register models with custom admin panels
admin.site.register(Location, LocationAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(RoomType, RoomTypeAdmin)
admin.site.register(BedType, BedTypeAdmin)
admin.site.register(Amenity, AmenityAdmin)
admin.site.register(Room, RoomAdmin)
