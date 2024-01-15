from django.contrib import admin
from .models import Client
# from .models import Marketing
# Register your models here.


class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'location', 'number', 'email')
    
admin.site.register(Client, ClientAdmin)
# admin.site.register(Marketing)
