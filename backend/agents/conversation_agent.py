"""
Conversation Agent - Handles AI conversations using Gemini 2.0 Flash
"""
import asyncio
import logging
import re
from typing import Dict, Any, Optional, List, Tuple
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
    
    async def generate_response_with_dialogue_plan(self, user_input: str, user_profile: Dict[str, Any], session_id: str, context: List[Dict[str, Any]] = None, dialogue_plan: Dict[str, Any] = None, memory_context: Dict[str, Any] = None) -> str:
        """Generate response with conversation context and dialogue plan"""
        try:
            # Determine age group
            age = user_profile.get('age', 5)
            age_group = self._get_age_group(age)
            
            # Get base system message
            base_system_message = self.system_messages[age_group]
            
            # Enhance with dialogue plan if provided
            if dialogue_plan:
                mode = dialogue_plan.get("mode", "chat")
                prosody = dialogue_plan.get("prosody", {})
                cultural_context = dialogue_plan.get("cultural_context", {})
                response_guidelines = dialogue_plan.get("response_guidelines", {})
                
                # Add mode-specific instructions
                mode_instructions = {
                    "story": "You are in storytelling mode. Be descriptive, engaging, and use narrative techniques.",
                    "game": "You are in game mode. Be encouraging, playful, and interactive.",
                    "comfort": "You are in comfort mode. Be empathetic, warm, and supportive.",
                    "teaching": "You are in teaching mode. Be patient, clear, and educational.",
                    "bedtime": "You are in bedtime mode. Be soothing, calm, and gentle.",
                    "calm": "You are in calming mode. Be peaceful, stabilizing, and reassuring."
                }
                
                if mode in mode_instructions:
                    base_system_message += f"\n\n{mode_instructions[mode]}"
                
                # Add prosody instructions
                tone = prosody.get("tone", "friendly")
                pace = prosody.get("pace", "normal")
                base_system_message += f"\n\nResponse tone: {tone}. Speech pace: {pace}."
                
                # Add cultural context
                if cultural_context.get("hinglish_usage", False):
                    base_system_message += "\n\nUse Indian English with occasional Hinglish words like 'yaar', 'accha', 'bahut', 'kya', 'hai na' naturally in conversation. Add relevant emojis."
                
                # Add response guidelines
                if response_guidelines.get("be_curious", False):
                    base_system_message += "\n\nBe curious and ask follow-up questions."
                if response_guidelines.get("use_examples", False):
                    base_system_message += "\n\nUse examples to explain concepts."
                
                # Add token budget constraint
                token_budget = dialogue_plan.get("token_budget", 150)
                base_system_message += f"\n\nKeep response under {token_budget} tokens."
            
            # Add user context
            enhanced_system_message = f"{base_system_message}\n\nUser Profile:\n"
            enhanced_system_message += f"- Age: {age}\n"
            enhanced_system_message += f"- Name: {user_profile.get('name', 'Friend')}\n"
            enhanced_system_message += f"- Interests: {', '.join(user_profile.get('interests', ['stories', 'games']))}\n"
            enhanced_system_message += f"- Location: {user_profile.get('location', 'Unknown')}\n"
            
            # Add conversation context if available
            if context:
                enhanced_system_message += f"\nRecent conversation context:\n"
                for ctx in context[-3:]:  # Last 3 context items
                    enhanced_system_message += f"- {ctx.get('text', '')}\n"
                enhanced_system_message += f"\nContinue this conversation naturally and remember what was said before."
            
            # Add memory context if available
            if memory_context and memory_context.get("user_id") != "unknown":
                enhanced_system_message += f"\n\nLong-term memory context:\n"
                
                # Add recent preferences
                recent_preferences = memory_context.get("recent_preferences", {})
                if recent_preferences:
                    enhanced_system_message += f"Recent preferences: {', '.join(f'{k}: {v}' for k, v in list(recent_preferences.items())[:3])}\n"
                
                # Add favorite topics
                favorite_topics = memory_context.get("favorite_topics", [])
                if favorite_topics:
                    topics_str = ', '.join([topic[0] if isinstance(topic, tuple) else str(topic) for topic in favorite_topics[:3]])
                    enhanced_system_message += f"Favorite topics: {topics_str}\n"
                
                # Add achievements
                achievements = memory_context.get("achievements", [])
                if achievements:
                    recent_achievements = achievements[-2:]  # Last 2 achievements
                    for achievement in recent_achievements:
                        if isinstance(achievement, dict):
                            achievement_type = achievement.get("type", "unknown")
                            enhanced_system_message += f"Recent achievement: {achievement_type}\n"
                
                enhanced_system_message += "Use this memory context to personalize the conversation and reference past interactions naturally."
            
            # Add ambient listening context
            enhanced_system_message += f"\n\nNote: This is an ambient listening conversation. The child may have said a wake word like 'Hey Buddy' before this message. Be natural and conversational."
            
            # Initialize chat with session
            max_tokens = dialogue_plan.get("token_budget", 200) if dialogue_plan else 200
            
            chat = LlmChat(
                api_key=self.gemini_api_key,
                session_id=session_id,
                system_message=enhanced_system_message
            ).with_model("gemini", "gemini-2.0-flash").with_max_tokens(max_tokens)
            
            # Create user message
            user_message = UserMessage(text=user_input)
            
            # Generate response
            response = await chat.send_message(user_message)
            
            # Post-process response based on dialogue plan
            if dialogue_plan:
                processed_response = self._post_process_with_dialogue_plan(response, dialogue_plan, age_group)
            else:
                processed_response = self._post_process_ambient_response(response, age_group)
            
            logger.info(f"Generated enhanced response for age {age}: {processed_response[:100]}...")
            return processed_response
            
        except Exception as e:
            logger.error(f"Error generating enhanced response: {str(e)}")
            return self._get_fallback_ambient_response(user_profile.get('age', 5))
    
    def _post_process_with_dialogue_plan(self, response: str, dialogue_plan: Dict[str, Any], age_group: str) -> str:
        """Post-process response based on dialogue plan"""
        
        mode = dialogue_plan.get("mode", "chat")
        prosody = dialogue_plan.get("prosody", {})
        cultural_context = dialogue_plan.get("cultural_context", {})
        
        # Apply mode-specific processing
        if mode == "story":
            # Add narrative elements
            if not any(starter in response.lower() for starter in ["once", "there was", "long ago"]):
                response = f"Let me tell you... {response}"
        elif mode == "game":
            # Add game enthusiasm
            if not any(word in response.lower() for word in ["great", "awesome", "good job", "well done"]):
                response = f"Great job! {response}"
        elif mode == "comfort":
            # Add comforting elements
            if not any(word in response.lower() for word in ["understand", "feel", "okay", "alright"]):
                response = f"I understand... {response}"
        
        # Apply cultural context
        if cultural_context.get("hinglish_usage", False):
            # Add occasional Hinglish words
            hinglish_replacements = {
                "yes": "haan",
                "no": "nahi",
                "good": "accha",
                "very": "bahut",
                "what": "kya",
                "friend": "yaar"
            }
            
            import random
            if random.random() < 0.3:  # 30% chance
                for eng, hindi in hinglish_replacements.items():
                    if eng in response.lower():
                        response = response.replace(eng, hindi, 1)
                        break
        
        # Apply prosody adjustments
        pace = prosody.get("pace", "normal")
        if pace == "slow" or pace == "very_slow":
            # Add more pauses
            response = response.replace(".", "... ").replace(",", ", ")
        
        return response

    async def generate_response_with_context(self, user_input: str, user_profile: Dict[str, Any], session_id: str, context: List[Dict[str, Any]] = None, dialogue_plan: Dict[str, Any] = None, memory_context: Dict[str, Any] = None) -> str:
        """Generate response with conversation context for ambient listening"""
        try:
            # Determine age group
            age = user_profile.get('age', 5)
            age_group = self._get_age_group(age)
            
            # Check if this is a story/content request
            is_story_request = self._is_story_request(user_input)
            is_song_request = self._is_song_request(user_input)
            is_content_request = is_story_request or is_song_request
            
            # Build context-aware system message
            system_message = self.system_messages[age_group]
            
            # Enhance system message for content requests
            if is_content_request:
                if is_story_request:
                    system_message += "\n\nIMPORTANT: The user is asking for a story. Please tell a COMPLETE, FULL-LENGTH story with:\n"
                    system_message += "- A clear beginning, middle, and end\n"
                    system_message += "- Detailed characters and settings\n"
                    system_message += "- An engaging plot with dialogue\n"
                    system_message += "- Age-appropriate length (300-800 words)\n"
                    system_message += "- Use storytelling language like 'Once upon a time' and 'The End'\n"
                    system_message += "- Include descriptive details to make it engaging\n"
                elif is_song_request:
                    system_message += "\n\nIMPORTANT: The user is asking for a song. Please provide a COMPLETE song with:\n"
                    system_message += "- Full verses and chorus\n"
                    system_message += "- Age-appropriate lyrics\n"
                    system_message += "- Rhyming pattern\n"
                    system_message += "- Fun and engaging content\n"
            
            # Add user context
            enhanced_system_message = f"{system_message}\n\nUser Profile:\n"
            enhanced_system_message += f"- Age: {age}\n"
            enhanced_system_message += f"- Name: {user_profile.get('name', 'Friend')}\n"
            enhanced_system_message += f"- Interests: {', '.join(user_profile.get('interests', ['stories', 'games']))}\n"
            enhanced_system_message += f"- Location: {user_profile.get('location', 'Unknown')}\n"
            
            # Add conversation context if available
            if context:
                enhanced_system_message += f"\nRecent conversation context:\n"
                for ctx in context[-3:]:  # Last 3 context items
                    enhanced_system_message += f"- {ctx.get('text', '')}\n"
                enhanced_system_message += f"\nContinue this conversation naturally and remember what was said before."
            
            # Add memory context if available
            if memory_context and memory_context.get("user_id") != "unknown":
                enhanced_system_message += f"\n\nLong-term memory context:\n"
                
                # Add recent preferences
                recent_preferences = memory_context.get("recent_preferences", {})
                if recent_preferences:
                    enhanced_system_message += f"Recent preferences: {', '.join(f'{k}: {v}' for k, v in list(recent_preferences.items())[:3])}\n"
                
                # Add favorite topics
                favorite_topics = memory_context.get("favorite_topics", [])
                if favorite_topics:
                    topics_str = ', '.join([topic[0] if isinstance(topic, tuple) else str(topic) for topic in favorite_topics[:3]])
                    enhanced_system_message += f"Favorite topics: {topics_str}\n"
                
                # Add achievements
                achievements = memory_context.get("achievements", [])
                if achievements:
                    recent_achievements = achievements[-2:]  # Last 2 achievements
                    for achievement in recent_achievements:
                        if isinstance(achievement, dict):
                            achievement_type = achievement.get("type", "unknown")
                            enhanced_system_message += f"Recent achievement: {achievement_type}\n"
                
                enhanced_system_message += "Use this memory context to personalize the conversation and reference past interactions naturally."
            
            # Add ambient listening context
            enhanced_system_message += f"\n\nNote: This is an ambient listening conversation. The child may have said a wake word like 'Hey Buddy' before this message. Be natural and conversational."
            
            # Set token limit based on content type
            max_tokens = 200  # Default for regular conversation
            if is_content_request:
                max_tokens = 1000  # Much higher for stories and songs
            
            # Initialize chat with session
            chat = LlmChat(
                api_key=self.gemini_api_key,
                session_id=session_id,
                system_message=enhanced_system_message
            ).with_model("gemini", "gemini-2.0-flash").with_max_tokens(max_tokens)
            
            # Create user message
            user_message = UserMessage(text=user_input)
            
            # Generate response
            response = await chat.send_message(user_message)
            
            # Post-process response for ambient conversation
            processed_response = self._post_process_ambient_response(response, age_group)
            
            logger.info(f"Generated context-aware response for age {age}: {processed_response[:100]}...")
            return processed_response
            
        except Exception as e:
            logger.error(f"Error generating context-aware response: {str(e)}")
            return self._get_fallback_ambient_response(user_profile.get('age', 5))
    
    def _post_process_ambient_response(self, response: str, age_group: str) -> str:
        """Post-process response for ambient conversation"""
        # Make responses more conversational and natural
        if age_group == "toddler":
            # Keep responses very short for toddlers
            sentences = response.split('.')
            if len(sentences) > 2:
                response = '. '.join(sentences[:2]) + '.'
        elif age_group == "child":
            # Moderate length for children
            sentences = response.split('.')
            if len(sentences) > 3:
                response = '. '.join(sentences[:3]) + '.'
        
        # Add natural conversation starters occasionally
        conversation_starters = {
            "toddler": ["Want to hear more?", "What do you think?", "Should we play?"],
            "child": ["What would you like to know?", "Want to try something fun?", "Tell me more!"],
            "preteen": ["What's your opinion?", "Want to explore this more?", "Any questions?"]
        }
        
        # Add conversation starter 20% of the time
        import random
        if random.random() < 0.2:
            starter = random.choice(conversation_starters[age_group])
            response = f"{response} {starter}"
        
        return response
    
    def _get_fallback_ambient_response(self, age: int) -> str:
        """Get fallback response for ambient conversation"""
        age_group = self._get_age_group(age)
        
        fallback_responses = {
            "toddler": "I'm here to help! What would you like to do?",
            "child": "Hi there! I'm listening. What can I help you with?",
            "preteen": "I'm ready to chat! What's on your mind?"
        }
        
        return fallback_responses[age_group]

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
    
    def _is_story_request(self, user_input: str) -> bool:
        """Check if the user is requesting a story"""
        story_keywords = [
            'story', 'tell me a story', 'once upon a time', 'fairy tale', 
            'bedtime story', 'tale', 'adventure', 'princess', 'dragon',
            'magic', 'kingdom', 'forest', 'castle', 'hero', 'villain'
        ]
        user_input_lower = user_input.lower()
        return any(keyword in user_input_lower for keyword in story_keywords)
    
    def _is_song_request(self, user_input: str) -> bool:
        """Check if the user is requesting a song"""
        song_keywords = [
            'song', 'sing', 'music', 'lullaby', 'nursery rhyme',
            'twinkle twinkle', 'abc song', 'happy birthday', 'rhyme',
            'melody', 'tune', 'lyrics', 'sing me'
        ]
        user_input_lower = user_input.lower()
        return any(keyword in user_input_lower for keyword in song_keywords)
    
    async def get_conversation_history(self, session_id: str) -> list:
        """Get conversation history for a session"""
        return self.conversations.get(session_id, [])
    
    async def clear_conversation_history(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self.conversations:
            del self.conversations[session_id]