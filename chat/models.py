from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


# ============================================================
# 🧭 CHAT SESSION MODEL
# ============================================================

class ChatSession(models.Model):
    """
    Represents a chat session between a user and the AI assistant.
    Each session can contain multiple messages.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True,
        related_name='chat_sessions'
    )
    session_key = models.CharField(max_length=40, unique=True)
    title = models.CharField(max_length=200, default="New Chat")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = "Chat Session"
        verbose_name_plural = "Chat Sessions"

    def __str__(self):
        return f"{self.title} ({self.session_key[:8]})"

    def get_message_count(self):
        """Return number of messages in this session."""
        return self.messages.count()


# ============================================================
# 💬 MESSAGE MODEL
# ============================================================

class Message(models.Model):
    """
    Represents an individual message in a chat session.
    """
    MESSAGE_TYPES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE,
        related_name='messages'
    )
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_edited = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)  # store AI model info, token usage, etc.

    class Meta:
        ordering = ['timestamp']
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."

    def save(self, *args, **kwargs):
        """
        On save, also update the parent session's updated_at timestamp.
        """
        super().save(*args, **kwargs)
        self.session.updated_at = timezone.now()
        self.session.save(update_fields=['updated_at'])


# ============================================================
# 👤 USER PREFERENCES MODEL
# ============================================================

class UserPreferences(models.Model):
    """
    Stores user-specific UI and behavior preferences for the chatbot.
    """
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='chat_preferences'
    )
    theme = models.CharField(
        max_length=20,
        default='light',
        choices=[
            ('light', 'Light'),
            ('dark', 'Dark'),
            ('auto', 'Auto'),
        ]
    )
    language = models.CharField(max_length=10, default='en')
    chat_history_enabled = models.BooleanField(default=True)
    typing_indicators = models.BooleanField(default=True)
    sound_notifications = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Preference"
        verbose_name_plural = "User Preferences"

    def __str__(self):
        return f"Preferences for {self.user.username}"


# ============================================================
# 🤖 CHATBOT CONFIGURATION MODEL
# ============================================================

class ChatbotConfiguration(models.Model):
    """
    Global configuration for the chatbot behavior.
    (This can be used later for admin panel customization)
    """
    name = models.CharField(max_length=100, default="QaderiChat")
    model_name = models.CharField(max_length=50, default="gpt-3.5-turbo")
    max_tokens = models.IntegerField(default=150)
    temperature = models.FloatField(default=0.7)
    system_prompt = models.TextField(
        default="You are QaderiChat, a helpful AI assistant."
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Chatbot Configuration"
        verbose_name_plural = "Chatbot Configurations"

    def __str__(self):
        return f"{self.name} ({self.model_name})"
