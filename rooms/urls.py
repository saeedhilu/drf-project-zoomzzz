from django.urls import path
from .views import RoomCreateAPIView, RoomDetailAPIView

urlpatterns = [
    path('create/', RoomCreateAPIView.as_view(), name='room-create'),
    path('rooms/edit/<int:pk>/', RoomDetailAPIView.as_view(), name='room-detail'),
]
