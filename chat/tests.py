from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
import json

from .models import ChatSession, Message, ChatbotConfiguration
from .services.chat_service import ChatService


class ChatModelsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.session = ChatSession.objects.create(
            user=self.user,
            session_key='test_session_123',
            title='Test Chat'
        )

    def test_chat_session_creation(self):
        self.assertEqual(self.session.title, 'Test Chat')
        self.assertEqual(self.session.session_key, 'test_session_123')
        self.assertTrue(self.session.is_active)

    def test_message_creation(self):
        message = Message.objects.create(
            session=self.session,
            message_type='user',
            content='Hello, world!'
        )
        self.assertEqual(message.content, 'Hello, world!')
        self.assertEqual(message.message_type, 'user')
        self.assertEqual(message.session, self.session)

    def test_message_count(self):
        Message.objects.create(session=self.session, message_type='user', content='Test 1')
        Message.objects.create(session=self.session, message_type='assistant', content='Test 2')
        self.assertEqual(self.session.get_message_count(), 2)


class ChatServiceTestCase(TestCase):
    def setUp(self):
        self.chat_service = ChatService()
        self.session_key = 'test_session_456'

    def test_get_or_create_session(self):
        session = self.chat_service.get_or_create_session(self.session_key)
        self.assertEqual(session.session_key, self.session_key)
        self.assertTrue(session.is_active)

        # Test getting existing session
        existing_session = self.chat_service.get_or_create_session(self.session_key)
        self.assertEqual(session.id, existing_session.id)

    def test_save_messages(self):
        session = self.chat_service.get_or_create_session(self.session_key)
        
        user_msg = self.chat_service.save_user_message(session, 'Hello')
        self.assertEqual(user_msg.message_type, 'user')
        self.assertEqual(user_msg.content, 'Hello')

        assistant_msg = self.chat_service.save_assistant_message(session, 'Hi there!')
        self.assertEqual(assistant_msg.message_type, 'assistant')
        self.assertEqual(assistant_msg.content, 'Hi there!')

    @patch('chat.services.openai_service.OpenAIService.get_chat_response_sync')
    def test_process_user_message(self, mock_openai):
        mock_openai.return_value = {
            'success': True,
            'message': 'Hello! How can I help you?',
            'metadata': {'tokens_used': 10}
        }

        result = self.chat_service.process_user_message(self.session_key, 'Hello')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['user_message']['content'], 'Hello')
        self.assertEqual(result['assistant_message']['content'], 'Hello! How can I help you?')


class ChatViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        ChatbotConfiguration.objects.create(
            name="Test Config",
            model_name="gpt-3.5-turbo",
            is_active=True
        )

    def test_index_view(self):
        response = self.client.get(reverse('chat:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'QaderiChat')

    def test_chat_view(self):
        response = self.client.get(reverse('chat:chat'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'chat-container')

    def test_get_messages_view(self):
        response = self.client.get(reverse('chat:get_messages'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIsInstance(data['messages'], list)

    @patch('chat.services.openai_service.OpenAIService.get_chat_response_sync')
    def test_send_message_view(self, mock_openai):
        mock_openai.return_value = {
            'success': True,
            'message': 'Test response',
            'metadata': {}
        }

        response = self.client.post(
            reverse('chat:send_message'),
            data=json.dumps({'message': 'Test message'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])

    def test_clear_chat_view(self):
        response = self.client.post(reverse('chat:clear_chat'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
