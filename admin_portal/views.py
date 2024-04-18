from .serializers import SuperAdminLoginSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated


class SuperAdminLoginView(APIView):


    
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
                    'username':username
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



"""
For Adding Catogory ,aminities  and 
"""

from .serializers import *

class AddCatogoryView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': f'successfully added {request.data.get("name", "")} Category'}, status=status.HTTP_201_CREATED)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddAminitiesView(APIView):
    permission_classes = [IsAuthenticated] 
    def post(self, request):
        serializers  = AmenitySerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response({'message': f'successfully added {request.data.get("name", "")} Aminity'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
class AddRoomsType(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        if not request.user.is_superuser:
            return Response({"meassage":'You do not have permission to perform this action.'},status=status.HTTP_403_FORBIDDEN)
        serializers = RoomTypeSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response({'message': f'successfully added {request.data.get("name", "")} Room Type'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)
class AddBedType(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        if not request.user.is_superuser:
            return Response({"message   ":'You do not have permission to perform this action.'},status=status.HTTP_403_FORBIDDEN)
        serializers = BedTypeSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response({'message': f'successfully added {request.data.get("name", "")} Bed Type'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)
