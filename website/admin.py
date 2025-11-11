from django.contrib import admin

# Register your models here.

from . models import Record,TicketType
from django.contrib import admin
from .models import RewardProfile

admin.site.register(Record)  #a model for recording people from the admin
admin.site.register(TicketType)  # a for recording a ticket type e.g children


@admin.register(RewardProfile)
class RewardProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_purchases', 'points')



