# Room Booking System - Setup and Installation Guide

## Overview

This guide provides step-by-step instructions for setting up the Room Booking System locally and deploying it to production. The system is built with Django REST Framework and includes user authentication, room management, booking functionality, and admin controls.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Environment Configuration](#environment-configuration)
4. [Database Setup](#database-setup)
5. [Redis Setup](#redis-setup)
6. [Frontend Setup](#frontend-setup)
7. [Running the Application](#running-the-application)
8. [Production Deployment](#production-deployment)
9. [Testing](#testing)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Python**: 3.8 or higher
- **Node.js**: 16.x or higher (for frontend dependencies)
- **PostgreSQL**: 12 or higher
- **Redis**: 6.x or higher
- **Git**: Latest version

### Development Tools

- **Code Editor**: VS Code, PyCharm, or similar
- **API Testing**: Postman, Insomnia, or curl
- **Database GUI**: pgAdmin, DBeaver, or similar (optional)

## Local Development Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd room-booking-system
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install Frontend Dependencies

```bash
npm install
```

## Environment Configuration

### 1. Create Environment File

Create a `.env` file in the project root directory:

```bash
touch .env
```

### 2. Configure Environment Variables

Add the following variables to your `.env` file:

```env
# Django Configuration
SECRET_KEY=your-secret-key-here-make-it-very-long-and-random
DEBUG=True

# Database Configuration
DB_NAME=zoomzzzawsdb
DB_USER=adminn
DB_PASSWORD=12345
DB_HOST=localhost
DB_PORT=5432

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_PORT=587
EMAIL_USE_TLS=True

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_SECRET=your-google-client-secret
SOCIAL_PASSWORD=your-social-auth-password

# Razorpay Configuration
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret

# SMS Configuration (Spring Edge)
SPRING_EDGE_API_KEY=your-spring-edge-api-key

# Redis Configuration (default values)
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0
```

### 3. Generate Django Secret Key

```python
# Run this in Python shell to generate a secret key
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

## Database Setup

### 1. Install PostgreSQL

**On Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**On macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**On Windows:**
Download and install from [PostgreSQL website](https://www.postgresql.org/download/windows/)

### 2. Create Database and User

```bash
# Access PostgreSQL shell
sudo -u postgres psql

# Create database and user
CREATE DATABASE zoomzzzawsdb;
CREATE USER adminn WITH PASSWORD '12345';
GRANT ALL PRIVILEGES ON DATABASE zoomzzzawsdb TO adminn;

# Grant additional privileges
ALTER USER adminn CREATEDB;
ALTER USER adminn SUPERUSER;

# Exit PostgreSQL shell
\q
```

### 3. Run Database Migrations

```bash
# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### 4. Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin user account.

## Redis Setup

### 1. Install Redis

**On Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install redis-server
```

**On macOS:**
```bash
brew install redis
brew services start redis
```

**On Windows:**
Download from [Redis website](https://redis.io/download) or use WSL

### 2. Start Redis Server

```bash
# Start Redis server
redis-server

# Test Redis connection
redis-cli ping
# Should return: PONG
```

### 3. Configure Redis (Optional)

Edit Redis configuration if needed:
```bash
sudo nano /etc/redis/redis.conf
```

## Frontend Setup

### 1. Frontend Dependencies

The project includes React components and uses the following frontend libraries:

```json
{
  "dependencies": {
    "@fortawesome/fontawesome-svg-core": "^6.5.2",
    "@fortawesome/free-solid-svg-icons": "^6.5.2",
    "@fortawesome/react-fontawesome": "^0.2.2",
    "axios": "^1.7.3",
    "chart.js": "^4.4.3",
    "react-chartjs-2": "^5.2.0"
  }
}
```

### 2. Build Frontend Assets

```bash
# Install dependencies
npm install

# Build for development
npm run dev

# Build for production
npm run build
```

## Running the Application

### 1. Start Django Development Server

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start Django server
python manage.py runserver
```

The API will be available at: `http://localhost:8000/`

### 2. Start Celery Worker (Background Tasks)

Open a new terminal window and run:

```bash
# Activate virtual environment
source venv/bin/activate

# Start Celery worker
celery -A django_rest_auth worker -l info
```

### 3. Start Celery Beat (Scheduled Tasks)

Open another terminal window and run:

```bash
# Activate virtual environment
source venv/bin/activate

# Start Celery beat scheduler
celery -A django_rest_auth beat -l info
```

### 4. Test the Setup

1. **API Health Check**: Visit `http://localhost:8000/admin/` to access Django admin
2. **User Registration**: Test user registration via `/accounts/generate-ph-otp/`
3. **Room Creation**: Create rooms via vendor endpoints
4. **Booking Flow**: Test the complete booking workflow

## Production Deployment

### 1. Environment Configuration

Update your `.env` file for production:

```env
DEBUG=False
ALLOWED_HOSTS=your-domain.com,your-ip-address

# Use production database
DB_HOST=your-production-db-host
DB_NAME=your-production-db-name
DB_USER=your-production-db-user
DB_PASSWORD=your-production-db-password

# Use production Redis
REDIS_HOST=your-production-redis-host

# Production email settings
EMAIL_HOST_USER=your-production-email@domain.com
EMAIL_HOST_PASSWORD=your-production-email-password
```

### 2. Install Production Dependencies

```bash
pip install gunicorn
pip install psycopg2-binary  # PostgreSQL adapter
```

### 3. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 4. Production Server Setup

**Using Gunicorn:**
```bash
gunicorn django_rest_auth.wsgi:application --bind 0.0.0.0:8000
```

**Using systemd service file:**
Create `/etc/systemd/system/django-app.service`:

```ini
[Unit]
Description=Django Room Booking App
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
RuntimeDirectory=django-app
WorkingDirectory=/path/to/your/project
ExecStart=/path/to/your/venv/bin/gunicorn django_rest_auth.wsgi:application --bind unix:/run/django-app/socket
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

### 5. Nginx Configuration

Create Nginx configuration file:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /path/to/your/project;
    }
    
    location /images/ {
        root /path/to/your/project;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/django-app/socket;
    }
}
```

### 6. SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Testing

### 1. Run Unit Tests

```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test accounts
python manage.py test rooms
python manage.py test vendor_management
python manage.py test admin_portal
```

### 2. API Testing

Use the provided cURL examples in the API documentation files:

- [Accounts API Tests](./ACCOUNTS_API.md)
- [Rooms API Tests](./ROOMS_API.md)
- [Vendor API Tests](./VENDOR_API.md)
- [Admin API Tests](./ADMIN_API.md)

### 3. Load Testing

```bash
# Install locust for load testing
pip install locust

# Create locustfile.py for testing
# Run load tests
locust -f locustfile.py --host=http://localhost:8000
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Error

```
django.db.utils.OperationalError: could not connect to server
```

**Solution:**
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Verify database credentials in `.env`
- Ensure database exists: `psql -U adminn -d zoomzzzawsdb`

#### 2. Redis Connection Error

```
redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379
```

**Solution:**
- Start Redis server: `redis-server`
- Check Redis status: `redis-cli ping`
- Verify Redis configuration in settings

#### 3. Celery Not Processing Tasks

**Solution:**
- Restart Celery worker: `celery -A django_rest_auth worker -l info`
- Check Redis connection
- Verify task registration in `celery.py`

#### 4. Email Not Sending

**Solution:**
- Verify SMTP settings in `.env`
- Check if Gmail App Password is used (not regular password)
- Test email configuration:
  ```python
  python manage.py shell
  from django.core.mail import send_mail
  send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
  ```

#### 5. File Upload Issues

**Solution:**
- Check `MEDIA_ROOT` and `MEDIA_URL` settings
- Ensure media directory has write permissions
- Verify file size limits in server configuration

#### 6. CORS Issues

**Solution:**
- Update `CORS_ALLOWED_ORIGINS` in settings
- Check frontend domain is included
- Verify CORS middleware is installed and configured

### Debug Mode

Enable debug mode for detailed error information:

```python
# In settings.py
DEBUG = True

# Add debug toolbar
INSTALLED_APPS = [
    # ... other apps
    'debug_toolbar',
]

MIDDLEWARE = [
    # ... other middleware
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = [
    '127.0.0.1',
]
```

### Logging Configuration

Add logging to debug issues:

```python
# In settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

## Performance Optimization

### 1. Database Optimization

```sql
-- Add database indexes for frequently queried fields
CREATE INDEX idx_room_location ON rooms_room(location_id);
CREATE INDEX idx_reservation_user ON accounts_reservation(user_id);
CREATE INDEX idx_reservation_status ON accounts_reservation(reservation_status);
```

### 2. Caching Configuration

```python
# In settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Cache configuration
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 300
CACHE_MIDDLEWARE_KEY_PREFIX = 'room_booking'
```

### 3. Static File Optimization

```bash
# Install whitenoise for static files
pip install whitenoise

# Add to MIDDLEWARE in settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ... other middleware
]

# Configure static files compression
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

## Monitoring and Maintenance

### 1. Health Checks

Create a health check endpoint:

```python
# In urls.py
path('health/', health_check_view, name='health_check'),

# Health check view
def health_check_view(request):
    return JsonResponse({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0'
    })
```

### 2. Backup Strategy

```bash
# Database backup
pg_dump -U adminn -h localhost zoomzzzawsdb > backup_$(date +%Y%m%d_%H%M%S).sql

# Media files backup
tar -czf media_backup_$(date +%Y%m%d_%H%M%S).tar.gz images/

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

pg_dump -U adminn -h localhost zoomzzzawsdb > $BACKUP_DIR/db_$DATE.sql
tar -czf $BACKUP_DIR/media_$DATE.tar.gz images/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

## Security Checklist

- [ ] Use HTTPS in production
- [ ] Update `SECRET_KEY` for production
- [ ] Set `DEBUG = False` in production
- [ ] Configure `ALLOWED_HOSTS` properly
- [ ] Use environment variables for sensitive data
- [ ] Enable CSRF protection
- [ ] Configure secure cookies
- [ ] Set up proper CORS policy
- [ ] Use strong database passwords
- [ ] Enable database connection encryption
- [ ] Configure proper file upload permissions
- [ ] Set up rate limiting
- [ ] Enable audit logging
- [ ] Regular security updates

For more information, refer to the individual API documentation files and Django's official documentation.