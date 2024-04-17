from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Room


class RoomListAPIView(APIView):
    def get(self, request):
        rooms = Room.objects.all()  # Retrieve all rooms
        serializer = RoomSerializer(rooms, many=True)  # Serialize all rooms
        return Response(serializer.data, status=status.HTTP_200_OK)

class RoomDetailAPIView(APIView):
    def get(self, request, pk):
        try:
            room = Room.objects.get(pk=pk)  # Retrieve room by primary key
        except Room.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = RoomSerializer(room)  # Serialize the retrieved room
        return Response(serializer.data, status=status.HTTP_200_OK)





from .models import Room
from .serializers import RoomSerializer



from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Room


class RoomCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can access

    def post(self, request, format=None):
        if not request.user.is_vendor:  # Check if user is a vendor
            return Response({'error': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)  # Assign the vendor as the creator of the room
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
