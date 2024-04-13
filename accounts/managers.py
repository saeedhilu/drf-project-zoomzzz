from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a regular user with the given email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)

# class User(AbstractBaseUser):
#     """
#     Custom user model with email as the unique identifier.
#     """
#     email = models.EmailField(unique=True)
#     # Add additional fields here as needed
    
#     objects = UserManager()

#     USERNAME_FIELD = 'email'
#     # Add any additional required fields to REQUIRED_FIELDS if necessary

#     def __str__(self):
#         return self.email
