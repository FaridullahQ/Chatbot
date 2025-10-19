from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.middleware.csrf import get_token
from django.conf import settings

import json
import logging

from .services.chat_service import ChatService
from .models import ChatSession

logger = logging.getLogger(__name__)

# ============================================================
# 🧭 PAGE VIEWS
# ============================================================

def index(request):
    """Landing page"""
    return render(request, 'chat/index.html')


def chat_view(request):
    """Main chat interface page"""
    if not request.session.session_key:
        request.session.create()

    context = {
        'session_key': request.session.session_key,
        'user': request.user if request.user.is_authenticated else None,
        'csrf_token': get_token(request),
        'ai_provider': getattr(settings, 'AI_PROVIDER', 'openai').capitalize(),
    }
    return render(request, 'chat/chat.html', context)


# ============================================================
# 💬 CORE CHAT API ENDPOINTS
# ============================================================

@csrf_exempt
@require_http_methods(["POST"])
def send_message(request):
    """Send a message and get an AI response"""
    try:
        data = json.loads(request.body)
        user_message = (data.get('message') or '').strip()
        if not user_message:
            return JsonResponse({'success': False, 'error': 'Message cannot be empty'}, status=400)

        if not request.session.session_key:
            request.session.create()

        service = ChatService()
        result = service.process_user_message(
            session_key=request.session.session_key,
            user_message=user_message,
            user=request.user if request.user.is_authenticated else None
        )
        return JsonResponse(result)

    except json.JSONDecodeError as e:
        logger.error(f"[send_message] JSON decode error: {e}")
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.exception(f"[send_message] {e}")
        return JsonResponse({'success': False, 'error': 'Unexpected error occurred'}, status=500)


@require_http_methods(["GET"])
def get_messages(request):
    """Retrieve chat history for the current active session"""
    try:
        if not request.session.session_key:
            request.session.create()

        limit = int(request.GET.get('limit', 50))
        service = ChatService()
        messages = service.get_session_messages(
            session_key=request.session.session_key,
            limit=limit
        )
        return JsonResponse({'success': True, 'messages': messages})

    except Exception as e:
        logger.exception(f"[get_messages] {e}")
        return JsonResponse({'success': False, 'error': 'Failed to retrieve messages'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def clear_chat(request):
    """Clear chat history for the current session"""
    try:
        if not request.session.session_key:
            request.session.create()

        service = ChatService()
        success = service.clear_session_messages(request.session.session_key)

        if success:
            return JsonResponse({'success': True, 'message': 'Chat history cleared successfully'})
        return JsonResponse({'success': False, 'error': 'Failed to clear chat history'}, status=500)

    except Exception as e:
        logger.exception(f"[clear_chat] {e}")
        return JsonResponse({'success': False, 'error': 'Unexpected error occurred'}, status=500)


# ============================================================
# 🆕 SIDEBAR: SESSION LIST & LOADING MESSAGES
# ============================================================

@require_http_methods(["GET"])
def get_sessions(request):
    """
    📜 List all active chat sessions for sidebar navigation.
    """
    try:
        sessions = ChatSession.objects.filter(is_active=True).order_by('-created_at')
        data = [
            {
                "id": str(s.id),
                "title": s.title,
                "created_at": s.created_at.isoformat(),
            }
            for s in sessions
        ]
        return JsonResponse({'success': True, 'sessions': data})
    except Exception as e:
        logger.exception(f"[get_sessions] {e}")
        return JsonResponse({'success': False, 'error': 'Failed to load sessions'}, status=500)


@require_http_methods(["GET"])
def get_session_messages(request, session_id):
    """
    📨 Load messages of a specific session (clicked from sidebar).
    """
    try:
        session = get_object_or_404(ChatSession, id=session_id)
        messages = session.messages.order_by('timestamp')
        formatted = [
            {
                'id': str(m.id),
                'content': m.content,
                'type': m.message_type,
                'timestamp': m.timestamp.isoformat()
            }
            for m in messages
        ]
        return JsonResponse({'success': True, 'messages': formatted})
    except Exception as e:
        logger.exception(f"[get_session_messages] {e}")
        return JsonResponse({'success': False, 'error': 'Failed to load messages'}, status=500)


# ============================================================
# 🧠 CLASS-BASED CHAT API (Optional REST)
# ============================================================

@method_decorator(csrf_exempt, name='dispatch')
class ChatAPIView(View):
    """REST API for chat operations (GET/POST/DELETE)"""

    def dispatch(self, request, *args, **kwargs):
        if not request.session.session_key:
            request.session.create()
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        """Retrieve chat history"""
        try:
            limit = int(request.GET.get('limit', 50))
            service = ChatService()
            messages = service.get_session_messages(request.session.session_key, limit)
            return JsonResponse({
                'success': True,
                'messages': messages,
                'session_key': request.session.session_key
            })
        except Exception as e:
            logger.exception(f"[ChatAPIView GET] {e}")
            return JsonResponse({'success': False, 'error': 'Failed to retrieve messages'}, status=500)

    def post(self, request):
        """Send a message to the AI provider"""
        try:
            data = json.loads(request.body)
            user_message = (data.get('message') or '').strip()
            if not user_message:
                return JsonResponse({'success': False, 'error': 'Message cannot be empty'}, status=400)

            service = ChatService()
            result = service.process_user_message(
                session_key=request.session.session_key,
                user_message=user_message,
                user=request.user if request.user.is_authenticated else None
            )
            return JsonResponse(result)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            logger.exception(f"[ChatAPIView POST] {e}")
            return JsonResponse({'success': False, 'error': 'Unexpected error occurred'}, status=500)

    def delete(self, request):
        """Clear chat history for the session"""
        try:
            service = ChatService()
            success = service.clear_session_messages(request.session.session_key)
            if success:
                return JsonResponse({'success': True, 'message': 'Chat history cleared successfully'})
            return JsonResponse({'success': False, 'error': 'Failed to clear chat history'}, status=500)
        except Exception as e:
            logger.exception(f"[ChatAPIView DELETE] {e}")
            return JsonResponse({'success': False, 'error': 'Unexpected error occurred'}, status=500)


# ============================================================
# 🧪 DEBUG ENDPOINT
# ============================================================

@csrf_exempt
@require_http_methods(["GET", "POST"])
def test_api(request):
    """
    🧪 Check API health, provider keys and SDK availability
    """
    try:
        ai_provider = getattr(settings, 'AI_PROVIDER', 'openai')

        has_openai = bool(getattr(settings, 'OPENAI_API_KEY', None) and settings.OPENAI_API_KEY != 'your_openai_api_key_here')
        has_anthropic = bool(getattr(settings, 'ANTHROPIC_API_KEY', None) and settings.ANTHROPIC_API_KEY != 'your_anthropic_api_key_here')
        has_openrouter = bool(getattr(settings, 'OPENROUTER_API_KEY', None) and settings.OPENROUTER_API_KEY)

        try:
            import anthropic
            anthropic_available = True
        except ImportError:
            anthropic_available = False

        return JsonResponse({
            'success': True,
            'message': 'API is working!',
            'method': request.method,
            'ai_provider': ai_provider,
            'has_openai_key': has_openai,
            'has_anthropic_key': has_anthropic,
            'has_openrouter_key': has_openrouter,
            'anthropic_available': anthropic_available,
            'session_key': request.session.session_key or 'No session',
            'debug': settings.DEBUG
        })

    except Exception as e:
        logger.exception(f"[test_api] {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
