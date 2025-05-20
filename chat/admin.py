from django.contrib import admin
from .models import Conversation, Message

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('sender', 'content', 'created_at', 'is_read')

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('car', 'buyer', 'seller', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('car__brand__name', 'car__model__name', 'buyer__email', 'seller__email')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [MessageInline]

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'sender', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('content', 'sender__email', 'conversation__car__brand__name')
    readonly_fields = ('created_at',)