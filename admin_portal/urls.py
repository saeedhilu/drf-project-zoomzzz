from django.urls import path
from .views import(
    SuperAdminLoginView,
    AddCatogoryView,
    AddAminitiesView,
    AddRoomsType,
    AddBedType,
    SuperAdminLoginView
) 
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('login-admin/', SuperAdminLoginView.as_view(), name='token_obtain_pair'),
    path('category/', AddCatogoryView.as_view(), name='add-category'),
    path('amenities/', AddAminitiesView.as_view(), name='add-amenities'),
    path('roomstype/', AddRoomsType.as_view(), name='add-rooms'),
    path('bedtype/', AddBedType.as_view(), name='add-bed-type'),
    
]