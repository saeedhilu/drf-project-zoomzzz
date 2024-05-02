from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Room
from .serializers import RoomSerializer
from rest_framework.exceptions import NotFound
from accounts.constants import *
from accounts.permission import IsActiveUser
class RoomCreateAPIView(APIView):
    """
    This view is used to create a room
    """
    permission_classes = [IsActiveUser]  # Only authenticated users can access

    def post(self, request, format=None):
        if not request.user.is_vendor:  # Check if user is a vendor
            return Response(
                {ERROR_MESSAGE: PERMISSION_DENIED},
                status=status.HTTP_403_FORBIDDEN
                            )
        
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)  # Assign the vendor as the creator of the room
            return Response(
                serializer.data, 
                status=status.HTTP_201_CREATED
                )
        return Response(serializer.errors, 
                        status=status.HTTP_400_BAD_REQUEST
                        )
from accounts.permission import IsVendor
from rest_framework.exceptions import PermissionDenied, NotFound





class RoomDetailAPIView(APIView):
    """
    This view is used to retrieve, update, or delete a room.
    """
    permission_classes = [IsVendor]  # Only vendors can access this view

    def get_object(self, pk):
        try:
            room = Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound(ROOM_NOT_FOUND)

        # Check if the requesting user is the creator of the room
        
        return room

    def get(self, request, pk):
        room = self.get_object(pk)
        serializer = RoomSerializer(room)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        room = self.get_object(pk)

        serializer = RoomSerializer(room, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        room = self.get_object(pk)
        room.delete()
        return Response(
            {MESSAGE    : f'DELETE_SUCCESS {room.name}.'}, 
            status=status.HTTP_204_NO_CONTENT
        )
    
class VendorRoomListAPIView(APIView):
    """
    This view is used to retrieve all rooms listed by the authenticated vendor.
    """
    permission_classes = [IsVendor]  # Only vendors can access this view

    def get(self, request):
        rooms = Room.objects.filter(created_by=request.user)
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)