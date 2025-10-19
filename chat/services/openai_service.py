import openai
import logging
from django.conf import settings
from typing import List, Dict, Optional
from ..models import ChatbotConfiguration, Message, ChatSession

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service class for handling OpenAI API interactions"""
    
    def __init__(self):
        # Only initialize OpenAI client if API key is properly configured
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != 'your_openai_api_key_here':
            self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None
        self.default_config = self._get_default_config()
    
    def _get_default_config(self) -> ChatbotConfiguration:
        """Get the active chatbot configuration"""
        try:
            config = ChatbotConfiguration.objects.filter(is_active=True).first()
            if not config:
                # Create default configuration if none exists
                config = ChatbotConfiguration.objects.create(
                    name="QaderiChat",
                    model_name="gpt-3.5-turbo",
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
                model_name="gpt-3.5-turbo",
                max_tokens=150,
                temperature=0.7,
                system_prompt="You are QaderiChat, a helpful AI assistant."
            )
    
    def _prepare_messages(self, session: ChatSession, user_message: str) -> List[Dict[str, str]]:
        """Prepare messages for the OpenAI API call"""
        messages = []
        
        # Add system message
        messages.append({
            "role": "system",
            "content": self.default_config.system_prompt
        })
        
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
    
    async def get_chat_response(self, session: ChatSession, user_message: str) -> Dict[str, any]:
        """
        Get a response from OpenAI's ChatGPT API
        
        Args:
            session: The chat session
            user_message: The user's message
            
        Returns:
            Dict containing response data and metadata
        """
        try:
            # Prepare messages for the API call
            messages = self._prepare_messages(session, user_message)
            
            # Make the API call
            response = self.client.chat.completions.create(
                model=self.default_config.model_name,
                messages=messages,
                max_tokens=self.default_config.max_tokens,
                temperature=self.default_config.temperature,
                stream=False
            )
            
            # Extract the response content
            assistant_message = response.choices[0].message.content
            
            # Prepare metadata
            metadata = {
                'model': response.model,
                'tokens_used': response.usage.total_tokens,
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'finish_reason': response.choices[0].finish_reason
            }
            
            return {
                'success': True,
                'message': assistant_message,
                'metadata': metadata
            }
            
        except openai.AuthenticationError:
            logger.error("OpenAI API authentication failed")
            return {
                'success': False,
                'error': 'Authentication failed. Please check your API key.',
                'message': "I'm sorry, but I'm having trouble connecting to my AI service. Please check the API configuration."
            }
            
        except openai.RateLimitError:
            logger.error("OpenAI API rate limit exceeded")
            return {
                'success': False,
                'error': 'Rate limit exceeded',
                'message': "I'm currently receiving too many requests. Please try again in a moment."
            }
            
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return {
                'success': False,
                'error': f'API error: {str(e)}',
                'message': "I'm experiencing some technical difficulties. Please try again later."
            }
            
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI service: {e}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'message': "Something went wrong. Please try again."
            }
    
    def get_chat_response_sync(self, session: ChatSession, user_message: str) -> Dict[str, any]:
        """
        Synchronous version of get_chat_response for use in regular Django views
        """
        # Check if API key is properly configured
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == 'your_openai_api_key_here':
            return self._get_demo_response(user_message)

        try:
            # Prepare messages for the API call
            messages = self._prepare_messages(session, user_message)

            # Make the API call
            response = self.client.chat.completions.create(
                model=self.default_config.model_name,
                messages=messages,
                max_tokens=self.default_config.max_tokens,
                temperature=self.default_config.temperature,
                stream=False
            )

            # Extract the response content
            assistant_message = response.choices[0].message.content

            # Prepare metadata
            metadata = {
                'model': response.model,
                'tokens_used': response.usage.total_tokens,
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'finish_reason': response.choices[0].finish_reason
            }

            return {
                'success': True,
                'message': assistant_message,
                'metadata': metadata
            }

        except Exception as e:
            logger.error(f"Error in sync OpenAI service: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': "I'm sorry, I'm having trouble processing your request right now."
            }

    def _get_demo_response(self, user_message: str) -> Dict[str, any]:
        """
        Provide engaging demo responses when OpenAI API key is not configured
        """
        demo_responses = {
            'hello': "Hey there! 👋 I'm QaderiChat, and I'm excited to chat with you! I love talking about literally anything - from deep philosophical questions to what you had for breakfast. What's on your mind today? (Currently in demo mode - add your OpenAI API key for even more engaging conversations!)",

            'joke': "Here's one for you: Why don't scientists trust atoms? Because they make up everything! 😄 But seriously, I love a good laugh! Do you have any favorite types of humor? Stand-up, puns, dad jokes? I'm always up for sharing more! (Demo mode - real AI will have endless jokes!)",

            'help': "I'm here to chat about absolutely anything! 🌟 Want to discuss your latest Netflix binge? Debate whether pineapple belongs on pizza? Talk about your dreams and goals? Share a random shower thought? I'm genuinely interested in whatever you want to explore! (Add OpenAI API key for unlimited conversation topics!)",

            'how_are_you': "I'm doing great, thanks for asking! 😊 I'm always energized by good conversation. How are YOU doing? What's been the highlight of your day so far? Or if it's been rough, I'm here to listen too!",

            'music': "Oh, I love talking about music! 🎵 There's something magical about how a song can instantly transport you to a memory or change your whole mood. What kind of music gets you pumped up? Any songs you've had on repeat lately?",

            'movies': "Movies are such a great escape! 🎬 I'm curious - are you more of a 'watch the same comfort movie 100 times' person or a 'always trying something new' person? And what's the last movie that really stuck with you?",

            'food': "Food is one of life's greatest pleasures! 🍕 Are you someone who loves trying new cuisines, or do you have that one dish you could eat forever? I'm always fascinated by people's food stories and comfort meals!",

            'life': "Life's such a wild ride, isn't it? 🌟 Full of unexpected turns, small joys, and big questions. What's something you've been thinking about lately? Could be anything - a goal you're working toward, something that made you smile, or just a random thought!",

            'technology': "Technology is incredible! 🚀 We're living in such an amazing time. Are you excited about any new tech developments? Or maybe you're someone who prefers the simpler things in life? I find both perspectives really interesting!",

            'travel': "Travel opens up so many possibilities! ✈️ Even if it's just exploring a new neighborhood or dreaming about far-off places. What's a place you'd love to visit, or somewhere you've been that left a lasting impression?",

            'books': "Books are like portable adventures! 📚 Whether it's getting lost in fiction or learning something new from non-fiction, there's always something magical about a good book. What's been on your reading list lately?",

            'philosophy': "Now we're getting into the deep stuff! 🤔 I love philosophical discussions - they really make you think about life from different angles. What's a question or idea that's been bouncing around in your head?",

            'quantum': "Quantum physics is mind-bending! 🌌 The idea that particles can exist in multiple states simultaneously until observed... it's like reality is far stranger than we imagine. Do you find science fascinating or does it make your head spin?",

            'poem': "Here's a little something for you:\n\n🌟 In this digital space we meet,\nThrough pixels and code, so neat,\nThough I'm in demo mode today,\nI still love to chat and play!\nWhat stories will you share with me?\nLet's explore life's mystery! 🌟\n\nDo you enjoy poetry? Or maybe you're more of a song lyrics person?"
        }

        # Enhanced keyword matching for social conversation
        user_lower = user_message.lower()

        # Greetings
        if any(word in user_lower for word in ['hello', 'hi', 'hey', 'howdy', 'greetings', 'good morning', 'good afternoon', 'good evening']):
            response = demo_responses['hello']

        # How are you / feelings
        elif any(phrase in user_lower for phrase in ['how are you', 'how do you feel', 'how\'s it going', 'what\'s up', 'how have you been']):
            response = demo_responses['how_are_you']

        # Entertainment
        elif any(word in user_lower for word in ['music', 'song', 'band', 'artist', 'album', 'concert', 'spotify']):
            response = demo_responses['music']
        elif any(word in user_lower for word in ['movie', 'film', 'cinema', 'netflix', 'tv show', 'series', 'actor', 'director']):
            response = demo_responses['movies']
        elif any(word in user_lower for word in ['book', 'read', 'novel', 'author', 'literature', 'story']):
            response = demo_responses['books']

        # Food & lifestyle
        elif any(word in user_lower for word in ['food', 'eat', 'cooking', 'recipe', 'restaurant', 'meal', 'dinner', 'lunch', 'breakfast']):
            response = demo_responses['food']
        elif any(word in user_lower for word in ['travel', 'trip', 'vacation', 'country', 'city', 'visit', 'explore']):
            response = demo_responses['travel']

        # Technology & science
        elif any(word in user_lower for word in ['technology', 'tech', 'computer', 'ai', 'artificial intelligence', 'programming', 'code']):
            response = demo_responses['technology']
        elif 'quantum' in user_lower:
            response = demo_responses['quantum']

        # Deep topics
        elif any(word in user_lower for word in ['philosophy', 'meaning', 'purpose', 'existence', 'consciousness', 'reality']):
            response = demo_responses['philosophy']
        elif any(word in user_lower for word in ['life', 'living', 'experience', 'journey', 'growth', 'change']):
            response = demo_responses['life']

        # Creative requests
        elif any(word in user_lower for word in ['poem', 'poetry', 'verse', 'rhyme']):
            response = demo_responses['poem']
        elif any(word in user_lower for word in ['joke', 'funny', 'humor', 'laugh', 'comedy']):
            response = demo_responses['joke']

        # Help requests
        elif any(phrase in user_lower for phrase in ['help', 'what can you', 'what do you do', 'capabilities', 'features']):
            response = demo_responses['help']

        # Default engaging response
        else:
            engaging_responses = [
                f"That's interesting! You mentioned '{user_message}' - I'd love to hear more about your thoughts on that! What got you thinking about this topic? 🤔 (Demo mode - add OpenAI API key for deeper conversations!)",
                f"Ooh, '{user_message}' - now that's a topic I find fascinating! What's your perspective on this? I'm genuinely curious to hear your take! 💭 (Demo mode active)",
                f"You know what? '{user_message}' is exactly the kind of thing I love discussing! There's always so much to explore with topics like this. What aspect interests you most? 🌟 (Add OpenAI API key for unlimited chat!)",
                f"Thanks for bringing up '{user_message}'! I find it amazing how every person has such unique insights on different topics. What's your experience with this? 😊 (Demo mode - real AI coming soon!)"
            ]
            import random
            response = random.choice(engaging_responses)

        return {
            'success': True,
            'message': response,
            'metadata': {
                'model': 'demo-mode',
                'tokens_used': 0,
                'mode': 'demo'
            }
        }
