from django.contrib import admin
from .models import Location, City, Category, RoomType, BedType, Room, Amenity

# Custom admin panel base class
class BaseModelAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.fields]

# Register models with custom admin panels
admin.site.register(Location, BaseModelAdmin)
admin.site.register(City, BaseModelAdmin)
admin.site.register(Category, BaseModelAdmin)
admin.site.register(RoomType, BaseModelAdmin)
admin.site.register(BedType, BaseModelAdmin)
admin.site.register(Room, BaseModelAdmin)
admin.site.register(Amenity, BaseModelAdmin)
