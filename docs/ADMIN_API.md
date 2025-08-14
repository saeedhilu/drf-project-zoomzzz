# Admin Portal API Documentation

## Overview

The Admin Portal API provides administrative functionality for managing the room booking platform. It includes endpoints for system configuration, user management, room management, vendor oversight, and analytics. All endpoints require super admin privileges.

## Base URL
```
/ (root paths)
```

## Authentication

All admin endpoints require super admin authentication.

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Permission:** User must have `is_superuser=True` in their profile.

## Admin Authentication

### Super Admin Login
**POST** `/login-admin/`

Authenticate super admin with username and password.

**Request Body:**
```json
{
    "username": "admin",
    "password": "adminpassword123"
}
```

**Response:**
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "username": "admin",
    "profile_image": "/images/user_profile_photo/admin.jpg",
    "is_superadmin": true
}
```

**Example cURL:**
```bash
curl -X POST http://localhost:8000/login-admin/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "adminpassword123"
  }'
```

## Configuration Management

### Category Management

#### List All Categories
**GET** `/category/`

Get all room categories.

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Response:**
```json
[
    {
        "id": 1,
        "name": "Hotel",
        "image": "/images/category_images/hotel.jpg",
        "image_url": "http://127.0.0.1:8000/images/category_images/hotel.jpg",
        "created_by": 1,
        "created_at": "2024-01-01T00:00:00Z"
    },
    {
        "id": 2,
        "name": "Apartment",
        "image": "/images/category_images/apartment.jpg",
        "image_url": "http://127.0.0.1:8000/images/category_images/apartment.jpg",
        "created_by": 1,
        "created_at": "2024-01-02T00:00:00Z"
    }
]
```

#### Create Category
**POST** `/category/`

Create a new room category.

**Headers:**
```
Authorization: Bearer <admin_access_token>
Content-Type: multipart/form-data
```

**Request Body (multipart/form-data):**
```json
{
    "name": "Villa",
    "image": "file_upload"
}
```

**Response:**
```json
{
    "id": 3,
    "name": "Villa",
    "image": "/images/category_images/villa.jpg",
    "image_url": "http://127.0.0.1:8000/images/category_images/villa.jpg",
    "created_by": 1,
    "created_at": "2024-01-03T00:00:00Z"
}
```

#### Update Category
**PATCH** `/category/{category_id}/`

Update an existing category.

**Headers:**
```
Authorization: Bearer <admin_access_token>
Content-Type: multipart/form-data
```

**Request Body (multipart/form-data):**
```json
{
    "name": "Luxury Villa",
    "image": "new_file_upload"
}
```

#### Delete Category
**DELETE** `/category/{category_id}/`

Delete a category.

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Response:**
```json
{
    "message": "Category deleted successfully."
}
```

### Amenity Management

#### List All Amenities
**GET** `/amenity/`

Get all available amenities.

**Response:**
```json
[
    {
        "id": 1,
        "name": "WiFi",
        "image": "/images/amenity_images/wifi.jpg",
        "image_url": "/images/amenity_images/wifi.jpg"
    },
    {
        "id": 2,
        "name": "Air Conditioning",
        "image": "/images/amenity_images/ac.jpg",
        "image_url": "/images/amenity_images/ac.jpg"
    }
]
```

#### Create Amenity
**POST** `/amenity/`

Create a new amenity.

**Headers:**
```
Authorization: Bearer <admin_access_token>
Content-Type: multipart/form-data
```

**Request Body (multipart/form-data):**
```json
{
    "name": "Swimming Pool",
    "image": "file_upload"
}
```

#### Update Amenity
**PATCH** `/amenity/{amenity_id}/`

Update an existing amenity.

#### Delete Amenity
**DELETE** `/amenity/{amenity_id}/`

Delete an amenity.

### Room Type Management

#### List All Room Types
**GET** `/roomstype/`

Get all room types.

**Response:**
```json
[
    {
        "id": 1,
        "name": "Single Room"
    },
    {
        "id": 2,
        "name": "Double Room"
    },
    {
        "id": 3,
        "name": "Suite"
    }
]
```

#### Create Room Type
**POST** `/roomstype/`

Create a new room type.

**Request Body:**
```json
{
    "name": "Presidential Suite"
}
```

#### Update Room Type
**PATCH** `/roomstype/{room_type_id}/`

#### Delete Room Type
**DELETE** `/roomstype/{room_type_id}/`

### Bed Type Management

#### List All Bed Types
**GET** `/bedtype/`

Get all bed types.

**Response:**
```json
[
    {
        "id": 1,
        "name": "Single Bed"
    },
    {
        "id": 2,
        "name": "Double Bed"
    },
    {
        "id": 3,
        "name": "King Size Bed"
    }
]
```

#### Create Bed Type
**POST** `/bedtype/`

Create a new bed type.

**Request Body:**
```json
{
    "name": "Queen Size Bed"
}
```

#### Update Bed Type
**PATCH** `/bedtype/{bed_type_id}/`

#### Delete Bed Type
**DELETE** `/bedtype/{bed_type_id}/`

### Location Management

#### List All Cities
**GET** `/cities/`

Get all cities.

**Response:**
```json
[
    {
        "id": 1,
        "name": "Mumbai"
    },
    {
        "id": 2,
        "name": "Delhi"
    },
    {
        "id": 3,
        "name": "Bangalore"
    }
]
```

#### Create City
**POST** `/cities/`

Create a new city.

**Request Body:**
```json
{
    "name": "Chennai"
}
```

#### Update City
**PATCH** `/cities/{city_id}/`

#### Delete City
**DELETE** `/cities/{city_id}/`

#### List All Countries
**GET** `/country/`

Get all countries.

**Response:**
```json
[
    {
        "id": 1,
        "name": "India"
    },
    {
        "id": 2,
        "name": "United States"
    }
]
```

#### Create Country
**POST** `/country/`

Create a new country.

**Request Body:**
```json
{
    "name": "Canada"
}
```

#### List All Locations
**GET** `/locations/`

Get all locations.

**Response:**
```json
[
    {
        "id": 1,
        "name": "Mumbai Central",
        "city": 1,
        "country": 1
    },
    {
        "id": 2,
        "name": "Delhi Airport",
        "city": 2,
        "country": 1
    }
]
```

#### Create Location
**POST** `/locations/`

Create a new location.

**Request Body:**
```json
{
    "name": "Bangalore Tech Park",
    "city": 3,
    "country": 1
}
```

## Room Management

### List All Rooms
**GET** `/all-room-listing/`

Get all rooms in the system with details.

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Query Parameters:**
- `search`: Search by room name or location
- `category`: Filter by category ID
- `vendor`: Filter by vendor ID
- `status`: Filter by availability status
- `page`: Page number for pagination

**Response:**
```json
{
    "count": 150,
    "next": "http://localhost:8000/all-room-listing/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Luxury Ocean View Suite",
            "location": {
                "name": "Mumbai Central",
                "city": "Mumbai",
                "country": "India"
            },
            "category": {
                "id": 1,
                "name": "Hotel"
            },
            "price_per_night": "8500.00",
            "max_occupancy": 4,
            "availability": true,
            "created_by": {
                "id": 2,
                "username": "vendor1",
                "email": "vendor1@example.com"
            },
            "average_rating": 4.5,
            "total_bookings": 25,
            "created_at": "2024-01-01T00:00:00Z"
        }
    ]
}
```

## User Management

### List All Users
**GET** `/Users-listing/`

Get all registered users (customers and vendors).

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Query Parameters:**
- `user_type`: Filter by user type (customer, vendor, all)
- `status`: Filter by active status (active, inactive, all)
- `search`: Search by name, email, or username
- `date_joined_from`: Filter users registered from date
- `date_joined_to`: Filter users registered to date
- `page`: Page number for pagination

**Response:**
```json
{
    "count": 500,
    "next": "http://localhost:8000/Users-listing/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "username": "john_doe",
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone_number": "+919876543210",
            "is_vendor": false,
            "is_active": true,
            "date_joined": "2024-01-01T00:00:00Z",
            "last_login": "2024-01-15T10:30:00Z",
            "total_bookings": 5,
            "total_spent": "25000.00"
        },
        {
            "id": 2,
            "username": "vendor1",
            "email": "vendor1@example.com",
            "first_name": "Vendor",
            "last_name": "One",
            "phone_number": "+919876543211",
            "is_vendor": true,
            "is_active": true,
            "date_joined": "2024-01-02T00:00:00Z",
            "total_rooms": 8,
            "total_revenue": "150000.00"
        }
    ]
}
```

### Block/Unblock User
**PATCH** `/users/{user_id}/block-unblock/`

Block or unblock a user account.

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Request Body:**
```json
{
    "is_active": false,
    "reason": "Violation of terms of service"
}
```

**Response:**
```json
{
    "message": "User blocked successfully",
    "user": {
        "id": 1,
        "username": "john_doe",
        "is_active": false,
        "blocked_at": "2024-01-20T15:30:00Z",
        "blocked_reason": "Violation of terms of service"
    }
}
```

### List All Vendors
**GET** `/all-vendors/`

Get all registered vendors with their performance metrics.

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Response:**
```json
[
    {
        "id": 2,
        "username": "vendor1",
        "email": "vendor1@example.com",
        "first_name": "Vendor",
        "last_name": "One",
        "phone_number": "+919876543211",
        "is_active": true,
        "date_joined": "2024-01-02T00:00:00Z",
        "total_rooms": 8,
        "total_bookings": 45,
        "total_revenue": "150000.00",
        "average_rating": 4.3,
        "commission_earned": "15000.00",
        "last_room_added": "2024-01-15T00:00:00Z"
    }
]
```

## Banner Management

### List All Banners
**GET** `/banners/`

Get all promotional banners.

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Response:**
```json
[
    {
        "id": 1,
        "title": "Summer Sale",
        "description": "Get 20% off on all bookings",
        "image": "/images/banners/summer_sale.jpg",
        "is_active": true,
        "start_date": "2024-06-01",
        "end_date": "2024-08-31",
        "created_at": "2024-05-15T00:00:00Z"
    }
]
```

### Create Banner
**POST** `/banners/`

Create a new promotional banner.

**Headers:**
```
Authorization: Bearer <admin_access_token>
Content-Type: multipart/form-data
```

**Request Body (multipart/form-data):**
```json
{
    "title": "Winter Special",
    "description": "Enjoy cozy winter stays with 30% discount",
    "image": "file_upload",
    "is_active": true,
    "start_date": "2024-12-01",
    "end_date": "2025-02-28"
}
```

### Update Banner
**PUT** `/banners/{banner_id}/`

Update an existing banner.

### Delete Banner
**DELETE** `/banners/{banner_id}/`

Delete a banner.

## Analytics and Reports

### Booking Statistics by Month
**GET** `/booking-sts/`

Get booking statistics grouped by month.

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Query Parameters:**
- `year`: Filter by specific year (default: current year)
- `vendor_id`: Filter by specific vendor

**Response:**
```json
{
    "booking_stats": [
        {
            "month": "2024-01",
            "total_bookings": 120,
            "confirmed_bookings": 105,
            "pending_bookings": 8,
            "canceled_bookings": 7,
            "total_revenue": "500000.00",
            "commission_earned": "50000.00"
        },
        {
            "month": "2024-02",
            "total_bookings": 145,
            "confirmed_bookings": 130,
            "pending_bookings": 10,
            "canceled_bookings": 5,
            "total_revenue": "650000.00",
            "commission_earned": "65000.00"
        }
    ],
    "yearly_summary": {
        "total_bookings": 1200,
        "total_revenue": "5500000.00",
        "total_commission": "550000.00",
        "average_monthly_bookings": 100,
        "growth_rate": 12.5
    }
}
```

### Top Vendors
**GET** `/top-vendors/`

Get top-performing vendors based on various metrics.

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Query Parameters:**
- `metric`: Sort by metric (revenue, bookings, rating, rooms)
- `period`: Time period (month, quarter, year, all_time)
- `limit`: Number of vendors to return (default: 10)

**Response:**
```json
[
    {
        "vendor": {
            "id": 2,
            "username": "vendor1",
            "first_name": "Vendor",
            "last_name": "One",
            "email": "vendor1@example.com"
        },
        "total_revenue": "250000.00",
        "total_bookings": 85,
        "total_rooms": 12,
        "average_rating": 4.7,
        "commission_earned": "25000.00",
        "rank": 1
    },
    {
        "vendor": {
            "id": 3,
            "username": "vendor2",
            "first_name": "Vendor",
            "last_name": "Two",
            "email": "vendor2@example.com"
        },
        "total_revenue": "180000.00",
        "total_bookings": 62,
        "total_rooms": 8,
        "average_rating": 4.4,
        "commission_earned": "18000.00",
        "rank": 2
    }
]
```

### Booking Status Chart
**GET** `/booking-status-chart/`

Get booking status distribution for charts and visualizations.

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Query Parameters:**
- `period`: Time period (week, month, quarter, year)
- `start_date`: Start date for custom period
- `end_date`: End date for custom period

**Response:**
```json
{
    "chart_data": {
        "labels": ["Confirmed", "Pending", "Canceled"],
        "data": [850, 45, 25],
        "colors": ["#28a745", "#ffc107", "#dc3545"],
        "percentages": [92.4, 4.9, 2.7]
    },
    "summary": {
        "total_bookings": 920,
        "confirmed_rate": 92.4,
        "cancellation_rate": 2.7,
        "pending_rate": 4.9
    },
    "trends": {
        "confirmed_growth": 5.2,
        "cancellation_change": -1.1,
        "booking_volume_change": 8.7
    }
}
```

## List Endpoints (Cached)

### Get Categories List
**GET** `/categories/`

Get cached list of all categories.

### Get Countries List
**GET** `/countries/`

Get cached list of all countries.

### Get Cities List
**GET** `/city/`

Get cached list of all cities.

### Get Amenities List
**GET** `/amenities/`

Get cached list of all amenities.

### Get Room Types List
**GET** `/room-types/`

Get cached list of all room types.

### Get Bed Types List
**GET** `/bed-types/`

Get cached list of all bed types.

## Data Models

### Banner Model
```python
class Banner(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='banners/')
    is_active = models.BooleanField(default=True)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
```

## Serializers

### SuperAdminLoginSerializer
For admin authentication.

**Fields:**
- `username`: Admin username (required)
- `password`: Admin password (required, write-only)

### CategorySerializer
For category management.

**Fields:**
- `id`: Category ID (read-only)
- `name`: Category name (required, unique)
- `image`: Category image
- `image_url`: Full image URL (read-only)
- `created_by`: Creator user ID (read-only)
- `created_at`: Creation timestamp (read-only)

### AmenitySerializer
For amenity management.

**Fields:**
- `id`: Amenity ID (read-only)
- `name`: Amenity name (required, unique)
- `image`: Amenity image
- `image_url`: Full image URL (read-only)

### UserBlockUnblockSerializer
For user management.

**Fields:**
- `is_active`: User active status
- `reason`: Reason for blocking (optional)

## Error Handling

### Common Error Responses

#### 400 Bad Request - Validation Error
```json
{
    "name": ["Category with this name already exists."],
    "image": ["Invalid image format."]
}
```

#### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

#### 403 Forbidden - Not Super Admin
```json
{
    "detail": "You do not have permission to perform this action."
}
```

#### 404 Not Found
```json
{
    "detail": "Object not found."
}
```

## Caching Strategy

The admin portal implements caching for frequently accessed data:

- **Category List**: Cached for 1 hour
- **Amenity List**: Cached for 1 hour
- **Location Data**: Cached for 2 hours
- **User Statistics**: Cached for 30 minutes
- **Dashboard Metrics**: Cached for 15 minutes

Cache keys follow the pattern: `{model_name}_list`

Cache is automatically invalidated when:
- New items are created
- Existing items are updated
- Items are deleted

## Permissions and Security

### Permission Classes
- `IsSuperUser`: Requires `is_superuser=True`
- `IsAuthenticatedUser`: Requires valid authentication
- `IsAdminUser`: Django's built-in admin permission

### Security Features
1. **Authentication Required**: All endpoints require super admin tokens
2. **Input Validation**: All input fields are validated and sanitized
3. **File Upload Security**: Images are validated for type and size
4. **Audit Logging**: Admin actions are logged for security
5. **Rate Limiting**: API calls are rate-limited to prevent abuse

## Integration with Other Apps

### With Accounts App
- User management and blocking functionality
- Booking statistics and user analytics
- Commission and payment tracking

### With Rooms App
- Room category and amenity management
- Room type and bed type configuration
- Location and city management

### With Vendor Management
- Vendor performance monitoring
- Vendor approval and management
- Revenue and commission tracking

## Real-time Features

Admin dashboard supports real-time updates for:
- New user registrations
- New vendor applications
- Booking notifications
- System alerts and errors

WebSocket endpoint: `ws://localhost:8000/ws/admin/`

## Export and Reporting

Admins can export data in various formats:
- **CSV Reports**: Users, bookings, vendors, revenue
- **PDF Reports**: Monthly summaries, vendor performance
- **Excel Reports**: Detailed analytics with charts
- **JSON API**: For custom integrations and dashboards