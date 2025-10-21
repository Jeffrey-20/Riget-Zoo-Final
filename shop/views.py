from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from .cart import Cart
from django.contrib.auth.decorators import login_required

def shop_home(request):
    products = Product.objects.all()
    return render(request, 'pages/shop_home.html', {'products': products})

def add_to_cart(request, product_id):
    cart = Cart(request)
    cart.add(product_id)
    return redirect('view_cart')

def remove_from_cart(request, product_id):
    cart = Cart(request)
    cart.remove(product_id)
    return redirect('view_cart')

def view_cart(request):
    cart = Cart(request)
    return render(request, 'pages/cart.html', {'cart': cart})

@login_required
def checkout(request):
    cart = Cart(request)
    if not any(True for _ in cart):
        return render(request, 'pages/cart.html', {'cart': cart, 'error': 'Your cart is empty!'})

    order = cart.create_order(request.user)
    return render(request, 'pages/checkout_success.html', {'order': order})
