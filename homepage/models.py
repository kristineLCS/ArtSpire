from django.db import models
import os
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class Post(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="post_images/", blank=True, null=True)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name='community_posts')


    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.title
    
    def get_absolute_url(self): # Change here
        return reverse('post-detail', kwargs={'pk': self.pk})
    

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    body = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s - %s' % (self.post.title, self.name)


class ArtPrompt(models.Model):
    CATEGORY_CHOICES = [
        ('animal', 'Animal'),
        ('nature', 'Nature'),
        ('character', 'Character'),
        # Add more categories as needed
    ]
    
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    prompt_text = models.TextField()

    def __str__(self):
        return self.prompt_text
