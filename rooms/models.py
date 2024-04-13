# from django.db import models
# from django.contrib.auth import get_user_model
# from admin_management.models import Category 
# User = get_user_model()
# class Room(models.Model):
#     name = models.CharField(max_length=100)
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)
#     description = models.TextField()
#     address = models.TextField()
    
#     price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
#     max_occupancy = models.IntegerField()
#     image = models.ImageField(upload_to='room_images/')
#     availability = models.BooleanField(default=True)
#     pet_allowed = models.BooleanField(default=True)
#     total_parking = models.IntegerField(default=True)
#     Terms_and_conditions = models.CharField( max_length=50)
#     # location = models.ForeignKey(Location, on_delete=models.CASCADE)
#     # facilities = models.TextField()
#     # amenities = models.TextField()
#     instructions = models.CharField( max_length=50)
#     def __str__(self):
#         return self.name
    
