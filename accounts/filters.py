import django_filters
from .models import Room
from rooms.models import *
class RoomFilter(django_filters.FilterSet):
    # Define filters
    min_price = django_filters.NumberFilter(field_name='price_per_night', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price_per_night', lookup_expr='lte')
    category = django_filters.ModelMultipleChoiceFilter(queryset=Category.objects.all())
    amenities = django_filters.ModelMultipleChoiceFilter(queryset=Amenity.objects.all())
    room_type = django_filters.ModelMultipleChoiceFilter(queryset=RoomType.objects.all())
    bed_type = django_filters.ModelMultipleChoiceFilter(queryset=BedType.objects.all())
    
    class Meta:
        model = Room
        fields = ['location', 'category', 'amenities', 'room_type', 'bed_type', 'price_per_night']
