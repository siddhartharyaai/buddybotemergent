"""
Voice Agent - Handles Speech-to-Text and Text-to-Speech using Deepgram with Wake Word Detection
"""
import asyncio
import logging
import base64
import io
import re
import time
from typing import Optional, Dict, Any, List
from deepgram import DeepgramClient, PrerecordedOptions, SpeakOptions, LiveTranscriptionEvents, LiveOptions

logger = logging.getLogger(__name__)

class VoiceAgent:
    """Handles voice processing with Deepgram Nova 3 STT and Aura 2 TTS with wake word detection"""
    
    def __init__(self, deepgram_api_key: str):
        self.deepgram_client = DeepgramClient(deepgram_api_key)
        self.voice_personalities = {
            "friendly_companion": {
                "model": "aura-2-amalthea-en",  # Use Aura 2 Amalthea as requested
                "encoding": "linear16",
                "sample_rate": 24000
            },
            "story_narrator": {
                "model": "aura-2-amalthea-en",  # Use Aura 2 Amalthea as requested
                "encoding": "linear16",
                "sample_rate": 24000
            },
            "learning_buddy": {
                "model": "aura-2-amalthea-en",  # Use Aura 2 Amalthea as requested
                "encoding": "linear16", 
                "sample_rate": 24000
            }
        }
        
        # Wake word configurations
        self.wake_words = [
            "hey buddy",
            "ai buddy", 
            "hello buddy",
            "hi buddy",
            "buddy"
        ]
        
        # Ambient listening state
        self.is_listening = False
        self.context_buffer = []
        self.last_interaction_time = None
        self.conversation_active = False
        self.silence_timeout = 5.0  # seconds
        
        logger.info("Voice Agent initialized with Deepgram and Wake Word Detection")
    
    async def detect_wake_word(self, text: str) -> bool:
        """Detect wake word in transcribed text"""
        if not text:
            return False
            
        text_lower = text.lower().strip()
        
        # Check for exact wake word matches
        for wake_word in self.wake_words:
            if wake_word in text_lower:
                logger.info(f"Wake word detected: {wake_word}")
                return True
                
        # Check for variations and partial matches
        wake_word_patterns = [
            r'\b(hey|hi|hello)\s+(buddy|ai)\b',
            r'\bbuddy\b',
            r'\bai\s+buddy\b'
        ]
        
        for pattern in wake_word_patterns:
            if re.search(pattern, text_lower):
                logger.info(f"Wake word pattern detected: {pattern}")
                return True
                
        return False
    
    async def start_ambient_listening(self, session_id: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Start ambient listening for wake word detection"""
        try:
            self.is_listening = True
            self.conversation_active = False
            
            return {
                "status": "listening",
                "message": "Ambient listening started. Say 'Hey Buddy' to activate.",
                "wake_words": self.wake_words,
                "listening_state": "ambient"
            }
            
        except Exception as e:
            logger.error(f"Error starting ambient listening: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def stop_ambient_listening(self) -> Dict[str, Any]:
        """Stop ambient listening"""
        try:
            self.is_listening = False
            self.conversation_active = False
            self.context_buffer.clear()
            
            return {
                "status": "stopped",
                "message": "Ambient listening stopped.",
                "listening_state": "inactive"
            }
            
        except Exception as e:
            logger.error(f"Error stopping ambient listening: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def process_ambient_audio(self, audio_data: bytes, session_id: str) -> Dict[str, Any]:
        """Process ambient audio for wake word detection and continuous conversation"""
        try:
            # Transcribe audio
            transcript = await self.speech_to_text(audio_data)
            
            if not transcript:
                return {"status": "no_speech", "listening_state": "ambient"}
            
            # Add to context buffer
            self.context_buffer.append({
                "text": transcript,
                "timestamp": time.time(),
                "session_id": session_id
            })
            
            # Keep only recent context (last 10 entries)
            if len(self.context_buffer) > 10:
                self.context_buffer = self.context_buffer[-10:]
            
            # Check for wake word if not in active conversation
            if not self.conversation_active:
                if await self.detect_wake_word(transcript):
                    self.conversation_active = True
                    self.last_interaction_time = time.time()
                    
                    # Extract command after wake word
                    command = self.extract_command_after_wake_word(transcript)
                    
                    return {
                        "status": "wake_word_detected",
                        "transcript": transcript,
                        "command": command,
                        "listening_state": "active",
                        "context": self.get_conversation_context()
                    }
                else:
                    return {
                        "status": "ambient_listening",
                        "transcript": transcript,
                        "listening_state": "ambient"
                    }
            else:
                # In active conversation
                self.last_interaction_time = time.time()
                
                # Check if user wants to end conversation
                if self.is_end_conversation_command(transcript):
                    self.conversation_active = False
                    return {
                        "status": "conversation_ended",
                        "transcript": transcript,
                        "listening_state": "ambient"
                    }
                
                return {
                    "status": "conversation_active",
                    "transcript": transcript,
                    "listening_state": "active",
                    "context": self.get_conversation_context()
                }
                
        except Exception as e:
            logger.error(f"Error processing ambient audio: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def extract_command_after_wake_word(self, text: str) -> str:
        """Extract command after wake word"""
        text_lower = text.lower()
        
        # Remove wake words and extract command
        for wake_word in self.wake_words:
            if wake_word in text_lower:
                parts = text_lower.split(wake_word, 1)
                if len(parts) > 1:
                    command = parts[1].strip()
                    if command:
                        return command
        
        return ""
    
    def is_end_conversation_command(self, text: str) -> bool:
        """Check if text contains conversation end command"""
        text_lower = text.lower()
        end_commands = [
            "goodbye", "bye", "see you later", "talk to you later",
            "stop", "end", "finish", "that's all", "thank you buddy"
        ]
        
        return any(cmd in text_lower for cmd in end_commands)
    
    def get_conversation_context(self) -> List[Dict[str, Any]]:
        """Get recent conversation context"""
        return self.context_buffer[-5:]  # Last 5 interactions
    
    def check_conversation_timeout(self) -> bool:
        """Check if conversation has timed out due to silence"""
        if not self.conversation_active or not self.last_interaction_time:
            return False
            
        return (time.time() - self.last_interaction_time) > self.silence_timeout
    
    async def handle_conversation_timeout(self) -> Dict[str, Any]:
        """Handle conversation timeout"""
        if self.check_conversation_timeout():
            self.conversation_active = False
            return {
                "status": "conversation_timeout",
                "message": "Conversation timed out. Say 'Hey Buddy' to start again.",
                "listening_state": "ambient"
            }
        return {"status": "active", "listening_state": "active"}

    async def speech_to_text(self, audio_data: bytes, enhanced_for_children: bool = True) -> Optional[str]:
        """Convert speech to text using Deepgram Nova 3 with enhanced child speech recognition"""
        try:
            # Configure STT options for child speech and ambient listening
            options = PrerecordedOptions(
                model="nova-3",  # Use Nova 3 for better multi-language speech recognition as requested
                language="multi",  # Support multi-language as requested
                smart_format=True,
                punctuate=True,
                diarize=False,
                alternatives=1,
                tier="nova",
                endpointing=300,  # Shorter endpointing for responsiveness
                vad_turnoff=300,  # Voice activity detection
                utterance_end_ms=1000  # Shorter utterance end for conversation flow
            )
            
            # Create audio source
            audio_source = {"buffer": audio_data}
            
            # Process audio
            response = self.deepgram_client.listen.rest.v("1").transcribe_file(
                audio_source, options
            )
            
            # Extract transcript
            if response.results and response.results.channels:
                transcript = response.results.channels[0].alternatives[0].transcript
                
                # Enhanced processing for child speech
                if enhanced_for_children:
                    transcript = self.enhance_child_speech_recognition(transcript)
                
                if transcript.strip():
                    logger.info(f"STT successful: {transcript[:100]}...")
                    return transcript.strip()
            
            return None
            
        except Exception as e:
            logger.error(f"STT error: {str(e)}")
            return None
    
    def enhance_child_speech_recognition(self, transcript: str) -> str:
        """Enhance transcript for common child speech patterns"""
        if not transcript:
            return transcript
            
        # Common child speech corrections
        corrections = {
            "twy": "try",
            "fwee": "free", 
            "bwue": "blue",
            "gweat": "great",
            "pwease": "please",
            "wove": "love",
            "vewy": "very",
            "widdle": "little",
            "wight": "right",
            "weally": "really"
        }
        
        words = transcript.split()
        corrected_words = []
        
        for word in words:
            word_lower = word.lower().strip('.,!?')
            if word_lower in corrections:
                corrected_word = corrections[word_lower]
                # Preserve original capitalization and punctuation
                if word[0].isupper():
                    corrected_word = corrected_word.capitalize()
                # Add back punctuation
                for punct in '.,!?':
                    if word.endswith(punct):
                        corrected_word += punct
                        break
                corrected_words.append(corrected_word)
            else:
                corrected_words.append(word)
        
        return ' '.join(corrected_words)
    
    async def text_to_speech_with_prosody(self, text: str, personality: str = "friendly_companion", prosody: Dict[str, Any] = None) -> Optional[str]:
        """Convert text to speech with prosody adjustments"""
        try:
            # Get voice configuration
            voice_config = self.voice_personalities.get(personality, self.voice_personalities["friendly_companion"])
            
            # Apply prosody adjustments if provided
            if prosody:
                # Adjust model based on prosody tone
                tone = prosody.get("tone", "friendly")
                if tone == "soothing":
                    voice_config["model"] = "aura-luna-en"  # Softer voice
                elif tone == "excited":
                    voice_config["model"] = "aura-asteria-en"  # More energetic
                elif tone == "narrative":
                    voice_config["model"] = "aura-luna-en"  # Good for storytelling
                
                # Adjust text based on prosody pace
                pace = prosody.get("pace", "normal")
                if pace == "slow" or pace == "very_slow":
                    # Add pauses for slower speech
                    text = text.replace(".", "... ").replace(",", ", ")
                elif pace == "fast":
                    # Remove some pauses for faster speech
                    text = text.replace("... ", ". ")
                
                # Adjust emphasis
                emphasis = prosody.get("emphasis", "balanced")
                if emphasis == "dramatic":
                    # Add more emphasis punctuation
                    text = text.replace("!", "!!").replace("?", "??")
                elif emphasis == "calming":
                    # Remove excessive punctuation
                    text = text.replace("!!", "!").replace("??", "?")
            
            # Configure TTS options
            options = SpeakOptions(
                model=voice_config["model"],
                encoding=voice_config["encoding"],
                sample_rate=voice_config["sample_rate"]
            )
            
            # Generate speech using the correct format
            response = self.deepgram_client.speak.rest.v("1").stream({
                "text": text
            }, options)
            
            # Convert to base64 for frontend
            audio_base64 = base64.b64encode(response.stream.read()).decode('utf-8')
            
            logger.info(f"TTS with prosody successful for text: {text[:50]}...")
            return audio_base64
            
        except Exception as e:
            logger.error(f"TTS with prosody error: {str(e)}")
            # Fallback to regular TTS
            return await self.text_to_speech(text, personality)

    async def text_to_speech(self, text: str, personality: str = "friendly_companion") -> Optional[str]:
        """Convert text to speech using Deepgram Aura 2"""
        try:
            # Get voice configuration
            voice_config = self.voice_personalities.get(personality, self.voice_personalities["friendly_companion"])
            
            # Configure TTS options
            options = SpeakOptions(
                model=voice_config["model"],
                encoding=voice_config["encoding"],
                sample_rate=voice_config["sample_rate"]
            )
            
            # Generate speech using the correct format
            response = self.deepgram_client.speak.rest.v("1").stream({
                "text": text
            }, options)
            
            # Convert to base64 for frontend
            audio_base64 = base64.b64encode(response.stream.read()).decode('utf-8')
            
            logger.info(f"TTS successful for text: {text[:50]}...")
            return audio_base64
            
        except Exception as e:
            logger.error(f"TTS error: {str(e)}")
            return None
    
    async def detect_language(self, audio_data: bytes) -> str:
        """Detect language from audio (supports English + Hindi/Hinglish)"""
        try:
            options = PrerecordedOptions(
                model="nova-2",
                detect_language=True,
                alternatives=1
            )
            
            audio_source = {"buffer": audio_data}
            response = self.deepgram_client.listen.rest.v("1").transcribe_file(
                audio_source, options
            )
            
            if response.results and response.results.channels:
                detected_lang = response.results.channels[0].detected_language
                logger.info(f"Detected language: {detected_lang}")
                return detected_lang
            
            return "en"  # Default to English
            
        except Exception as e:
            logger.error(f"Language detection error: {str(e)}")
            return "en"
    
    def get_available_voices(self) -> Dict[str, Any]:
        """Get available voice personalities"""
        return {
            "friendly_companion": {
                "name": "Friendly Companion",
                "description": "Warm and encouraging voice for daily conversations",
                "sample_text": "Hi there! I'm your friendly AI companion. What would you like to talk about today?"
            },
            "story_narrator": {
                "name": "Story Narrator", 
                "description": "Engaging storyteller voice for bedtime stories",
                "sample_text": "Once upon a time, in a magical forest far away, there lived a very special little rabbit..."
            },
            "learning_buddy": {
                "name": "Learning Buddy",
                "description": "Patient teacher voice for educational content",
                "sample_text": "That's a great question! Let me help you understand this step by step."
            }
        }