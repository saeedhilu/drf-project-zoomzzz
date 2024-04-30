from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
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
from accounts.serializers import UserProfileEditSerializer
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
            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.is_superuser:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh),
                    'username': username
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'Invalid credentials'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
        else:
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )





class AbstractCRUDView(APIView):
    """
    Abstract base class for CRUD operations on models with permission checks.
    """
    permission_classes = [ IsSuperUser]
    model = None  # To be defined by subclasses
    serializer_class = None  # To be defined by subclasses

    def get_object(self, pk):
        try:
            return self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        obj = self.get_object(pk)
        serializer = self.serializer_class(obj)
        return Response(serializer.data)

    def post(self, request):
        
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': f'successfully added {request.data.get("name", "")} {self.model._meta.verbose_name}'},
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )

    def put(self, request, pk):
        
        
        obj = self.get_object(pk)
        serializer = self.serializer_class(
            obj, data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': f'successfully updated {request.data.get("name", "")} {self.model._meta.verbose_name}'},
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        
        obj = self.get_object(pk)
        obj.delete()
        return Response(
            {'message': f'successfully deleted {self.model._meta.verbose_name}'}, 
            status=status.HTTP_204_NO_CONTENT
        )


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



# ########################

class AdminRoomListingView(generics.ListAPIView):

    
    """
    API view to list all rooms efficiently for the admin dashboard, with summary statistics.
    """
    queryset = cache_queryset(
        'allrooms',
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
        

        summary_statistics = get_summary_statistics()
        
        
        custom_response_data = {

            'summary_statistics': summary_statistics,
            'rooms': response.data,
        }
        
        
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
        queryset_cache_key = 'vendor_queryset'
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
        queryset_cache_key = 'user_queryset'
        queryset = cache.get(queryset_cache_key)

        if queryset is None:
            queryset = User.objects.all()
            cache.set(queryset_cache_key, queryset, timeout=300)  # Cache for 5 minutes

        return queryset
    
class UserBlockUnblockView(generics.GenericAPIView):
    serializer_class = UserProfileEditSerializer
    permission_classes = [IsSuperUser]  # Only allow access to admin users

    def post(self, request, pk):
        # Get the user object based on the provided primary key (user ID)
        user = get_object_or_404(User, pk=pk)

        
        is_active = user.is_active
        print(user)

        # Toggle the is_active field (block/unblock the user)
        user.is_active = not is_active
        user.save(update_fields=['is_active'])

        # Return the updated user data
        serializer = self.serializer_class(user)
        if not is_active:
            message = UNBLOCK_SUCCESS
        else:
            message = BLOCK_SUCCESS

        return Response({
            'message': message,
            'user': serializer.data
        }, status=status.HTTP_200_OK)



