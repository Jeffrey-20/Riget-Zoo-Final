
from django.urls import path
from . import views
from django.urls import path
from django.contrib.auth import views as auth_views


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

    path('trivia/', views.trivia, name='trivia'),
    path('reptile-trivia/', views.reptile_trivia, name='reptile_trivia'),
    path('mammal-trivia/', views.mammal_trivia, name='mammal_trivia'),
    path('birds-trivia/', views.bird_trivia, name='bird_trivia'),
    path('fish-trivia/', views.fish_trivia, name='fish_trivia'),
    path('dino-trivia/', views.dino_trivia, name='dino_trivia'),
    path('plants-trivia/', views.plant_trivia, name='plant_trivia'),
    path('trivia/', views.trivia, name='trivia'),
    path('trivia/random/', views.random_trivia, name='random_trivia'),

     path('contact/', views.contact_view, name='contact'),
     path('success/', views.success_view, name='success'),

    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='pages/password_reset_form.html',
            email_template_name='pages/password_reset_email.html',
            subject_template_name='pages/password_reset_subject.txt',
            success_url='/password-reset/done/',
        ),
        name='password_reset'
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='pages/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='pages/password_reset_confirm.html',
            success_url='/password-reset/complete/'
        ),
        name='password_reset_confirm'
    ),
    path(
        'password-reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='pages/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),

      # 🆕 New discount form URL
    path('discount/', views.apply_discount, name='apply_discount'),

]

#'add/<int:product_id>/' This is a dynamic URL pattern that contains a path converter


