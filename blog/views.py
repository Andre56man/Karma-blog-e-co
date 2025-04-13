from django.shortcuts import render

# Create your views here.
# blog/views.py
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponse
from django.core.files.storage import FileSystemStorage
import logging
from .models import  UserProfile, BlogPost, Comment


def blog(request):
    latest_posts = BlogPost.objects.all().order_by('-created_at')
    featured_post = latest_posts.first()
    return render(request, 'blog.html', {'latest_posts': latest_posts, 'featured_post': featured_post})

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Ensure only the comment's author can delete it
    if request.user != comment.user:
        messages.error(request, "You do not have permission to banish this commentary!")
        return redirect('blog_detaille', id=comment.blog_post.id)

    if request.method == 'POST':
        blog_post_id = comment.blog_post.id
        comment.delete()
        messages.success(request, "Your royal commentary has been banished from the archives!")
        return redirect('blog_detaille', id=blog_post_id)
    
    # For GET requests, you might want to show a confirmation page
    return render(request, 'confirm_delete.html', {'comment': comment})

def save_images(request):
    if request.method == 'POST':
        image_urls = {}
        for key, file in request.FILES.items():
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
            image_urls[key] = fs.url(filename)
        return JsonResponse({'imageUrls': image_urls})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def blog_detail(request, id):  # Changed from blog_title to id
    post = get_object_or_404(BlogPost, id=id)  # Fetch by id instead of title
    return render(request, 'blog_detaille.html', {'post': post})

@login_required
@user_passes_test(lambda u: u.is_staff)
def blog_edit(request, id):
    post = get_object_or_404(BlogPost, id=id)
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog')
    else:
        form = BlogPostForm(instance=post)
    return render(request, 'blog_edit.html', {'form': form, 'post': post})

@login_required
@user_passes_test(lambda u: u.is_staff)
def blog_delete(request, id):
    post = get_object_or_404(BlogPost, id=id)
    if request.method == 'POST':
        post.delete()
        return JsonResponse({'status': 'success'}, status=200)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import BlogPost
from .forms import BlogPostForm  # Import the new form

@login_required
@user_passes_test(lambda u: u.is_staff)
def blog_add(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog')
    else:
        form = BlogPostForm()
    return render(request, 'blog_add.html', {'form': form})

@login_required
def add_comment(request, blog_id):
    if request.method == 'POST':
        post = get_object_or_404(BlogPost, id=blog_id)
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                blog_post=post,
                user=request.user,
                content=content
            )
            messages.success(request, "Your royal commentary has been inscribed!")
        return redirect('blog_detaille', id=post.id)  # Redirect back to blog_detail with id
    return redirect('index')

@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    # Ensure only the comment's author can edit it
    if request.user != comment.user:
        messages.error(request, "You do not have permission to amend this commentary.")
        return redirect('blog_detaille', id=comment.blog_post.id)

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            comment.content = content
            comment.save()
            messages.success(request, "Your royal commentary has been amended!")
            return redirect('blog_detaille', id=comment.blog_post.id)
    
    # Render the edit form for GET requests
    return render(request, 'edit_comment.html', {'comment': comment})

