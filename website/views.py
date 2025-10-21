from django.shortcuts import render, redirect,  get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import CreateUserForm, LoginForm
from .models import Record
from django.shortcuts import render, redirect
from .forms import CreateUserForm, LoginForm, CreateRecordForm, UpdateRecordForm
from django.urls import reverse
from .forms import BookingForm
from .models import Booking, TicketType
from django.contrib import messages
from .forms import CancelBookingForm
from .models import Product
import logging

logging.basicConfig(filename='santa_log.log', level=logging.DEBUG,
                    format='%(asctime)s-%(levelname)s -%(message)s')

logger = logging.getLogger(__name__)




# Home page
def home(request):
    logger.info("Home page loaded")
    return render(request, 'pages/index.html')


# Register a user
def register(request):
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()   # ✅ hashes password properly
            return redirect('my-login')
    else:
        form = CreateUserForm()

    context = {'form': form}
    return render(request, 'pages/register.html', context)


# Login
def my_login(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            logger.info("User Logged in")
            user = form.get_user()   # ✅ AuthenticationForm handles authenticate
            login(request, user)
            return redirect('dashboard')
    else:
        form = LoginForm()

    context = {'login_form': form}
    return render(request, 'pages/my-login.html', context)


# Logout
def user_logout(request):
    logger.info("User Logged Out")
    logout(request)
    return redirect('my-login')


# Dashboard (protected page)
@login_required(login_url='my-login')
def dashboard(request):
    '''dashboard
    This dashboard requires the user to be logged in. It wil
    the fetch all the records from the database, and add them to
    the context with the key - records.
    it then sends this to the dashboard  
    '''
    my_records = Record.objects.all()
    context = {'records':my_records}

    return render(request, 'pages/dashboard.html',context)

# Creating a record
@login_required(login_url='my-login')
def create_record(request):

    form = CreateRecordForm()
    if request.method == "POST":
        form = CreateRecordForm(request.POST)
        if form.is_valid():
            form.save()  # ✅ This saves to the database
            return redirect('dashboard')
        else:
            form = CreateRecordForm()
    context = {'form': form}
    return render(request, 'pages/create_record.html', context)


# Reading/viewing a record
@login_required(login_url='my-login')
def view_record(request,pk):

    one_record = Record.objects.get(id=pk)
    context = {'record':one_record}
    return render(request, 'pages/view-record.html', context=context)


#  update records
@login_required(login_url='my-login')
def update_record(request, pk):
    one_record = Record.objects.get(id=pk)

    if request.method == 'POST':
        form = UpdateRecordForm(request.POST, instance=one_record)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = UpdateRecordForm(instance=one_record)

    context = {'form': form, 'record': one_record}
    return render(request, 'pages/update-record.html', context)



#deleting a record
@login_required(login_url='my-login')
def delete_record(request, pk):
    record = Record.objects.get(id=pk)
    record.delete()

    return redirect("dashboard")

#booking a ticket
@login_required(login_url='my-login')
def book_tickets(request):
    """Handles the ticket booking form submission and initial price display."""
    
    # Fetch ticket prices for display on the page
    prices = {t.name: t.base_price for t in TicketType.objects.all()}

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            # The .save() method automatically calculates and sets the total_price
            booking = form.save() 
            
            # Redirect to the confirmation page
            return redirect(reverse('booking_confirmation', args=[booking.id]))
    else:
        # Initial GET request: display an empty form
        form = BookingForm()

    context = {
        'form': form,
        'ticket_prices': prices,
        'title': 'Book Zoo Tickets',
    }
    return render(request, 'pages/book_tickets.html', context)


#confirming booked tickets
@login_required(login_url='my-login')
def booking_confirmation(request, booking_id):
    """Displays the confirmed booking details and total price."""
    
    # Use get_object_or_404 to handle invalid IDs gracefully
    booking = get_object_or_404(Booking, id=booking_id)

    context = {
        'booking': booking,
        'title': 'Booking Confirmed',
    }
    return render(request, 'pages/confirmation.html', context)


#cancel a booking
@login_required(login_url='my-login')
def cancel_booking(request):
    if request.method == "POST":
        form = CancelBookingForm(request.POST)
        if form.is_valid():
            booking = form.cleaned_data["booking"]
            booking.cancel()

            messages.success(request, f"Booking #{booking.id} has been cancelled.")
            return redirect("cancel_booking")
    else:
        form = CancelBookingForm()

    return render(request, "pages/cancel_booking.html", {"form": form})

####### Shopping views ###########

def shop_home(request):  # shop home
    products = Product.objects.all()
    return render(request, 'pages/shop_home.html', {'products': products})

def add_to_cart(request, product_id): # adding to the cart
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart      # Save the updated 'cart' dictionary back into the session.
    return redirect('view_cart')         # Redirect the user to the 'view_cart' page

def remove_from_cart(request, product_id):  # remnoving from  the cart
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
    request.session['cart'] = cart
    return redirect('view_cart')

def view_cart(request):  # Viewing the cart
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys())
    total = sum(product.price * cart[str(product.id)] for product in products)
    return render(request, 'pages/cart.html', {'cart': cart, 'products': products, 'total': total}) 

#############################################




