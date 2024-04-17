from django.contrib import admin
from .models import Location, City, Category, RoomType, BedType, Room, Amenity

# Custom admin panel for Room model
class RoomAdmin(admin.ModelAdmin):
    list_display = ['id','location', 'name', 'get_country', 'get_city_name', 'category', 'description', 'price_per_night', 'max_occupancy', 'availability', 'pet_allowed', 'room_type', 'bed_type', 'created_by', 'created_at']
    

    def get_country(self, obj):
        return obj.location.country if obj.location else None
    get_country.short_description = 'Country'

    def get_city_name(self, obj):
        return obj.location.city.name if obj.location else None
    get_city_name.short_description = 'City'

# Register models with custom admin panels
admin.site.register(Location)
admin.site.register(Amenity)
admin.site.register(City)
admin.site.register(Category)
admin.site.register(RoomType)
admin.site.register(BedType)
admin.site.register(Room, RoomAdmin)
