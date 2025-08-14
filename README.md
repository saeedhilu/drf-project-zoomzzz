# Room Booking System API

A comprehensive Django REST Framework-based room booking platform that provides APIs for user authentication, room management, vendor management, and admin operations. The system supports hotel/accommodation room bookings with features like user reviews, wishlist management, payment processing, and real-time analytics.

## 🌟 Features

### For Users
- **Authentication**: Phone OTP and Google OAuth integration
- **Room Search**: Advanced filtering by location, dates, price, amenities
- **Bookings**: Complete reservation management with payment integration
- **Wishlists**: Save favorite rooms for later
- **Reviews**: Rate and review accommodations
- **Profile Management**: Update personal information and preferences

### For Vendors
- **Room Management**: Create, update, and manage room listings
- **Dashboard**: Track bookings, revenue, and performance metrics
- **Analytics**: Monthly statistics and top-performing rooms
- **Profile Management**: Update vendor information and settings

### For Administrators
- **System Configuration**: Manage categories, amenities, locations
- **User Management**: Monitor and manage user accounts
- **Vendor Oversight**: Track vendor performance and manage approvals
- **Analytics**: Platform-wide statistics and reporting
- **Content Management**: Manage banners and promotional content

## 🏗️ Architecture

### Technology Stack
- **Backend**: Django 4.2.11, Django REST Framework 3.14.0
- **Database**: PostgreSQL
- **Authentication**: JWT (Simple JWT)
- **Task Queue**: Celery with Redis
- **Real-time**: Django Channels with Redis
- **Payment**: Razorpay Integration
- **Email**: SMTP via Gmail
- **Frontend**: React, Chart.js, FontAwesome

### Project Structure
```
django_rest_auth/
├── accounts/           # User authentication and profile management
├── admin_portal/       # Admin operations and dashboard
├── rooms/             # Room management and booking
├── vendor_management/ # Vendor operations and dashboard
├── django_rest_auth/  # Main project configuration
├── docs/              # API documentation
└── requirements.txt   # Python dependencies
```

## 📚 Documentation

### API Documentation
- **[Main API Overview](./API_DOCUMENTATION.md)** - Project overview, authentication, and configuration
- **[Accounts API](./docs/ACCOUNTS_API.md)** - User authentication, bookings, and profile management
- **[Rooms API](./docs/ROOMS_API.md)** - Room management for vendors
- **[Vendor Management API](./docs/VENDOR_API.md)** - Vendor registration, dashboard, and analytics
- **[Admin Portal API](./docs/ADMIN_API.md)** - Administrative functions and system management

### Setup and Deployment
- **[Setup Guide](./docs/SETUP.md)** - Complete installation and deployment instructions

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16.x+
- PostgreSQL 12+
- Redis 6.x+

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd room-booking-system
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   npm install
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Start services**
   ```bash
   # Terminal 1: Django server
   python manage.py runserver
   
   # Terminal 2: Celery worker
   celery -A django_rest_auth worker -l info
   
   # Terminal 3: Celery beat
   celery -A django_rest_auth beat -l info
   
   # Terminal 4: Redis server
   redis-server
   ```

The API will be available at `http://localhost:8000/`

## 🔗 API Endpoints Overview

### Base URLs
- **Accounts**: `/accounts/` - User operations
- **Vendor**: `/vendor/` - Vendor operations  
- **Rooms**: `/rooms/` - Room management
- **Admin**: `/` - Admin operations

### Key Endpoints

#### Authentication
```
POST /accounts/google/auth/          # Google OAuth login
POST /accounts/generate-ph-otp/      # Generate phone OTP
POST /accounts/verify-ph-otp/        # Verify OTP and login
POST /vendor/signup-vendor/          # Vendor registration
POST /vendor/login/                  # Vendor login
POST /login-admin/                   # Admin login
```

#### Room Operations
```
GET    /accounts/room-search/        # Search rooms
GET    /accounts/room-detail/{id}/   # Room details
POST   /rooms/create/                # Create room (vendor)
PUT    /rooms/edit/{id}/             # Update room (vendor)
DELETE /rooms/edit/{id}/             # Delete room (vendor)
```

#### Booking Operations
```
POST /accounts/reservations/{room_id}/     # Create booking
GET  /accounts/confirmed-rooms/            # User's confirmed bookings
GET  /accounts/canceled-rooms/             # User's canceled bookings
POST /accounts/initiate_payment/           # Payment processing
```

#### Admin Operations
```
GET  /Users-listing/           # List all users
GET  /all-room-listing/        # List all rooms
POST /category/                # Create category
GET  /booking-sts/             # Booking statistics
```

## 🔐 Authentication

The API uses JWT (JSON Web Token) authentication:

```http
Authorization: Bearer <access_token>
```

### Token Lifecycle
- **Access Token**: 12 hours
- **Refresh Token**: 10 days

### User Types
- **Customer**: Regular users who book rooms
- **Vendor**: Property owners who list rooms
- **Admin**: System administrators

## 💾 Data Models

### Core Models
- **User**: Custom user model supporting customers, vendors, and admins
- **Room**: Property listings with images, amenities, and pricing
- **Reservation**: Booking records with status tracking
- **Rating**: User reviews and ratings for rooms
- **Location**: Geographic organization (Country → City → Location)

### Configuration Models
- **Category**: Room types (Hotel, Apartment, Villa)
- **Amenity**: Available facilities (WiFi, AC, Pool)
- **RoomType/BedType**: Room specifications

## 🔧 Configuration

### Environment Variables
Key configuration options in `.env`:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
DB_NAME=zoomzzzawsdb
DB_USER=adminn
DB_PASSWORD=12345
GOOGLE_CLIENT_ID=your-google-client-id
RAZORPAY_KEY_ID=your-razorpay-key
EMAIL_HOST_USER=your-email@gmail.com
```

### Database Configuration
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'zoomzzzawsdb',
        'USER': 'adminn',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 📊 Real-time Features

### WebSocket Endpoints
- **Admin Notifications**: `ws://localhost:8000/ws/admin/`
- **Vendor Updates**: `ws://localhost:8000/ws/vendor/{vendor_id}/`

### Real-time Events
- New user registrations
- Booking confirmations/cancellations
- New reviews and ratings
- Payment notifications

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python manage.py test

# Run tests for specific apps
python manage.py test accounts
python manage.py test rooms
python manage.py test vendor_management
python manage.py test admin_portal
```

API testing with cURL examples available in individual API documentation files.

## 📈 Performance Features

### Caching Strategy
- Room listings cached for 30 minutes
- User statistics cached for 15 minutes
- Configuration data cached for 1 hour

### Database Optimization
- Indexed foreign keys for faster lookups
- Optimized queries with select_related/prefetch_related
- Connection pooling for database efficiency

### Background Tasks
- Email sending via Celery
- Reservation status updates
- Analytics calculations
- Periodic cleanup tasks

## 🔒 Security Features

- JWT token authentication
- CSRF protection enabled
- CORS properly configured
- Input validation and sanitization
- File upload security
- Rate limiting on sensitive endpoints
- Secure password handling

## 🌍 Deployment

### Production Checklist
- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use environment variables for secrets
- [ ] Set up HTTPS with SSL certificates
- [ ] Configure production database
- [ ] Set up Redis for production
- [ ] Configure email settings
- [ ] Set up monitoring and logging

### Deployment Options
- **Traditional**: Gunicorn + Nginx
- **Containerized**: Docker + Docker Compose
- **Cloud**: AWS/Azure/GCP with managed services

## 📝 API Usage Examples

### User Registration and Login
```bash
# Generate OTP
curl -X POST http://localhost:8000/accounts/generate-ph-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+919876543210"}'

# Verify OTP
curl -X POST http://localhost:8000/accounts/verify-ph-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+919876543210", "otp": "123456"}'
```

### Room Search
```bash
curl -X GET "http://localhost:8000/accounts/room-search/?location=mumbai&check_in=2024-02-01&check_out=2024-02-03&guests=2"
```

### Create Booking
```bash
curl -X POST http://localhost:8000/accounts/reservations/1/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "check_in": "2024-02-01",
    "check_out": "2024-02-03",
    "total_guest": 2,
    "email": "user@example.com",
    "contact_number": "+919876543210",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:

1. Check the [Setup Guide](./docs/SETUP.md) for installation issues
2. Review the relevant API documentation for usage questions
3. Check the troubleshooting section in the setup guide
4. Open an issue for bugs or feature requests

## 📊 API Statistics

- **Total Endpoints**: 50+ REST API endpoints
- **Authentication Methods**: JWT, Google OAuth, Phone OTP
- **File Upload**: Multi-image support with validation
- **Real-time**: WebSocket integration
- **Background Jobs**: Celery task queue
- **Caching**: Redis-based caching strategy
- **Database**: PostgreSQL with optimized queries

---

**Built with ❤️ using Django REST Framework**