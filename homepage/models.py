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
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    likes = models.ManyToManyField(User, related_name='community_posts', blank=True)


    is_active = models.BooleanField(default=True)  # Delete inappropiate posts recieved from report submissions


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
    

class Feedback(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} - {self.user.username if self.user else 'Anonymous'} on {self.created_at}"


class PostReport(models.Model):
    REPORT_CATEGORIES = [
        ('spam', 'Spam or misleading'),
        ('offensive', 'Offensive content'),
        ('harassment', 'Harassment or bullying'),
        ('violence', 'Violent or dangerous content'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('action_taken', 'Action Taken'),
        ('dismissed', 'Dismissed'),
    ]

    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='reports')
    category = models.CharField(max_length=50, choices=REPORT_CATEGORIES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report by {self.reporter} on Post {self.post.id} - {self.category}. "


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
