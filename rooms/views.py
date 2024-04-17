from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Room
from .serializers import RoomSerializer,RoomUpdateSerializer
from rest_framework.exceptions import NotFound
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

class       RoomDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can access

    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound("Room not found")

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

        # Check permission (modify this as needed)
        if not request.user.is_vendor :
            return Response({'error': 'You do not have permission to delete this room.'}, status=status.HTTP_403_FORBIDDEN)

        room.delete()
        return Response({'message': f'Successfully deleted {room.name}.'}, status=status.HTTP_204_NO_CONTENT)
