from django.db import models
from django.contrib.auth.models import User



# Product
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User

class Order(models.Model):
    PAYMENT_METHODS = (
        ('orange_money', 'Orange Money'),
        ('mtn_money', 'MTN Mobile Money'),
        ('card', 'Carte bancaire'),
        ('cash_on_delivery', 'Paiement à la livraison'),
    )
    
    SHIPPING_METHODS = (
        ('standard', 'Livraison standard'),
        ('express', 'Livraison express'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('2000.00'))
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash_on_delivery')
    shipping_method = models.CharField(max_length=20, choices=SHIPPING_METHODS, default='standard')
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postcode = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_completed = models.BooleanField(default=False)

    def grand_total(self):
        # Assure-toi que les deux valeurs sont des objets Decimal avant de les additionner
        return self.total + Decimal(self.shipping_cost)

    def grand_total_display(self):
        return f"{self.grand_total:,.2f}".replace(",", " ").replace(".", ",")

    def __str__(self):
        return f"Commande {self.id} - {self.user.username}"


# OrderItem
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='orderitem_set')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.subtotal is None:  # Only calculate if not set
            self.subtotal = self.quantity * self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

# Signal pour créer UserProfile
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from blog.models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Création du profil avec UUID automatique
        profile = UserProfile.objects.create(user=instance)

        # Désactiver le compte utilisateur
        instance.is_active = False
        instance.save()

        # Lien d’activation avec le token UUID
        activation_link = f"http://localhost:8000{reverse('activate_account', args=[str(profile.activation_token)])}"

        # Envoi de l’email d’activation
        send_mail(
            'Activation de votre compte',
            f'Bonjour {instance.username},\n\nMerci pour votre inscription.\n\nPour activer votre compte, cliquez sur le lien suivant :\n\n{activation_link}\n\nÀ bientôt !',
            settings.DEFAULT_FROM_EMAIL,
            [instance.email],
            fail_silently=False,
        )

# Article
class Article(models.Model):
    title = models.CharField(max_length=200, primary_key=True)
    content = models.TextField()
    category = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

