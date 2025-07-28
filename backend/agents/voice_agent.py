"""
Voice Agent - Handles Speech-to-Text and Text-to-Speech using Deepgram
"""
import asyncio
import logging
import base64
import io
from typing import Optional, Dict, Any
from deepgram import DeepgramClient, PrerecordedOptions, SpeakOptions
from deepgram.clients.speak.v1 import SpeakSource

logger = logging.getLogger(__name__)

class VoiceAgent:
    """Handles voice processing with Deepgram Nova 3 STT and Aura 2 TTS"""
    
    def __init__(self, deepgram_api_key: str):
        self.deepgram_client = DeepgramClient(deepgram_api_key)
        self.voice_personalities = {
            "friendly_companion": {
                "model": "aura-asteria-en",
                "encoding": "linear16",
                "sample_rate": 24000
            },
            "story_narrator": {
                "model": "aura-luna-en", 
                "encoding": "linear16",
                "sample_rate": 24000
            },
            "learning_buddy": {
                "model": "aura-stella-en",
                "encoding": "linear16", 
                "sample_rate": 24000
            }
        }
        
        logger.info("Voice Agent initialized with Deepgram")
    
    async def speech_to_text(self, audio_data: bytes) -> Optional[str]:
        """Convert speech to text using Deepgram Nova 3"""
        try:
            # Configure STT options for child speech
            options = PrerecordedOptions(
                model="nova-2",  # Use Nova 2 for better child speech recognition
                language="en-US",
                smart_format=True,
                punctuate=True,
                diarize=False,
                alternatives=1,
                tier="nova"
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
                logger.info(f"STT successful: {transcript[:100]}...")
                return transcript.strip()
            
            return None
            
        except Exception as e:
            logger.error(f"STT error: {str(e)}")
            return None
    
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
            
            # Create speak source
            speak_source = SpeakSource(text)
            
            # Generate speech
            response = self.deepgram_client.speak.rest.v("1").stream(speak_source, options)
            
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