from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse


import uuid


# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    activation_token = models.UUIDField(default=uuid.uuid4, unique=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
# BlogPost
class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    excerpt = models.TextField(max_length=500, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='blog_images/', null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# Comment
class Comment(models.Model):
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.blog_post}"
    
