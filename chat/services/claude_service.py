import logging
from django.conf import settings
from typing import List, Dict, Optional
from ..models import ChatbotConfiguration, Message, ChatSession

logger = logging.getLogger(__name__)

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic library not installed. Claude API will not be available.")


class ClaudeService:
    """Service class for handling Anthropic Claude API interactions"""
    
    def __init__(self):
        # Only initialize Claude client if API key is properly configured and library is available
        if (ANTHROPIC_AVAILABLE and 
            settings.ANTHROPIC_API_KEY and 
            settings.ANTHROPIC_API_KEY != 'your_anthropic_api_key_here'):
            self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        else:
            self.client = None
        self.default_config = self._get_default_config()
    
    def _get_default_config(self) -> ChatbotConfiguration:
        """Get the active chatbot configuration"""
        try:
            config = ChatbotConfiguration.objects.filter(is_active=True).first()
            if not config:
                # Create default configuration for Claude
                config = ChatbotConfiguration.objects.create(
                    name="QaderiChat",
                    model_name="claude-3-haiku-20240307",
                    max_tokens=300,
                    temperature=0.8,
                    system_prompt="""You are QaderiChat, a friendly, engaging, and socially intelligent AI assistant created by Qaderi. 

Your personality:
- Warm, conversational, and approachable
- Curious about the user's thoughts and experiences
- Able to discuss any topic with enthusiasm and knowledge
- Good at keeping conversations flowing naturally
- Empathetic and emotionally intelligent
- Has a good sense of humor when appropriate

Conversation style:
- Ask follow-up questions to keep conversations engaging
- Share interesting insights and perspectives
- Use a natural, friendly tone (not overly formal)
- Remember context from the conversation
- Be genuinely interested in what the user has to say
- Adapt your communication style to match the user's energy

Topics you excel at:
- Current events and news
- Technology and science
- Entertainment (movies, music, books, games)
- Philosophy and deep thoughts
- Personal development and life advice
- Hobbies and interests
- Travel and culture
- Food and cooking
- Sports and fitness
- Art and creativity
- Relationships and social dynamics
- Career and education
- And literally any other topic the user wants to explore!

Always aim to be helpful, engaging, and make the conversation enjoyable for the user."""
                )
            return config
        except Exception as e:
            logger.error(f"Error getting chatbot configuration: {e}")
            # Return a default configuration object
            return ChatbotConfiguration(
                name="QaderiChat",
                model_name="claude-3-haiku-20240307",
                max_tokens=300,
                temperature=0.8,
                system_prompt="You are QaderiChat, a friendly AI assistant."
            )
    
    def _prepare_messages(self, session: ChatSession, user_message: str) -> List[Dict[str, str]]:
        """Prepare messages for the Claude API call"""
        messages = []
        
        # Add conversation history (last 10 messages to stay within token limits)
        recent_messages = session.messages.order_by('-timestamp')[:10]
        for msg in reversed(recent_messages):
            if msg.message_type == 'user':
                messages.append({"role": "user", "content": msg.content})
            elif msg.message_type == 'assistant':
                messages.append({"role": "assistant", "content": msg.content})
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def get_chat_response_sync(self, session: ChatSession, user_message: str) -> Dict[str, any]:
        """
        Get a response from Claude API
        """
        # Check if Claude API is properly configured
        if not self.client:
            return self._get_demo_response(user_message)
        
        try:
            # Prepare messages for the API call
            messages = self._prepare_messages(session, user_message)
            
            # Make the API call to Claude
            response = self.client.messages.create(
                model=self.default_config.model_name,
                max_tokens=self.default_config.max_tokens,
                temperature=self.default_config.temperature,
                system=self.default_config.system_prompt,
                messages=messages
            )
            
            # Extract the response content
            assistant_message = response.content[0].text
            
            # Prepare metadata
            metadata = {
                'model': self.default_config.model_name,
                'tokens_used': response.usage.input_tokens + response.usage.output_tokens,
                'input_tokens': response.usage.input_tokens,
                'output_tokens': response.usage.output_tokens,
                'provider': 'claude'
            }
            
            return {
                'success': True,
                'message': assistant_message,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Error in Claude service: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': "I'm sorry, I'm having trouble processing your request right now."
            }
    
    def _get_demo_response(self, user_message: str) -> Dict[str, any]:
        """
        Provide engaging demo responses when Claude API is not configured
        """
        demo_responses = {
            'hello': "Hey there! 👋 I'm QaderiChat, powered by Claude! I'm excited to chat with you about absolutely anything. Whether you want to dive deep into philosophy, share what's on your mind, discuss your latest obsessions, or just have a fun conversation - I'm all ears! What's going on in your world today? (Currently in demo mode - add your Anthropic API key for full Claude conversations!)",
            
            'how_are_you': "I'm doing wonderfully, thanks for asking! 😊 I love connecting with people and having meaningful conversations. How are YOU doing? What's been the highlight of your day so far? Or if it's been challenging, I'm here to listen and chat about whatever you need!",
            
            'music': "Music is such a universal language! 🎵 I find it fascinating how different genres can evoke completely different emotions and memories. What kind of music speaks to your soul? Are you someone who discovers new artists constantly, or do you have those timeless favorites you return to?",
            
            'movies': "Cinema is such an incredible art form! 🎬 I love how movies can transport us to different worlds and make us feel so deeply. Are you more drawn to thought-provoking films that stick with you for days, or do you prefer something that's pure entertainment and fun?",
            
            'books': "Books are like portable adventures for the mind! 📚 There's something magical about getting completely absorbed in a story or learning something that changes your perspective. What's been capturing your reading attention lately? Fiction, non-fiction, or a bit of both?",
            
            'food': "Food is one of life's greatest pleasures! 🍕 It's not just about sustenance - it's about culture, memories, and bringing people together. Are you someone who loves experimenting with new cuisines, or do you have those comfort foods that never get old?",
            
            'travel': "Travel is such a beautiful way to expand our horizons! ✈️ Even if it's just exploring a new part of your own city, there's always something exciting about discovering new places and perspectives. What's a place that's captured your imagination recently?",
            
            'technology': "We're living in such a fascinating time technologically! 🚀 The pace of change is incredible. Are you excited about where technology is heading, or do you sometimes feel like it's all moving a bit too fast? I find both perspectives really valid!",
            
            'philosophy': "Philosophy is where things get really interesting! 🤔 Those big questions about existence, meaning, consciousness... they're endlessly fascinating. What's a philosophical question or idea that's been on your mind lately?",
            
            'life': "Life is such an incredible journey, isn't it? 🌟 Full of unexpected moments, growth, challenges, and beautiful surprises. What's something about life that's been on your mind recently? Could be anything - big or small!",
            
            'joke': "Here's one that always makes me smile: Why don't scientists trust atoms? Because they make up everything! 😄 But honestly, I think the best humor comes from those unexpected moments in everyday life. What kind of things make you laugh?",
            
            'help': "I'm here for whatever kind of conversation you need! 🌟 Whether you want to explore deep topics, share what's on your mind, get a different perspective on something, or just chat about your interests - I'm genuinely excited to connect with you. What feels right for you today?"
        }
        
        # Enhanced keyword matching for social conversation
        user_lower = user_message.lower()
        
        # Greetings
        if any(word in user_lower for word in ['hello', 'hi', 'hey', 'howdy', 'greetings']):
            response = demo_responses['hello']
        
        # How are you / feelings
        elif any(phrase in user_lower for phrase in ['how are you', 'how do you feel', 'how\'s it going', 'what\'s up']):
            response = demo_responses['how_are_you']
        
        # Entertainment & culture
        elif any(word in user_lower for word in ['music', 'song', 'band', 'artist', 'album']):
            response = demo_responses['music']
        elif any(word in user_lower for word in ['movie', 'film', 'cinema', 'netflix', 'tv show']):
            response = demo_responses['movies']
        elif any(word in user_lower for word in ['book', 'read', 'novel', 'author', 'literature']):
            response = demo_responses['books']
        
        # Lifestyle
        elif any(word in user_lower for word in ['food', 'eat', 'cooking', 'recipe', 'restaurant']):
            response = demo_responses['food']
        elif any(word in user_lower for word in ['travel', 'trip', 'vacation', 'country', 'city']):
            response = demo_responses['travel']
        
        # Technology & deep topics
        elif any(word in user_lower for word in ['technology', 'tech', 'ai', 'computer', 'future']):
            response = demo_responses['technology']
        elif any(word in user_lower for word in ['philosophy', 'meaning', 'purpose', 'existence']):
            response = demo_responses['philosophy']
        elif any(word in user_lower for word in ['life', 'living', 'experience', 'journey']):
            response = demo_responses['life']
        
        # Fun requests
        elif any(word in user_lower for word in ['joke', 'funny', 'humor', 'laugh']):
            response = demo_responses['joke']
        elif any(phrase in user_lower for phrase in ['help', 'what can you', 'what do you do']):
            response = demo_responses['help']
        
        # Default engaging response
        else:
            engaging_responses = [
                f"That's really interesting! You mentioned '{user_message}' - I'd love to hear more about your thoughts on that. What drew you to this topic? 🤔 (Demo mode - add Anthropic API key for full Claude conversations!)",
                f"Ooh, '{user_message}' is such a fascinating subject! I find there are always so many different angles to explore. What's your personal take on this? 💭 (Claude demo mode active)",
                f"You know what I love about '{user_message}'? There's always more depth to discover! What aspect of this interests you most? I'm genuinely curious! 🌟 (Add Anthropic API key for unlimited Claude chat!)",
                f"Thanks for bringing up '{user_message}'! It's amazing how every person brings such unique perspectives to different topics. What's been your experience with this? 😊 (Demo mode - full Claude coming soon!)"
            ]
            import random
            response = random.choice(engaging_responses)
        
        return {
            'success': True,
            'message': response,
            'metadata': {
                'model': 'claude-demo-mode',
                'tokens_used': 0,
                'provider': 'claude-demo'
            }
        }
