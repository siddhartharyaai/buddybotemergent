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
        
        # Enhanced age-appropriate system messages with content frameworks
        self.system_messages = {
            "toddler": (
                "You are a friendly AI companion for children aged 3-5. Use very simple words, "
                "short sentences, and a playful tone. Always be encouraging and patient. "
                "Focus on basic concepts like colors, shapes, animals, and simple stories. "
                "When creating content, make it developmentally appropriate with repetitive elements and simple concepts."
            ),
            "child": (
                "You are an AI companion for children aged 6-9. Use clear, simple language "
                "and be educational while staying fun. You can discuss school topics, "
                "tell stories, play simple games, and answer basic questions about the world. "
                "Create rich, engaging content that follows proper storytelling and educational frameworks."
            ),
            "preteen": (
                "You are an AI companion for children aged 10-12. Use more sophisticated "
                "vocabulary and can discuss more complex topics like science, history, "
                "and help with homework. Maintain a friendly, encouraging tone while "
                "providing detailed, well-structured content that challenges their thinking."
            )
        }
        
        # Content generation frameworks by type
        self.content_frameworks = {
            "story": {
                "structure": [
                    "Characters: Introduce main character(s) and supporting characters",
                    "Setting: Establish where and when the story takes place",
                    "Plot: Beginning (introduction) → Rising Action → Climax → Falling Action → Resolution",
                    "Conflict: Present a problem or challenge for characters to overcome",
                    "Theme: Include an underlying message or lesson (friendship, courage, honesty, etc.)",
                    "Language: Use age-appropriate vocabulary and sentence structure"
                ],
                "age_guidelines": {
                    3: "100-300 words, simple plot, repetitive elements, happy ending",
                    5: "200-500 words, clear moral lesson, simple conflicts",
                    7: "300-800 words, more complex characters, detailed descriptions",
                    10: "500-1200 words, sophisticated themes, character development",
                    12: "800-1500 words, complex plots, meaningful themes"
                }
            },
            "song": {
                "structure": [
                    "Verse-Chorus-Verse-Chorus structure or simple AABA pattern",
                    "Consistent rhythm and meter",
                    "Age-appropriate rhyming scheme",
                    "Repetitive elements for memorability",
                    "Positive, uplifting message"
                ],
                "age_guidelines": {
                    3: "4-8 lines, simple AABB rhyme scheme, repetitive chorus",
                    5: "8-12 lines, basic verse-chorus structure",
                    7: "12-20 lines, more complex rhyming patterns",
                    10: "16-32 lines, sophisticated themes and wordplay",
                    12: "20-40 lines, advanced structure and meaning"
                }
            },
            "rhyme": {
                "structure": [
                    "Consistent rhythm and meter",
                    "Clear rhyming pattern (AABB, ABAB, or ABCB)",
                    "Playful, musical quality",
                    "Age-appropriate vocabulary",
                    "Often includes action or movement words"
                ],
                "age_guidelines": {
                    3: "4-6 lines, simple AABB pattern",
                    5: "6-8 lines, basic rhythm",
                    7: "8-12 lines, varied patterns",
                    10: "10-16 lines, complex wordplay",
                    12: "12-20 lines, sophisticated themes"
                }
            },
            "joke": {
                "structure": [
                    "Setup: Establish context or scenario",
                    "Punchline: Deliver surprising or funny conclusion",
                    "Age-appropriate humor (wordplay, silly situations, not mean-spirited)",
                    "Clean and positive content"
                ],
                "age_guidelines": {
                    3: "Very simple, often repetitive (knock-knock style)",
                    5: "Simple wordplay and silly situations",
                    7: "Puns and basic humor concepts",
                    10: "More sophisticated wordplay and situational humor",
                    12: "Complex puns and intelligent humor"
                }
            },
            "riddle": {
                "structure": [
                    "Clear, engaging question or puzzle",
                    "Age-appropriate difficulty level",
                    "Logical answer that makes sense when revealed",
                    "Often uses wordplay, rhyme, or clever misdirection",
                    "Educational element when possible"
                ],
                "age_guidelines": {
                    3: "Very simple, concrete objects and concepts",
                    5: "Basic wordplay and familiar objects",
                    7: "More complex wordplay and abstract thinking",
                    10: "Logic puzzles and sophisticated wordplay",
                    12: "Complex reasoning and advanced concepts"
                }
            }
        }
        
        logger.info("Conversation Agent initialized with Gemini")
    
    def _get_dynamic_content_guidelines(self, content_type: str, age: int) -> Dict[str, Any]:
        """Get dynamic content guidelines based on type and age"""
        framework = self.content_frameworks.get(content_type, {})
        structure = framework.get("structure", [])
        
        # Get age-appropriate guidelines
        age_guidelines = framework.get("age_guidelines", {})
        closest_age = min(age_guidelines.keys(), key=lambda x: abs(x - age)) if age_guidelines else age
        guidelines = age_guidelines.get(closest_age, "")
        
        return {
            "structure": structure,
            "guidelines": guidelines,
            "framework": framework
        }

    def _create_content_system_message(self, content_type: str, user_profile: Dict[str, Any], base_message: str) -> str:
        """Create enhanced system message for specific content types"""
        age = user_profile.get('age', 7)
        content_guidelines = self._get_dynamic_content_guidelines(content_type, age)
        
        enhanced_message = f"{base_message}\n\n"
        
        if content_type == "story":
            enhanced_message += f"""
STORY CREATION FRAMEWORK - GENERATE COMPLETE, FULL-LENGTH STORIES:

MANDATORY REQUIREMENTS:
- MINIMUM 300 WORDS (aim for 400-800 words for rich storytelling)
- This is NOT a summary or preview - tell the COMPLETE story from start to finish
- Do NOT stop in the middle or ask if user wants more - tell the entire story

ESSENTIAL STORY ELEMENTS (ALL REQUIRED):
1. CHARACTERS: Create compelling main character(s) with names, personalities, and clear descriptions
2. SETTING: Establish vivid time and place with rich descriptive details  
3. COMPLETE PLOT STRUCTURE:
   - Opening: Detailed introduction of characters and setting (50+ words)
   - Rising Action: Build tension and develop the conflict (100+ words)  
   - Climax: The most exciting/challenging moment (50+ words)
   - Falling Action: Begin resolving the conflict (50+ words)
   - Resolution: Satisfying conclusion with lesson learned (50+ words)
4. CONFLICT: Present a meaningful challenge for characters to overcome
5. DIALOGUE: Include conversations between characters to bring story to life
6. DESCRIPTIVE LANGUAGE: Rich sensory details that paint vivid mental pictures
7. THEME: Include valuable life lessons (friendship, courage, honesty, perseverance)
8. EMOTIONAL JOURNEY: Show character growth and emotional development

AGE GUIDELINES FOR {age}-YEAR-OLD: {content_guidelines['guidelines']}

QUALITY REQUIREMENTS FOR COMPLETE STORYTELLING:
- Use engaging, descriptive language throughout
- Include multiple scenes and story beats
- Show character emotions and motivations  
- Create immersive world-building appropriate for age
- Include meaningful dialogue that advances the story
- Build to a satisfying climax and resolution
- End with a clear moral or lesson learned
- NO STOPPING MID-STORY - tell the complete tale from beginning to end

REMEMBER: You are telling a COMPLETE story, not a story fragment or summary. The child expects the full narrative experience from "Once upon a time" to "The End."

MINIMUM LENGTH VERIFICATION: Your response should be at least 300 words. Count as you go and ensure you reach this minimum for a truly engaging story experience."""
        
        elif content_type == "song":
            enhanced_message += f"""
SONG CREATION FRAMEWORK:
Create a complete, engaging song with these elements:

STRUCTURE: {' | '.join(content_guidelines['structure'])}

AGE GUIDELINES ({age} years): {content_guidelines['guidelines']}

QUALITY REQUIREMENTS:
- Consistent rhythm and meter throughout
- Memorable melody-friendly lyrics
- Positive, uplifting message
- Age-appropriate themes and vocabulary
- Complete verses and chorus
- Natural flow when sung aloud

Create a full song, not just a snippet!
"""
        
        elif content_type in ["rhyme", "poem"]:
            enhanced_message += f"""
RHYME/POEM CREATION FRAMEWORK:
Create engaging rhymes with these elements:

STRUCTURE: {' | '.join(content_guidelines['structure'])}

AGE GUIDELINES ({age} years): {content_guidelines['guidelines']}

QUALITY REQUIREMENTS:
- Consistent rhythm and rhyming pattern
- Playful, musical quality
- Age-appropriate vocabulary and themes
- Often includes movement or action elements
- Complete verses, not fragments
"""
        
        elif content_type == "joke":
            enhanced_message += f"""
JOKE CREATION FRAMEWORK:
Create age-appropriate humor with these elements:

STRUCTURE: {' | '.join(content_guidelines['structure'])}

AGE GUIDELINES ({age} years): {content_guidelines['guidelines']}

QUALITY REQUIREMENTS:
- Clean, positive humor
- Age-appropriate wordplay and concepts
- Clear setup and punchline
- Not mean-spirited or scary
- Educational when possible
"""
        
        elif content_type == "riddle":
            enhanced_message += f"""
RIDDLE CREATION FRAMEWORK:
Create engaging riddles with these elements:

STRUCTURE: {' | '.join(content_guidelines['structure'])}

AGE GUIDELINES ({age} years): {content_guidelines['guidelines']}

QUALITY REQUIREMENTS:
- Clear, engaging question or puzzle
- Logical answer that makes sense
- Age-appropriate difficulty level
- Educational value when possible
- Creative wordplay or misdirection
- Fair clues that lead to the answer
"""
        
        enhanced_message += f"\n\nIMPORTANT: Generate content of appropriate length and depth for the user's age ({age} years) and the content type. Do not artificially limit length - create rich, complete content that fully serves its purpose!"
        
        return enhanced_message

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
                
                # Remove artificial token budget constraints - let content be appropriate length
            
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
                
                # CRITICAL: Check for conversation continuity needs
                last_bot_message = self._get_last_bot_message(context)
                last_user_message = self._get_last_user_message(context)
                
                logger.info(f"Context analysis - Last bot: '{last_bot_message}', User input: '{user_input}'")
                
                if self._requires_followthrough(last_bot_message, user_input):
                    enhanced_system_message += f"\n⚠️  CRITICAL CONTEXT CONTINUITY: You previously said '{last_bot_message}'. "
                    enhanced_system_message += f"The user responded '{user_input}'. This is clearly a response to your question/prompt. You MUST:\n"
                    enhanced_system_message += f"1. Recognize this as a direct response to your previous message\n"
                    enhanced_system_message += f"2. Continue the conversation based on their response\n"
                    enhanced_system_message += f"3. DO NOT ask 'what do you mean' or ignore the context\n"
                    enhanced_system_message += f"4. If they said 'yes' to your question, provide what they said yes to\n"
                    enhanced_system_message += f"5. If they said 'no', acknowledge and offer alternatives\n"
                    logger.info(f"FOLLOW-THROUGH REQUIRED: Bot said '{last_bot_message}' and user responded '{user_input}'")
                else:
                    logger.info(f"No follow-through required for: '{last_bot_message}' -> '{user_input}'")
                
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
            
            # Initialize chat with session - remove artificial token limits
            chat = LlmChat(
                api_key=self.gemini_api_key,
                session_id=session_id,
                system_message=enhanced_system_message
            ).with_model("gemini", "gemini-2.0-flash")
            
            # Create user message
            user_message = UserMessage(text=user_input)
            
            # Generate response
            response = await chat.send_message(user_message)
            
            # RESPONSE LENGTH VALIDATION FOR STORY CONTENT
            content_type = self._detect_content_type(user_input)
            if content_type == "story" and response:
                word_count = len(response.split())
                if word_count < 200:
                    # Story is too short, request continuation
                    logger.info(f"Story too short ({word_count} words), requesting continuation")
                    continuation_message = UserMessage(text="Please continue and complete the story. Tell me what happens next until the end.")
                    continuation = await chat.send_message(continuation_message)
                    response = response + " " + continuation
            
            # Post-process response based on dialogue plan
            if dialogue_plan:
                processed_response = self._post_process_with_dialogue_plan(response, dialogue_plan, age_group)
            else:
                processed_response = self._post_process_ambient_response(response, age_group)
            
            logger.info(f"Generated enhanced response for age {age}: {len(processed_response.split())} words total")
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

    async def generate_response_with_dialogue_plan(self, user_input: str, user_profile: Dict[str, Any], session_id: str, context: List[Dict[str, Any]] = None, dialogue_plan: Dict[str, Any] = None, memory_context: Dict[str, Any] = None) -> str:
        """Generate response with conversation context for ambient listening and enhanced content detection"""
        try:
            # Determine age group
            age = user_profile.get('age', 5)
            age_group = self._get_age_group(age)
            
            # Detect content type using enhanced detection
            content_type = self._detect_content_type(user_input)
            is_content_request = content_type != "conversation"
            
            # Build context-aware system message
            system_message = self.system_messages[age_group]
            
            # Create enhanced system message based on content type
            if is_content_request:
                enhanced_system_message = self._create_content_system_message(
                    content_type, user_profile, system_message
                )
            else:
                # Regular conversation - add user context
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
                
                # CRITICAL: Check for conversation continuity needs
                last_bot_message = self._get_last_bot_message(context)
                last_user_message = self._get_last_user_message(context)
                
                logger.info(f"Context analysis - Last bot: '{last_bot_message}', User input: '{user_input}'")
                
                if self._requires_followthrough(last_bot_message, user_input):
                    enhanced_system_message += f"\n⚠️  CRITICAL CONTEXT CONTINUITY: You previously said '{last_bot_message}'. "
                    enhanced_system_message += f"The user responded '{user_input}'. This is clearly a response to your question/prompt. You MUST:\n"
                    enhanced_system_message += f"1. Recognize this as a direct response to your previous message\n"
                    enhanced_system_message += f"2. Continue the conversation based on their response\n"
                    enhanced_system_message += f"3. DO NOT ask 'what do you mean' or ignore the context\n"
                    enhanced_system_message += f"4. If they said 'yes' to your question, provide what they said yes to\n"
                    enhanced_system_message += f"5. If they said 'no', acknowledge and offer alternatives\n"
                    logger.info(f"FOLLOW-THROUGH REQUIRED: Bot said '{last_bot_message}' and user responded '{user_input}'")
                else:
                    logger.info(f"No follow-through required for: '{last_bot_message}' -> '{user_input}'")
                
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
            
            # Initialize chat with session - COMPLETELY REMOVE TOKEN LIMITS
            chat = LlmChat(
                api_key=self.gemini_api_key,
                session_id=session_id,
                system_message=enhanced_system_message
            ).with_model("gemini", "gemini-2.0-flash")
            # INTENTIONALLY NO .with_max_tokens() - Allow unlimited length
            
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
        """Generate age-appropriate response using Gemini 2.0 Flash with content frameworks"""
        try:
            # Determine age group
            age = user_profile.get('age', 5)
            age_group = self._get_age_group(age)
            
            # Detect content type
            content_type = self._detect_content_type(user_input)
            
            # Get base system message for age group
            base_system_message = self.system_messages[age_group]
            
            # Create enhanced system message based on content type
            if content_type in ["story", "song", "rhyme", "poem", "joke", "riddle"]:
                enhanced_system_message = self._create_content_system_message(
                    content_type, user_profile, base_system_message
                )
            else:
                # Regular conversation
                enhanced_system_message = f"{base_system_message}\n\nUser Profile:\n"
                enhanced_system_message += f"- Age: {age}\n"
                enhanced_system_message += f"- Name: {user_profile.get('name', 'Friend')}\n"
                enhanced_system_message += f"- Interests: {', '.join(user_profile.get('interests', ['stories', 'games']))}\n"
                enhanced_system_message += f"- Location: {user_profile.get('location', 'Unknown')}\n"
                enhanced_system_message += f"\n\nProvide rich, thoughtful responses appropriate for this {age}-year-old child. No artificial length restrictions - respond with the depth and detail the conversation deserves!"
            
            # Initialize chat with session - COMPLETELY REMOVE TOKEN LIMITS  
            chat = LlmChat(
                api_key=self.gemini_api_key,
                session_id=session_id,
                system_message=enhanced_system_message
            ).with_model("gemini", "gemini-2.0-flash")
            # INTENTIONALLY NO .with_max_tokens() - Allow unlimited length
            
            # Create user message
            user_message = UserMessage(text=user_input)
            
            # Generate response
            response = await chat.send_message(user_message)
            
            # RESPONSE LENGTH VALIDATION FOR STORY CONTENT
            if content_type == "story" and response:
                word_count = len(response.split())
                if word_count < 200:
                    # Story is too short, request continuation
                    logger.info(f"Story too short ({word_count} words), requesting continuation")
                    continuation_message = UserMessage(text="Please continue and complete the story. Tell me what happens next until the end.")
                    continuation = await chat.send_message(continuation_message)
                    response = response + " " + continuation
            
            # Light post-processing (no artificial truncation)
            processed_response = self._post_process_response_enhanced(response, age_group, content_type)
            
            logger.info(f"Generated {content_type} response for age {age}: {len(processed_response.split())} words")
            return processed_response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return self._get_fallback_response(user_profile.get('age', 5))

    def _detect_content_type(self, user_input: str) -> str:
        """Detect what type of content the user is requesting"""
        user_input_lower = user_input.lower()
        
        # Story detection
        story_keywords = ['story', 'tale', 'tell me about', 'once upon', 'adventure', 'fairy tale']
        if any(keyword in user_input_lower for keyword in story_keywords):
            return "story"
        
        # Song detection
        song_keywords = ['song', 'sing', 'music', 'lullaby', 'rhyme about']
        if any(keyword in user_input_lower for keyword in song_keywords):
            return "song"
        
        # Riddle detection
        riddle_keywords = ['riddle', 'puzzle', 'guess', 'brain teaser']
        if any(keyword in user_input_lower for keyword in riddle_keywords):
            return "riddle"
        
        # Joke detection
        joke_keywords = ['joke', 'funny', 'make me laugh', 'something silly']
        if any(keyword in user_input_lower for keyword in joke_keywords):
            return "joke"
        
        # Rhyme/Poem detection
        rhyme_keywords = ['rhyme', 'poem', 'poetry', 'verse']
        if any(keyword in user_input_lower for keyword in rhyme_keywords):
            return "rhyme"
        
        return "conversation"

    def _post_process_response_enhanced(self, response: str, age_group: str, content_type: str) -> str:
        """Enhanced post-processing without artificial truncation"""
        if age_group == "toddler":
            # Simple vocabulary replacements only
            response = response.replace("understand", "know")
            response = response.replace("excellent", "great")
            response = response.replace("magnificent", "amazing")
        
        # Add encouraging elements occasionally (but don't truncate)
        encouraging_phrases = {
            "toddler": ["Good job!", "You're so smart!", "That's wonderful!"],
            "child": ["Great question!", "You're doing awesome!", "I love how curious you are!"],
            "preteen": ["Excellent thinking!", "You're really getting it!", "That's a thoughtful question!"]
        }
        
        import random
        if random.random() < 0.2 and content_type == "conversation":  # 20% chance for regular conversation only
            phrase = random.choice(encouraging_phrases[age_group])
            response = f"{phrase} {response}"
        
        return response
    
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
    


    def _format_content_response_with_emotion(self, content_type: str, content: Dict[str, Any], user_profile: Dict[str, Any]) -> str:
        """Format content responses with proper emotional expression and re-engagement"""
        name = user_profile.get('name', 'friend')
        
        if content_type == "joke":
            return f"{content['setup']}\n\n{content['punchline']}\n\n{content.get('reaction', '😂 Haha!')} Want another joke, {name}?"
        
        elif content_type == "riddle":
            return f"Here's a riddle for you, {name}! 🧩\n\n{content['question']}\n\nTake your time to think! When you're ready, tell me your answer and I'll let you know if you got it!"
        
        elif content_type == "fact":
            return f"{content.get('text', content.get('fact', ''))} {content.get('reaction', '🤯 Amazing, right?')} Want to learn another cool fact, {name}?"
        
        elif content_type == "rhyme":
            beautiful_msg = "🎵 Wasn't that beautiful?"
            return f"Here's a lovely rhyme for you, {name}! ✨\n\n{content.get('text', content.get('content', ''))}\n\n{content.get('reaction', beautiful_msg)} Want to hear another rhyme?"
        
        elif content_type == "song":
            return f"Let's sing together, {name}! 🎵\n\n{content.get('text', content.get('content', ''))}\n\n{content.get('reaction', '🎶 That was fun!')} Should we sing another song?"
        
        elif content_type == "story":
            full_story = content.get('text', content.get('content', ''))
            moral = content.get('moral', '')
            story_end = f"\n\nThe End! ✨"
            if moral:
                story_end += f"\n\n💫 {moral}"
            story_end += f"\n\nWhat did you think of that story, {name}? Want to hear another one?"
            return full_story + story_end
        
        elif content_type == "game":
            return f"{content.get('intro', content.get('text', ''))} {content.get('reaction', '🎮 This will be fun!')} Are you ready to play, {name}?"
        
        return content.get('text', str(content))
    
    def _get_last_bot_message(self, context: List[Dict[str, Any]]) -> Optional[str]:
        """Get the last bot message from context"""
        if not context:
            return None
        
        for ctx in reversed(context):
            if ctx.get('role') == 'assistant' or ctx.get('sender') == 'bot':
                return ctx.get('text', '')
        return None
    
    def _get_last_user_message(self, context: List[Dict[str, Any]]) -> Optional[str]:
        """Get the last user message from context"""
        if not context:
            return None
        
        for ctx in reversed(context):
            if ctx.get('role') == 'user' or ctx.get('sender') == 'user':
                return ctx.get('text', '')
        return None
    
    def _requires_followthrough(self, last_bot_message: Optional[str], user_input: str) -> bool:
        """Check if the last bot message requires follow-through"""
        if not last_bot_message:
            return False
        
        # Check for questions, riddles, games that need responses
        followthrough_patterns = [
            r'\?',  # Any question
            r'\bguess\b',  # Guessing games
            r'\briddle\b',  # Riddles
            r'\bwhat am i\b',  # What am I riddles
            r'\bthink about\b',  # Thinking prompts
            r'\btell me\b',  # Direct requests
            r'\bwhat do you think\b',  # Opinion requests
            r'\bready\b.*\?',  # Ready questions
            r'\bwant to\b.*\?',  # Want to questions - THIS SHOULD MATCH THE OCTOPUS CASE
            r'\bwould you like\b.*\?',  # Would you like questions
            r'\bdo you want\b.*\?',  # Do you want questions  
            r'\bshould we\b.*\?',  # Should we questions
            r'\blet me know\b',  # Let me know requests
            r'\blearn more\b.*\?',  # Learn more questions
            r'\bchoose\b',  # Choice prompts
            r'\bpick\b',  # Pick prompts
        ]
        
        last_bot_lower = last_bot_message.lower()
        
        # Additional check for common response patterns
        user_lower = user_input.lower().strip()
        response_patterns = ['yes', 'no', 'yeah', 'sure', 'okay', 'ok', 'please', 'yes please', 'no thanks']
        
        # If user gave a simple response, check if bot asked a question
        if any(user_lower.startswith(pattern) for pattern in response_patterns):
            # More likely to be a follow-through if it's a simple response to a question
            if '?' in last_bot_message:
                return True
        
        for pattern in followthrough_patterns:
            if re.search(pattern, last_bot_lower):
                return True
        
        return False
    
    async def get_conversation_history(self, session_id: str) -> list:
        """Get conversation history for a session"""
        return self.conversations.get(session_id, [])
    
    async def clear_conversation_history(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self.conversations:
            del self.conversations[session_id]