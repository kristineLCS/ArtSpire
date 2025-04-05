from django.db import models
from django.contrib.auth import get_user_model
from cloudinary.models import CloudinaryField

User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = CloudinaryField('image', blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'
    
    @property
    def image_url(self):
        # If user has uploaded an image, use it; otherwise use the static default
        if self.image:
            return self.image.url
        return "https://res.cloudinary.com/djv5ebxzp/image/upload/v1743859123/default_wip6er.jpg"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)