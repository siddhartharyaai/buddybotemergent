"""
Enhanced Content Agent - 3-Tier Content Sourcing System
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import random
import re
import json

logger = logging.getLogger(__name__)

class EnhancedContentAgent:
    """Enhanced Content Agent with 3-tier sourcing and content type detection"""
    
    def __init__(self, db, gemini_api_key: str = None):
        self.db = db
        self.gemini_api_key = gemini_api_key
        self.content_cache = {}
        
        # Content type detection patterns
        self.content_patterns = {
            "joke": [
                r"\b(joke|funny|laugh|giggle|humor|hilarious)\b",
                r"\b(tell me something funny|make me laugh)\b",
                r"\b(know any jokes|got a joke)\b"
            ],
            "riddle": [
                r"\b(riddle|puzzle|guess|brain teaser|mystery)\b",
                r"\b(can you give me a riddle|riddle me this)\b",
                r"\b(what am I|guess what)\b"
            ],
            "fact": [
                r"\b(fact|did you know|tell me about|trivia|interesting|learn)\b",
                r"\b(what is|how does|why does|explain)\b",
                r"\b(cool fact|amazing fact)\b"
            ],
            "rhyme": [
                r"\b(rhyme|poem|nursery rhyme|poetry|verse)\b",
                r"\b(roses are red|twinkle twinkle|hickory dickory)\b",
                r"\b(recite a poem|tell me a rhyme)\b"
            ],
            "song": [
                r"\b(song|sing|music|melody|tune|lullaby)\b",
                r"\b(let's sing|can you sing|sing me|play a song)\b",
                r"\b(favorite song|nursery song)\b"
            ],
            "story": [
                r"\b(story|tale|once upon|tell me about|adventure|fairy tale)\b",
                r"\b(bedtime story|read me|story time)\b",
                r"\b(what happened|tell me the story)\b"
            ],
            "game": [
                r"\b(game|play|fun|activity|challenge|let's play)\b",
                r"\b(what can we do|something fun|play with me)\b",
                r"\b(bored|entertain me)\b"
            ]
        }
        
        # Tier 1: Local content library (fastest, most reliable)
        self.local_content = self._initialize_local_content()
        
        logger.info("Enhanced Content Agent with 3-tier sourcing initialized")

    def _initialize_local_content(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize Tier 1 local content library"""
        return {
            "jokes": [
                {
                    "id": "joke_elephant_computer",
                    "setup": "Why don't elephants use computers?",
                    "punchline": "They're afraid of the mouse!",
                    "reaction": "😂 Haha! Get it? Computer mouse! Want another one?",
                    "age_groups": ["3-6", "7-9", "10-12"],
                    "tags": ["animals", "wordplay", "technology"],
                    "emotional_cue": "giggle"
                },
                {
                    "id": "joke_banana_doctor",
                    "setup": "Why did the banana go to the doctor?",
                    "punchline": "Because it wasn't peeling well!",
                    "reaction": "😄 That's bananas! Want to hear another joke?",
                    "age_groups": ["4-8", "9-12"],
                    "tags": ["food", "wordplay", "health"],
                    "emotional_cue": "laugh"
                },
                {
                    "id": "joke_math_book",
                    "setup": "Why was the math book so sad?",
                    "punchline": "Because it had too many problems!",
                    "reaction": "😆 Math humor is the best! Get it? Problems! Want more?",
                    "age_groups": ["6-9", "10-12"],
                    "tags": ["school", "math", "wordplay"],
                    "emotional_cue": "chuckle"
                }
            ],
            "riddles": [
                {
                    "id": "riddle_candle",
                    "question": "I'm tall when I'm young and short when I'm old. What am I?",
                    "answer": "A candle!",
                    "hint": "Think about something that gets smaller as it's used...",
                    "celebration": "🎉 Excellent! You got it right! Candles do get shorter as they burn!",
                    "followup": "Want to try another riddle?",
                    "age_groups": ["5-8", "9-12"],
                    "tags": ["objects", "logic", "everyday_items"],
                    "difficulty": "easy"
                },
                {
                    "id": "riddle_elephant",
                    "question": "I have a long trunk and big ears, I never forget and I love peanuts. What am I?",
                    "answer": "An elephant!",
                    "hint": "I'm the largest land animal...",
                    "celebration": "🎊 Fantastic! Elephants are amazing creatures with incredible memories!",
                    "followup": "Ready for another brain teaser?",
                    "age_groups": ["3-6", "7-9"],
                    "tags": ["animals", "easy", "memory"],
                    "difficulty": "very_easy"
                }
            ],
            "facts": [
                {
                    "id": "fact_honey_spoils",
                    "fact": "Did you know that honey never spoils? Archaeologists have found honey in ancient Egyptian tombs that's over 3000 years old and still perfectly good to eat!",
                    "reaction": "🍯 Isn't that amazing? Bees are incredible little chemists!",
                    "followup": "Want to learn another cool fact?",
                    "age_groups": ["4-8", "9-12"],
                    "tags": ["food", "science", "history", "animals"],
                    "category": "science_facts"
                },
                {
                    "id": "fact_venus_day",
                    "fact": "Did you know that one day on Venus is longer than one year on Venus? Venus spins so slowly that it takes 243 Earth days to rotate once, but only 225 Earth days to orbit the Sun!",
                    "reaction": "🪐 Space is full of incredible surprises!",
                    "followup": "Want to explore more amazing space facts?",
                    "age_groups": ["7-12"],
                    "tags": ["space", "science", "planets"],
                    "category": "space_facts"
                }
            ],
            "rhymes": [
                {
                    "id": "rhyme_twinkle_star",
                    "title": "Twinkle, Twinkle, Little Star",
                    "content": "Twinkle, twinkle, little star,\nHow I wonder what you are!\nUp above the world so high,\nLike a diamond in the sky.\nTwinkle, twinkle, little star,\nHow I wonder what you are!",
                    "reaction": "✨ Such a beautiful classic! Should we sing it together?",
                    "followup": "Want to hear another lovely rhyme?",
                    "age_groups": ["2-6", "7-9"],
                    "tags": ["classic", "stars", "bedtime", "singing"],
                    "category": "nursery_rhymes"
                }
            ],
            "songs": [
                {
                    "id": "song_row_boat",
                    "title": "Row, Row, Row Your Boat",
                    "content": "Row, row, row your boat,\nGently down the stream.\nMerrily, merrily, merrily, merrily,\nLife is but a dream!\n\nRow, row, row your boat,\nGently down the creek.\nIf you see a little mouse,\nDon't forget to squeak!",
                    "reaction": "🚣‍♀️ What a fun song to sing! Let's row together!",
                    "followup": "Should we sing another song?",
                    "age_groups": ["2-8"],
                    "tags": ["classic", "action", "fun", "imagination"],
                    "category": "action_songs"
                }
            ],
            "stories": [
                {
                    "id": "story_clever_rabbit",
                    "title": "The Clever Rabbit and the Lion",
                    "content": "Once upon a time, in a dense forest, there lived a fierce lion who was the king of all animals. This lion was very proud and would hunt many animals every day just for fun...",
                    "moral": "Intelligence and wit can overcome even the strongest opponent.",
                    "reaction": "🐰 What a smart rabbit! Cleverness is better than strength!",
                    "followup": "Would you like to hear another story?",
                    "age_groups": ["5-10"],
                    "tags": ["wisdom", "cleverness", "animals", "moral"],
                    "category": "panchatantra"
                }
            ],
            "games": [
                {
                    "id": "game_quick_math",
                    "name": "Quick Math Challenge",
                    "intro": "Let's play Quick Math! I'll give you a simple math problem, and you solve it as fast as you can! Ready?",
                    "instructions": "I'll ask you math questions, and you give me the answer! Let's start easy!",
                    "reaction": "🧮 Math is fun when it's a game!",
                    "age_groups": ["5-12"],
                    "tags": ["math", "learning", "quick", "educational"],
                    "category": "educational_games"
                }
            ]
        }

    def detect_content_type(self, user_input: str) -> Optional[str]:
        """Detect content type from user input using pattern matching"""
        user_input_lower = user_input.lower()
        
        # Check patterns for each content type
        for content_type, patterns in self.content_patterns.items():
            for pattern in patterns:
                if re.search(pattern, user_input_lower):
                    return content_type
        
        return None

    async def get_content_with_3tier_sourcing(self, content_type: str, user_profile: Dict[str, Any], user_input: str = "") -> Dict[str, Any]:
        """
        3-Tier Content Sourcing:
        Tier 1: Local curated content (fastest)
        Tier 2: Internet knowledge sources (medium)
        Tier 3: LLM-generated content (fallback)
        """
        
        # Tier 1: Try local content first
        local_content = await self._get_local_content(content_type, user_profile)
        if local_content:
            logger.info(f"Content served from Tier 1 (Local): {content_type}")
            return {
                "content": local_content,
                "source": "tier_1_local",
                "response_type": "structured"
            }
        
        # Tier 2: Try internet knowledge sources
        internet_content = await self._get_internet_content(content_type, user_profile, user_input)
        if internet_content:
            logger.info(f"Content served from Tier 2 (Internet): {content_type}")
            return {
                "content": internet_content,
                "source": "tier_2_internet",
                "response_type": "structured"
            }
        
        # Tier 3: Generate with LLM as fallback
        llm_content = await self._generate_llm_content(content_type, user_profile, user_input)
        logger.info(f"Content served from Tier 3 (LLM): {content_type}")
        return {
            "content": llm_content,
            "source": "tier_3_llm",
            "response_type": "generated"
        }

    async def _get_local_content(self, content_type: str, user_profile: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Tier 1: Get content from local curated library"""
        if content_type not in self.local_content:
            return None
        
        age = user_profile.get('age', 5)
        age_group = self._get_age_group(age)
        interests = user_profile.get('interests', [])
        
        # Filter content by age group and interests
        suitable_content = []
        for content in self.local_content[content_type]:
            # Check age appropriateness
            if age_group in content.get('age_groups', []):
                # Boost score for matching interests
                score = 1
                for interest in interests:
                    if interest in content.get('tags', []):
                        score += 1
                suitable_content.append((content, score))
        
        if not suitable_content:
            # Fallback to any age-appropriate content
            suitable_content = [(c, 1) for c in self.local_content[content_type]]
        
        if suitable_content:
            # Sort by score and pick the best match
            suitable_content.sort(key=lambda x: x[1], reverse=True)
            selected_content = suitable_content[0][0].copy()
            
            # Add formatting based on content type
            return self._format_content_response(content_type, selected_content, user_profile)
        
        return None

    async def _get_internet_content(self, content_type: str, user_profile: Dict[str, Any], user_input: str) -> Optional[Dict[str, Any]]:
        """Tier 2: Get content from internet knowledge sources"""
        # TODO: Implement internet content sourcing
        # This would integrate with APIs like:
        # - Wikipedia Kids API
        # - Kiddle search
        # - DuckDuckGo instant answers
        # - Free trivia APIs
        
        # For now, return None to fallback to LLM
        return None

    async def _generate_llm_content(self, content_type: str, user_profile: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """Tier 3: Generate content using LLM"""
        from emergentintegrations import LlmChat, UserMessage
        
        age = user_profile.get('age', 5)
        age_group = self._get_age_group(age)
        interests = user_profile.get('interests', [])
        name = user_profile.get('name', 'friend')
        
        # Create specialized prompts for each content type
        prompt_templates = {
            "joke": f"Tell a clean, age-appropriate joke for a {age} year old child named {name} who likes {', '.join(interests)}. Make it funny but not scary. Include a cheerful reaction and ask if they want another joke.",
            
            "riddle": f"Create a fun riddle for a {age} year old child named {name}. Make it challenging but solvable for their age. Include a hint, the answer, a celebration response, and ask if they want another riddle.",
            
            "fact": f"Share an amazing, age-appropriate fact for a {age} year old child named {name} who enjoys {', '.join(interests)}. Make it fascinating and include an enthusiastic reaction. Ask if they want to learn more.",
            
            "rhyme": f"Recite or create a beautiful nursery rhyme appropriate for a {age} year old child named {name}. Make it classic or create something new related to their interests: {', '.join(interests)}. Include a sweet reaction.",
            
            "song": f"Share or create a complete song with verses appropriate for a {age} year old child named {name} who likes {', '.join(interests)}. Include a joyful reaction and ask if they want to sing together.",
            
            "story": f"Tell a complete, engaging story for a {age} year old child named {name} who enjoys {', '.join(interests)}. Make it 300-500 words with a clear beginning, middle, and end. Include a moral lesson and ask if they want another story.",
            
            "game": f"Suggest and start a fun, interactive game for a {age} year old child named {name} who likes {', '.join(interests)}. Explain the rules clearly and begin the first round."
        }
        
        try:
            chat = LlmChat(
                api_key=self.gemini_api_key,
                system_message=f"You are a friendly AI companion for children. Always include emotional expressions and re-engagement prompts. Keep content age-appropriate and positive."
            ).with_model("gemini", "gemini-2.0-flash").with_max_tokens(800)
            
            prompt = prompt_templates.get(content_type, f"Help with {content_type} content for {name}")
            user_message = UserMessage(text=prompt)
            
            response = await chat.send_message(user_message)
            
            return {
                "text": response,
                "emotional_cue": "friendly",
                "followup": f"Want to try something else, {name}?",
                "generated": True
            }
            
        except Exception as e:
            logger.error(f"Error generating LLM content: {str(e)}")
            # Return fallback content
            return {
                "text": f"I'd love to help you with that! Let's try something fun together, {name}!",
                "emotional_cue": "encouraging",
                "followup": "What would you like to do?",
                "generated": False
            }

    def _format_content_response(self, content_type: str, content: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Format content response based on type with emotional expressions"""
        name = user_profile.get('name', 'friend')
        
        if content_type == "joke":
            return {
                "text": f"{content['setup']}\n\n{content['punchline']}\n\n{content['reaction']}",
                "emotional_cue": content.get('emotional_cue', 'laugh'),
                "followup": f"Want another joke, {name}?",
                "structured": True,
                "interaction_type": "immediate_response"
            }
        
        elif content_type == "riddle":
            return {
                "text": f"Here's a riddle for you, {name}! 🧩\n\n{content['question']}\n\nTake your time to think about it! Need a hint?",
                "hint": content.get('hint'),
                "answer": content['answer'],
                "celebration": content.get('celebration'),
                "followup": content.get('followup'),
                "emotional_cue": "curious",
                "structured": True,
                "interaction_type": "interactive_wait"
            }
        
        elif content_type == "fact":
            return {
                "text": f"{content['fact']}\n\n{content['reaction']}",
                "followup": content.get('followup'),
                "emotional_cue": "excited",
                "structured": True,
                "interaction_type": "immediate_response"
            }
        
        elif content_type == "rhyme":
            return {
                "text": f"Here's a lovely rhyme for you, {name}! ✨\n\n{content['content']}\n\n{content['reaction']}",
                "followup": content.get('followup'),
                "emotional_cue": "gentle",
                "structured": True,
                "interaction_type": "immediate_response"
            }
        
        elif content_type == "song":
            return {
                "text": f"Let's sing together, {name}! 🎵\n\n{content['content']}\n\n{content['reaction']}",
                "followup": content.get('followup'),
                "emotional_cue": "joyful",
                "structured": True,
                "interaction_type": "sing_along"
            }
        
        elif content_type == "story":
            return {
                "text": f"Here's a wonderful story for you, {name}! 📚\n\n{content['content']}\n\n{content.get('reaction', 'What did you think of that story?')}",
                "moral": content.get('moral'),
                "followup": content.get('followup'),
                "emotional_cue": "storytelling",
                "structured": True,
                "interaction_type": "narrative"
            }
        
        elif content_type == "game":
            return {
                "text": f"{content['intro']}\n\n{content['instructions']}\n\n{content.get('reaction', 'Ready to play?')}",
                "followup": "Let's start!",
                "emotional_cue": "playful",
                "structured": True,
                "interaction_type": "game_start"
            }
        
        return content

    def _get_age_group(self, age: int) -> str:
        """Get age group classification"""
        if age <= 3:
            return "2-3"
        elif age <= 6:
            return "3-6"
        elif age <= 9:
            return "7-9"
        else:
            return "10-12"

    async def enhance_response_with_content_detection(self, response: str, user_input: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance response with content detection and 3-tier sourcing"""
        
        # Detect if user is requesting specific content
        content_type = self.detect_content_type(user_input)
        
        if content_type:
            # Get content using 3-tier sourcing
            content_result = await self.get_content_with_3tier_sourcing(content_type, user_profile, user_input)
            
            return {
                "text": content_result["content"]["text"],
                "content_type": content_type,
                "source": content_result["source"],
                "metadata": content_result["content"],
                "enhanced": True
            }
        
        # If no specific content type detected, return original response
        return {
            "text": response,
            "content_type": "conversation",
            "source": "conversation_agent",
            "metadata": {},
            "enhanced": False
        }