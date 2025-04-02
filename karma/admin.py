from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Product, Order, OrderItem, UserProfile

admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(UserProfile)