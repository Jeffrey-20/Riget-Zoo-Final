from django.contrib import admin

# Register your models here.

from . models import Record,TicketType

admin.site.register(Record)  #a model for recording people from the admin
admin.site.register(TicketType)  # a for recording a ticket type e.g children