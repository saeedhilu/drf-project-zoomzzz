from django.urls import path
from .views import RoomCreateAPIView  # Replace with your view class name

urlpatterns = [
    
    path('add-rooms/', RoomCreateAPIView.as_view(), name='add-rooms'),
]
