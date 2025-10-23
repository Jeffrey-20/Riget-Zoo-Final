from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Record
from django import forms
from .models import Booking
from datetime import date

# User Registration form
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


# Login form
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))


# Record creation form
class CreateRecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'city']



#Update Record Form
class UpdateRecordForm(forms.ModelForm):
    class Meta:
        model= Record
        fields =['first_name', 'last_name', 'email', 'phone', 'address', 'city']


#A class for booking 
class BookingForm(forms.ModelForm):
    # This field uses the HTML5 'date' input type for a native calendar/date picker
    booking_date = forms.DateField(
        label='Select Visit Date',
        widget=forms.DateInput(attrs={'type': 'date', 'min': date.today().isoformat()}),
        initial=date.today
    )

    class Meta:
        model = Booking
        fields = ['booking_date', 'adult_tickets', 'child_tickets',  'customer_name', 'email']
        widgets = {
            # Ensure ticket counts can't be negative
            'adult_tickets': forms.NumberInput(attrs={'min': 1, 'max': 50}), 
            'child_tickets': forms.NumberInput(attrs={'min': 0, 'max': 50}),  
        }

    def clean(self):
        """Custom validation to ensure at least one ticket is selected."""
        cleaned_data = super().clean()
        adults = cleaned_data.get('adult_tickets', 0)
        children = cleaned_data.get('child_tickets', 0)
     

        # Check that the sum of tickets is greater than zero
        if adults + children  == 0:
            raise forms.ValidationError("You must select at least one ticket to proceed.")

        return cleaned_data
    
# This class is responsible for cancelling bookings
class CancelBookingForm(forms.Form):
    email = forms.EmailField(label="Enter your email to cancel booking")
    booking_id = forms.IntegerField(label="Booking ID")

    def clean(self):
        """ This is validation for ensuring deletion of bookings"""
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        booking_id = cleaned_data.get("booking_id")

        # This is validation for removing bookings
        try:
            booking = Booking.objects.get(id=booking_id, email=email)
        except Booking.DoesNotExist:
            raise forms.ValidationError("No booking found for that email and ID.")

        if booking.is_cancelled:
            raise forms.ValidationError("This booking has already been cancelled.")

        cleaned_data["booking"] = booking
        return cleaned_data



class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label='Your Name')
    email = forms.EmailField(label='Your Email')
    message = forms.CharField(widget=forms.Textarea, label='Message')


    
