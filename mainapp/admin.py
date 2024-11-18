from django.contrib import admin

from mainapp.models import Bookings, Contact, Message, Review, Tour, Agent

# Register your models here.
admin.site.register(Contact)
admin.site.register(Tour)
admin.site.register(Message)
admin.site.register(Bookings)
admin.site.register(Agent)
admin.site.register(Review)