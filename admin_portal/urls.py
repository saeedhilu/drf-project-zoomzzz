from django.urls import path
from .views import(
    SuperAdminLoginView,
    AddCategoryView,
    AddAmenitiesView,
    AddRoomsTypeView,
    AddBedTypeView,
    AddCityView,
    AddLocationView,
    AddCountry,
    AdminRoomListingView,
    UserDetailaView,
    UserBlockUnblockView,
    VebdorsListView,
    BannerListCreateView,
    BannerDetailView,

    
    ReservationsByMonthView,
    BookingStatusChartView,
    TopVendorsView,
) 
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    # Login
    path('login-admin/', SuperAdminLoginView.as_view(), name='token_obtain_pair'),

    # Catogary
    path('category/', AddCategoryView.as_view(), name='add-category'),
    path('category/<int:pk>/', AddCategoryView.as_view(), name='update-delete-category'),


    # Aminity
    path('amenity/', AddAmenitiesView.as_view(), name='add-amenities'),
    path('amenity/<int:pk>/', AddAmenitiesView.as_view(), name='update-delete-amenities'),

    # RoomType
    path('roomstype/', AddRoomsTypeView.as_view(), name='add-roomstype'),
    path('roomstype/<int:pk>/', AddRoomsTypeView.as_view(), name='update-delete-roomstype'),

    # BedType
    path('bedtype/', AddBedTypeView.as_view(), name='add-bedtype'),
    path('bedtype/<int:pk>/', AddBedTypeView.as_view(), name='update-delete-bedtype'),

    # Cities
    path('cities/', AddCityView.as_view(), name='add-city'),
    path('cities/<int:pk>/', AddCityView.as_view(), name='add-city'),



    # Location
    path('locations/', AddLocationView.as_view(), name='update-loation'),
    path('locations/<int:pk>/', AddLocationView.as_view(), name='add-location'),



    # Country
    path('country/', AddCountry.as_view(), name='add-country'),
    path('country/<int:pk>/', AddCountry.as_view(), name='update-update'),



    path('s/', AddBanner.as_view(), name='s'),
    path('s/<int:pk>/', AddBanner.as_view(), name='s'),




    # admin dashboard
    path('all-room-listing/',AdminRoomListingView.as_view(),name='admin-dashboard-roomlisting'),

    path('Users-listing/',UserDetailaView.as_view(),name='All Users Details'),

    path('users/<int:pk>/block-unblock/', UserBlockUnblockView.as_view(), name='user-block-unblock'),
    
    path('all-vendors/', VebdorsListView.as_view(), name='Listing alll vendors list'),

    # Banner Management
    path('banners/<int:pk>/', BannerDetailView.as_view(), name='banner-detail'),




    path('categories/', CategoryListView.as_view(), name='category-list'),
    
    path('countries/', CountryListView.as_view(), name='country-list'),

    path('city/', CityLIstView.as_view(), name='city-list'),

    path('amenities/', AmenityListView.as_view(), name='amenity-list'),

    
    path('room-types/', RoomTypeListView.as_view(), name='room-type-list'),
    
    path('bed-types/', BedTypeListView.as_view(), name='bed-type-list'),

    path('banners/', BannerListCreateView.as_view(), name='banner-list-create'),
    
    # For admin statis
    # -------------------



    
    path('booking-sts/', ReservationsByMonthView.as_view(), name='reservations-by-month'),
    path('top-vendors/', TopVendorsView.as_view(), name='top-vendors-list'),
    path('booking-status-chart/', BookingStatusChartView.as_view(), name='booking-status-chart'),

]
    
