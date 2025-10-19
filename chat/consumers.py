import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .services.chat_service import ChatService
from .models import ChatSession

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time chat functionality"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to QaderiChat'
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'chat_message')
            
            if message_type == 'chat_message':
                await self.handle_chat_message(text_data_json)
            elif message_type == 'typing_indicator':
                await self.handle_typing_indicator(text_data_json)
            elif message_type == 'clear_chat':
                await self.handle_clear_chat(text_data_json)
            else:
                await self.send_error('Unknown message type')
                
        except json.JSONDecodeError:
            await self.send_error('Invalid JSON format')
        except Exception as e:
            logger.error(f"Error in WebSocket receive: {e}")
            await self.send_error('An error occurred processing your message')
    
    async def handle_chat_message(self, data):
        """Handle chat message"""
        try:
            user_message = data.get('message', '').strip()
            session_key = data.get('session_key', self.room_name)
            
            if not user_message:
                await self.send_error('Message cannot be empty')
                return
            
            # Send typing indicator to room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_status',
                    'is_typing': True,
                    'user': 'QaderiChat'
                }
            )
            
            # Process message using chat service
            result = await self.process_message_async(session_key, user_message)
            
            # Stop typing indicator
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_status',
                    'is_typing': False,
                    'user': 'QaderiChat'
                }
            )
            
            # Send response to room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message_response',
                    'data': result
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling chat message: {e}")
            await self.send_error('Failed to process message')
    
    async def handle_typing_indicator(self, data):
        """Handle typing indicator"""
        is_typing = data.get('is_typing', False)
        user = data.get('user', 'User')
        
        # Broadcast typing status to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_status',
                'is_typing': is_typing,
                'user': user
            }
        )
    
    async def handle_clear_chat(self, data):
        """Handle clear chat request"""
        try:
            session_key = data.get('session_key', self.room_name)
            success = await self.clear_chat_async(session_key)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_cleared',
                    'success': success
                }
            )
            
        except Exception as e:
            logger.error(f"Error clearing chat: {e}")
            await self.send_error('Failed to clear chat')
    
    async def chat_message_response(self, event):
        """Send chat message response to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'chat_response',
            'data': event['data']
        }))
    
    async def typing_status(self, event):
        """Send typing status to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'typing_indicator',
            'is_typing': event['is_typing'],
            'user': event['user']
        }))
    
    async def chat_cleared(self, event):
        """Send chat cleared notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'chat_cleared',
            'success': event['success']
        }))
    
    async def send_error(self, message):
        """Send error message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))
    
    @database_sync_to_async
    def process_message_async(self, session_key, user_message):
        """Process message asynchronously"""
        chat_service = ChatService()
        return chat_service.process_user_message(session_key, user_message)
    
    @database_sync_to_async
    def clear_chat_async(self, session_key):
        """Clear chat asynchronously"""
        chat_service = ChatService()
        return chat_service.clear_session_messages(session_key)
