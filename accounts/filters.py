import django_filters
from django_filters.rest_framework import FilterSet, DateFilter
from datetime import datetime
from django.db.models import Q
from django_filters import rest_framework as filters

from rooms.models import Room, Category, Amenity, RoomType, BedType
from .models import Booking

class RoomFilter(FilterSet):
    """
    Filter for rooms based on price, category, amenities, room type, bed type, and availability within specified date ranges.
    """
    # Define filters
    min_price = django_filters.NumberFilter(field_name='price_per_night', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price_per_night', lookup_expr='lte')
    category = django_filters.ModelMultipleChoiceFilter(queryset=Category.objects.all())
    amenities = django_filters.ModelMultipleChoiceFilter(queryset=Amenity.objects.all())
    room_type = django_filters.ModelMultipleChoiceFilter(queryset=RoomType.objects.all())
    bed_type = django_filters.ModelMultipleChoiceFilter(queryset=BedType.objects.all())
    
    # Custom filters for availability
    check_in = DateFilter(field_name='bookings__check_in', label='Check-In Date', method='filter_by_availability')
    check_out = DateFilter(field_name='bookings__check_out', label='Check-Out Date', method='filter_by_availability')

    def filter_by_availability(self, queryset, name, value):
        """
        Custom filter method to filter rooms based on availability within the specified date range.
        """
        # Retrieve check-in and check-out dates from the request
        check_in_date = self.request.GET.get('check_in')
        check_out_date = self.request.GET.get('check_out')

        # Return the original queryset if dates are not provided
        if not check_in_date or not check_out_date:
            return queryset

        # Convert the dates from strings to datetime objects
        try:
            check_in_date = datetime.strptime(check_in_date, '%Y-%m-%d')
            check_out_date = datetime.strptime(check_out_date, '%Y-%m-%d')
        except ValueError:
            # Return the original queryset if date conversion fails
            return queryset

        # Filter rooms based on availability in the specified date range
        # Exclude rooms that have bookings overlapping with the specified date range
        available_rooms = queryset.exclude(
            Q(bookings__check_in__lt=check_out_date) & Q(bookings__check_out__gt=check_in_date)
        ).distinct()

        return available_rooms

    class Meta:
        model = Room
        fields = [
            'location',
            'category',
            'amenities',
            'room_type',
            'bed_type',
            'price_per_night',
            'check_in',
            'check_out',
        ]
