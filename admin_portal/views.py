from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.permission import IsAuthenticatedUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import SuperAdminLoginSerializer
from .serializers import *
from accounts.constants import *
from accounts.constants import PERMISSION_DENIED
from rest_framework import generics
from rest_framework.response import Response
from rooms.models import Room
from rooms.serializers import RoomSerializer
from accounts.utils import cache_queryset, get_summary_statistics
from vendor_management.serializers import VendorProfileSerializer
from accounts.serializers import UserProfileEditSerializer,BlockAndUnblockSerializer
from .serializers import UserBlockUnblockSerializer
from rest_framework import status, generics
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAdminUser
from accounts.models import User
from accounts.permission import IsSuperUser



class SuperAdminLoginView(APIView):
    """
    This view is for super admin login
    """
    def post(self, request):
        serializer = SuperAdminLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            print('user is :',user,user.image.url)
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'username': user.username,
                'profile_image': user.image.url if user.image else None, 
                'is_superadmin': True,
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )


from accounts.permission import *
class AbstractCRUDView(APIView):
    """
    Abstract base class for CRUD operations on models with permission checks.
    """
    permission_classes = [IsSuperUser]
    model = None
    serializer_class = None
    cache_timeout = 3600  # Cache timeout in seconds (1 hour)

    def get_object(self, pk):
        """
        Retrieve an object by its primary key.
        """
        try:
            return self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            raise Http404("Object not found.")

    def get(self, request, pk=None):
        """
        Retrieve a single object by primary key or list all objects.
        If pk is provided, return the object with that primary key.
        Otherwise, return a list of all objects and cache it.
        """
        if pk:
            obj = self.get_object(pk)
            serializer = self.serializer_class(obj)
            return Response(serializer.data)
        else:
            cache_key = f'{self.model.__name__.lower()}_list'
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)

            queryset = self.model.objects.all()
            serializer = self.serializer_class(queryset, many=True)
            cache.set(cache_key, serializer.data, timeout=self.cache_timeout)
            return Response(serializer.data)

    def post(self, request):
        """
        Create a new object.
        """
        print('request os :',request.data)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            self._invalidate_cache()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,                
            )
        return Response(
            
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):
        """
        Partially update an existing object by primary key.
        """
        print('requesrion os :',request.data)
        obj = self.get_object(pk)
        serializer = self.serializer_class(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            self._invalidate_cache()
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


    def delete(self, request, pk):
        print('pk is :',pk)
        """
        Delete an object by primary key.
        """
        obj = self.get_object(pk)
        obj.delete()
        self._invalidate_cache()
        return Response(
            {"message": f"{self.model._meta.verbose_name} deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )

    def _invalidate_cache(self):
        """
        Invalidate the cache for the model's list.
        """
        cache_key = f'{self.model.__name__.lower()}_list'
        cache.delete(cache_key)


class AddCategoryView(AbstractCRUDView):
    """
    This view is used to edit category
    """
    model = Category
    serializer_class = CategorySerializer


class AddAmenitiesView(AbstractCRUDView):
    """
    This view is used to edit amenity
    """
    model = Amenity
    serializer_class = AmenitySerializer


class AddRoomsTypeView(AbstractCRUDView):
    """
    This view is used to edit amenity
    """
    model = RoomType
    serializer_class = RoomTypeSerializer


class AddBedTypeView(AbstractCRUDView):
    """
    This view is used to edit bed type
    """
    model = BedType
    serializer_class = BedTypeSerializer


class AddCityView(AbstractCRUDView):
    """
    This view is used to add cities.
    """
    model = City
    serializer_class = CitySerializer


class AddLocationView(AbstractCRUDView):
    """
    This view is used to add location.
    """
    model = Location
    serializer_class = LocationSerializer
class AddCountry(AbstractCRUDView):
    """
    This view is used to add country.
    """
    
    model = Country
    serializer_class = CountrySerializer


class AddBanner(AbstractCRUDView):
    """
    This view is used to add banner.
    """
    model = Banner
    serializer_class = BannerSerializer


# ########################

class AdminRoomListingView(generics.ListAPIView):

    
    """
    API view to list all rooms efficiently for the admin dashboard, with summary statistics.
    """
    queryset = cache_queryset(
        ALL_ROOMS,
        Room.objects.select_related(
            'category', #
            'room_type', 
            'bed_type', 
            'location__city', 
            'location__country'
            )
        .prefetch_related('amenities')
        .only(
            'id', 'name', 'description', 
            'price_per_night', 'max_occupancy', 
            'availability','pet_allowed', 'image',
            'created_by', 'created_at',
            'category__name', 'room_type__name', 
            'bed_type__name','location__name', 
            'location__city__name', 'location__country__name'
        ),
        timeout=300
    )


    serializer_class = RoomSerializer
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        print('room',response.data)
        summary_statistics = get_summary_statistics()
        custom_response_data = {
            'summary_statistics': summary_statistics,
            'rooms': response.data,
        }
        print('respomse ios :',custom_response_data)
        
        return Response(custom_response_data)

from django.core.cache import cache
from rest_framework import generics



class VebdorsListView(generics.ListAPIView):
    """
    This view for listing all Vendors on Admin dashboard
    """
    serializer_class = VendorProfileSerializer  # Add serializer_class attribute
    permission_classes = [IsSuperUser]

    def get_queryset(self):
        queryset_cache_key = VENDOR_QUERY_SET
        queryset = cache.get(queryset_cache_key)

        if queryset is None:
            queryset = User.objects.filter(is_vendor=True)
            cache.set(queryset_cache_key, queryset, timeout=300)  # Cache for 5 minutes

        return queryset


class UserDetailaView(generics.ListAPIView):
    """
    This view for listing all Users details on Admin dashboard
    """
    serializer_class = UserProfileEditSerializer
    permission_classes = [IsSuperUser]

    def get_queryset(self):
        queryset_cache_key = USER_QUERY_SET
        queryset = cache.get(queryset_cache_key)

        if queryset is None:
            queryset = User.objects.all()
            cache.set(queryset_cache_key, queryset, timeout=300)  
        print('query set is ',queryset)
        return queryset
    


    
class UserBlockUnblockView(generics.GenericAPIView):

    """
    This view for block/unblock user on Admin dashboard
    """
    serializer_class = BlockAndUnblockSerializer
    permission_classes = [IsSuperUser] 

    def post(self, request, pk):
        # Get the user object based on the provided primary key (user ID)
        user = get_object_or_404(User, pk=pk)

        
        is_active = user.is_active
        print(user)

        # Toggle the is_active field (block/unblock the user)
        user.is_active = not is_active
        user.save(update_fields=['is_active'])

        
        serializer = self.serializer_class(user)
        if not is_active:
            message = UNBLOCK_SUCCESS
        else:
            message = BLOCK_SUCCESS

        return Response({
            MESSAGE: message,
            is_active:is_active,
        }, status=status.HTTP_200_OK)




class BannerListCreateView(generics.ListAPIView):
    """
    Listing Banners
    """

    queryset = Banner.objects.all()
    serializer_class = BannerSerializer

class BannerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Detail and Update Banners
    """
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer







class CategoryListView(generics.ListAPIView):
    """
    API view to list all categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class AmenityListView(generics.ListAPIView):
    """
    API view to list all amenities.
    """
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
class CountryListView(generics.ListAPIView):
    """
    Api view to List ALl amenitities
    """
    
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
class CityLIstView(generics.ListAPIView):
    """
    Api view to List ALl amenitities
    """
    
    queryset = City.objects.all()
    serializer_class = CitySerializer



class RoomTypeListView(generics.ListAPIView):
    """
    API view to list all room types.
    """
    queryset = RoomType.objects.all()
    serializer_class = RoomTypeSerializer




class BedTypeListView(generics.ListAPIView):
    """
    API view to list all bed types.
    """
    queryset = BedType.objects.all()
    serializer_class = BedTypeSerializer


from accounts.models import Reservation
from accounts.serializers import ReservationSerializer
class ReservationsByMonthView(APIView):
    """
    API view to get reservations by month and status.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        month = request.query_params.get('month')
        year = request.query_params.get('year')

        if not month or not year:
            return Response({'error': 'Month and year are required parameters.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            month = int(month)
            year = int(year)
        except ValueError:
            return Response({'error': 'Month and year must be integers.'}, status=status.HTTP_400_BAD_REQUEST)

        if month < 1 or month > 12:
            return Response({'error': 'Month must be between 1 and 12.'}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare date range for the requested month
        start_date = f'{year}-{month:02d}-01'
        end_date = f'{year}-{month + 1:02d}-01'

        # Fetch reservations with different statuses
        reservations = Reservation.objects.filter(check_in__range=[start_date, end_date])
        data = {
            'confirmed': reservations.filter(reservation_status='Confirmed').values('check_in').annotate(total=Count('id')).order_by('check_in'),
            'upcoming': reservations.filter(reservation_status='Pending').values('check_in').annotate(total=Count('id')).order_by('check_in'),
            'canceled': reservations.filter(reservation_status='Canceled').values('check_in').annotate(total=Count('id')).order_by('check_in'),
        }

        return Response(data, status=status.HTTP_200_OK)    










from django.db.models import Count
class TopVendorsView(APIView):
    """
    API view to get top vendors based on the number of reservations.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        # Query to get vendors with booking counts
        vendors_with_booking_counts = User.objects.filter(is_vendor=True) \
            .annotate(total_bookings=Count('created_rooms__bookings')) \
            .order_by('-total_bookings')[:5]

        serializer = TOPVendorSerializer(
            vendors_with_booking_counts, 
            many=True, 
            context={'request': request}
        )
        print('chart data is :',serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BookingStatusChartView(APIView):
    """
    API view to get booking statuses for chart representation.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        # Aggregate the count of reservations by status
        status_data = Reservation.objects.values('reservation_status').annotate(count=Count('id'))

        # Create a dictionary to hold the counts for each status
        booking_statuses = {
            'Pending': 0,
            'Confirmed': 0,
            'Canceled': 0,
        }

        for item in status_data:
            status = item['reservation_status']
            if status in booking_statuses:
                booking_statuses[status] = item['count']

        return Response(booking_statuses)