from django.contrib import admin
from .models import ChatBot
# Register your models here.

class ChatBotAdmin(admin.ModelAdmin):
    list_display = ('owner', 'client', 'outbound_purpose', 'messages', 'created_at','updated_at')
    
admin.site.register(ChatBot, ChatBotAdmin)
