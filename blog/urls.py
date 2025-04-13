# blog/urls.py
from django.urls import path
from . import views
from django.urls import path
from django.contrib.auth import views as auth_views

from .api import BlogPostListCreateAPIView, BlogPostDetailAPIView, CommentListCreateAPIView

urlpatterns = [
    path('comment/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('blog/delete/<int:id>/', views.blog_delete, name='blog_delete'),
    path('blog/<int:id>/', views.blog_detail, name='blog_detaille'),
    path('blog/edit/<int:id>/', views.blog_edit, name='blog_edit'),
    path('blog/add/', views.blog_add, name='blog_add'),
    path('blog/<int:blog_id>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),  # New pattern
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('blog/', views.blog, name='blog'),
    path('save-images', views.save_images, name='save_images'),
    path('api/posts/', BlogPostListCreateAPIView.as_view(), name='api-post-list'),
    path('api/posts/<int:pk>/', BlogPostDetailAPIView.as_view(), name='api-post-detail'),
    path('api/comments/', CommentListCreateAPIView.as_view(), name='api-comment-list'),


]
