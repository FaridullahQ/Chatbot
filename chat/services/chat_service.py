import logging
from django.conf import settings
from django.utils import timezone
from django.contrib.sessions.models import Session

from ..models import ChatSession, Message
from .openai_service import OpenAIService
from .claude_service import ClaudeService
from .openrouter_service import openrouter_chat   # ✅ OpenRouter support

logger = logging.getLogger(__name__)

class ChatService:
    """Service class for handling chat operations"""

    def __init__(self):
        # Initialize available AI services
        self.openai_service = OpenAIService()
        self.claude_service = ClaudeService()

        # Detect active AI provider
        self.ai_provider = getattr(settings, 'AI_PROVIDER', 'openai').lower()

        # Select the service
        if self.ai_provider == 'claude':
            self.ai_service = self.claude_service
        elif self.ai_provider == 'openai':
            self.ai_service = self.openai_service
        elif self.ai_provider == 'openrouter':
            self.ai_service = None  # handled through function
        else:
            logger.warning(f"⚠️ Unknown AI provider '{self.ai_provider}', defaulting to OpenAI.")
            self.ai_service = self.openai_service

    # ============================================================
    # 📌 Session Handling
    # ============================================================
    def get_or_create_session(self, session_key: str, user=None) -> ChatSession:
        """Return existing chat session or create a new one"""
        try:
            return ChatSession.objects.get(session_key=session_key, is_active=True)
        except ChatSession.DoesNotExist:
            return ChatSession.objects.create(
                session_key=session_key,
                user=user,
                title="New Chat with QaderiChat"
            )

    # ============================================================
    # 📨 Message Saving
    # ============================================================
    def save_user_message(self, session: ChatSession, content: str) -> Message:
        return Message.objects.create(
            session=session,
            message_type='user',
            content=content
        )

    def save_assistant_message(self, session: ChatSession, content: str, metadata: dict = None) -> Message:
        return Message.objects.create(
            session=session,
            message_type='assistant',
            content=content,
            metadata=metadata or {}
        )

    # ============================================================
    # 🤖 Main Message Processing
    # ============================================================
    def process_user_message(self, session_key: str, user_message: str, user=None) -> dict:
        """
        Handles user message:
        - saves user message
        - sends to selected AI provider
        - saves assistant response
        - returns serialized response
        """
        try:
            session = self.get_or_create_session(session_key, user)

            # Save user message
            user_msg = self.save_user_message(session, user_message)

            # Route to provider
            if self.ai_provider == 'openrouter':
                ai_response = openrouter_chat(user_message)
            else:
                ai_response = self.ai_service.get_chat_response_sync(session, user_message)

            # ✅ Handle AI success
            if ai_response.get('success'):
                assistant_msg = self.save_assistant_message(
                    session,
                    ai_response['message'],
                    ai_response.get('metadata', {})
                )

                # Update title if first interaction
                if session.get_message_count() <= 2:
                    session.title = self._generate_session_title(user_message)
                    session.save(update_fields=["title"])

                return {
                    'success': True,
                    'user_message': self._serialize_message(user_msg),
                    'assistant_message': self._serialize_message(assistant_msg),
                    'session_id': str(session.id),
                    'metadata': ai_response.get('metadata', {})
                }

            # ❌ Handle AI error
            error_msg = self.save_assistant_message(
                session,
                ai_response.get('message', '⚠️ An error occurred')
            )
            return {
                'success': False,
                'user_message': self._serialize_message(user_msg),
                'assistant_message': self._serialize_message(error_msg),
                'error': ai_response.get('error', 'Unknown error'),
                'session_id': str(session.id)
            }

        except Exception as e:
            logger.exception("❌ Error processing user message")
            return {
                'success': False,
                'error': str(e),
                'message': 'An error occurred while processing your message.'
            }

    # ============================================================
    # 🕑 Session History Utilities
    # ============================================================
    def get_session_messages(self, session_key: str, limit: int = 50) -> list:
        """Return messages of a specific session (used for sidebar loading)"""
        try:
            session = ChatSession.objects.get(session_key=session_key, is_active=True)
            messages = session.messages.order_by('timestamp')[:limit]
            return [self._serialize_message(msg) for msg in messages]
        except ChatSession.DoesNotExist:
            return []
        except Exception as e:
            logger.error(f"Error getting session messages: {e}")
            return []

    def clear_session_messages(self, session_key: str) -> bool:
        """Clear all messages in a session"""
        try:
            session = ChatSession.objects.get(session_key=session_key, is_active=True)
            session.messages.all().delete()
            session.title = "New Chat with QaderiChat"
            session.save(update_fields=["title"])
            return True
        except ChatSession.DoesNotExist:
            return False
        except Exception as e:
            logger.error(f"Error clearing session messages: {e}")
            return False

    # ============================================================
    # 📝 Helper Methods
    # ============================================================
    def _generate_session_title(self, first_message: str) -> str:
        """Generate a session title from the first user message"""
        words = first_message.split()[:5]
        title = ' '.join(words)
        title = title.strip()
        if len(title) > 50:
            title = title[:47] + "..."
        return title or "Chat with QaderiChat"

    def _serialize_message(self, msg: Message) -> dict:
        """Convert message object to JSON-friendly dict"""
        return {
            'id': str(msg.id),
            'content': msg.content,
            'type': msg.message_type,
            'timestamp': msg.timestamp.isoformat(),
            'metadata': msg.metadata
        }
