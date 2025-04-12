from django.db import models
import os
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.urls import reverse
import re
from django.utils.text import slugify


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Tag')
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)  # Fixed typo: self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="post_images/", blank=True, null=True)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    likes = models.ManyToManyField(User, related_name='community_posts', blank=True)


    is_active = models.BooleanField(default=True)  # Delete inappropiate posts recieved from report submissions


    def extract_and_save_tags(self):
        self.tags.clear()  # Clear old tags to prevent duplicates/stale data
        hashtags = set(re.findall(r'#(\w+)', self.content))
        for tag_name in hashtags:
            tag, created = Tag.objects.get_or_create(name=tag_name, defaults={'slug': slugify(tag_name)})
            self.tags.add(tag)


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.extract_and_save_tags()

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})


class WeeklyChallenge(models.Model):
    challenge_text = models.CharField(max_length=255, help_text="Enter the weekly challenge text.")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.challenge_text
    

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
