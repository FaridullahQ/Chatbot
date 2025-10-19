from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # 🌐 Main pages
    path('', views.index, name='index'),
    path('chat/', views.chat_view, name='chat'),

    # 💬 Core Chat API
    path('api/send-message/', views.send_message, name='send_message'),
    path('api/chat/', views.send_message, name='chat_api'),  # Alias for frontend

    # 🕑 Sessions & History (Sidebar Navigation)
    path('api/get-messages/', views.get_messages, name='get_messages'),  # Current session messages
    path('api/clear-chat/', views.clear_chat, name='clear_chat'),        # Clear current session
    path('api/get-sessions/', views.get_sessions, name='get_sessions'),  # List all chat sessions
    path('api/get-session-messages/<uuid:session_id>/', 
         views.get_session_messages, name='get_session_messages'),       # Load messages for a session

    # 🧪 Debug
    path('api/test/', views.test_api, name='test_api'),
]
