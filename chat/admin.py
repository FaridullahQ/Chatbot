from django.contrib import admin
from .models import ChatSession, Message, UserPreferences, ChatbotConfiguration


# ============================================================
# 🧭 CHAT SESSION ADMIN
# ============================================================

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'session_key', 'user', 'created_at',
        'updated_at', 'is_active'
    ]
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['title', 'session_key', 'user__username']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-updated_at']
    list_per_page = 25

    fieldsets = (
        ('Basic Info', {
            'fields': ('id', 'title', 'session_key', 'user', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def get_queryset(self, request):
        """
        Optimize queryset to fetch related user data.
        """
        return super().get_queryset(request).select_related('user')


# ============================================================
# 💬 MESSAGE ADMIN
# ============================================================

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [
        'session', 'message_type', 'content_preview',
        'timestamp', 'is_edited'
    ]
    list_filter = ['message_type', 'timestamp', 'is_edited']
    search_fields = ['content', 'session__title']
    readonly_fields = ['id', 'timestamp']
    ordering = ['-timestamp']
    list_per_page = 50

    fieldsets = (
        ('Message Details', {
            'fields': ('id', 'session', 'message_type', 'content', 'is_edited', 'metadata')
        }),
        ('Timestamp', {
            'fields': ('timestamp',)
        }),
    )

    def content_preview(self, obj):
        """
        Display a truncated preview of the message content in admin list.
        """
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content Preview'

    def get_queryset(self, request):
        """
        Optimize queryset with related session for performance.
        """
        return super().get_queryset(request).select_related('session')


# ============================================================
# 👤 USER PREFERENCES ADMIN
# ============================================================

@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'theme', 'language',
        'chat_history_enabled', 'typing_indicators', 'updated_at'
    ]
    list_filter = ['theme', 'language', 'chat_history_enabled', 'typing_indicators']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 25

    fieldsets = (
        ('User Settings', {
            'fields': ('user', 'theme', 'language', 'chat_history_enabled', 'typing_indicators', 'sound_notifications')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


# ============================================================
# 🤖 CHATBOT CONFIGURATION ADMIN
# ============================================================

@admin.register(ChatbotConfiguration)
class ChatbotConfigurationAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'model_name', 'max_tokens',
        'temperature', 'is_active', 'updated_at'
    ]
    list_filter = ['model_name', 'is_active', 'created_at']
    search_fields = ['name', 'model_name']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 25

    fieldsets = (
        ('Configuration Details', {
            'fields': ('name', 'model_name', 'max_tokens', 'temperature', 'system_prompt', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
