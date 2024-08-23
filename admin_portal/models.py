
from django.db import models

class Banner(models.Model):
    image       = models.ImageField(max_length=200)
    title           = models.CharField(max_length=100)
    banner_content  = models.CharField(max_length=100,default='') 
    button_text     = models.CharField(max_length=50)
    
    def __str__(self):
        return self.title
