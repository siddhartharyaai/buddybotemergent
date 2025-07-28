"""
Main Orchestrator Agent - Central coordinator for all sub-agents with enhanced emotional intelligence
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
from .emotional_sensing_agent import EmotionalSensingAgent
from .dialogue_orchestrator import DialogueOrchestrator
from .repair_agent import RepairAgent
from .micro_game_agent import MicroGameAgent
from .memory_agent import MemoryAgent
from .telemetry_agent import TelemetryAgent

logger = logging.getLogger(__name__)

class OrchestratorAgent:
    """Main orchestrator that coordinates all sub-agents with emotional intelligence"""
    
    def __init__(self, db, gemini_api_key: str, deepgram_api_key: str):
        self.db = db
        self.session_store = {}
        
        # Initialize all sub-agents
        self.voice_agent = VoiceAgent(deepgram_api_key)
        self.conversation_agent = ConversationAgent(gemini_api_key)
        self.content_agent = ContentAgent(db)
        self.safety_agent = SafetyAgent()
        self.emotional_sensing_agent = EmotionalSensingAgent(gemini_api_key)
        self.dialogue_orchestrator = DialogueOrchestrator()
        self.repair_agent = RepairAgent()
        self.micro_game_agent = MicroGameAgent()
        
        logger.info("Enhanced Orchestrator Agent initialized successfully")
    
    async def process_ambient_audio_enhanced(self, session_id: str, audio_data: bytes) -> Dict[str, Any]:
        """Enhanced ambient audio processing with emotional intelligence"""
        try:
            # Get user profile from session
            user_profile = self.session_store.get(session_id, {}).get("user_profile", {})
            
            # Process audio through voice agent
            voice_result = await self.voice_agent.process_ambient_audio(audio_data, session_id)
            
            if voice_result["status"] == "wake_word_detected":
                # Wake word detected, process command if present
                command = voice_result.get("command", "")
                
                if command:
                    # Process the command through enhanced pipeline
                    conversation_result = await self.process_enhanced_conversation(
                        session_id, command, user_profile, voice_result.get("context", [])
                    )
                    
                    voice_result.update({
                        "conversation_response": conversation_result,
                        "has_response": True
                    })
                else:
                    # Just acknowledge wake word
                    voice_result.update({
                        "conversation_response": {
                            "response_text": "Hi there! How can I help you today?",
                            "response_audio": None
                        },
                        "has_response": True
                    })
                
            elif voice_result["status"] == "conversation_active":
                # Continue active conversation
                transcript = voice_result.get("transcript", "")
                if transcript:
                    conversation_result = await self.process_enhanced_conversation(
                        session_id, transcript, user_profile, voice_result.get("context", [])
                    )
                    
                    voice_result.update({
                        "conversation_response": conversation_result,
                        "has_response": True
                    })
            
            return voice_result
            
        except Exception as e:
            logger.error(f"Error processing ambient audio: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def process_enhanced_conversation(self, session_id: str, user_input: str, user_profile: Dict[str, Any], context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Enhanced conversation processing with emotional intelligence and repair"""
        try:
            # Step 1: Emotional analysis
            emotional_state = await self.emotional_sensing_agent.analyze_emotional_state(
                user_input, user_profile, {"context": context}
            )
            
            # Step 2: Check for repair needs
            stt_confidence = context[-1].get("stt_confidence", 1.0) if context else 1.0
            repair_info = await self.repair_agent.detect_repair_need(
                user_input, stt_confidence, {"context": context}
            )
            
            # Step 3: Handle repair if needed
            if repair_info.get("repair_needed", False):
                repair_response = await self.repair_agent.generate_repair_response(
                    repair_info, user_profile, {"context": context}
                )
                
                if repair_response.get("repair_response"):
                    # Convert repair response to speech
                    audio_response = await self.voice_agent.text_to_speech(
                        repair_response["repair_response"], 
                        user_profile.get('voice_personality', 'friendly_companion')
                    )
                    
                    return {
                        "response_text": repair_response["repair_response"],
                        "response_audio": audio_response,
                        "content_type": "repair",
                        "metadata": repair_response
                    }
            
            # Step 4: Check for micro-game trigger
            engagement_context = {
                "silence_duration": 0,  # Will be set by frontend
                "engagement_level": 0.7,  # Will be calculated
                "last_user_input": user_input,
                "consecutive_neutral_responses": 0  # Will be tracked
            }
            
            should_trigger_game = await self.micro_game_agent.should_trigger_game(
                session_id, emotional_state, engagement_context
            )
            
            if should_trigger_game:
                # Select and start appropriate game
                selected_game = await self.micro_game_agent.select_appropriate_game(
                    user_profile, emotional_state, engagement_context
                )
                
                if selected_game:
                    game_result = await self.micro_game_agent.start_game(
                        session_id, selected_game, user_profile
                    )
                    
                    if game_result.get("game_started"):
                        # Convert game introduction to speech
                        audio_response = await self.voice_agent.text_to_speech(
                            game_result["introduction"], 
                            user_profile.get('voice_personality', 'friendly_companion')
                        )
                        
                        return {
                            "response_text": game_result["introduction"],
                            "response_audio": audio_response,
                            "content_type": "game",
                            "metadata": game_result
                        }
            
            # Step 5: Dialogue orchestration
            dialogue_plan = await self.dialogue_orchestrator.orchestrate_response(
                user_input, emotional_state, user_profile, {"context": context}
            )
            
            # Step 6: Safety check
            safety_result = await self.safety_agent.check_content_safety(user_input, user_profile.get('age', 5))
            
            if not safety_result.get('is_safe', False):
                return {
                    "response_text": "Let's talk about something else! What would you like to know?",
                    "response_audio": None,
                    "content_type": "safety_response",
                    "metadata": {"safety_result": safety_result}
                }
            
            # Step 7: Generate response with dialogue plan
            response = await self.conversation_agent.generate_response_with_context(
                user_input, user_profile, session_id, context, dialogue_plan
            )
            
            # Step 8: Content enhancement
            enhanced_response = await self.content_agent.enhance_response(response, user_profile)
            
            # Step 9: Convert to speech with prosody
            audio_response = await self.voice_agent.text_to_speech_with_prosody(
                enhanced_response['text'], 
                user_profile.get('voice_personality', 'friendly_companion'),
                dialogue_plan.get('prosody', {})
            )
            
            # Step 10: Store conversation with emotional context
            await self._store_enhanced_conversation(session_id, user_input, enhanced_response['text'], user_profile, emotional_state, dialogue_plan)
            
            return {
                "response_text": enhanced_response['text'],
                "response_audio": audio_response,
                "content_type": enhanced_response.get('content_type', 'conversation'),
                "metadata": {
                    "emotional_state": emotional_state,
                    "dialogue_plan": dialogue_plan,
                    "content_metadata": enhanced_response.get('metadata', {})
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing enhanced conversation: {str(e)}")
            return {
                "response_text": "I'm having trouble understanding right now. Can you try again?",
                "response_audio": None,
                "content_type": "error_response",
                "metadata": {"error": str(e)}
            }
    
    async def process_game_interaction(self, session_id: str, user_response: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Process game interaction"""
        try:
            # Analyze emotional state
            emotional_state = await self.emotional_sensing_agent.analyze_emotional_state(
                user_response, user_profile
            )
            
            # Process game response
            game_result = await self.micro_game_agent.process_game_response(
                session_id, user_response, emotional_state
            )
            
            if game_result.get("game_continues"):
                # Game continues, convert response to speech
                feedback_text = game_result.get("feedback", "")
                if game_result.get("next_challenge"):
                    feedback_text += f" {game_result['next_challenge']['question']}"
                
                audio_response = await self.voice_agent.text_to_speech(
                    feedback_text, 
                    user_profile.get('voice_personality', 'friendly_companion')
                )
                
                return {
                    "response_text": feedback_text,
                    "response_audio": audio_response,
                    "content_type": "game_continue",
                    "metadata": game_result
                }
            
            elif game_result.get("game_ended"):
                # Game ended, convert end message to speech
                end_message = game_result.get("message", "Thanks for playing!")
                
                audio_response = await self.voice_agent.text_to_speech(
                    end_message, 
                    user_profile.get('voice_personality', 'friendly_companion')
                )
                
                return {
                    "response_text": end_message,
                    "response_audio": audio_response,
                    "content_type": "game_end",
                    "metadata": game_result
                }
            
            else:
                # Error or no response
                return {
                    "response_text": "Let's try something different!",
                    "response_audio": None,
                    "content_type": "game_error",
                    "metadata": game_result
                }
                
        except Exception as e:
            logger.error(f"Error processing game interaction: {str(e)}")
            return {
                "response_text": "Let's try a different game!",
                "response_audio": None,
                "content_type": "game_error",
                "metadata": {"error": str(e)}
            }
    
    async def _store_enhanced_conversation(self, session_id: str, user_input: str, ai_response: str, user_profile: Dict[str, Any], emotional_state: Dict[str, Any], dialogue_plan: Dict[str, Any]):
        """Store enhanced conversation with emotional context"""
        try:
            conversation_data = {
                "session_id": session_id,
                "user_input": user_input,
                "ai_response": ai_response,
                "timestamp": datetime.utcnow(),
                "user_age": user_profile.get('age'),
                "user_id": user_profile.get('user_id'),
                "content_type": "enhanced_conversation",
                "emotional_state": emotional_state,
                "dialogue_mode": dialogue_plan.get("mode", "chat"),
                "prosody": dialogue_plan.get("prosody", {}),
                "cultural_context": dialogue_plan.get("cultural_context", {})
            }
            
            await self.db.conversations.insert_one(conversation_data)
        except Exception as e:
            logger.error(f"Error storing enhanced conversation: {str(e)}")
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            "orchestrator": "active",
            "voice_agent": "active",
            "conversation_agent": "active",
            "content_agent": "active",
            "safety_agent": "active",
            "emotional_sensing_agent": "active",
            "dialogue_orchestrator": "active",
            "repair_agent": "active",
            "micro_game_agent": "active",
            "active_games": len(self.micro_game_agent.active_games),
            "session_count": len(self.session_store)
        }
    
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