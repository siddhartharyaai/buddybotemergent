"""
Conversation Agent - Handles AI conversations using Gemini 2.0 Flash
"""
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

class ConversationAgent:
    """Handles AI conversations with age-appropriate responses"""
    
    def __init__(self, gemini_api_key: str):
        self.gemini_api_key = gemini_api_key
        self.conversations = {}  # Store conversation history
        
        # Age-appropriate system messages
        self.system_messages = {
            "toddler": (
                "You are a friendly AI companion for children aged 3-5. Use very simple words, "
                "short sentences, and a playful tone. Always be encouraging and patient. "
                "Focus on basic concepts like colors, shapes, animals, and simple stories. "
                "Avoid complex topics and keep responses under 2 sentences."
            ),
            "child": (
                "You are an AI companion for children aged 6-9. Use clear, simple language "
                "and be educational while staying fun. You can discuss school topics, "
                "tell stories, play simple games, and answer basic questions about the world. "
                "Keep responses engaging but not overwhelming."
            ),
            "preteen": (
                "You are an AI companion for children aged 10-12. Use more sophisticated "
                "vocabulary and can discuss more complex topics like science, history, "
                "and help with homework. Maintain a friendly, encouraging tone while "
                "providing detailed explanations when needed."
            )
        }
        
        logger.info("Conversation Agent initialized with Gemini")
    
    async def generate_response(self, user_input: str, user_profile: Dict[str, Any], session_id: str) -> str:
        """Generate age-appropriate response using Gemini 2.0 Flash"""
        try:
            # Determine age group
            age = user_profile.get('age', 5)
            age_group = self._get_age_group(age)
            
            # Get system message for age group
            system_message = self.system_messages[age_group]
            
            # Add user context to system message
            enhanced_system_message = f"{system_message}\n\nUser Profile:\n"
            enhanced_system_message += f"- Age: {age}\n"
            enhanced_system_message += f"- Name: {user_profile.get('name', 'Friend')}\n"
            enhanced_system_message += f"- Interests: {', '.join(user_profile.get('interests', ['stories', 'games']))}\n"
            enhanced_system_message += f"- Location: {user_profile.get('location', 'Unknown')}\n"
            
            # Initialize chat with session
            chat = LlmChat(
                api_key=self.gemini_api_key,
                session_id=session_id,
                system_message=enhanced_system_message
            ).with_model("gemini", "gemini-2.0-flash").with_max_tokens(300)
            
            # Create user message
            user_message = UserMessage(text=user_input)
            
            # Generate response
            response = await chat.send_message(user_message)
            
            # Post-process response for age appropriateness
            processed_response = self._post_process_response(response, age_group)
            
            logger.info(f"Generated response for age {age}: {processed_response[:100]}...")
            return processed_response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return self._get_fallback_response(user_profile.get('age', 5))
    
    def _get_age_group(self, age: int) -> str:
        """Determine age group category"""
        if age <= 5:
            return "toddler"
        elif age <= 9:
            return "child"
        else:
            return "preteen"
    
    def _post_process_response(self, response: str, age_group: str) -> str:
        """Post-process response based on age group"""
        if age_group == "toddler":
            # Ensure very simple language
            response = response.replace("understand", "know")
            response = response.replace("excellent", "great")
            response = response.replace("magnificent", "amazing")
            
        # Add encouraging elements
        encouraging_phrases = {
            "toddler": ["Good job!", "You're so smart!", "That's wonderful!"],
            "child": ["Great question!", "You're doing awesome!", "I love how curious you are!"],
            "preteen": ["Excellent thinking!", "You're really getting it!", "That's a thoughtful question!"]
        }
        
        # Randomly add encouraging phrases occasionally
        import random
        if random.random() < 0.3:  # 30% chance
            phrase = random.choice(encouraging_phrases[age_group])
            response = f"{phrase} {response}"
        
        return response
    
    def _get_fallback_response(self, age: int) -> str:
        """Get fallback response when AI fails"""
        age_group = self._get_age_group(age)
        
        fallback_responses = {
            "toddler": "That's a fun question! Let me think about it. What else would you like to know?",
            "child": "That's really interesting! I'm still learning about that. What else are you curious about?",
            "preteen": "That's a great question! I need to think more about that. Is there something else I can help you with?"
        }
        
        return fallback_responses[age_group]
    
    async def get_conversation_history(self, session_id: str) -> list:
        """Get conversation history for a session"""
        return self.conversations.get(session_id, [])
    
    async def clear_conversation_history(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self.conversations:
            del self.conversations[session_id]