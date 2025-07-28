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
            
            # Check if audio looks like a valid audio format
            audio_header = audio_data[:12] if len(audio_data) >= 12 else audio_data
            logger.info(f"Audio header: {audio_header}")
            
            # Prepare headers
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "audio/wav"  # Assume WAV format
            }
            
            # If the audio data looks like WebM, try to handle it
            if audio_data.startswith(b'\x1a\x45\xdf\xa3'):  # WebM signature
                logger.info("Detected WebM audio format")
                headers["Content-Type"] = "audio/webm"
            elif audio_data.startswith(b'RIFF'):
                logger.info("Detected RIFF/WAV audio format")
                headers["Content-Type"] = "audio/wav"
            elif audio_data.startswith(b'OggS'):
                logger.info("Detected OGG audio format")
                headers["Content-Type"] = "audio/ogg"
            else:
                logger.warning("Unknown audio format, assuming WAV")
            
            # Prepare query parameters for STT options
            params = {
                "model": "nova-3",  # Use Nova 3 for better multi-language speech recognition as requested
                "language": "multi",  # Support multi-language as requested
                "smart_format": "true",
                "punctuate": "true",
                "diarize": "false",
                "alternatives": "1",
                "tier": "nova",
                "endpointing": "300",  # Shorter endpointing for responsiveness
                "vad_turnoff": "300",  # Voice activity detection
                "utterance_end_ms": "1000"  # Shorter utterance end for conversation flow
            }
            
            logger.info(f"Making STT request to Deepgram: {len(audio_data)} bytes, Content-Type: {headers['Content-Type']}")
            
            # Make REST API call using requests in async context
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(
                    f"{self.base_url}/listen",
                    headers=headers,
                    params=params,
                    data=audio_data
                )
            )
            
            logger.info(f"STT response: status={response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"STT result structure: {list(result.keys()) if isinstance(result, dict) else 'not dict'}")
                
                # Extract transcript
                if result.get("results") and result["results"].get("channels"):
                    transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
                    
                    # Enhanced processing for child speech
                    if enhanced_for_children:
                        transcript = self.enhance_child_speech_recognition(transcript)
                    
                    if transcript.strip():
                        logger.info(f"STT successful: '{transcript}'")
                        return transcript.strip()
                    else:
                        logger.info("STT returned empty transcript")
                        return None
                else:
                    logger.warning(f"STT response missing expected structure: {result}")
                    return None
            else:
                error_text = response.text
                logger.error(f"STT API error: {response.status_code} - {error_text}")
                return None
            
        except Exception as e:
            logger.error(f"STT processing error: {str(e)}", exc_info=True)
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
        """Convert text to speech with prosody adjustments using REST API"""
        try:
            # Get voice configuration
            voice_config = self.voice_personalities.get(personality, self.voice_personalities["friendly_companion"])
            
            # Apply prosody adjustments if provided
            model = voice_config["model"]
            if prosody:
                # Adjust model based on prosody tone
                tone = prosody.get("tone", "friendly")
                if tone == "soothing":
                    model = "aura-luna-en"  # Softer voice
                elif tone == "excited":
                    model = "aura-asteria-en"  # More energetic
                elif tone == "narrative":
                    model = "aura-luna-en"  # Good for storytelling
                
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
                "model": model
            }
            
            # Make REST API call using requests in async context
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(
                    f"{self.base_url}/speak",
                    headers=headers,
                    params=params,
                    json=payload
                )
            )
            
            if response.status_code == 200:
                audio_data = response.content
                # Convert to base64 for frontend
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                logger.info(f"TTS with prosody successful for text: {text[:50]}...")
                return audio_base64
            else:
                logger.error(f"TTS API error: {response.status_code} - {response.text}")
            
            return None
            
        except Exception as e:
            logger.error(f"TTS with prosody error: {str(e)}")
            # Fallback to regular TTS
            return await self.text_to_speech(text, personality)

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
            
            # Make REST API call using requests in async context
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(
                    f"{self.base_url}/speak",
                    headers=headers,
                    params=params,
                    json=payload
                )
            )
            
            if response.status_code == 200:
                audio_data = response.content
                # Convert to base64 for frontend
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                logger.info(f"TTS successful for text: {text[:50]}...")
                return audio_base64
            else:
                logger.error(f"TTS API error: {response.status_code} - {response.text}")
            
            return None
            
        except Exception as e:
            logger.error(f"TTS error: {str(e)}")
            return None
    
    async def detect_language(self, audio_data: bytes) -> str:
        """Detect language from audio using REST API (supports English + Hindi/Hinglish)"""
        try:
            # Prepare headers
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "audio/wav"
            }
            
            # Prepare query parameters
            params = {
                "model": "nova-2",
                "detect_language": "true",
                "alternatives": "1"
            }
            
            # Make REST API call using requests in async context
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(
                    f"{self.base_url}/listen",
                    headers=headers,
                    params=params,
                    data=audio_data
                )
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("results") and result["results"].get("channels"):
                    detected_lang = result["results"]["channels"][0].get("detected_language", "en")
                    logger.info(f"Detected language: {detected_lang}")
                    return detected_lang
            else:
                logger.error(f"Language detection API error: {response.status_code} - {response.text}")
            
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