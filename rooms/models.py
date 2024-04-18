from django.db import models
from django.urls import reverse
from accounts.models import User

from django.db import models

class City(models.Model):
    name = models.CharField(max_length=50, unique=True)  # Ensure unique city names

    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=50, blank=True)  # Optional country field
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='locations')

    def __str__(self):
        return str(self.name)



class Category(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='category_images/', blank=True)  # Optional image for category
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_categories', blank=True, null=True)  # User who created the category (optional)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of category creation (optional)

    def __str__(self):
        return self.name


class RoomType(models.Model):
    ROOM_TYPE_CHOICES = (
        ('SINGLE', 'Single'),
        ('DOUBLE', 'Double'),
        ('FAMILY', 'Family'),
    )
    name = models.CharField(max_length=50, choices=ROOM_TYPE_CHOICES)

    def __str__(self):
        return self.get_name_display()  # Use get_name_display() for human-readable representation


class BedType(models.Model):
    BED_TYPE_CHOICES = (
        ('KING', 'King'),
        ('QUEEN', 'Queen'),
        ('TWIN', 'Twin'),
    )
    name = models.CharField(max_length=50, choices=BED_TYPE_CHOICES)

    def __str__(self):
        return self.get_name_display()  # Use get_name_display() for human-readable representation


class Amenity(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='amenity_images/', blank=True)  # Optional image for amenity

    def __str__(self):
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=100)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='rooms')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='rooms', blank=True, null=True)  # Optional foreign key to Category
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    max_occupancy = models.IntegerField()
    image = models.ImageField(upload_to='room_images/')
    availability = models.BooleanField(default=True)
    pet_allowed = models.BooleanField(default=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, blank=True, null=True)  # Optional foreign key to RoomType
    bed_type = models.ForeignKey(BedType, on_delete=models.CASCADE, blank=True, null=True)  # Optional foreign key to BedType
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms', blank=True, null=True)  # User who created the room (optional)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of room creation (optional)
    amenities = models.ManyToManyField(Amenity, blank=True)  # ManyToMany relationship with Amenity

    def get_absolute_url(self):
        return reverse('room-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name