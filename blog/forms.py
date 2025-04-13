from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import BlogPost

class BlogPostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].widget = CKEditor5Widget(config_name='default')
    class Meta:
        model = BlogPost
        fields = ['title', 'excerpt', 'category', 'content', 'image']