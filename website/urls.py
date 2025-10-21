
from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name=""), # home

    path('register', views.register, name="register"), #register

    path('my-login', views.my_login, name="my-login"), #login

    path('user-logout', views.user_logout, name= "user-logout"), #logout
    
    path('dashboard', views.dashboard, name="dashboard"), #dashboard

    path('create-record/', views.create_record, name="create-record"), # Record urls
    path('update-record/<int:pk>/', views.update_record, name="update-record"),
    path('view_record/<int:pk>/', views.view_record,name="view_record"),
    path('delete-record/<int:pk>/', views.delete_record, name="delete-record"),

    path('book-tickets/', views.book_tickets, name="book-tickets"), # Tickets urls
    path('confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
    path('cancel_booking/', views.cancel_booking, name='cancel_booking'),

    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'), # Cart urls
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.view_cart, name='view_cart'),

    

]

#'add/<int:product_id>/' This is a dynamic URL pattern that contains a path converter

