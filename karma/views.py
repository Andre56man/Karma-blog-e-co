from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Product, Order, OrderItem, UserProfile
from django.core.mail import send_mail
from django.conf import settings

def is_admin(user):
    return user.is_staff



def categorie(request):
    return render(request, 'category.html')

def singleproduct(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'single-product.html', {'product': product})

def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, 'Votre panier est vide.')
        return redirect('cart')
    
    if request.method == 'POST':
        order = Order.objects.create(user=request.user, total=0)
        total = 0
        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            if product.stock >= quantity:
                price = product.price * quantity
                total += price
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )
                product.stock -= quantity
                product.save()
            else:
                messages.error(request, f"Stock insuffisant pour {product.name}")
                return redirect('cart')
        
        order.total = total
        order.is_completed = True
        order.save()
        del request.session['cart']
        messages.success(request, 'Commande passée avec succès!')
        return redirect('confirmation')
    return render(request, 'checkout.html')

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

def tracking(request):
    return render(request, 'tracking.html')

def elements(request):
    return render(request, 'elements.html')

def blog(request):
    return render(request, 'blog.html')

def contact(request):
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

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'register.html')
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return render(request, 'register.html')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, 'register.html')
        user = User.objects.create_user(username=username, email=email, password=password1)
        messages.success(request, "Registration successful! You can now log in.")
        return redirect('login')
    return render(request, 'register.html')

def password_reset(request):
    return render(request, 'password_reset.html')

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
        user_profile = UserProfile.objects.get(activation_token=token)
        user = user_profile.user
        user.is_active = True
        user.save()
        messages.success(request, "Compte activé avec succès.")
        return redirect("login")
    except UserProfile.DoesNotExist:
        messages.error(request, "Lien d'activation invalide.")
        return redirect("register")

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Order

@login_required
def historique(request):
    # Récupérer les informations de l'utilisateur et ses commandes
    all_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    # Pagination (10 commandes par page)
    paginator = Paginator(all_orders, 10)
    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)
    
    context = {
        'user': request.user,
        'orders': orders,
    }
    return render(request, 'historique.html', context)

@login_required
def order_detail(request, order_name):
    order = get_object_or_404(Order, id=order_name, user=request.user)
    context = {
        'order': order,
    }
    return render(request, 'order_detail.html', context)




@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order,
    }
    return render(request, 'order_detail.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product
from django.core.exceptions import ValidationError

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Product
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect

def index(request):
    # Récupérer le produit vedette (par exemple, le plus récent)
    featured_product = Product.objects.order_by('-created_at').first()
    
    # Récupérer tous les produits avec pagination
    latest_products = Product.objects.order_by('-created_at')
    paginator = Paginator(latest_products,8)  # 6 produits par page
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
    
    return render(request, 'add_product.html', {
        'product': product,
    })

@login_required
@login_required
def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id, added_by=request.user)
    if request.method == 'POST':
        product.delete()
        return redirect('index')  # Redirige vers la page d'index
    return render(request, 'product_confirm_delete.html', {'product': product})

def product_list(request):
    products = Product.objects.all()
    paginator = Paginator(products, 8)  # 6 produits par page
    page = request.GET.get('page')
    
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    return render(request, 'product_list.html', {'products': products})


