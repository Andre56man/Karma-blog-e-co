from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, BlogPost, Comment

# Serializer for User (to include basic user info in other serializers)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        ref_name = 'BlogUser'

# Serializer for UserProfile
class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # Nested serializer for the related User

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'activation_token', 'is_active']

# Serializer for Comment
class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # Nested user info
    blog_post = serializers.PrimaryKeyRelatedField(queryset=BlogPost.objects.all())  # Reference to BlogPost

    class Meta:
        model = Comment
        fields = ['id', 'blog_post', 'user', 'content', 'created_at']

# Serializer for BlogPost
class BlogPostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)  # Nested author info
    comments = CommentSerializer(many=True, read_only=True)  # Nested comments (related_name='comments')
    image = serializers.ImageField(allow_empty_file=True, required=False)  # Handle image field

    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'excerpt', 'content', 'image', 'author', 'category', 'created_at', 'updated_at', 'comments']