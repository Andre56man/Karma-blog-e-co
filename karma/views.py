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
from .models import Product, Order, OrderItem, UserProfile, Article
import logging

# Configure logger
logger = logging.getLogger(__name__)

def is_admin(user):
    return user.is_staff

def policy(request):
    return render(request, 'policy.html')

def singleproduct(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'single-product.html', {'product': product})


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Product, Order, OrderItem
from datetime import datetime

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, 'Votre panier est vide.')
        return redirect('cart')
    
    # Ensure cart keys are strings
    cart = {str(k): v for k, v in cart.items()}
    products = Product.objects.filter(id__in=cart.keys())
    cart_items = [
        {'product': product, 'quantity': cart[str(product.id)], 'subtotal': product.price * cart[str(product.id)]}
        for product in products
    ]
    total = sum(item['subtotal'] for item in cart_items)
    
    if request.method == 'POST':
        # Récupérer les données du formulaire
        address = request.POST.get('address')
        city = request.POST.get('city')
        postcode = request.POST.get('postcode')
        country = request.POST.get('country')
        phone = request.POST.get('phone')
        shipping_method = request.POST.get('shipping_method', 'standard')
        payment_method = request.POST.get('payment_method', 'cash_on_delivery')
        
        # Valider les champs requis
        if not all([address, city, postcode, country, phone]):
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
            return render(request, 'checkout.html', {
                'cart_items': cart_items,
                'cart_total': total,
                'user': request.user
            })
        
        # Calculer les frais de livraison
        shipping_cost = 2000.00 if shipping_method == 'standard' else 5000.00
        
        # Créer la commande
        order = Order.objects.create(
            user=request.user,
            total=0,
            address=address,
            city=city,
            postcode=postcode,
            country=country,
            phone=phone,
            shipping_method=shipping_method,
            payment_method=payment_method,
            shipping_cost=shipping_cost,
            is_completed=False
        )
        
        order_total = 0
        
        # Ajouter les articles à la commande
        try:
            for product_id, quantity in cart.items():
                try:
                    product = Product.objects.get(id=product_id)
                    if product.stock >= quantity:
                        price = product.price * quantity
                        order_total += price
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity,
                            price=product.price,
                            subtotal=price  # Set here, save method will override if needed
                        )
                        product.stock -= quantity
                        product.save()
                    else:
                        messages.error(request, f"Stock insuffisant pour {product.name}")
                        order.delete()
                        return redirect('cart')
                except Product.DoesNotExist:
                    messages.error(request, f"Produit introuvable : ID {product_id}")
                    order.delete()
                    return redirect('cart')
            
            # Mettre à jour le total
            order.total = order_total
            order.is_completed = True
            order.save()
        
        except Exception as e:
            messages.error(request, f"Erreur lors de la création de la commande : {e}")
            order.delete()
            return redirect('cart')
        
        # Envoyer l'email de confirmation
        if hasattr(settings, 'DEFAULT_FROM_EMAIL'):
            try:
                subject = f"Confirmation de votre commande #{order.id}"
                html_message = render_to_string('order_confirmation.html', {
                    'user': request.user,
                    'order': order,
                    'order_items': order.orderitem_set.all(),
                    'shipping_cost': shipping_cost,
                    'year': datetime.now().year,
                })
                plain_message = (
                    f"Cher(e) {request.user.username},\n\n"
                    f"Merci pour votre achat. Votre commande #{order.id} a été enregistrée.\n"
                    f"Total: {order.grand_total():.2f} FCFA\n\n"
                    f"Karma Shop"
                )
                
                send_mail(
                    subject,
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [request.user.email],
                    html_message=html_message,
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Erreur lors de l'envoi de l'email: {e}")
                messages.warning(request, "Commande passée, mais l'email n'a pas pu être envoyé.")
        else:
            messages.warning(request, "Email non configuré. Commande passée sans confirmation par email.")
        
        # Vider le panier
        if 'cart' in request.session:
            del request.session['cart']
            request.session.modified = True
        
        messages.success(request, 'Commande passée avec succès!')
        return render(request, 'confirmation.html', {
            'order': order,
            'user': request.user,
            'shipping_cost': shipping_cost
        })
    
    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'cart_total': total,
        'user': request.user
    })

def cart(request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys())
    cart_items = [
        {'product': product, 'quantity': cart[str(product.id)], 'subtotal': product.price * cart[str(product.id)]}
        for product in products
    ]
    total = sum(item['subtotal'] for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})

def confirmation(request):
    return render(request, 'confirmation.html')

def about(request):
    return render(request, 'about.html')

def policy(request):
    return render(request,'policy.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        full_message = f"Message de : {name} ({email})\n\n{message}"

        try:
            send_mail(subject, full_message, email, ['matrixharck@gmail.com'])  # destinataire
            messages.success(request, 'Votre message a bien été envoyé.')
        except Exception as e:
            print(f"Erreur d'envoi: {e}")
            messages.error(request, "Une erreur est survenue, réessayez plus tard.")

        return redirect('contact')

    return render(request, 'contact.html')

def singleblog(request):
    return render(request, 'single-blog.html')

def logout_view(request):
    logout(request)
    return redirect('index')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')

from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse
from django.shortcuts import render, redirect
from .models import UserProfile

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur est déjà pris.")
            return render(request, 'register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà enregistré.")
            return render(request, 'register.html')

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.is_active = False  # Empêche la connexion avant activation
        user.save()

        # Récupère le profil lié au user via le signal
        profile = user.userprofile  
        activation_link = f"http://localhost:8000{reverse('activate_account', args=[str(profile.activation_token)])}"

        # Envoie de l'email d'activation
        send_mail(
            subject="Activation de votre compte Karma Shop",
            message=f"Bonjour {username},\n\nMerci pour votre inscription ! Veuillez activer votre compte en cliquant sur ce lien :\n\n{activation_link}\n\nSi vous n’avez pas créé de compte, ignorez cet email.",
            from_email="noreply@karma-shop.com",
            recipient_list=[email],
            fail_silently=False,
        )

        messages.success(request, "Inscription réussie ! Vérifiez votre email pour activer votre compte.")
        return redirect('login')

    return render(request, 'register.html')


from django.contrib.auth.forms import PasswordResetForm
from django.contrib import messages
from django.shortcuts import render, redirect

def password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(
                request=request, 
                email_template_name='password_reset_email.html'
            )
            messages.success(request, "Si un compte avec cet email existe, un lien de réinitialisation a été envoyé.")
            return redirect('password_reset_done')  # Redirige vers la page de confirmation
        else:
            messages.error(request, "L'email n'est pas valide.")
    else:
        form = PasswordResetForm()
    return render(request, 'password_reset.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def add_product(request):
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        price = request.POST['price']
        stock = request.POST['stock']
        image = request.FILES.get('image')
        product = Product(
            name=name,
            description=description,
            price=price,
            stock=stock,
            image=image,
            added_by=request.user
        )
        product.save()
        messages.success(request, 'Produit ajouté avec succès!')
        return redirect('index')
    return render(request, 'add_product.html')

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity <= product.stock:
            cart = request.session.get('cart', {})
            cart[product_id] = cart.get(product_id, 0) + quantity
            request.session['cart'] = cart
            messages.success(request, 'Produit ajouté au panier!')
            return redirect('cart')
        else:
            messages.error(request, 'Quantité demandée supérieure au stock.')
    return redirect('single-product', product_id=product_id)

def activate_account(request, token):
    try:
        profile = UserProfile.objects.get(activation_token=token)
        user = profile.user
        user.is_active = True
        user.save()
        profile.is_active = True
        profile.save()
        messages.success(request, "Votre compte a été activé avec succès. Vous pouvez maintenant vous connecter.")
        return redirect("login")
    except UserProfile.DoesNotExist:
        messages.error(request, "Lien d'activation invalide ou expiré.")
        return redirect("register")

@login_required
def historique(request):
    all_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(all_orders, 10)
    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)
    context = {
        'user': request.user,
        'orders': orders,
    }
    return render(request, 'historique.html', context)

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order,
    }
    return render(request, 'order_detail.html', context)

def index(request):
    featured_product = Product.objects.order_by('-created_at').first()
    latest_products = Product.objects.order_by('-created_at')
    paginator = Paginator(latest_products, 8)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    return render(request, 'index.html', {
        'featured_product': featured_product,
        'latest_products': products,
    })

@login_required
def product_add_edit(request, product_id=None):
    if product_id:
        product = get_object_or_404(Product, id=product_id, added_by=request.user)
    else:
        product = None
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        image = request.FILES.get('image')
        
        errors = {}
        if not name:
            errors['name'] = "Le nom est requis."
        if not description:
            errors['description'] = "La description est requise."
        try:
            price = float(price) if price else None
            if price is None or price < 0:
                errors['price'] = "Le prix doit être un nombre positif."
        except (ValueError, TypeError):
            errors['price'] = "Le prix doit être un nombre valide."
        try:
            stock = int(stock) if stock else None
            if stock is None or stock < 0:
                errors['stock'] = "Le stock doit être un nombre positif."
        except (ValueError, TypeError):
            errors['stock'] = "Le stock doit être un nombre valide."
        
        if not errors:
            if product:
                product.name = name
                product.description = description
                product.price = price
                product.stock = stock
                if image:
                    product.image = image
            else:
                product = Product(
                    name=name,
                    description=description,
                    price=price,
                    stock=stock,
                    image=image,
                    added_by=request.user
                )
            product.save()
            return redirect('index')
        
        return render(request, 'add_product.html', {
            'product': product,
            'errors': errors,
            'form_data': request.POST,
        })
    
    return render(request, 'add_product.html', {'product': product})

@login_required
def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id, added_by=request.user)
    if request.method == 'POST':
        product.delete()
        return redirect('index')
    return render(request, 'product_confirm_delete.html', {'product': product})

from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import Product

def product_list(request):
    # Get the search query from the 'q' parameter
    query = request.GET.get('q', '').strip()
    
    # Get all products or filter by query
    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()
    
    # Paginate the results (8 products per page)
    paginator = Paginator(products, 8)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    # Pass products and query to the template
    return render(request, 'product_list.html', {'products': products, 'query': query})

def search(request):
    query = request.GET.get('q', '').strip()
    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()
    
    paginator = Paginator(products, 8)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    return render(request, 'product_list.html', {'products': products, 'query': query})




@login_required
def confirmation(request):
    order = Order.objects.filter(user=request.user, is_completed=True).order_by('-created_at').first()
    return render(request, 'confirmation.html', {
        'order': order,
        'user': request.user,
        'shipping_cost': order.shipping_cost if order else 2000
    })

def payment_webhook(request):
    if request.method == 'POST':
        try:
            order = Order.objects.get(payment_id=request.POST.get('payment_id'))
            if order.status != 'confirmed':
                order.status = 'confirmed'
                order.save()
                send_order_confirmation_email(request, order)
        except Order.DoesNotExist:
            logger.error(f"Commande non trouvée pour le payment_id: {request.POST.get('payment_id')}")
        return HttpResponse(status=200)
    return HttpResponse(status=400)

@login_required
def resend_confirmation_email(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    try:
        send_order_confirmation_email(request, order)
        messages.success(request, "L'email de confirmation a été renvoyé avec succès.")
    except Exception as e:
        logger.error(f"Erreur lors du renvoi de l'email de confirmation: {e}")
        messages.error(request, "Une erreur est survenue lors de l'envoi de l'email.")
    return redirect('order_confirmation', order_id=order.id)

def send_order_confirmation_email(request, order):
    subject = f'{settings.EMAIL_SUBJECT_PREFIX} Confirmation de commande #{order.id}'
    context = {
        'order': order,
        'user': request.user,
        'site_url': settings.SITE_URL,
        'support_email': settings.SUPPORT_EMAIL
    }
    html_message = render_to_string('emails/order_confirmation.html', context)
    text_message = render_to_string('emails/order_confirmation.txt', context)
    email = EmailMultiAlternatives(
        subject,
        text_message,
        settings.DEFAULT_FROM_EMAIL,
        [request.user.email],
        reply_to=[settings.SUPPORT_EMAIL]
    )
    email.attach_alternative(html_message, "text/html")
    email.send(fail_silently=False)
    logger.info(f"Email de confirmation envoyé pour la commande #{order.id} à {request.user.email}")

