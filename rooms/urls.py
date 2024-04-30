from django.urls import path
from .views import RoomCreateAPIView, RoomDetailAPIView,VendorRoomListAPIView

urlpatterns = [
    path('create/', RoomCreateAPIView.as_view(), name='room-create'),
    path('rooms/edit/<int:pk>/', RoomDetailAPIView.as_view(), name='room-detail'),
    path('vendor/rooms/', VendorRoomListAPIView.as_view(), name='vendor-room-list')
]
