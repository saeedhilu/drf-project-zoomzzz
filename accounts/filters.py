# import django_filters
# from django_filters.rest_framework import FilterSet, DateFilter
# from datetime import datetime
# from django.db.models import Q
# from rooms.models import Room, Category, Amenity, RoomType, BedType

# class RoomFilter(FilterSet):
#     """
#     Filter for rooms based on price, category, amenities, room type, bed type, availability within specified date ranges, and guest count.
#     """
#     min_price = django_filters.NumberFilter(field_name='price_per_night', lookup_expr='gte')
#     max_price = django_filters.NumberFilter(field_name='price_per_night', lookup_expr='lte')
#     category = django_filters.ModelMultipleChoiceFilter(queryset=Category.objects.all())
#     amenities = django_filters.ModelMultipleChoiceFilter(queryset=Amenity.objects.all())
#     room_type = django_filters.ModelMultipleChoiceFilter(queryset=RoomType.objects.all())
#     bed_type = django_filters.ModelMultipleChoiceFilter(queryset=BedType.objects.all())
#     check_in = DateFilter(field_name='bookings__check_in', label='Check-In Date', method='filter_by_availability')
#     check_out = DateFilter(field_name='bookings__check_out', label='Check-Out Date', method='filter_by_availability')
#     guest_count = django_filters.NumberFilter(field_name='max_occupancy', lookup_expr='gte', label='Guest Count')
#     ordering = django_filters.OrderingFilter(
#         fields=(
#             ('price_per_night', 'price'),
#         ),
#         field_labels={
#             'price_per_night': 'Price',
#         },
#         label='Sort by'
#     )

#     def filter_by_availability(self, queryset, name, value):
#         check_in_date = self.request.GET.get('check_in')
#         check_out_date = self.request.GET.get('check_out')

#         if not check_in_date or not check_out_date:
#             return queryset

#         try:
#             check_in_date = datetime.strptime(check_in_date, '%Y-%m-%d')
#             check_out_date = datetime.strptime(check_out_date, '%Y-%m-%d')
#         except ValueError:
#             return queryset

#         excluded_statuses = ['PENDING', 'Pending']
#         exclude_conditions = Q()
#         for status in excluded_statuses:
#             exclude_conditions |= Q(bookings__reservation_status=status)
#         available_rooms = queryset.exclude(
#             Q(bookings__check_in__lt=check_out_date) &
#             Q(bookings__check_out__gt=check_in_date) &
#             Q(bookings__is_active=True) &
#             exclude_conditions
#         ).distinct()
#         return available_rooms

#     class Meta:
#         model = Room
#         fields = [
#             'location',
#             'category',
#             'amenities',
#             'room_type',
#             'bed_type',
#             'price_per_night',
#             'check_in',
#             'check_out',
#             'guest_count',
#         ]





import django_filters
from django_filters.rest_framework import FilterSet, DateFilter
from datetime import datetime
from django.db.models import Q
from rooms.models import Room, Category, Amenity, RoomType, BedType

class RoomFilter(FilterSet):
    """
    Filter for rooms based on price, category, amenities, room type, bed type, availability within specified date ranges, and guest count.
    """
    min_price = django_filters.NumberFilter(field_name='price_per_night', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price_per_night', lookup_expr='lte')
    category = django_filters.CharFilter(method='filter_multiple_categories')
    amenities = django_filters.CharFilter(method='filter_multiple_amenities')
    room_type = django_filters.CharFilter(method='filter_multiple_room_types')
    bed_type = django_filters.CharFilter(method='filter_multiple_bed_types')
    check_in = DateFilter(field_name='bookings__check_in', label='Check-In Date', method='filter_by_availability')
    check_out = DateFilter(field_name='bookings__check_out', label='Check-Out Date', method='filter_by_availability')
    guest_count = django_filters.NumberFilter(field_name='max_occupancy', lookup_expr='gte', label='Guest Count')
    ordering = django_filters.OrderingFilter(
        fields=(
            ('price_per_night', 'price'),
        ),
        field_labels={
            'price_per_night': 'Price',
        },
        label='Sort by'
    )

    def filter_by_availability(self, queryset, name, value):
        check_in_date = self.request.GET.get('check_in')
        check_out_date = self.request.GET.get('check_out')

        if not check_in_date or not check_out_date:
            return queryset

        try:
            check_in_date = datetime.strptime(check_in_date, '%Y-%m-%d')
            check_out_date = datetime.strptime(check_out_date, '%Y-%m-%d')
        except ValueError:
            return queryset

        excluded_statuses = ['PENDING', 'Pending']
        exclude_conditions = Q()
        for status in excluded_statuses:
            exclude_conditions |= Q(bookings__reservation_status=status)
        available_rooms = queryset.exclude(
            Q(bookings__check_in__lt=check_out_date) &
            Q(bookings__check_out__gt=check_in_date) &
            Q(bookings__is_active=True) &
            exclude_conditions
        ).distinct()
        return available_rooms

    def filter_multiple_categories(self, queryset, name, value):
        categories = value.split(',')
        return queryset.filter(category__in=categories).distinct()

    def filter_multiple_amenities(self, queryset, name, value):
        amenities = value.split(',')
        return queryset.filter(amenities__in=amenities).distinct()

    def filter_multiple_room_types(self, queryset, name, value):
        room_types = value.split(',')
        return queryset.filter(room_type__in=room_types).distinct()

    def filter_multiple_bed_types(self, queryset, name, value):
        bed_types = value.split(',')
        return queryset.filter(bed_type__in=bed_types).distinct()

    class Meta:
        model = Room
        fields = [
            'location',  
            'min_price',
            'max_price',
            'category',
            'amenities',
            'room_type',
            'bed_type',
            'check_in',
            'check_out',
            'guest_count',
            'ordering',
        ]
