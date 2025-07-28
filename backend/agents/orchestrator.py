"""
Main Orchestrator Agent - Central coordinator for all sub-agents
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from .voice_agent import VoiceAgent
from .conversation_agent import ConversationAgent  
from .content_agent import ContentAgent
from .safety_agent import SafetyAgent

logger = logging.getLogger(__name__)

class OrchestratorAgent:
    """Main orchestrator that coordinates all sub-agents"""
    
    def __init__(self, db, gemini_api_key: str, deepgram_api_key: str):
        self.db = db
        self.session_store = {}
        
        # Initialize sub-agents
        self.voice_agent = VoiceAgent(deepgram_api_key)
        self.conversation_agent = ConversationAgent(gemini_api_key)
        self.content_agent = ContentAgent(db)
        self.safety_agent = SafetyAgent()
        
        logger.info("Orchestrator Agent initialized successfully")
    
    async def start_ambient_listening(self, session_id: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Start ambient listening for wake word detection"""
        try:
            result = await self.voice_agent.start_ambient_listening(session_id, user_profile)
            
            # Store ambient listening state
            if session_id not in self.session_store:
                self.session_store[session_id] = {}
            
            self.session_store[session_id]["ambient_listening"] = True
            self.session_store[session_id]["user_profile"] = user_profile
            
            logger.info(f"Ambient listening started for session: {session_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error starting ambient listening: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def stop_ambient_listening(self, session_id: str) -> Dict[str, Any]:
        """Stop ambient listening"""
        try:
            result = await self.voice_agent.stop_ambient_listening()
            
            # Update session state
            if session_id in self.session_store:
                self.session_store[session_id]["ambient_listening"] = False
            
            logger.info(f"Ambient listening stopped for session: {session_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error stopping ambient listening: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def process_ambient_audio(self, session_id: str, audio_data: bytes) -> Dict[str, Any]:
        """Process ambient audio for wake word detection and continuous conversation"""
        try:
            # Get user profile from session
            user_profile = self.session_store.get(session_id, {}).get("user_profile", {})
            
            # Process audio through voice agent
            result = await self.voice_agent.process_ambient_audio(audio_data, session_id)
            
            if result["status"] == "wake_word_detected":
                # Wake word detected, process command if present
                command = result.get("command", "")
                
                if command:
                    # Process the command as a conversation
                    conversation_result = await self.process_conversation_command(
                        session_id, command, user_profile, result.get("context", [])
                    )
                    
                    result.update({
                        "conversation_response": conversation_result,
                        "has_response": True
                    })
                else:
                    # Just acknowledge wake word
                    result.update({
                        "conversation_response": {
                            "response_text": "Hi there! How can I help you today?",
                            "response_audio": None
                        },
                        "has_response": True
                    })
                
            elif result["status"] == "conversation_active":
                # Continue active conversation
                transcript = result.get("transcript", "")
                if transcript:
                    conversation_result = await self.process_conversation_command(
                        session_id, transcript, user_profile, result.get("context", [])
                    )
                    
                    result.update({
                        "conversation_response": conversation_result,
                        "has_response": True
                    })
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing ambient audio: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def process_conversation_command(self, session_id: str, command: str, user_profile: Dict[str, Any], context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process a conversation command with context"""
        try:
            # Safety check
            safety_result = await self.safety_agent.check_content_safety(command, user_profile.get('age', 5))
            
            if not safety_result.get('is_safe', False):
                return {
                    "response_text": "Let's talk about something else! What would you like to know?",
                    "response_audio": None,
                    "content_type": "safety_response"
                }
            
            # Generate response with context
            response = await self.conversation_agent.generate_response_with_context(
                command, user_profile, session_id, context
            )
            
            # Content enhancement
            enhanced_response = await self.content_agent.enhance_response(response, user_profile)
            
            # Convert to speech
            audio_response = await self.voice_agent.text_to_speech(
                enhanced_response['text'], 
                user_profile.get('voice_personality', 'friendly_companion')
            )
            
            # Store conversation
            await self._store_conversation(session_id, command, enhanced_response['text'], user_profile)
            
            return {
                "response_text": enhanced_response['text'],
                "response_audio": audio_response,
                "content_type": enhanced_response.get('content_type', 'conversation'),
                "metadata": enhanced_response.get('metadata', {})
            }
            
        except Exception as e:
            logger.error(f"Error processing conversation command: {str(e)}")
            return {
                "response_text": "I'm having trouble understanding right now. Can you try again?",
                "response_audio": None,
                "content_type": "error_response"
            }
    
    async def check_conversation_timeout(self, session_id: str) -> Dict[str, Any]:
        """Check and handle conversation timeout"""
        try:
            result = await self.voice_agent.handle_conversation_timeout()
            return result
            
        except Exception as e:
            logger.error(f"Error checking conversation timeout: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def process_voice_input(self, session_id: str, audio_data: bytes, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Process voice input through the agent pipeline"""
        try:
            # Step 1: Voice processing (STT)
            transcript = await self.voice_agent.speech_to_text(audio_data)
            
            if not transcript:
                return {"error": "Could not understand audio"}
            
            # Step 2: Safety check
            safety_result = await self.safety_agent.check_content_safety(transcript, user_profile.get('age', 5))
            
            if not safety_result.get('is_safe', False):
                return {
                    "error": "Content not appropriate", 
                    "message": "Let's talk about something else!"
                }
            
            # Step 3: Generate response
            response = await self.conversation_agent.generate_response(
                transcript, 
                user_profile, 
                session_id
            )
            
            # Step 4: Content enhancement
            enhanced_response = await self.content_agent.enhance_response(response, user_profile)
            
            # Step 5: Convert to speech
            audio_response = await self.voice_agent.text_to_speech(
                enhanced_response['text'], 
                user_profile.get('voice_personality', 'friendly_companion')
            )
            
            # Store conversation
            await self._store_conversation(session_id, transcript, enhanced_response['text'], user_profile)
            
            return {
                "transcript": transcript,
                "response_text": enhanced_response['text'],
                "response_audio": audio_response,
                "content_type": enhanced_response.get('content_type', 'conversation'),
                "metadata": enhanced_response.get('metadata', {})
            }
            
        except Exception as e:
            logger.error(f"Error processing voice input: {str(e)}")
            return {"error": "Processing error occurred"}
    
    async def process_text_input(self, session_id: str, text: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Process text input through the agent pipeline"""
        try:
            # Step 1: Safety check
            safety_result = await self.safety_agent.check_content_safety(text, user_profile.get('age', 5))
            
            if not safety_result.get('is_safe', False):
                return {
                    "error": "Content not appropriate", 
                    "message": "Let's talk about something else!"
                }
            
            # Step 2: Generate response
            response = await self.conversation_agent.generate_response(
                text, 
                user_profile, 
                session_id
            )
            
            # Step 3: Content enhancement
            enhanced_response = await self.content_agent.enhance_response(response, user_profile)
            
            # Step 4: Convert to speech
            audio_response = await self.voice_agent.text_to_speech(
                enhanced_response['text'], 
                user_profile.get('voice_personality', 'friendly_companion')
            )
            
            # Store conversation
            await self._store_conversation(session_id, text, enhanced_response['text'], user_profile)
            
            return {
                "response_text": enhanced_response['text'],
                "response_audio": audio_response,
                "content_type": enhanced_response.get('content_type', 'conversation'),
                "metadata": enhanced_response.get('metadata', {})
            }
            
        except Exception as e:
            logger.error(f"Error processing text input: {str(e)}")
            return {"error": "Processing error occurred"}
    
    async def get_content_suggestion(self, user_profile: Dict[str, Any], content_type: str) -> Dict[str, Any]:
        """Get content suggestions based on user profile"""
        return await self.content_agent.get_content_by_type(content_type, user_profile)
    
    async def _store_conversation(self, session_id: str, user_input: str, ai_response: str, user_profile: Dict[str, Any]):
        """Store conversation in database"""
        try:
            conversation_data = {
                "session_id": session_id,
                "user_input": user_input,
                "ai_response": ai_response,
                "timestamp": datetime.utcnow(),
                "user_age": user_profile.get('age'),
                "user_id": user_profile.get('user_id'),
                "content_type": "conversation"
            }
            
            await self.db.conversations.insert_one(conversation_data)
        except Exception as e:
            logger.error(f"Error storing conversation: {str(e)}")