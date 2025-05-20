from django.contrib import admin
from .models import ChatbotIntent, ChatSession, ChatMessage

@admin.register(ChatbotIntent)
class ChatbotIntentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'pattern', 'response')

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'user', 'created_at')
    search_fields = ('session_id', 'user__username')

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'user_message', 'bot_response', 'created_at')
    list_filter = ('session', 'created_at')
    search_fields = ('user_message', 'bot_response')
