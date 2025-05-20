from django.db import models
from django.conf import settings


class ChatbotIntent(models.Model):
    """Model to store chatbot intents and responses"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    pattern = models.TextField(help_text="Comma-separated patterns to match this intent")
    response = models.TextField(help_text="Response template for this intent")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ChatSession(models.Model):
    """Model to store chatbot sessions"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Session {self.session_id}"


class ChatMessage(models.Model):
    """Model to store chat messages"""
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    user_message = models.TextField()
    bot_response = models.TextField()
    intent = models.ForeignKey(ChatbotIntent, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message in {self.session}"
