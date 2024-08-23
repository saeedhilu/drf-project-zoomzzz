"""
Django settings for django_rest_auth project.

Generated by 'django-admin startproject' using Django 4.2.11.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
from datetime import timedelta
import os

from dotenv import load_dotenv
load_dotenv()
from pathlib import Path#








SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1), 
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),     
    'AUTH_HEADER_TYPES':('Bearer',),
}

# settings.py

# Use database-backed sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Ensure the session data is saved correctly
SESSION_SAVE_EVERY_REQUEST = True

# Other session settings
SESSION_COOKIE_SECURE = False  # Use True in production with HTTPS
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 1209600  # 2 weeks, adjust as needed


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# settings.py
MEDIA_URL = 'images/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'images') 

#  Using psql Data base 
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'zoomzzz',
        'HOST':'localhost',
        'PORT':'5432',
        'USER':'postgres',
        'PASSWORD':'12345'}
}

AUTHENTICATION_BACKENDS = (
    ('django.contrib.auth.backends.ModelBackend'),
)


# os.getenv.Env.read_env(BASE_DIR / '.env')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')





RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG =True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'saeednm1124@gmail.com'
EMAIL_HOST_PASSWORD = 'sviv cjrr iqgs hwsp'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# settings.py

ALLOWED_HOSTS = ['127.0.0.1', 'localhost',' https://7148-2405-201-f00d-3040-d1c-1fd7-1c4d-fd97.ngrok-free.app ']

TIME_ZONE = 'Asia/Kolkata'
AUTH_USER_MODEL = 'accounts.User'







APPEND_SLASH = False

CORS_ALLOW_ALL_ORIGINS = True 
CORS_URL_REGEX = r"^/api/.*"





# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

INSTALLED_APPS = [
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # customer_apps
    'rest_framework',
    'accounts',  
    'admin_portal',  
    'vendor_management',  
    'rooms',  
    'django_filters',
    'celery',
    'django_celery_results',
    'django_celery_beat',

    #corsheaders apps
    'corsheaders',
    'debug_toolbar',
     'channels',

]

ASGI_APPLICATION = 'django_rest_auth.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}


CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/kolkata'

CELERY_BEAT_SCHEDULE = {
    'update_reservation_status': {
        'task': 'accounts.tasks.update_reservation_status',
        'schedule': 200,  
    },
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
}



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
     'django.contrib.auth.middleware.AuthenticationMiddleware', 
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]





ROOT_URLCONF = 'django_rest_auth.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'django_rest_auth.wsgi.application'






CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_SECRET")
CUSTOM_PASSWORD_FOR_AUTH = os.getenv("SOCIAL_PASSWORD")
SPRING_EDGE_API_KEY = '621492a44a89m36c2209zs4l7e74672cj'


INTERNAL_IPS = [
    "127.0.0.1",
]
CORS_ALLOW_ALL_ORIGINS = True 
CORS_URL_REGEX = r"^/api/.*"
# settings.py

CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
]
