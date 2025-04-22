from django.contrib import admin
from .models import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'timestamp', 'message_type')
    list_filter = ('message_type', 'timestamp', 'user')
    search_fields = ('content', 'user__username')
