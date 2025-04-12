from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('', views.index, name="index"),
    path('category/', views.categorie, name="category"),
    path('single-product/<int:product_id>/', views.singleproduct, name="single-product"),
    path('checkout/', views.checkout, name="checkout"),
    path('cart/', views.cart, name="cart"),
    path('confirmation/', views.confirmation, name="confirmation"),
    path('contact/', views.contact, name='contact'),
    path('blog/', views.blog, name='blog'),
    path('tracking/', views.tracking, name='tracking'),
    path('single-blog/<str:article_title>/', views.single_blog, name='single-blog'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('elements/', views.elements, name='elements'),
    path('register/', views.register, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("password_reset/", views.password_reset, name="password_reset"),
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='password_reset_form.html',
             email_template_name='password_reset_email.html',
             success_url='/password-reset/done/'
         ), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='password_reset_confirm.html',
             success_url='/reset/done/'
         ), 
         name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    path('activate/<uuid:token>/', views.activate_account, name='activate_account'),
    path('accounts/historique/', views.historique, name='historique'),
    path('add-product/', views.add_product, name='add_product'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('delete-product/<int:product_id>/', views.product_delete, name='product_delete'),  # URL corrigée    path('historique/', views.historique, name='historique'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('add-product/', views.product_add_edit, name='product_add'),
    path('edit-product/<int:product_id>/', views.product_add_edit, name='product_edit'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('products/', views.product_list, name='product_list'),
    path('article/<int:article_id>/', views.single_blog, name='blog_detaille'),
    path('save-images', views.save_images, name='save_images'),
    path('blog/<int:id>/', views.blog_detail, name='blog_detaille'),
    path('blog/edit/<int:id>/', views.blog_edit, name='blog_edit'),
    path('blog/delete/<int:id>/', views.blog_delete, name='blog_delete'),
    path('blog/add/', views.blog_add, name='blog_add'),
    path('blog/<int:blog_id>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),  # New pattern
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('blog/<int:blog_id>/comment/', views.add_comment, name='add_comment'),
    path('api/webhook/payment/', views.payment_webhook, name='payment_webhook'),
    path('resend-email/<int:order_id>/', views.resend_confirmation_email, name='resend_confirmation_email'),
    path('comment/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('confirmation/', views.confirmation, name='confirmation'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)