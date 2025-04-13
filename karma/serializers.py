from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Product, Order, OrderItem, Article

# Serializer for User (to include basic user info in other serializers)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        ref_name = 'KarmaUser'  # ou un autre nom unique selon l'app

# Serializer for Product
class ProductSerializer(serializers.ModelSerializer):
    added_by = UserSerializer(read_only=True)  # Nested user info for the product creator
    image = serializers.ImageField(allow_empty_file=True, required=False)  # Handle image field

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'image', 'created_at', 'added_by']

# Serializer for OrderItem
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)  # Nested product info
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())  # Reference to Order

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'quantity', 'price', 'subtotal']

# Serializer for Order
class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # Nested user info
    orderitem_set = OrderItemSerializer(many=True, read_only=True)  # Nested order items (related_name='orderitem_set')
    grand_total = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'created_at', 'total', 'shipping_cost', 'payment_method', 'shipping_method',
            'address', 'city', 'postcode', 'country', 'phone', 'is_completed', 'grand_total', 'orderitem_set'
        ]

# Serializer for Article
class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['title', 'content', 'category', 'created_at']