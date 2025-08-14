# Accounts API Documentation

## Overview

The Accounts API handles user authentication, profile management, room bookings, wishlists, ratings, and user-related operations. It supports both traditional OTP-based authentication and Google OAuth integration.

## Base URL
```
/accounts/
```

## Models

### User Model
The custom user model extends Django's AbstractBaseUser and supports multiple user types.

```python
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    username = models.CharField(max_length=50, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    is_vendor = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='user_profile_photo', null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
```

**Properties:**
- `tokens`: Returns JWT access and refresh tokens
- `get_full_name`: Returns concatenated first and last name

### OTP Model
Handles OTP verification for phone number authentication.

```python
class OTP(models.Model):
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True)
    otp_code = models.CharField(max_length=6)
    otp_expiry = models.DateTimeField(default=default_expiry)  # 5 minutes from creation
    password = models.CharField(max_length=128, null=True, blank=True)
```

### Reservation Model
Manages room bookings and reservations.

```python
class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()
    total_guest = models.IntegerField()
    reservation_status = models.CharField(max_length=10, choices=RESERVATION_STATUS_CHOICES, default='Pending')
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    email = models.EmailField()
    contact_number = models.CharField(max_length=15)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Status Choices:**
- `Pending`: Default status for new reservations
- `Confirmed`: Confirmed booking
- `Canceled`: Canceled booking

### WishList Model
Manages user's favorite rooms.

```python
class WishList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Rating Model
Handles room ratings and feedback.

```python
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField()  # 1-5 rating scale
    feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'room')  # One rating per user per room
```

## Authentication Endpoints

### Google Sign-In
**POST** `/accounts/google/auth/`

Authenticate users using Google OAuth tokens.

**Request Body:**
```json
{
    "access_token": "google_oauth_access_token"
}
```

**Response:**
```json
{
    "access": "jwt_access_token",
    "refresh": "jwt_refresh_token",
    "user": {
        "id": 1,
        "username": "user@example.com",
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe"
    }
}
```

**Example cURL:**
```bash
curl -X POST http://localhost:8000/accounts/google/auth/ \
  -H "Content-Type: application/json" \
  -d '{"access_token": "ya29.a0AfH6SMA..."}'
```

### Generate OTP
**POST** `/accounts/generate-ph-otp/`

Generate and send OTP to phone number for authentication.

**Request Body:**
```json
{
    "phone_number": "+919876543210"
}
```

**Response:**
```json
{
    "message": "OTP sent successfully"
}
```

**Error Responses:**
```json
{
    "error_message": "Failed to send OTP"
}
```

### Verify OTP
**POST** `/accounts/verify-ph-otp/`

Verify OTP and create/authenticate user.

**Request Body:**
```json
{
    "phone_number": "+919876543210",
    "otp": "123456"
}
```

**Response:**
```json
{
    "message": "OTP verified successfully",
    "access": "jwt_access_token",
    "refresh": "jwt_refresh_token",
    "user": {
        "id": 1,
        "phone_number": "+919876543210",
        "username": "user123"
    }
}
```

### Resend OTP
**POST** `/accounts/resend-otp/`

Resend OTP to the phone number.

**Request Body:**
```json
{
    "phone_number": "+919876543210"
}
```

### Token Refresh
**POST** `/accounts/api/token/refresh/`

Refresh JWT access token using refresh token.

**Request Body:**
```json
{
    "refresh": "refresh_token"
}
```

**Response:**
```json
{
    "access": "new_access_token"
}
```

## User Profile Endpoints

### Update User Profile
**PUT** `/accounts/user/update/`

Update authenticated user's profile information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body (multipart/form-data):**
```json
{
    "username": "newusername",
    "email": "newemail@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "image": "file_upload"
}
```

**Response:**
```json
{
    "id": 1,
    "username": "newusername",
    "email": "newemail@example.com",
    "phone_number": "+919876543210",
    "image": "/images/user_profile_photo/profile.jpg",
    "is_active": true,
    "date_joined": "2024-01-01T00:00:00Z",
    "is_superuser": false,
    "is_vendor": false
}
```

### Change Phone Number
**POST** `/accounts/phone-number/update/`

Initiate phone number change process.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "new_phone_number": "+919876543211"
}
```

### Verify Phone Number Change
**POST** `/accounts/verify-otp/update/`

Verify OTP for phone number change.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "new_phone_number": "+919876543211",
    "otp": "123456"
}
```

## Room and Search Endpoints

### Search Rooms
**GET** `/accounts/room-search/`

Search and filter rooms with various criteria.

**Query Parameters:**
- `location`: Filter by location name
- `category`: Filter by category ID
- `check_in`: Check-in date (YYYY-MM-DD)
- `check_out`: Check-out date (YYYY-MM-DD)
- `guests`: Number of guests
- `min_price`: Minimum price per night
- `max_price`: Maximum price per night
- `amenities`: Amenity IDs (comma-separated)
- `room_type`: Room type ID
- `bed_type`: Bed type ID
- `search`: General search term
- `page`: Page number for pagination
- `page_size`: Number of results per page

**Example Request:**
```
GET /accounts/room-search/?location=mumbai&check_in=2024-02-01&check_out=2024-02-03&guests=2&page=1
```

**Response:**
```json
{
    "count": 50,
    "next": "http://localhost:8000/accounts/room-search/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Luxury Suite",
            "location": {
                "id": 1,
                "name": "Mumbai Central",
                "city": "Mumbai",
                "country": "India"
            },
            "price_per_night": "5000.00",
            "max_occupancy": 4,
            "image": "/images/room_images/suite1.jpg",
            "amenities": [
                {"id": 1, "name": "WiFi"},
                {"id": 2, "name": "AC"}
            ],
            "average_rating": 4.5,
            "availability": true
        }
    ]
}
```

### Get All Rooms
**GET** `/accounts/all-rooms/`

Get all available rooms with pagination.

**Response:** Same structure as room search

### Get Room Detail
**GET** `/accounts/room-detail/{room_id}/`

Get detailed information about a specific room.

**Response:**
```json
{
    "id": 1,
    "name": "Luxury Suite",
    "description": "A beautiful luxury suite with ocean view",
    "location": {
        "id": 1,
        "name": "Mumbai Central",
        "city": "Mumbai",
        "country": "India"
    },
    "category": {
        "id": 1,
        "name": "Hotel"
    },
    "price_per_night": "5000.00",
    "max_occupancy": 4,
    "google_map_url": "https://maps.google.com/...",
    "image": "/images/room_images/suite1.jpg",
    "image2": "/images/room_images/suite1_2.jpg",
    "image3": "/images/room_images/suite1_3.jpg",
    "image4": "/images/room_images/suite1_4.jpg",
    "image5": "/images/room_images/suite1_5.jpg",
    "availability": true,
    "pet_allowed": true,
    "room_type": {
        "id": 1,
        "name": "Suite"
    },
    "bed_type": {
        "id": 1,
        "name": "King Size"
    },
    "amenities": [
        {
            "id": 1,
            "name": "WiFi",
            "image": "/images/amenity_images/wifi.jpg"
        }
    ],
    "average_rating": 4.5,
    "created_at": "2024-01-01T00:00:00Z"
}
```

## Wishlist Endpoints

### Get User Wishlists
**GET** `/accounts/wishlists/`

Get all rooms in user's wishlist.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
[
    {
        "id": 1,
        "room": {
            "id": 1,
            "name": "Luxury Suite",
            "price_per_night": "5000.00",
            "image": "/images/room_images/suite1.jpg"
        },
        "created_at": "2024-01-01T00:00:00Z"
    }
]
```

### Add to Wishlist
**POST** `/accounts/wishlists/`

Add a room to user's wishlist.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "room_id": 1
}
```

### Remove from Wishlist
**DELETE** `/accounts/wishlists/{wishlist_id}/`

Remove a room from user's wishlist.

**Headers:**
```
Authorization: Bearer <access_token>
```

## Booking Endpoints

### Create Reservation
**POST** `/accounts/reservations/{room_id}/`

Create a new room reservation.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "check_in": "2024-02-01",
    "check_out": "2024-02-03",
    "total_guest": 2,
    "email": "user@example.com",
    "contact_number": "+919876543210",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Response:**
```json
{
    "id": 1,
    "room": {
        "id": 1,
        "name": "Luxury Suite"
    },
    "check_in": "2024-02-01",
    "check_out": "2024-02-03",
    "total_guest": 2,
    "reservation_status": "Pending",
    "amount": "10000.00",
    "email": "user@example.com",
    "contact_number": "+919876543210",
    "first_name": "John",
    "last_name": "Doe",
    "created_at": "2024-01-01T00:00:00Z"
}
```

### Cancel Reservation
**PATCH** `/accounts/reservations/canellation/{reservation_id}/`

Cancel a reservation.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
    "message": "Reservation cancelled successfully"
}
```

### Get User Reservations by Status

#### Canceled Reservations
**GET** `/accounts/canceled-rooms/`

#### Confirmed Reservations
**GET** `/accounts/confirmed-rooms/`

#### Pending Reservations
**GET** `/accounts/pending-rooms/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response Structure:**
```json
[
    {
        "id": 1,
        "room": {
            "id": 1,
            "name": "Luxury Suite",
            "image": "/images/room_images/suite1.jpg"
        },
        "check_in": "2024-02-01",
        "check_out": "2024-02-03",
        "total_guest": 2,
        "reservation_status": "Confirmed",
        "amount": "10000.00",
        "created_at": "2024-01-01T00:00:00Z"
    }
]
```

## Payment Endpoints

### Initiate Payment
**POST** `/accounts/initiate_payment/`

Initiate Razorpay payment for a reservation.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "reservation_id": 1,
    "amount": 10000
}
```

**Response:**
```json
{
    "order_id": "order_razorpay_id",
    "amount": 10000,
    "currency": "INR",
    "key": "razorpay_key_id"
}
```

## Rating Endpoints

### Create Rating
**POST** `/accounts/rooms/{room_id}/ratings/create/`

Create a rating for a room.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "rating": 5,
    "feedback": "Excellent room with great amenities!"
}
```

**Response:**
```json
{
    "id": 1,
    "user": {
        "id": 1,
        "username": "user123"
    },
    "room": {
        "id": 1,
        "name": "Luxury Suite"
    },
    "rating": 5,
    "feedback": "Excellent room with great amenities!",
    "created_at": "2024-01-01T00:00:00Z"
}
```

### Update Rating
**PUT** `/accounts/rooms/{room_id}/ratings/{rating_id}/`

Update an existing rating.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "rating": 4,
    "feedback": "Good room, but could be better"
}
```

### Delete Rating
**DELETE** `/accounts/rooms/{room_id}/ratings/{rating_id}/`

Delete a rating.

**Headers:**
```
Authorization: Bearer <access_token>
```

## Statistics Endpoints

### Top Rated Rooms
**GET** `/accounts/rooms/top-rated/`

Get top-rated rooms based on average ratings.

**Response:**
```json
[
    {
        "id": 1,
        "name": "Luxury Suite",
        "average_rating": 4.8,
        "price_per_night": "5000.00",
        "image": "/images/room_images/suite1.jpg",
        "location": "Mumbai Central"
    }
]
```

### User Summary Statistics
**GET** `/accounts/summary-statistics/`

Get user's booking and activity statistics.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
    "total_bookings": 10,
    "confirmed_bookings": 8,
    "pending_bookings": 1,
    "canceled_bookings": 1,
    "total_spent": "50000.00",
    "favorite_location": "Mumbai",
    "total_ratings": 5
}
```

## Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
    "error_message": "Invalid input data"
}
```

#### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

#### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

#### 404 Not Found
```json
{
    "detail": "Not found."
}
```

#### 500 Internal Server Error
```json
{
    "error_message": "Internal server error"
}
```

## Pagination

Most list endpoints support pagination with the following parameters:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 10, max: 100)

Paginated responses include:
```json
{
    "count": 100,
    "next": "http://localhost:8000/accounts/endpoint/?page=3",
    "previous": "http://localhost:8000/accounts/endpoint/?page=1",
    "results": []
}
```

## Rate Limiting

OTP generation and sending operations are rate-limited to prevent abuse:
- Maximum 3 OTP requests per phone number per hour
- OTP expires after 5 minutes

## Security Notes

1. All authenticated endpoints require valid JWT tokens
2. OTP codes are 6 digits and expire after 5 minutes
3. Phone numbers must include country code
4. Google OAuth tokens are validated against Google's servers
5. Passwords are hashed using Django's built-in password hashers
6. User sessions are database-backed for security