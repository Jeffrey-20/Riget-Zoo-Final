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
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm
from .forms import DiscountForm

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
@login_required(login_url='my-login')
def shop_home(request):  # shop home
    products = Product.objects.all()
    return render(request, 'pages/shop_home.html', {'products': products})

@login_required(login_url='my-login')
def add_to_cart(request, product_id): # adding to the cart
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart      # Save the updated 'cart' dictionary back into the session.
    return redirect('view_cart')         # Redirect the user to the 'view_cart' page

@login_required(login_url='my-login')
def remove_from_cart(request, product_id):  # remnoving from  the cart
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
    request.session['cart'] = cart
    return redirect('view_cart')

@login_required(login_url='my-login')
def view_cart(request):  # Viewing the cart
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys())
    total = sum(product.price * cart[str(product.id)] for product in products)
    return render(request, 'pages/cart.html', {'cart': cart, 'products': products, 'total': total}) 

#############################################



@login_required(login_url='my-login')
def book_tickets(request):
    ticket_prices = {
        'Adult': 20,
        'Child': 10,
    }

    # 🎯 Step 1: Get discount code from URL
    discount_code = request.GET.get('discount', '').upper().strip()
    discount_percentage = 0
    discount_name = None
    discount_type = None  # <-- NEW

    # 🎯 Step 2: Detect discount type
    if discount_code.startswith("SEASONAL10"):
        discount_percentage = 10
        discount_name = "10% Off Seasonal Discount"
        discount_type = "Seasonal Discount"
    elif discount_code.startswith("SEASONAL15"):
        discount_percentage = 15
        discount_name = "15% Off Seasonal Discount"
        discount_type = "Seasonal Discount"
    elif discount_code.startswith("SEASONAL20"):
        discount_percentage = 20
        discount_name = "20% Off Seasonal Discount"
        discount_type = "Seasonal Discount"
    elif discount_code.startswith("FAMILY30"):
        discount_percentage = 30
        discount_name = "30% Off Family Package"
        discount_type = "Family Package"
    elif discount_code.startswith("ANNUAL40"):
        discount_percentage = 40
        discount_name = "40% Off Annual Pass"
        discount_type = "Annual Pass"

    total_price = None
    discounted_price = None

    # 🎟️ Step 3: Process form submission
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            adult_tickets = form.cleaned_data.get('adult_tickets', 0)
            child_tickets = form.cleaned_data.get('child_tickets', 0)

            total_price = (
                adult_tickets * ticket_prices['Adult'] +
                child_tickets * ticket_prices['Child']
            )

            # 🧮 Step 4: Apply discount
            if discount_percentage > 0:
                discounted_price = round(total_price * (1 - discount_percentage / 100), 2)
            else:
                discounted_price = total_price
    else:
        form = BookingForm()

    # 🎯 Step 5: Render template
    return render(request, 'pages/book_tickets.html', {
        'form': form,
        'ticket_prices': ticket_prices,
        'discount_code': discount_code,
        'discount_name': discount_name,
        'discount_type': discount_type,  # <-- NEW
        'discount_percentage': discount_percentage,
        'total_price': total_price,
        'discounted_price': discounted_price,
    })

##############################################
@login_required(login_url='my-login')
def book_tickets(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save()  # save booking to database
            # ✅ Redirect to confirmation with booking ID
            return redirect('booking_confirmation', booking_id=booking.id)
    else:
        form = BookingForm()

    return render(request, 'pages/book_tickets.html', {'form': form})


from django.shortcuts import render, get_object_or_404
from .models import Booking

@login_required(login_url='my-login')
def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # ✅ Simply render the template — do NOT redirect here
    return render(request, 'pages/confirmation.html', {
        'booking': booking,
        'title': 'Booking Confirmation'
    })


###############################################
    
@login_required(login_url='my-login')
def trivia(request):
    return render(request, 'pages/trivia.html')

@login_required(login_url='my-login')
def mammal_trivia(request):
    return render(request, 'pages/mammal_trivia.html')

@login_required(login_url='my-login')
def fish_trivia(request):
    return render(request, 'pages/fish_trivia.html')

@login_required(login_url='my-login')
def reptile_trivia(request):
    return render(request, 'pages/reptile_trivia.html')

@login_required(login_url='my-login')
def birds_trivia(request):
    return render(request, 'pages/bird_trivia.html')


@login_required(login_url='my-login')
def dino_trivia(request):
    return render(request, 'pages/dino_trivia.html')
    

@login_required(login_url='my-login')
def plant_trivia(request):
    return render(request, 'pages/plant_trivia.html')

@login_required(login_url='my-login')
def bird_trivia(request):
    return render(request, 'pages/bird_trivia.html')


#################################################################

from django.shortcuts import render
from .models import TriviaQuestion

import random
# Note: This function assumes the 'render' function is available from your web framework (e.g., Django or Flask).

@login_required(login_url='my-login')
def random_trivia(request):
    """
    Selects 5 random multiple-choice trivia questions from a large pool 
    covering Reptiles, Mammals, Birds, Fishes, Dinosaurs, and Plants.
    """

    reptile_questions = [
        {"question": "What do snakes use to smell?", "answers": ["Tongue", "Nose", "Eyes"], "correct": "Tongue"},
        {"question": "Which reptile can regrow its tail?", "answers": ["Crocodile", "Lizard", "Turtle"], "correct": "Lizard"},
        {"question": "Which large snake is native to the Amazon rainforest?", "answers": ["Python", "Cobra", "Anaconda"], "correct": "Anaconda"},
        {"question": "What is a baby crocodile called?", "answers": ["Pup", "Kit", "Hatchling"], "correct": "Hatchling"},
        {"question": "Which group of reptiles is characterized by having a shell?", "answers": ["Lizards", "Snakes", "Turtles"], "correct": "Turtles"},
        {"question": "What is the fastest snake species?", "answers": ["Sidewinder", "Black Mamba", "King Cobra"], "correct": "Black Mamba"},
        {"question": "What substance makes up a reptile's scales?", "answers": ["Chitin", "Calcium", "Keratin"], "correct": "Keratin"},
        {"question": "Which famous gecko species is known for changing color?", "answers": ["Iguana", "Chameleon", "Skink"], "correct": "Chameleon"},
        {"question": "Most reptiles are ectothermic. What does that mean?", "answers": ["Warm-blooded", "Cold-blooded", "Amphibious"], "correct": "Cold-blooded"},
        {"question": "Which large monitor lizard is native to Indonesia?", "answers": ["Komodo Dragon", "Gila Monster", "Alligator"], "correct": "Komodo Dragon"},
        {"question": "How many chambers does a typical reptile heart have?", "answers": ["Two", "Three", "Four"], "correct": "Three"},
        {"question": "What term describes a snake shedding its skin?", "answers": ["Moulting", "Ecdysis", "Molting"], "correct": "Ecdysis"},
        {"question": "What is the largest living species of sea turtle?", "answers": ["Loggerhead", "Green Turtle", "Leatherback"], "correct": "Leatherback"},
        {"question": "Which reptile is often referred to as a 'living fossil'?", "answers": ["Tuatara", "Komodo Dragon", "Galapagos Tortoise"], "correct": "Tuatara"},
        {"question": "The American alligator is native to which continent?", "answers": ["South America", "Africa", "North America"], "correct": "North America"},
        {"question": "Which continent has no native snakes?", "answers": ["Australia", "Antarctica", "Europe"], "correct": "Antarctica"},
        {"question": "What is the primary diet of most turtles?", "answers": ["Herbivorous", "Carnivorous", "Omnivorous"], "correct": "Omnivorous"},
        {"question": "What venomous snake has a rattle on its tail?", "answers": ["Copperhead", "Coral Snake", "Rattlesnake"], "correct": "Rattlesnake"},
        {"question": "Which reptile can store sperm for years, allowing for delayed fertilization?", "answers": ["Crocodile", "Green Sea Turtle", "Boa Constrictor"], "correct": "Boa Constrictor"},
        {"question": "Which anatomical structure do crocodiles use to swim?", "answers": ["Front Legs", "Tail", "Scales"], "correct": "Tail"},
    ]

    mammal_questions = [
        {"question": "Which mammal lays eggs?", "answers": ["Bat", "Platypus", "Kangaroo"], "correct": "Platypus"},
        {"question": "Which family of marine mammals includes whales and dolphins?", "answers": ["Pinnipeds", "Sirenians", "Cetaceans"], "correct": "Cetaceans"},
        {"question": "What is the world's largest mammal?", "answers": ["African Elephant", "Giraffe", "Blue Whale"], "correct": "Blue Whale"},
        {"question": "What unique feature do all mammals possess?", "answers": ["Feathers", "Scales", "Mammary Glands"], "correct": "Mammary Glands"},
        {"question": "Which nocturnal mammal is known for hanging upside down?", "answers": ["Sloth", "Bat", "Koala"], "correct": "Bat"},
        {"question": "How many stomachs does a cow have?", "answers": ["One", "Two", "Four"], "correct": "Four"},
        {"question": "Which African animal is the tallest mammal on Earth?", "answers": ["Elephant", "Rhino", "Giraffe"], "correct": "Giraffe"},
        {"question": "What is a group of lions called?", "answers": ["Herd", "Pack", "Pride"], "correct": "Pride"},
        {"question": "Which mammal can retract its claws?", "answers": ["Dog", "Bear", "Cat"], "correct": "Cat"},
        {"question": "What is the only marsupial native to North America?", "answers": ["Raccoon", "Opossum", "Armadillo"], "correct": "Opossum"},
        {"question": "What is the fastest land animal?", "answers": ["Lion", "Cheetah", "Gazelle"], "correct": "Cheetah"},
        {"question": "Which large bear primarily eats bamboo?", "answers": ["Grizzly Bear", "Panda", "Polar Bear"], "correct": "Panda"},
        {"question": "Which sense is the most developed in most dogs?", "answers": ["Sight", "Smell", "Hearing"], "correct": "Smell"},
        {"question": "What is the collective noun for a group of kangaroos?", "answers": ["Mob", "Troop", "Flock"], "correct": "Mob"},
        {"question": "What specialized structure allows marine mammals to hold their breath for long periods?", "answers": ["Gills", "Swim Bladder", "Myoglobin"], "correct": "Myoglobin"},
        {"question": "Which mammal is famous for building dams in rivers?", "answers": ["Otter", "Beaver", "Marmot"], "correct": "Beaver"},
        {"question": "Which mammal has the longest lifespan?", "answers": ["Elephant", "Bowhead Whale", "Human"], "correct": "Bowhead Whale"},
        {"question": "What are young rabbits called?", "answers": ["Pups", "Kits", "Cubs"], "correct": "Kits"},
        {"question": "Which unique defense mechanism does the skunk use?", "answers": ["Playing dead", "Spraying venom", "Spraying musk"], "correct": "Spraying musk"},
        {"question": "Mammals belong to which class in taxonomy?", "answers": ["Reptilia", "Aves", "Mammalia"], "correct": "Mammalia"},
    ]

    bird_questions = [
        {"question": "Which bird can fly backward?", "answers": ["Hawk", "Eagle", "Hummingbird"], "correct": "Hummingbird"},
        {"question": "What is the largest living bird?", "answers": ["Emu", "Ostrich", "Condor"], "correct": "Ostrich"},
        {"question": "What is the function of a bird's gizzard?", "answers": ["Pumping blood", "Grinding food", "Producing oil"], "correct": "Grinding food"},
        {"question": "Which type of feather is used for insulation?", "answers": ["Flight", "Contour", "Down"], "correct": "Down"},
        {"question": "Which seabird is known for its long, narrow wings and long migrations?", "answers": ["Pelican", "Albatross", "Gull"], "correct": "Albatross"},
        {"question": "Which bird is a symbol of peace?", "answers": ["Eagle", "Dove", "Falcon"], "correct": "Dove"},
        {"question": "What is the study of birds called?", "answers": ["Entomology", "Ornithology", "Zoology"], "correct": "Ornithology"},
        {"question": "Which bird is capable of mimicking human speech?", "answers": ["Parrot", "Pigeon", "Woodpecker"], "correct": "Parrot"},
        {"question": "What is the collective noun for a group of crows?", "answers": ["Flock", "Cackle", "Murder"], "correct": "Murder"},
        {"question": "Which bird is native to Antarctica and cannot fly?", "answers": ["Puffin", "Penguin", "Pterodactyl"], "correct": "Penguin"},
        {"question": "What structure on a bird's leg helps it grip a perch while sleeping?", "answers": ["Talons", "Tendon Locking Mechanism", "Claws"], "correct": "Tendon Locking Mechanism"},
        {"question": "Which bird migrates the longest distance?", "answers": ["Barn Swallow", "Arctic Tern", "Siberian Crane"], "correct": "Arctic Tern"},
        {"question": "What is the primary component of a bird's beak?", "answers": ["Bone", "Cartilage", "Keratin"], "correct": "Keratin"},
        {"question": "Which bird is considered the smartest?", "answers": ["Pigeon", "Raven", "Sparrow"], "correct": "Raven"},
        {"question": "How many toes does a typical perching bird have?", "answers": ["Two", "Three", "Four"], "correct": "Four"},
        {"question": "Which iconic American bird was once nearly extinct due to hunting?", "answers": ["Eagle Owl", "Bald Eagle", "Osprey"], "correct": "Bald Eagle"},
        {"question": "What type of egg is typically laid by ground-nesting birds?", "answers": ["Bright Blue", "Perfectly White", "Speckled"], "correct": "Speckled"},
        {"question": "Which bird of prey is known for its spectacular diving speed?", "answers": ["Golden Eagle", "Peregrine Falcon", "Kestrel"], "correct": "Peregrine Falcon"},
        {"question": "What is the process of birds replacing old feathers?", "answers": ["Preening", "Molting", "Plumage"], "correct": "Molting"},
        {"question": "The skeleton of a bird is unique because many bones are what?", "answers": ["Heavy", "Solid", "Hollow (Pneumatic)"], "correct": "Hollow (Pneumatic)"},
    ]

    fish_questions = [
        {"question": "What organ do most fish use to breathe?", "answers": ["Lungs", "Gills", "Spleen"], "correct": "Gills"},
        {"question": "What is the world's largest fish?", "answers": ["Great White Shark", "Manta Ray", "Whale Shark"], "correct": "Whale Shark"},
        {"question": "What is a group of fish called?", "answers": ["Herd", "School", "Swarm"], "correct": "School"},
        {"question": "What bony structure protects a fish's gills?", "answers": ["Gill Raker", "Operculum", "Mandible"], "correct": "Operculum"},
        {"question": "Which fish can generate a powerful electrical discharge?", "answers": ["Catfish", "Electric Eel", "Mackerel"], "correct": "Electric Eel"},
        {"question": "Which species of fish is known for making a long migration to spawn in freshwater?", "answers": ["Tuna", "Cod", "Salmon"], "correct": "Salmon"},
        {"question": "What is the function of a fish's lateral line system?", "answers": ["Producing light", "Detecting vibrations", "Changing color"], "correct": "Detecting vibrations"},
        {"question": "What is a baby fish called?", "answers": ["Tadpole", "Fry", "Calf"], "correct": "Fry"},
        {"question": "Which fish can walk on land for short distances?", "answers": ["Trout", "Mudskipper", "Halibut"], "correct": "Mudskipper"},
        {"question": "What type of skeleton do sharks and rays have?", "answers": ["Bony", "Cartilage", "Exoskeleton"], "correct": "Cartilage"},
        {"question": "What is the specialized pouch used by seahorses for reproduction?", "answers": ["Brood Pouch", "Womb", "Incubator"], "correct": "Brood Pouch"},
        {"question": "Which predatory fish is known for its sharp teeth and aggressive feeding frenzy?", "answers": ["Swordfish", "Piranha", "Barracuda"], "correct": "Piranha"},
        {"question": "What is the process of fish reproducing by releasing eggs and sperm into the water?", "answers": ["Internal Fertilization", "Spawning", "Incubation"], "correct": "Spawning"},
        {"question": "What gives a clownfish protection from a sea anemone's sting?", "answers": ["Hard Scales", "Mucus Layer", "Poison"], "correct": "Mucus Layer"},
        {"question": "Which fish is flat and lives mostly on the ocean floor?", "answers": ["Tuna", "Flounder", "Mahi-Mahi"], "correct": "Flounder"},
        {"question": "What organ allows fish to maintain buoyancy?", "answers": ["Spleen", "Swim Bladder", "Air Sacs"], "correct": "Swim Bladder"},
        {"question": "Which fish is able to puff up into a ball of spines?", "answers": ["Stonefish", "Anglerfish", "Pufferfish"], "correct": "Pufferfish"},
        {"question": "Fish are classified as which type of animal?", "answers": ["Amphibian", "Reptile", "Vertebrate"], "correct": "Vertebrate"},
        {"question": "What is the largest freshwater fish in North America?", "answers": ["Catfish", "Sturgeon", "Pike"], "correct": "Sturgeon"},
        {"question": "What are the small, overlapping plates that cover most fish?", "answers": ["Armor", "Scales", "Scutes"], "correct": "Scales"},
    ]

    dinosaur_questions = [
        {"question": "The name 'Tyrannosaurus Rex' means what?", "answers": ["King of the Dinosaurs", "Great Clawed Hunter", "Tyrant Lizard King"], "correct": "Tyrant Lizard King"},
        {"question": "Which dinosaur is famous for having three horns?", "answers": ["Stegosaurus", "Triceratops", "Velociraptor"], "correct": "Triceratops"},
        {"question": "The extinction of the dinosaurs occurred how many years ago?", "answers": ["6.6 million", "66 million", "166 million"], "correct": "66 million"},
        {"question": "What were dinosaurs generally believed to have evolved from?", "answers": ["Birds", "Mammals", "Reptiles"], "correct": "Reptiles"},
        {"question": "Which flying reptile lived alongside dinosaurs but was not a dinosaur?", "answers": ["Pterosaur", "Icthyosaur", "Mosasaurs"], "correct": "Pterosaur"},
        {"question": "What is the largest known herbivorous dinosaur?", "answers": ["Brachiosaurus", "Triceratops", "Argentinosaurus"], "correct": "Argentinosaurus"},
        {"question": "What is a group of long-necked, plant-eating dinosaurs called?", "answers": ["Theropods", "Sauropods", "Ornithopods"], "correct": "Sauropods"},
        {"question": "Which theory suggests a massive impact caused the dinosaur extinction?", "answers": ["Volcanic Eruption Theory", "Disease Theory", "Asteroid Impact Theory"], "correct": "Asteroid Impact Theory"},
        {"question": "Which dinosaur had large bony plates running down its back?", "answers": ["Ankylosaurus", "Stegosaurus", "Apatosaurus"], "correct": "Stegosaurus"},
        {"question": "What continent was home to the most dinosaur species discovered?", "answers": ["Asia", "South America", "North America"], "correct": "North America"},
        {"question": "Which feathered dinosaur is often considered the link between dinosaurs and birds?", "answers": ["Compsognathus", "Archaeopteryx", "Microraptor"], "correct": "Archaeopteryx"},
        {"question": "What type of diet did Velociraptor have?", "answers": ["Herbivorous", "Carnivorous", "Omnivorous"], "correct": "Carnivorous"},
        {"question": "What are fossilized dinosaur droppings called?", "answers": ["Gastroliths", "Coprolites", "Trace Fossils"], "correct": "Coprolites"},
        {"question": "Which long-necked dinosaur had a whip-like tail?", "answers": ["Diplodocus", "Brachiosaurus", "Mamenchisaurus"], "correct": "Diplodocus"},
        {"question": "The Triassic, Jurassic, and Cretaceous periods make up what era?", "answers": ["Paleozoic", "Mesozoic", "Cenozoic"], "correct": "Mesozoic"},
        {"question": "Which armor-plated dinosaur used a bony club on its tail for defense?", "answers": ["Triceratops", "Ankylosaurus", "Iguanodon"], "correct": "Ankylosaurus"},
        {"question": "What feature defines an ornithischian dinosaur?", "answers": ["Lizard-hips", "Bird-hips", "Four legs"], "correct": "Bird-hips"},
        {"question": "What was the dominant theory for dinosaur body temperature regulation for decades?", "answers": ["Warm-blooded", "Cold-blooded", "Heterothermic"], "correct": "Cold-blooded"},
        {"question": "What is the name for the study of fossils and prehistoric life?", "answers": ["Archaeology", "Geology", "Paleontology"], "correct": "Paleontology"},
        {"question": "Which dinosaur name means 'Heavy-clawed lizard'?", "answers": ["Baryonyx", "Megalosaurus", "Allosaurus"], "correct": "Baryonyx"},
    ]

    plant_questions = [
        {"question": "What process do plants use to convert light into energy?", "answers": ["Respiration", "Transpiration", "Photosynthesis"], "correct": "Photosynthesis"},
        {"question": "What part of the plant absorbs water and nutrients from the soil?", "answers": ["Stem", "Leaves", "Roots"], "correct": "Roots"},
        {"question": "What gas do plants primarily absorb from the atmosphere?", "answers": ["Oxygen", "Carbon Monoxide", "Carbon Dioxide"], "correct": "Carbon Dioxide"},
        {"question": "What is the waxy outer layer of a leaf called?", "answers": ["Epidermis", "Cuticle", "Stomata"], "correct": "Cuticle"},
        {"question": "Which flower is known for following the sun's movement?", "answers": ["Rose", "Tulip", "Sunflower"], "correct": "Sunflower"},
        {"question": "What are plants that bloom for only one season called?", "answers": ["Perennials", "Biennials", "Annuals"], "correct": "Annuals"},
        {"question": "What substance gives plants their green color?", "answers": ["Carotene", "Anthocyanin", "Chlorophyll"], "correct": "Chlorophyll"},
        {"question": "The transfer of pollen from the stamen to the pistil is known as what?", "answers": ["Fertilization", "Pollination", "Germination"], "correct": "Pollination"},
        {"question": "Which type of plant produces cones instead of flowers or fruits?", "answers": ["Ferns", "Conifers", "Mosses"], "correct": "Conifers"},
        {"question": "What is the primary function of a plant's stem?", "answers": ["Anchor to soil", "Producing seeds", "Support and transport"], "correct": "Support and transport"},
        {"question": "Which plant is known for quickly folding its leaves when touched?", "answers": ["Sensitive Plant (Mimosa Pudica)", "Pitcher Plant", "Dandelion"], "correct": "Sensitive Plant (Mimosa Pudica)"},
        {"question": "What is the process by which water evaporates from plant leaves?", "answers": ["Condensation", "Transpiration", "Sublimation"], "correct": "Transpiration"},
        {"question": "What term is used for plants that grow in or on water?", "answers": ["Xerophytic", "Hydroponic", "Aquatic"], "correct": "Aquatic"},
        {"question": "Which specialized root structure stores food, such as in a carrot?", "answers": ["Fibrous Root", "Taproot", "Aerial Root"], "correct": "Taproot"},
        {"question": "What is the largest known flower in the world?", "answers": ["Lotus", "Tulip", "Rafflesia Arnoldii"], "correct": "Rafflesia Arnoldii"},
        {"question": "Which part of the plant develops into a fruit after fertilization?", "answers": ["Stamen", "Ovary", "Petal"], "correct": "Ovary"},
        {"question": "Which carnivorous plant has leaves that snap shut to trap insects?", "answers": ["Sundew", "Venus Flytrap", "Pitcher Plant"], "correct": "Venus Flytrap"},
        {"question": "What is the main purpose of a flower's petals?", "answers": ["Storing water", "Attracting pollinators", "Protecting the stem"], "correct": "Attracting pollinators"},
        {"question": "What is the primary function of the xylem tissue in a plant?", "answers": ["Transporting sugar", "Transporting water", "Storing energy"], "correct": "Transporting water"},
        {"question": "What is the process called when a seed sprouts and begins to grow?", "answers": ["Dormancy", "Germination", "Photosynthesis"], "correct": "Germination"},
    ]

    # Combine all question pools
    all_questions = reptile_questions + mammal_questions + bird_questions + fish_questions + dinosaur_questions + plant_questions

    # Select a maximum of 5 random questions from the entire pool
    selected = random.sample(all_questions, min(5, len(all_questions)))

    # In a typical web framework, 'render' would load a template and pass the data.
    # For demonstration, we assume a template 'pages/random_trivia.html' exists.
    return render(request, 'pages/random_trivia.html', {'questions': selected})



@login_required(login_url='my-login')
def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            # Optional: send email
            send_mail(
                subject=f"New message from {name}",
                message=message,
                from_email=email,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
            )

            return render(request, 'pages/success.html', {'name': name})
    else:
        form = ContactForm()

    return render(request, 'pages/contact.html', {'form': form})


def success_view(request):
    logger.info("message sent")
    return render(request, 'pages/success.html')


def apply_discount(request):
    discounted_price = None
    base_price = 100  # Example price

    if request.method == "POST":
        form = DiscountForm(request.POST)
        if form.is_valid():
            discount_type = form.cleaned_data["discount_type"]

            if discount_type == "seasonal":
                discounted_price = base_price * 0.8
            elif discount_type == "annual":
                discounted_price = base_price * 0.6
            elif discount_type == "family":
                discounted_price = base_price * 0.7
            else:
                discounted_price = base_price
    else:
        form = DiscountForm()

    return render(request, "pages/discount_form.html", {"form": form, "discounted_price": discounted_price})





