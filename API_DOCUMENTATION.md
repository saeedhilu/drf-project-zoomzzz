# Room Booking System API Documentation

## Overview

This is a comprehensive Django REST Framework-based room booking system that provides APIs for user authentication, room management, vendor management, and admin operations. The system supports hotel room bookings with features like user reviews, wishlist management, and payment processing.

## Table of Contents

1. [Project Structure](#project-structure)
2. [Authentication](#authentication)
3. [Base URLs](#base-urls)
4. [API Endpoints](#api-endpoints)
   - [Accounts API](#accounts-api)
   - [Rooms API](#rooms-api)
   - [Vendor Management API](#vendor-management-api)
   - [Admin Portal API](#admin-portal-api)
5. [Models](#models)
6. [Error Handling](#error-handling)
7. [Examples](#examples)
8. [Setup Instructions](#setup-instructions)

## Project Structure

```
django_rest_auth/
├── accounts/           # User authentication and profile management
├── admin_portal/       # Admin operations and dashboard
├── rooms/             # Room management and booking
├── vendor_management/ # Vendor operations and dashboard
├── django_rest_auth/  # Main project configuration
└── requirements.txt   # Python dependencies
```

## Technology Stack

- **Backend**: Django 4.2.11, Django REST Framework 3.14.0
- **Database**: PostgreSQL
- **Authentication**: JWT (Simple JWT)
- **Task Queue**: Celery with Redis
- **Real-time**: Django Channels with Redis
- **Payment**: Razorpay Integration
- **Email**: SMTP via Gmail
- **Frontend Dependencies**: React, Chart.js, FontAwesome

## Authentication

The API uses JWT (JSON Web Token) authentication with the following flow:

### Token Types
- **Access Token**: Expires in 12 hours
- **Refresh Token**: Expires in 10 days

### Authentication Headers
```http
Authorization: Bearer <access_token>
```

### JWT Configuration
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=12), 
    'REFRESH_TOKEN_LIFETIME': timedelta(days=10),     
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

## Base URLs

- **Development**: `http://localhost:8000/`
- **Production**: `http://13.236.110.220/`
- **Admin Panel**: `http://localhost:8000/admin/`

## API Endpoints

All API endpoints are organized by their respective applications:

### URL Patterns
- `/accounts/` - User authentication and profile management
- `/vendor/` - Vendor operations and management
- `/rooms/` - Room management (vendor operations)
- `/` - Admin portal operations (root paths)

## Environment Variables

The following environment variables are required:

```env
SECRET_KEY=your_django_secret_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_SECRET=your_google_client_secret
SOCIAL_PASSWORD=your_social_auth_password
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_secret
```

## Database Configuration

The system uses PostgreSQL with the following configuration:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'zoomzzzawsdb',
        'USER': 'adminn',
        'PASSWORD': '12345',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## CORS Configuration

CORS is configured to allow all origins for development:

```python
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',  # React frontend
]
```

## Media Files

Media files (images) are configured as follows:

```python
MEDIA_URL = 'images/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'images')
```

## Real-time Features

The system supports real-time features using Django Channels with Redis:

```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}
```

## Celery Configuration

Background tasks are handled by Celery with Redis broker:

```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_TIMEZONE = 'Asia/kolkata'

CELERY_BEAT_SCHEDULE = {
    'update_reservation_status': {
        'task': 'accounts.tasks.update_reservation_status',
        'schedule': 200,  # Every 200 seconds
    },
}
```

## Email Configuration

Email functionality uses Gmail SMTP:

```python
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'saeednm1124@gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
```

## Time Zone

The application is configured for Indian Standard Time:

```python
TIME_ZONE = 'Asia/Kolkata'
```

## Debug and Development

Debug toolbar is enabled for development:

```python
DEBUG = True
INTERNAL_IPS = ["127.0.0.1"]
```

## Next Sections

Continue reading the detailed API endpoint documentation for each application:

- [Accounts API Documentation](./docs/ACCOUNTS_API.md)
- [Rooms API Documentation](./docs/ROOMS_API.md)
- [Vendor Management API Documentation](./docs/VENDOR_API.md)
- [Admin Portal API Documentation](./docs/ADMIN_API.md)
- [Setup and Installation Guide](./docs/SETUP.md)