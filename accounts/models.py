from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from pytz import timezone
from .managers import UserManager
from datetime import timedelta, datetime
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import models
from django.utils import timezone

from django.db.models.functions import Now




class User(AbstractBaseUser, PermissionsMixin):
    """
    This model for user,vendor and admin
    """
    email        = models.EmailField(_('email address'), unique=True, null=True, blank=True) 
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    username     = models.CharField(max_length=50, unique=True, null=True, blank=True)
    first_name   = models.CharField(max_length=50, blank=True, null=True)
    last_name    = models.CharField(max_length=50, blank=True, null=True)
    is_vendor    = models.BooleanField(default=False)
    date_joined  = models.DateTimeField(auto_now_add=True)
    last_login   = models.DateTimeField(auto_now=True)
    is_staff     = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active    = models.BooleanField(default=True)
    image        = models.ImageField(default='default.jpg', upload_to='user_profile_photo',null=True)
    objects      = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        """
        Return the string representation of the user.
        """
        return self.username or self.phone_number or self.email

    @property
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    @property
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}' 

# class Profile(models.Model):
#     """
#     Model for storing updated user profile information.
#     """
#     image        = models.ImageField(default='default.jpg', upload_to='profile')
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    



def default_expiry():
    return timezone.now() + timezone.timedelta(minutes=5)

class OTP(models.Model):
    phone_number = models.CharField(max_length=15 , unique=True, null=True, blank=True)
    email = models.EmailField(_('email address'), unique=True, null=True) 
    otp_code = models.CharField(max_length=6)
    otp_expiry = models.DateTimeField(default=default_expiry)
    password = models.CharField(max_length=128, null=True, blank=True)  # Password field to temporarily store password

    @classmethod
    def create(cls, phone_number, otp_code, otp_expiry, password):
        return cls.objects.create(phone_number=phone_number, otp_code=otp_code, otp_expiry=otp_expiry, password=password)

    def is_expired(self):
        return timezone.now() > self.otp_expiry

    
# OTP.objects.filter(otp_expiry__gte=Now()-timespan(days=1))
