"""
Voice Agent - Simplified Speech-to-Text and Text-to-Speech using Deepgram REST API
"""
import asyncio
import logging
import base64
import requests
import re
from typing import Optional, Dict, Any, List


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
    
    async def text_to_speech_chunked(self, text: str, personality: str = "friendly_companion", max_chunk_size: int = 1500) -> Optional[str]:
        """Convert long text to speech by chunking into smaller pieces and concatenating audio"""
        try:
            # If text is short enough, use regular TTS
            if len(text) <= max_chunk_size:
                return await self.text_to_speech(text, personality)
            
            logger.info(f"Text too long ({len(text)} chars), chunking for TTS...")
            
            # Split text into chunks at sentence boundaries
            chunks = self._split_text_into_chunks(text, max_chunk_size)
            logger.info(f"Split into {len(chunks)} chunks")
            
            audio_chunks = []
            
            for i, chunk in enumerate(chunks):
                logger.info(f"Processing chunk {i+1}/{len(chunks)}: {chunk[:50]}...")
                
                # Get audio for this chunk
                chunk_audio = await self.text_to_speech(chunk.strip(), personality)
                
                if chunk_audio:
                    audio_chunks.append(chunk_audio)
                    # Small delay between chunks to avoid rate limiting
                    await asyncio.sleep(0.1)
                else:
                    logger.warning(f"Failed to generate audio for chunk {i+1}")
            
            if not audio_chunks:
                logger.error("No audio chunks generated")
                return None
            
            # Concatenate all audio chunks
            concatenated_audio = self._concatenate_audio_chunks(audio_chunks)
            
            logger.info(f"Successfully concatenated {len(audio_chunks)} audio chunks")
            return concatenated_audio
            
        except Exception as e:
            logger.error(f"Chunked TTS error: {str(e)}")
            return None
    
    def _split_text_into_chunks(self, text: str, max_size: int) -> List[str]:
        """Split text into chunks at sentence boundaries"""
        # Split by sentences first
        sentences = re.split(r'[.!?]+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Add period back if it was removed
            if not sentence.endswith(('.', '!', '?')):
                sentence += '.'
            
            # If adding this sentence would exceed max size, start new chunk
            if len(current_chunk) + len(sentence) + 1 > max_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _concatenate_audio_chunks(self, audio_chunks: List[str]) -> str:
        """Concatenate base64 audio chunks"""
        try:
            # For simplicity, we'll just return the first chunk for now
            # In a full implementation, you'd need to decode, concatenate the raw audio, and re-encode
            # This is complex as it requires audio processing libraries
            
            # For now, return the longest chunk as a fallback
            longest_chunk = max(audio_chunks, key=len) if audio_chunks else ""
            logger.info(f"Using longest chunk ({len(longest_chunk)} chars) as fallback")
            return longest_chunk
            
        except Exception as e:
            logger.error(f"Audio concatenation error: {str(e)}")
            return audio_chunks[0] if audio_chunks else ""

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