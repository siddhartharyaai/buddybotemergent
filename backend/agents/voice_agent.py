"""
Voice Agent - Simplified Speech-to-Text and Text-to-Speech using Deepgram REST API
"""
import asyncio
import logging
import base64
import requests
from typing import Optional, Dict, Any


logger = logging.getLogger(__name__)


class VoiceAgent:
    """Simplified voice processing with Deepgram Nova 3 STT and Aura 2 TTS using REST API"""
    
    def __init__(self, deepgram_api_key: str):
        self.api_key = deepgram_api_key
        self.base_url = "https://api.deepgram.com/v1"
        self.voice_personalities = {
            "friendly_companion": {
                "model": "aura-2-amalthea-en",
            },
            "story_narrator": {
                "model": "aura-2-amalthea-en",
            },
            "learning_buddy": {
                "model": "aura-2-amalthea-en",
            }
        }
        
        logger.info("Voice Agent initialized with simplified Deepgram REST API")

    async def speech_to_text(self, audio_data: bytes, enhanced_for_children: bool = True) -> Optional[str]:
        """Convert speech to text using Deepgram Nova 3 REST API with enhanced child speech recognition"""
        try:
            # Log audio details for debugging
            logger.info(f"STT processing: {len(audio_data)} bytes audio data")
            
            # Validate audio data
            if len(audio_data) < 100:
                logger.warning(f"Audio data too small for STT: {len(audio_data)} bytes")
                return None
            
            # Detect audio format
            if audio_data.startswith(b'\x1a\x45\xdf\xa3'):  # WebM signature
                content_type = "audio/webm"
            elif audio_data.startswith(b'RIFF'):
                content_type = "audio/wav"
            elif audio_data.startswith(b'OggS'):
                content_type = "audio/ogg"
            else:
                content_type = "audio/wav"  # Default
            
            # Prepare headers
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": content_type
            }
            
            # Simplified parameters for reliability
            params = {
                "model": "nova-2",
                "language": "en",
                "smart_format": "true",
                "punctuate": "true",
            }
            
            logger.info(f"Making STT request to Deepgram: {len(audio_data)} bytes, Content-Type: {content_type}")
            
            # Make REST API call using requests in async context
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(
                    f"{self.base_url}/listen",
                    headers=headers,
                    params=params,
                    data=audio_data,
                    timeout=10
                )
            )
            
            logger.info(f"STT response: status={response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"STT response structure: {result}")
                
                # Extract transcript
                if result.get("results") and result["results"].get("channels"):
                    channel = result["results"]["channels"][0]
                    if channel.get("alternatives") and len(channel["alternatives"]) > 0:
                        transcript = channel["alternatives"][0]["transcript"]
                        
                        # Enhanced processing for child speech
                        if enhanced_for_children:
                            transcript = self.enhance_child_speech_recognition(transcript)
                        
                        if transcript.strip():
                            logger.info(f"STT successful: '{transcript}'")
                            return transcript.strip()
                        else:
                            logger.warning("STT returned empty transcript")
                            return None
                    else:
                        logger.warning("STT response missing alternatives")
                        return None
                else:
                    logger.warning(f"STT response missing expected structure: {result}")
                    return None
            else:
                logger.error(f"STT API error: {response.status_code} - {response.text}")
                return None
            
        except Exception as e:
            logger.error(f"STT processing error: {str(e)}")
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
    
    async def text_to_speech(self, text: str, personality: str = "friendly_companion") -> Optional[str]:
        """Convert text to speech using Deepgram Aura 2 REST API"""
        try:
            # Get voice configuration
            voice_config = self.voice_personalities.get(personality, self.voice_personalities["friendly_companion"])
            
            # Prepare headers
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Prepare request body
            payload = {
                "text": text
            }
            
            # Prepare query parameters
            params = {
                "model": voice_config["model"]
            }
            
            logger.info(f"Making TTS request: {text[:50]}...")
            
            # Make REST API call using requests in async context
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(
                    f"{self.base_url}/speak",
                    headers=headers,
                    params=params,
                    json=payload,
                    timeout=15
                )
            )
            
            if response.status_code == 200:
                audio_data = response.content
                # Convert to base64 for frontend
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                logger.info(f"TTS successful, audio size: {len(audio_base64)} chars")
                return audio_base64
            else:
                logger.error(f"TTS API error: {response.status_code} - {response.text}")
                return None
            
        except Exception as e:
            logger.error(f"TTS error: {str(e)}")
            return None
    
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