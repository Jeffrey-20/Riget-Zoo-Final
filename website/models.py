from django.db import models
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.core.validators import RegexValidator, EmailValidator

# Create your models here.

class Record(models.Model):  # Model for the record in dashboard
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    creation_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.first_name + " " + self.last_name
    




class TicketType(models.Model):
    """Defines the different types of tickets and their base prices."""
    name = models.CharField(max_length=50, unique=True) # e.g., 'Adult', 'Child', 'Senior'
    base_price = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0.01)])

    def __str__(self):
        return f"{self.name} (${self.base_price})"

# website/models.py
class Booking(models.Model):
    # --- REQUIRED CUSTOMER DETAIL FIELDS ---
    customer_name = models.CharField(max_length=100)
    email = models.EmailField()
    
    # --- TICKET FIELDS ---
    adult_tickets = models.IntegerField(default=0)
    child_tickets = models.IntegerField(default=0)
    
    # --- DATE/TIME FIELDS ---
    booking_date = models.DateField()
    
    # --- STORED PRICE FIELD (REQUIRED for the save() logic to work) ---
    # We must define 'total_price' as a field if we want to set it in save()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0) 

#Cancellation fields
    is_cancelled = models.BooleanField(default=False)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    # --- OPTIONAL: AUTO TIMESTAMPS ---
    created_at = models.DateTimeField(default=timezone.now)

    def cancel(self):
        """Marks a booking as cancelled."""
        self.is_cancelled = True
        self.cancelled_at = timezone.now()
        self.save()

    def __str__(self):
        status = "Cancelled" if self.is_cancelled else "Active"
        return f"{self.customer_name} ({self.booking_date}) - {status}"





    def calculate_total_price(self):
        """Calculates and returns the total price based on current ticket counts."""
        try:
            # Assuming you have TicketType objects named 'Adult' and 'Child'
            adult_price = TicketType.objects.get(name='Adult').base_price
            child_price = TicketType.objects.get(name='Child').base_price

            print(f"DEBUG: Adult Price Found: {adult_price}")
            print(f"DEBUG: Child Price Found: {child_price}")
            print(f"DEBUG: Booking counts: Adult={self.adult_tickets}, Child={self.child_tickets}")
        
            total = (
                (self.adult_tickets * adult_price) +
                (self.child_tickets * child_price)
            )
        
            print(f"DEBUG: Calculated Total: {total}")
            return round(total, 2)
            
        except TicketType.DoesNotExist:
           print("ERROR: TicketType 'Adult' or 'Child' does not exist in the database!")
           return 0.00
       


    def save(self, *args, **kwargs):
        """Overrides save to automatically calculate total price before saving."""
        
        # FIX: The method self.calculate_total_price() is now defined above.
        self.total_price = self.calculate_total_price()

        print("BOOKING:SAVE: ", self.total_price)
        
        super().save(*args, **kwargs)

    
    def __str__(self):
        # FIX: The __str__ method was defined twice; keep only one.
        return f"Booking for {self.customer_name} on {self.booking_date} (Total: ${self.total_price})"



class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='shop_images/', blank=True, null=True)

    def __str__(self):
        return self.name


from django.db import models
import random

class TriviaQuestion(models.Model):
    CATEGORY_CHOICES = [
        ('reptile', 'Reptile'),
        ('mammal', 'Mammal'),
        ('bird', 'Bird'),
    ]
    question_text = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    option_a = models.CharField(max_length=100)
    option_b = models.CharField(max_length=100)
    option_c = models.CharField(max_length=100)
    correct_answer = models.CharField(max_length=1, choices=[('A','A'),('B','B'),('C','C')])

    def __str__(self):
        return f"{self.question_text} ({self.category})"

    @staticmethod
    def get_random_questions(n=5):
        """Get n random questions across all categories."""
        questions = list(TriviaQuestion.objects.all())
        random.shuffle(questions)
        return questions[:n]






