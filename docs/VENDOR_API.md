# Vendor Management API Documentation

## Overview

The Vendor Management API handles vendor registration, authentication, profile management, and vendor-specific dashboard operations. It provides vendors with tools to manage their account, view bookings, track earnings, and access analytics.

## Base URL
```
/vendor/
```

## Authentication

Vendor endpoints require authentication with JWT tokens. Users must have `is_vendor=True` in their profile.

**Headers:**
```
Authorization: Bearer <access_token>
```

## Registration and Authentication Endpoints

### Vendor Signup
**POST** `/vendor/signup-vendor/`

Register a new vendor account with email verification.

**Request Body:**
```json
{
    "first_name": "John",
    "last_name": "Doe",
    "email": "vendor@example.com",
    "phone_number": "+919876543210",
    "password": "securepassword123",
    "confirm_password": "securepassword123"
}
```

**Validation Rules:**
- Email must be unique and valid
- Phone number must include country code
- Password and confirm_password must match
- Password must meet Django's password validation requirements

**Response:**
```json
{
    "message": "OTP sent to your email address"
}
```

**Example cURL:**
```bash
curl -X POST http://localhost:8000/vendor/signup-vendor/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "vendor@example.com",
    "phone_number": "+919876543210",
    "password": "securepassword123",
    "confirm_password": "securepassword123"
  }'
```

### Verify Email OTP
**POST** `/vendor/verify-email-otp/`

Verify the OTP sent to email and complete vendor registration.

**Request Body:**
```json
{
    "email": "vendor@example.com",
    "otp": "123456",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+919876543210"
}
```

**Response:**
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token_expiry": "2024-02-08T00:00:00.000Z",
    "user": {
        "username": "vendor",
        "id": 1,
        "email": "vendor@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+919876543210"
    },
    "message": "Signup successful"
}
```

### Resend Email OTP
**POST** `/vendor/resend-otp/`

Resend OTP to email address if the previous one expired.

**Request Body:**
```json
{
    "data": "vendor@example.com"
}
```

**Response:**
```json
{
    "message": "OTP resent successfully"
}
```

### Vendor Login
**POST** `/vendor/login/`

Authenticate vendor with email and password.

**Request Body:**
```json
{
    "email": "vendor@example.com",
    "password": "securepassword123"
}
```

**Response:**
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "username": "vendor",
        "email": "vendor@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "is_vendor": true,
        "is_active": true
    },
    "message": "Login successful"
}
```

## Password Management Endpoints

### Forgot Password Email
**POST** `/vendor/forgot-password-email/`

Send password reset link to vendor's email.

**Request Body:**
```json
{
    "email": "vendor@example.com"
}
```

**Response:**
```json
{
    "message": "Password reset link sent to your email"
}
```

### Reset Password with Token
**POST** `/vendor/forgot_password_change/{uidb64}/{token}/`

Reset password using the token from email link.

**URL Parameters:**
- `uidb64`: Base64 encoded user ID
- `token`: Password reset token

**Request Body:**
```json
{
    "new_password": "newsecurepassword123",
    "confirm_password": "newsecurepassword123"
}
```

**Response:**
```json
{
    "message": "Password changed successfully"
}
```

### Change Password (Authenticated)
**POST** `/vendor/change-password/`

Change password for authenticated vendor.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "old_password": "currentsecurepassword123",
    "new_password": "newsecurepassword123",
    "confirm_password": "newsecurepassword123"
}
```

**Response:**
```json
{
    "message": "Password changed successfully"
}
```

## Profile Management Endpoints

### Update Vendor Profile
**PUT** `/vendor/vendor/update/`

Update vendor profile information.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body (multipart/form-data):**
```json
{
    "first_name": "John",
    "last_name": "Smith",
    "phone_number": "+919876543211",
    "image": "file_upload"
}
```

**Response:**
```json
{
    "id": 1,
    "username": "vendor",
    "email": "vendor@example.com",
    "phone_number": "+919876543211",
    "first_name": "John",
    "last_name": "Smith",
    "image": "/images/user_profile_photo/vendor_profile.jpg",
    "is_active": true,
    "date_joined": "2024-01-01T00:00:00Z",
    "is_superuser": false,
    "is_vendor": true
}
```

### Change Email
**POST** `/vendor/change-email/`

Initiate email change process (sends OTP to new email).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "new_email": "newemail@example.com",
    "password": "currentpassword123"
}
```

**Response:**
```json
{
    "message": "OTP sent to new email address"
}
```

### Verify Email Change
**POST** `/vendor/verify-email/`

Verify OTP and complete email change.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "new_email": "newemail@example.com",
    "otp": "123456"
}
```

**Response:**
```json
{
    "message": "Email changed successfully"
}
```

## Dashboard and Analytics Endpoints

### Vendor Dashboard
**GET** `/vendor/vendor-dashboard/`

Get vendor dashboard overview with key metrics.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
    "total_rooms": 15,
    "total_bookings": 45,
    "confirmed_bookings": 40,
    "pending_bookings": 3,
    "canceled_bookings": 2,
    "total_revenue": "125000.00",
    "monthly_revenue": "15000.00",
    "average_rating": 4.2,
    "total_reviews": 38,
    "occupancy_rate": 78.5,
    "recent_bookings": [
        {
            "id": 1,
            "room_name": "Luxury Suite",
            "guest_name": "Jane Smith",
            "check_in": "2024-02-01",
            "check_out": "2024-02-03",
            "status": "Confirmed",
            "amount": "5000.00"
        }
    ]
}
```

### Vendor Bookings
**GET** `/vendor/bookings/`

Get all bookings for vendor's rooms with pagination and filtering.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `status`: Filter by booking status (Pending, Confirmed, Canceled)
- `start_date`: Filter bookings from date (YYYY-MM-DD)
- `end_date`: Filter bookings to date (YYYY-MM-DD)
- `room_id`: Filter by specific room ID
- `page`: Page number for pagination
- `page_size`: Number of items per page

**Example Request:**
```
GET /vendor/bookings/?status=Confirmed&start_date=2024-01-01&end_date=2024-01-31&page=1
```

**Response:**
```json
{
    "count": 25,
    "next": "http://localhost:8000/vendor/bookings/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "room": {
                "id": 1,
                "name": "Luxury Ocean View Suite",
                "image": "/images/room_images/suite1.jpg"
            },
            "user": {
                "id": 1,
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane@example.com"
            },
            "check_in": "2024-02-01",
            "check_out": "2024-02-03",
            "total_guest": 2,
            "reservation_status": "Confirmed",
            "amount": "10000.00",
            "contact_number": "+919876543210",
            "created_at": "2024-01-15T10:30:00Z"
        }
    ]
}
```

### Vendor Room Ratings
**GET** `/vendor/vendor/ratings/`

Get ratings and reviews for all vendor's rooms.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
[
    {
        "room": {
            "id": 1,
            "name": "Luxury Ocean View Suite",
            "image": "/images/room_images/suite1.jpg"
        },
        "average_rating": 4.5,
        "total_ratings": 12,
        "recent_reviews": [
            {
                "id": 1,
                "user": {
                    "first_name": "John",
                    "last_name": "Doe"
                },
                "rating": 5,
                "feedback": "Excellent room with amazing ocean view!",
                "created_at": "2024-01-20T14:30:00Z"
            }
        ]
    }
]
```

### Vendor Reservations by Month
**GET** `/vendor/vendor-booking-sts/`

Get booking statistics grouped by month for analytics.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `year`: Filter by specific year (default: current year)

**Response:**
```json
{
    "booking_stats": [
        {
            "month": "2024-01",
            "total_bookings": 8,
            "confirmed_bookings": 7,
            "pending_bookings": 1,
            "canceled_bookings": 0,
            "revenue": "35000.00"
        },
        {
            "month": "2024-02",
            "total_bookings": 12,
            "confirmed_bookings": 10,
            "pending_bookings": 1,
            "canceled_bookings": 1,
            "revenue": "48000.00"
        }
    ],
    "yearly_total": {
        "total_bookings": 45,
        "total_revenue": "125000.00",
        "average_monthly_bookings": 7.5
    }
}
```

### Top Performing Rooms
**GET** `/vendor/top-rooms/`

Get vendor's top-performing rooms based on bookings and revenue.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `period`: Time period for analysis (month, quarter, year, all_time)
- `metric`: Sort metric (bookings, revenue, rating)

**Response:**
```json
[
    {
        "room": {
            "id": 1,
            "name": "Luxury Ocean View Suite",
            "image": "/images/room_images/suite1.jpg",
            "price_per_night": "5000.00"
        },
        "total_bookings": 15,
        "total_revenue": "75000.00",
        "average_rating": 4.8,
        "occupancy_rate": 85.2,
        "rank": 1
    },
    {
        "room": {
            "id": 2,
            "name": "Mountain View Cabin",
            "image": "/images/room_images/cabin1.jpg",
            "price_per_night": "3500.00"
        },
        "total_bookings": 12,
        "total_revenue": "42000.00",
        "average_rating": 4.3,
        "occupancy_rate": 72.1,
        "rank": 2
    }
]
```

### All Users (Vendor View)
**GET** `/vendor/all-users/`

Get list of users who have booked vendor's rooms.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
[
    {
        "id": 1,
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane@example.com",
        "phone_number": "+919876543210",
        "total_bookings": 3,
        "total_spent": "15000.00",
        "last_booking_date": "2024-01-20T00:00:00Z",
        "favorite_room": "Luxury Ocean View Suite"
    }
]
```

## Serializers

### GenerateEmailSerializer
For vendor registration.

**Fields:**
- `first_name`: Vendor's first name (required)
- `last_name`: Vendor's last name (required)
- `email`: Unique email address (required)
- `phone_number`: Phone number with country code (required)
- `password`: Password (required, write-only)
- `confirm_password`: Password confirmation (required, write-only)

### VendorLoginSerializer
For vendor authentication.

**Fields:**
- `email`: Email address (required)
- `password`: Password (required, write-only)

### VendorProfileSerializer
For profile management.

**Fields:**
- `id`: User ID (read-only)
- `username`: Username (read-only)
- `email`: Email address
- `first_name`: First name
- `last_name`: Last name
- `phone_number`: Phone number
- `image`: Profile image
- `is_vendor`: Vendor status (read-only)
- `is_active`: Account status (read-only)
- `date_joined`: Registration date (read-only)

### ChangePasswordSerializer
For password changes.

**Fields:**
- `old_password`: Current password (required, write-only)
- `new_password`: New password (required, write-only)
- `confirm_password`: New password confirmation (required, write-only)

### ChangeEmailSerializer
For email changes.

**Fields:**
- `new_email`: New email address (required)
- `password`: Current password for verification (required, write-only)

## Error Handling

### Common Error Responses

#### 400 Bad Request - Validation Error
```json
{
    "email": ["User with this email already exists."],
    "password": ["Password must be at least 8 characters long."],
    "phone_number": ["Invalid phone number format."]
}
```

#### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

#### 403 Forbidden - Not a Vendor
```json
{
    "detail": "You must be a vendor to access this endpoint."
}
```

#### 404 Not Found
```json
{
    "error": "OTP entry not found"
}
```

#### OTP Specific Errors
```json
{
    "error": "Invalid OTP or OTP expired"
}
```

```json
{
    "message": "OTP already exists and is still valid"
}
```

## Rate Limiting and Security

### OTP Security
- OTP expires after 5 minutes
- Only one active OTP per email at a time
- OTP is automatically deleted after successful verification

### Session Management
- JWT tokens are used for authentication
- Refresh tokens expire after 10 days
- Access tokens expire after 12 hours

### Password Security
- Django's built-in password validation is enforced
- Passwords must meet complexity requirements
- Old password verification required for changes

## Real-time Features

Vendor dashboard supports real-time notifications for:
- New bookings
- Booking cancellations
- New reviews and ratings
- Payment confirmations

WebSocket connection endpoint: `ws://localhost:8000/ws/vendor/{vendor_id}/`

## Analytics and Reporting

### Key Metrics Tracked
1. **Booking Metrics**: Total bookings, confirmation rate, cancellation rate
2. **Revenue Metrics**: Total revenue, monthly revenue, average booking value
3. **Performance Metrics**: Occupancy rate, average rating, response time
4. **Customer Metrics**: Repeat customers, customer satisfaction, booking patterns

### Data Export
Vendors can export their data in various formats:
- CSV reports for bookings and revenue
- PDF summaries for monthly performance
- JSON API endpoints for custom integrations

## Integration Notes

### With Room Management
- Vendor dashboard shows room performance metrics
- Booking data is linked to specific rooms
- Room availability is updated based on bookings

### With Payment System
- Revenue tracking includes payment status
- Vendor earnings are calculated after platform fees
- Payout information is tracked for settlements

### With Admin Portal
- Admin can view vendor performance metrics
- Vendor approval/suspension is managed by admin
- Commission rates are set by admin