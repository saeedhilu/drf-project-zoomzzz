from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import SuperAdminLoginSerializer
from .serializers import *
from rest_framework import permissions
from accounts.constants import PERMISSION_DENIED


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


class IsSuperUser(permissions.BasePermission):
    """
    Custom permission class to allow access only to superusers.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class AbstractCRUDView(APIView):
    """
    Abstract base class for CRUD operations on models with permission checks.
    """
    permission_classes = [IsAuthenticated, IsSuperUser]
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
        if not request.user.is_superuser:
            return Response(
                {"message": PERMISSION_DENIED}, 
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = self.serializer_class(data=request.data)
        print('hekl')
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
        if not request.user.is_superuser:
            return Response(
                {"message": PERMISSION_DENIED}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
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
        if not request.user.is_superuser:
            return Response(
                {"message": PERMISSION_DENIED}, 
                status=status.HTTP_403_FORBIDDEN
            )
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

