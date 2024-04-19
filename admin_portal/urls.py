from django.urls import path
from .views import(
    SuperAdminLoginView,
    AddCategoryView,
    AddAmenitiesView,
    AddRoomsTypeView,
    AddBedTypeView,
    AddCityView,
    AddLocationView,
    AddCountry
) 
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('login-admin/', SuperAdminLoginView.as_view(), name='token_obtain_pair'),
    path('category/', AddCategoryView.as_view(), name='add-category'),
    path('category/<int:pk>/', AddCategoryView.as_view(), name='update-delete-category'),
    path('amenities/', AddAmenitiesView.as_view(), name='add-amenities'),
    path('amenities/<int:pk>/', AddAmenitiesView.as_view(), name='update-delete-amenities'),
    path('roomstype/', AddRoomsTypeView.as_view(), name='add-roomstype'),
    path('roomstype/<int:pk>/', AddRoomsTypeView.as_view(), name='update-delete-roomstype'),
    path('bedtype/', AddBedTypeView.as_view(), name='add-bedtype'),
    path('bedtype/<int:pk>/', AddBedTypeView.as_view(), name='update-delete-bedtype'),
    path('cities/', AddCityView.as_view(), name='add-city'),
    path('cities/<int:pk>/', AddCityView.as_view(), name='add-city'),
    path('locations/', AddLocationView.as_view(), name='update-loation'),
    path('locations/<int:pk>/', AddLocationView.as_view(), name='add-location'),
    path('country/', AddCountry.as_view(), name='add-country'),
    path('country/<int:pk>/', AddCountry.as_view(), name='update-update'),
]