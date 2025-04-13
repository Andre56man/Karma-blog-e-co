from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from knox import views as knox_views
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token
from django.contrib.auth.views import LoginView
from .api import ProductListCreateAPIView, ProductDetailAPIView, OrderListCreateAPIView, OrderDetailAPIView

urlpatterns = [
    path('', views.index, name="index"),
    path('policy/', views.policy, name="policy"),
    path('single-product/<int:product_id>/', views.singleproduct, name="single-product"),
    path('checkout/', views.checkout, name="checkout"),
    path('cart/', views.cart, name="cart"),
    path('confirmation/', views.confirmation, name="confirmation"),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
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
    path('api/webhook/payment/', views.payment_webhook, name='payment_webhook'),
    path('resend-email/<int:order_id>/', views.resend_confirmation_email, name='resend_confirmation_email'),
    path('confirmation/', views.confirmation, name='confirmation'),
    path('search/', views.search, name='search'),
    path('api/products/', ProductListCreateAPIView.as_view(), name='api-product-list'),
    path('api/products/<int:pk>/', ProductDetailAPIView.as_view(), name='api-product-detail'),
    path('api/orders/', OrderListCreateAPIView.as_view(), name='api-order-list'),
    path('api/orders/<int:pk>/', OrderDetailAPIView.as_view(), name='api-order-detail'),
    path('api/login/', knox_views.LoginView.as_view(), name='knox_login'),
    path('api/logout/', knox_views.LogoutView.as_view(), name='knox_logout'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)