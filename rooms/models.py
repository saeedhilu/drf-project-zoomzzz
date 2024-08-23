from django.db import models
from django.urls import reverse
from accounts.models import User

from django.db import models





class City(models.Model):
    name = models.CharField(max_length=50, unique=True)  # Ensure unique city names

    def __str__(self):
        return self.name

from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name
class Location(models.Model):
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name



class   Category(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='category_images/', blank=True)  
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_categories', blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return self.name


class RoomType(models.Model):
    
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name  # Use get_name_display() for human-readable representation


class BedType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name  # Use get_name_display() for human-readable representation


class Amenity(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='amenity_images/', blank=True) 

    def __str__(self):
        return self.name


from django.core.exceptions import ValidationError
from django.db.models import Avg
from django.apps import apps
class Room(models.Model):
    name        = models.CharField(max_length=100)
    location    = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='rooms')
    category    = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='rooms', blank=True, null=True)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    max_occupancy   = models.IntegerField()
    google_map_url  = models.URLField(blank=True, null=True, verbose_name="Google Maps URL",max_length=400)
    
    image  = models.ImageField(upload_to='room_images/')
    image2 = models.ImageField(upload_to='room_images/', default='https://example.com/default_image.jpg')
    image3 = models.ImageField(upload_to='room_images/', default='https://example.com/default_image.jpg')
    image4 = models.ImageField(upload_to='room_images/', default='https://example.com/default_image.jpg', blank=True, null=True)
    image5 = models.ImageField(upload_to='room_images/', default='https://example.com/default_image.jpg', blank=True, null=True)
    availability = models.BooleanField(default=True)
    pet_allowed  = models.BooleanField(default=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, blank=True, null=True)
    bed_type = models.ForeignKey(BedType, on_delete=models.CASCADE, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    amenities = models.ManyToManyField(Amenity, blank=True)

    def clean(self):
        super().clean()
        # Ensure at least three image fields are populated
        images = [self.image, self.image2, self.image3, self.image4, self.image5]
        filled_images = [img for img in images if img]
        if len(filled_images) < 3:
            raise ValidationError('At least three images are required.')

    def get_absolute_url(self):
        return reverse('room-detail', kwargs={'pk': self.pk})

    def get_average_rating(self):
        average_rating = self.rating_set.aggregate(average=Avg('rating'))
        return average_rating['average']

    def __str__(self):
        return self.name
