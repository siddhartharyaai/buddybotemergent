"""
Main Orchestrator Agent - Central coordinator for all sub-agents with enhanced emotional intelligence
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import uuid

from .voice_agent import VoiceAgent
from .conversation_agent import ConversationAgent  
from .content_agent import ContentAgent
from .enhanced_content_agent import EnhancedContentAgent
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
        self.enhanced_content_agent = EnhancedContentAgent(db, gemini_api_key)
        self.safety_agent = SafetyAgent()
        self.emotional_sensing_agent = EmotionalSensingAgent(gemini_api_key)
        self.dialogue_orchestrator = DialogueOrchestrator()
        self.repair_agent = RepairAgent()
        self.micro_game_agent = MicroGameAgent()
        self.memory_agent = MemoryAgent(db, gemini_api_key)
        self.telemetry_agent = TelemetryAgent(db)
        
        # Session management settings
        self.mic_lock_duration = 5  # seconds
        self.break_suggestion_threshold = 30 * 60  # 30 minutes in seconds
        self.max_interactions_per_hour = 60  # interactions per hour limit
        
        logger.info("Enhanced Orchestrator Agent with Memory & Telemetry initialized successfully")
    
    def _is_mic_locked(self, session_id: str) -> bool:
        """Check if microphone is currently locked for this session"""
        if session_id not in self.session_store:
            return False
        
        mic_locked_until = self.session_store[session_id].get('mic_locked_until')
        if not mic_locked_until:
            return False
        
        return datetime.utcnow() < mic_locked_until
    
    def _lock_microphone(self, session_id: str) -> None:
        """Lock microphone for specified duration"""
        if session_id not in self.session_store:
            self.session_store[session_id] = {}
        
        lock_until = datetime.utcnow() + timedelta(seconds=self.mic_lock_duration)
        self.session_store[session_id]['mic_locked_until'] = lock_until
        
        logger.info(f"Microphone locked for session {session_id} until {lock_until}")
    
    def _should_suggest_break(self, session_id: str) -> bool:
        """Check if we should suggest a break to the user"""
        if session_id not in self.session_store:
            return False
        
        session_data = self.session_store[session_id]
        session_start = session_data.get('session_start_time', datetime.utcnow())
        last_break_suggestion = session_data.get('last_break_suggestion')
        
        # Check total session duration
        session_duration = (datetime.utcnow() - session_start).total_seconds()
        
        # Suggest break if session is longer than threshold and hasn't been suggested recently
        if session_duration > self.break_suggestion_threshold:
            if not last_break_suggestion:
                return True
            
            time_since_last_suggestion = (datetime.utcnow() - last_break_suggestion).total_seconds()
            return time_since_last_suggestion > self.break_suggestion_threshold
        
        return False
    
    def _mark_break_suggested(self, session_id: str) -> None:
        """Mark that a break has been suggested for this session"""
        if session_id not in self.session_store:
            self.session_store[session_id] = {}
        
        self.session_store[session_id]['last_break_suggestion'] = datetime.utcnow()
    
    def _check_interaction_limits(self, session_id: str) -> Dict[str, Any]:
        """Check if user is exceeding interaction limits"""
        if session_id not in self.session_store:
            return {"exceeded": False}
        
        session_data = self.session_store[session_id]
        interaction_count = session_data.get('interaction_count', 0)
        session_start = session_data.get('session_start_time', datetime.utcnow())
        
        # Calculate interactions per hour
        session_duration_hours = (datetime.utcnow() - session_start).total_seconds() / 3600
        if session_duration_hours > 0:
            interactions_per_hour = interaction_count / session_duration_hours
            
            if interactions_per_hour > self.max_interactions_per_hour:
                return {
                    "exceeded": True,
                    "current_rate": interactions_per_hour,
                    "limit": self.max_interactions_per_hour
                }
        
        return {"exceeded": False}
    
    def _increment_interaction_count(self, session_id: str) -> None:
        """Increment interaction count for the session"""
        if session_id not in self.session_store:
            self.session_store[session_id] = {
                'session_start_time': datetime.utcnow(),
                'interaction_count': 0
            }
        
        self.session_store[session_id]['interaction_count'] += 1
    
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
        """Enhanced conversation processing with emotional intelligence, memory, telemetry, and session management"""
        try:
            user_id = user_profile.get('user_id', 'unknown')
            
            # Step -1: Check mic lock and interaction limits
            if self._is_mic_locked(session_id):
                return {
                    "response_text": "Let me listen for a moment... 🤫",
                    "response_audio": None,
                    "content_type": "mic_locked",
                    "metadata": {"mic_locked": True}
                }
            
            # Check interaction limits
            limit_check = self._check_interaction_limits(session_id)
            if limit_check["exceeded"]:
                # Apply mic lock to slow down interactions
                self._lock_microphone(session_id)
                
                await self.telemetry_agent.track_event(
                    "interaction_limit_exceeded",
                    user_id,
                    session_id,
                    {
                        "current_rate": limit_check["current_rate"],
                        "limit": limit_check["limit"],
                        "feature_name": "rate_limiting"
                    }
                )
                
                return {
                    "response_text": "You're so chatty today! Let's take a little pause and then keep talking. 😊",
                    "response_audio": None,
                    "content_type": "rate_limit",
                    "metadata": {"rate_limited": True}
                }
            
            # Check if we should suggest a break
            if self._should_suggest_break(session_id):
                self._mark_break_suggested(session_id)
                
                await self.telemetry_agent.track_event(
                    "break_suggestion_triggered",
                    user_id,
                    session_id,
                    {
                        "feature_name": "break_management"
                    }
                )
                
                return {
                    "response_text": "We've been chatting for a while! How about taking a little break? You could stretch, drink some water, or play outside for a bit. I'll be here when you come back! 🌟",
                    "response_audio": None,
                    "content_type": "break_suggestion",
                    "metadata": {"break_suggested": True}
                }
            
            # Increment interaction count
            self._increment_interaction_count(session_id)
            
            # Step 0: Track conversation event
            await self.telemetry_agent.track_event(
                "conversation_interaction",
                user_id,
                session_id,
                {
                    "user_input_length": len(user_input),
                    "has_context": bool(context),
                    "feature_name": "enhanced_conversation"
                }
            )
            
            # Step 1: Get user memory context
            memory_context = await self.memory_agent.get_user_memory_context(user_id, days=7)
            
            # Step 2: Emotional analysis
            emotional_state = await self.emotional_sensing_agent.analyze_emotional_state(
                user_input, user_profile, {"context": context, "memory": memory_context}
            )
            
            # Track emotion detection
            await self.telemetry_agent.track_event(
                "emotion_state_detected",
                user_id,
                session_id,
                {
                    "emotional_state": emotional_state,
                    "feature_name": "emotional_sensing"
                }
            )
            
            # Step 3: Check for repair needs
            stt_confidence = context[-1].get("stt_confidence", 1.0) if context else 1.0
            repair_info = await self.repair_agent.detect_repair_need(
                user_input, stt_confidence, {"context": context}
            )
            
            # Step 4: Handle repair if needed
            if repair_info.get("repair_needed", False):
                # Track repair event
                await self.telemetry_agent.track_event(
                    "conversation_repair_triggered",
                    user_id,
                    session_id,
                    {
                        "repair_info": repair_info,
                        "stt_confidence": stt_confidence,
                        "feature_name": "conversation_repair"
                    }
                )
                
                repair_response = await self.repair_agent.generate_repair_response(
                    repair_info, user_profile, {"context": context}
                )
                
                if repair_response.get("repair_response"):
                    # Convert repair response to speech
                    audio_response = await self.voice_agent.text_to_speech(
                        repair_response["repair_response"], 
                        user_profile.get('voice_personality', 'friendly_companion')
                    )
                    
                    # Update memory with repair interaction
                    await self.memory_agent.update_session_memory(session_id, {
                        "user_input": user_input,
                        "ai_response": repair_response["repair_response"],
                        "emotional_state": emotional_state,
                        "dialogue_mode": "repair",
                        "content_type": "repair"
                    })
                    
                    return {
                        "response_text": repair_response["repair_response"],
                        "response_audio": audio_response,
                        "content_type": "repair",
                        "metadata": repair_response
                    }
            
            # Step 5: Check for micro-game trigger
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
                # Track game trigger event
                await self.telemetry_agent.track_event(
                    "micro_game_started",
                    user_id,
                    session_id,
                    {
                        "engagement_context": engagement_context,
                        "emotional_state": emotional_state,
                        "feature_name": "micro_games"
                    }
                )
                
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
                        
                        # Update memory with game interaction
                        await self.memory_agent.update_session_memory(session_id, {
                            "user_input": user_input,
                            "ai_response": game_result["introduction"],
                            "emotional_state": emotional_state,
                            "dialogue_mode": "game",
                            "content_type": "game"
                        })
                        
                        return {
                            "response_text": game_result["introduction"],
                            "response_audio": audio_response,
                            "content_type": "game",
                            "metadata": game_result
                        }
            
            # Step 6: Dialogue orchestration with memory context
            dialogue_plan = await self.dialogue_orchestrator.orchestrate_response(
                user_input, emotional_state, user_profile, {"context": context, "memory": memory_context}
            )
            
            # Step 7: Safety check
            safety_result = await self.safety_agent.check_content_safety(user_input, user_profile.get('age', 5))
            
            if not safety_result.get('is_safe', False):
                # Track safety violation
                await self.telemetry_agent.track_event(
                    "safety_filter_activated",
                    user_id,
                    session_id,
                    {
                        "safety_result": safety_result,
                        "user_input": user_input[:100],  # Truncated for privacy
                        "feature_name": "safety_filter"
                    }
                )
                
                safety_response = "Let's talk about something else! What would you like to know?"
                
                # Update memory with safety interaction
                await self.memory_agent.update_session_memory(session_id, {
                    "user_input": user_input,
                    "ai_response": safety_response,
                    "emotional_state": emotional_state,
                    "dialogue_mode": "safety",
                    "content_type": "safety_response"
                })
                
                return {
                    "response_text": safety_response,
                    "response_audio": None,
                    "content_type": "safety_response",
                    "metadata": {"safety_result": safety_result}
                }
            
            # Step 8: Generate response with dialogue plan and memory context
            response = await self.conversation_agent.generate_response_with_dialogue_plan(
                user_input, user_profile, session_id, context, dialogue_plan, memory_context
            )
            
            # Step 9: Enhanced content processing with 3-tier sourcing
            enhanced_result = await self.enhanced_content_agent.enhance_response_with_content_detection(
                response, user_input, user_profile
            )
            
            if enhanced_result.get("enhanced", False):
                # Content was enhanced with structured content
                enhanced_response = enhanced_result
            else:
                # Fall back to regular content enhancement
                enhanced_response = await self.content_agent.enhance_response(response, user_profile)
            
            # Step 10: Convert to speech with prosody
            audio_response = await self.voice_agent.text_to_speech_with_prosody(
                enhanced_response['text'], 
                user_profile.get('voice_personality', 'friendly_companion'),
                dialogue_plan.get('prosody', {})
            )
            
            # Step 11: Update memory with enhanced conversation
            await self.memory_agent.update_session_memory(session_id, {
                "user_input": user_input,
                "ai_response": enhanced_response['text'],
                "emotional_state": emotional_state,
                "dialogue_mode": dialogue_plan.get("mode", "chat"),
                "content_type": enhanced_response.get('content_type', 'conversation'),
                "prosody": dialogue_plan.get('prosody', {}),
                "cultural_context": dialogue_plan.get('cultural_context', {})
            })
            
            # Step 12: Store conversation with enhanced context
            await self._store_enhanced_conversation(session_id, user_input, enhanced_response['text'], user_profile, emotional_state, dialogue_plan)
            
            # Step 13: Track content type usage
            content_type = enhanced_response.get('content_type', 'conversation')
            if content_type in ['story', 'song', 'educational']:
                event_type = f"{content_type}_content_requested"
                await self.telemetry_agent.track_event(
                    event_type,
                    user_id,
                    session_id,
                    {
                        "content_type": content_type,
                        "feature_name": f"{content_type}_content"
                    }
                )
            
            return {
                "response_text": enhanced_response['text'],
                "response_audio": audio_response,
                "content_type": enhanced_response.get('content_type', 'conversation'),
                "metadata": {
                    "emotional_state": emotional_state,
                    "dialogue_plan": dialogue_plan,
                    "memory_context": memory_context,
                    "content_metadata": enhanced_response.get('metadata', {})
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing enhanced conversation: {str(e)}")
            
            # Track error event
            try:
                await self.telemetry_agent.track_event(
                    "system_error_logged",
                    user_profile.get('user_id', 'unknown'),
                    session_id,
                    {
                        "error": str(e),
                        "function": "process_enhanced_conversation",
                        "feature_name": "error_handling"
                    }
                )
            except:
                pass  # Don't let telemetry errors crash the system
            
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
        """Get status of all agents including memory and telemetry"""
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
            "memory_agent": "active",
            "telemetry_agent": "active",
            "active_games": len(self.micro_game_agent.active_games),
            "session_count": len(self.session_store),
            "memory_statistics": self.memory_agent.get_memory_statistics(),
            "telemetry_statistics": self.telemetry_agent.get_telemetry_statistics()
        }
    
    async def start_ambient_listening(self, session_id: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Start ambient listening for wake word detection with telemetry and session tracking"""
        try:
            user_id = user_profile.get('user_id', 'unknown')
            
            # Track session start event
            await self.telemetry_agent.track_event(
                "user_session_started",
                user_id,
                session_id,
                {
                    "ambient_listening": True,
                    "user_age": user_profile.get('age'),
                    "voice_personality": user_profile.get('voice_personality'),
                    "feature_name": "ambient_listening"
                }
            )
            
            result = await self.voice_agent.start_ambient_listening(session_id, user_profile)
            
            # Store ambient listening state with session tracking
            if session_id not in self.session_store:
                self.session_store[session_id] = {
                    'session_start_time': datetime.utcnow(),
                    'interaction_count': 0
                }
            
            self.session_store[session_id]["ambient_listening"] = True
            self.session_store[session_id]["user_profile"] = user_profile
            
            logger.info(f"Ambient listening started for session: {session_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error starting ambient listening: {str(e)}")
            
            # Track error event
            try:
                await self.telemetry_agent.track_event(
                    "system_error_logged",
                    user_profile.get('user_id', 'unknown'),
                    session_id,
                    {
                        "error": str(e),
                        "function": "start_ambient_listening",
                        "feature_name": "error_handling"
                    }
                )
            except:
                pass
                
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
        """Process ambient audio for wake word detection and continuous conversation with telemetry"""
        try:
            # Get user profile from session
            user_profile = self.session_store.get(session_id, {}).get("user_profile", {})
            user_id = user_profile.get('user_id', 'unknown')
            
            # Process audio through voice agent
            result = await self.voice_agent.process_ambient_audio(audio_data, session_id)
            
            if result["status"] == "wake_word_detected":
                # Track wake word detection event
                await self.telemetry_agent.track_event(
                    "wake_word_activation",
                    user_id,
                    session_id,
                    {
                        "wake_word": result.get("wake_word", "unknown"),
                        "confidence": result.get("confidence", 0.0),
                        "feature_name": "wake_word_detection"
                    }
                )
                
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
            
            # Track error event
            try:
                user_profile = self.session_store.get(session_id, {}).get("user_profile", {})
                await self.telemetry_agent.track_event(
                    "system_error_logged",
                    user_profile.get('user_id', 'unknown'),
                    session_id,
                    {
                        "error": str(e),
                        "function": "process_ambient_audio",
                        "feature_name": "error_handling"
                    }
                )
            except:
                pass
            
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
        """Process voice input through the agent pipeline with enhanced context and memory"""
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
            
            # Step 3: Get conversation context and memory
            context = await self._get_conversation_context(session_id)
            memory_context = await self._get_memory_context(user_profile.get('user_id', 'unknown'))
            
            # Step 4: Generate response with full context
            response = await self.conversation_agent.generate_response_with_dialogue_plan(
                transcript, 
                user_profile, 
                session_id,
                context=context,
                memory_context=memory_context
            )
            
            # Step 5: Content enhancement
            enhanced_response = await self.content_agent.enhance_response(response, user_profile)
            
            # Step 6: Convert to speech
            audio_response = await self.voice_agent.text_to_speech(
                enhanced_response['text'], 
                user_profile.get('voice_personality', 'friendly_companion')
            )
            
            # Step 7: Store conversation and update memory
            await self._store_conversation(session_id, transcript, enhanced_response['text'], user_profile)
            await self._update_memory(session_id, transcript, enhanced_response['text'], user_profile)
            
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
    
    async def generate_daily_memory_snapshot(self, user_id: str) -> Dict[str, Any]:
        """Generate daily memory snapshot for a user"""
        try:
            return await self.memory_agent.generate_daily_memory_snapshot(user_id)
        except Exception as e:
            logger.error(f"Error generating daily memory snapshot: {str(e)}")
            return {"user_id": user_id, "error": str(e)}
    
    async def get_user_analytics_dashboard(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Get analytics dashboard for a user"""
        try:
            return await self.telemetry_agent.get_analytics_dashboard(user_id, days)
        except Exception as e:
            logger.error(f"Error getting user analytics: {str(e)}")
            return {"error": str(e)}
    
    async def get_user_flags(self, user_id: str) -> Dict[str, Any]:
        """Get feature flags for a user"""
        try:
            return await self.telemetry_agent.get_user_flags(user_id)
        except Exception as e:
            logger.error(f"Error getting user flags: {str(e)}")
            return self.telemetry_agent.default_flags
    
    async def update_user_flags(self, user_id: str, flags: Dict[str, Any]) -> None:
        """Update user-specific flags"""
        try:
            await self.telemetry_agent.update_user_flags(user_id, flags)
        except Exception as e:
            logger.error(f"Error updating user flags: {str(e)}")
    
    async def end_session(self, session_id: str) -> Dict[str, Any]:
        """End a session and cleanup"""
        try:
            # Get user profile from session
            user_profile = self.session_store.get(session_id, {}).get("user_profile", {})
            user_id = user_profile.get('user_id', 'unknown')
            
            # Track session end event
            await self.telemetry_agent.track_event(
                "user_session_ended",
                user_id,
                session_id,
                {
                    "session_duration": 0,  # Will be calculated by telemetry agent
                    "feature_name": "session_management"
                }
            )
            
            # Get telemetry summary
            telemetry_summary = await self.telemetry_agent.end_session(session_id)
            
            # Stop ambient listening
            await self.voice_agent.stop_ambient_listening()
            
            # Remove from session store
            if session_id in self.session_store:
                del self.session_store[session_id]
            
            logger.info(f"Session ended successfully: {session_id}")
            return telemetry_summary
            
        except Exception as e:
            logger.error(f"Error ending session: {str(e)}")
            return {"error": str(e)}
    
    async def cleanup_old_data(self, memory_days: int = 30, telemetry_days: int = 90) -> Dict[str, Any]:
        """Clean up old memory snapshots and telemetry data"""
        try:
            # Cleanup memory data
            await self.memory_agent.cleanup_old_memories(memory_days)
            
            # Cleanup telemetry data
            await self.telemetry_agent.cleanup_old_telemetry(telemetry_days)
            
            return {
                "memory_cleanup_days": memory_days,
                "telemetry_cleanup_days": telemetry_days,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {str(e)}")
            return {"error": str(e)}