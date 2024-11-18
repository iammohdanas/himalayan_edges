from django.contrib import admin
from mainapp.models import Bookings, Contact, Message, Tour, Agent
from django.contrib import admin
from .models import LoginLogoutActivity

@admin.register(LoginLogoutActivity)
class LoginLogoutActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_time', 'logout_time')
    readonly_fields = ('user', 'login_time', 'logout_time')

# Register your models here.
admin.site.register(Contact)
admin.site.register(Tour)
admin.site.register(Message)
admin.site.register(Bookings)
admin.site.register(Agent)