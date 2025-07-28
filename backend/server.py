"""
AI Companion Device Backend - Multi-Agent Architecture
"""
from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import logging
from pathlib import Path
import base64
import json
from typing import Dict, List, Any
from datetime import datetime

# Import models
from models.user_models import UserProfile, UserProfileCreate, UserProfileUpdate, ParentalControls, ParentalControlsCreate, ParentalControlsUpdate
from models.conversation_models import ConversationSession, ConversationSessionCreate, VoiceInput, TextInput, AIResponse, ConversationHistory
from models.content_models import ContentCreate, ContentUpdate, ContentSuggestion, ContentLibrary

# Import agents
from agents.orchestrator import OrchestratorAgent

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment variables
MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
DEEPGRAM_API_KEY = os.environ.get('DEEPGRAM_API_KEY')

# Validate API keys
if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_key_here":
    logger.warning("GEMINI_API_KEY not set properly. Please add your key to .env file.")
if not DEEPGRAM_API_KEY or DEEPGRAM_API_KEY == "your_deepgram_key_here":
    logger.warning("DEEPGRAM_API_KEY not set properly. Please add your key to .env file.")

# MongoDB connection
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Create FastAPI app
app = FastAPI(
    title="AI Companion Device API",
    description="Multi-agent AI companion system for children",
    version="1.0.0"
)

# Create API router
api_router = APIRouter(prefix="/api")

# Initialize orchestrator agent
orchestrator = None

@app.on_event("startup")
async def startup_event():
    """Initialize the multi-agent system"""
    global orchestrator
    try:
        orchestrator = OrchestratorAgent(
            db=db,
            gemini_api_key=GEMINI_API_KEY,
            deepgram_api_key=DEEPGRAM_API_KEY
        )
        logger.info("Multi-agent system initialized successfully")
        
        # Initialize default content if database is empty
        await init_default_content()
        
    except Exception as e:
        logger.error(f"Failed to initialize multi-agent system: {str(e)}")

# User Profile Management
@api_router.post("/users/profile", response_model=UserProfile)
async def create_user_profile(profile_data: UserProfileCreate):
    """Create a new user profile"""
    try:
        profile = UserProfile(**profile_data.dict())
        await db.user_profiles.insert_one(profile.dict())
        
        # Create default parental controls
        parental_controls = ParentalControls(
            user_id=profile.id,
            time_limits={"monday": 60, "tuesday": 60, "wednesday": 60, "thursday": 60, "friday": 60, "saturday": 90, "sunday": 90},
            content_restrictions=[],
            allowed_content_types=["story", "song", "rhyme", "educational"],
            quiet_hours={"start": "20:00", "end": "07:00"},
            monitoring_enabled=True,
            notification_preferences={"activity_summary": True, "safety_alerts": True}
        )
        await db.parental_controls.insert_one(parental_controls.dict())
        
        logger.info(f"Created user profile: {profile.id}")
        return profile
        
    except Exception as e:
        logger.error(f"Error creating user profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create user profile")

@api_router.get("/users/profile/{user_id}", response_model=UserProfile)
async def get_user_profile(user_id: str):
    """Get user profile by ID"""
    try:
        profile = await db.user_profiles.find_one({"id": user_id})
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        return UserProfile(**profile)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user profile")

@api_router.put("/users/profile/{user_id}", response_model=UserProfile)
async def update_user_profile(user_id: str, profile_data: UserProfileUpdate):
    """Update user profile"""
    try:
        update_data = {k: v for k, v in profile_data.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        result = await db.user_profiles.update_one(
            {"id": user_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        updated_profile = await db.user_profiles.find_one({"id": user_id})
        return UserProfile(**updated_profile)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update user profile")

# Parental Controls
@api_router.get("/users/{user_id}/parental-controls", response_model=ParentalControls)
async def get_parental_controls(user_id: str):
    """Get parental controls for user"""
    try:
        controls = await db.parental_controls.find_one({"user_id": user_id})
        if not controls:
            raise HTTPException(status_code=404, detail="Parental controls not found")
        
        return ParentalControls(**controls)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting parental controls: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve parental controls")

@api_router.put("/users/{user_id}/parental-controls", response_model=ParentalControls)
async def update_parental_controls(user_id: str, controls_data: ParentalControlsUpdate):
    """Update parental controls"""
    try:
        update_data = {k: v for k, v in controls_data.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        result = await db.parental_controls.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Parental controls not found")
        
        updated_controls = await db.parental_controls.find_one({"user_id": user_id})
        return ParentalControls(**updated_controls)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating parental controls: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update parental controls")

# Conversation Management
@api_router.post("/conversations/session", response_model=ConversationSession)
async def create_conversation_session(session_data: ConversationSessionCreate):
    """Create a new conversation session"""
    try:
        session = ConversationSession(**session_data.dict())
        await db.conversation_sessions.insert_one(session.dict())
        
        logger.info(f"Created conversation session: {session.id}")
        return session
        
    except Exception as e:
        logger.error(f"Error creating conversation session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create conversation session")

# Ambient Listening Endpoints
@api_router.post("/ambient/start")
async def start_ambient_listening(request: dict):
    """Start ambient listening for wake word detection"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="Multi-agent system not initialized")
        
        session_id = request.get("session_id")
        user_id = request.get("user_id")
        
        if not session_id or not user_id:
            raise HTTPException(status_code=400, detail="session_id and user_id are required")
        
        # Get user profile
        user_profile = await db.user_profiles.find_one({"id": user_id})
        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        result = await orchestrator.start_ambient_listening(session_id, user_profile)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting ambient listening: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start ambient listening")

@api_router.post("/ambient/stop")
async def stop_ambient_listening(request: dict):
    """Stop ambient listening"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="Multi-agent system not initialized")
        
        session_id = request.get("session_id")
        if not session_id:
            raise HTTPException(status_code=400, detail="session_id is required")
        
        result = await orchestrator.stop_ambient_listening(session_id)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping ambient listening: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to stop ambient listening")

@api_router.post("/ambient/process")
async def process_ambient_audio(request: dict):
    """Process ambient audio for wake word detection"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="Multi-agent system not initialized")
        
        session_id = request.get("session_id")
        audio_base64 = request.get("audio_base64")
        
        if not session_id or not audio_base64:
            raise HTTPException(status_code=400, detail="session_id and audio_base64 are required")
        
        # Decode audio data
        audio_data = base64.b64decode(audio_base64)
        
        # Process through orchestrator
        result = await orchestrator.process_ambient_audio(session_id, audio_data)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing ambient audio: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process ambient audio")

@api_router.get("/ambient/status/{session_id}")
async def get_ambient_status(session_id: str):
    """Get ambient listening status"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="Multi-agent system not initialized")
        
        # Check conversation timeout
        timeout_result = await orchestrator.check_conversation_timeout(session_id)
        
        # Get session info
        session_info = orchestrator.session_store.get(session_id, {})
        
        return {
            "session_id": session_id,
            "ambient_listening": session_info.get("ambient_listening", False),
            "conversation_active": timeout_result.get("status") == "active",
            "listening_state": timeout_result.get("listening_state", "inactive"),
            "timeout_status": timeout_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ambient status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get ambient status")

@api_router.post("/conversations/voice", response_model=AIResponse)
async def process_voice_input(voice_input: VoiceInput):
    """Process voice input through the multi-agent system"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="Multi-agent system not initialized")
        
        # Get user profile
        user_profile = await db.user_profiles.find_one({"id": voice_input.user_id})
        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Decode audio data
        audio_data = base64.b64decode(voice_input.audio_base64)
        
        # Process through orchestrator
        result = await orchestrator.process_voice_input(
            voice_input.session_id,
            audio_data,
            user_profile
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return AIResponse(
            response_text=result["response_text"],
            response_audio=result.get("response_audio"),
            content_type=result.get("content_type", "conversation"),
            metadata=result.get("metadata", {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing voice input: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process voice input")

@api_router.post("/conversations/text", response_model=AIResponse)
async def process_text_input(text_input: TextInput):
    """Process text input through the multi-agent system"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="Multi-agent system not initialized")
        
        # Get user profile
        user_profile = await db.user_profiles.find_one({"id": text_input.user_id})
        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Process through orchestrator
        result = await orchestrator.process_text_input(
            text_input.session_id,
            text_input.message,
            user_profile
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return AIResponse(
            response_text=result["response_text"],
            response_audio=result.get("response_audio"),
            content_type=result.get("content_type", "conversation"),
            metadata=result.get("metadata", {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing text input: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process text input")

# Content Management
@api_router.get("/content/suggestions/{user_id}", response_model=List[ContentSuggestion])
async def get_content_suggestions(user_id: str):
    """Get content suggestions for user"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="Multi-agent system not initialized")
        
        # Get user profile
        user_profile = await db.user_profiles.find_one({"id": user_id})
        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Get suggestions from content agent
        suggestions = await orchestrator.content_agent.get_content_suggestions(user_profile)
        
        return [ContentSuggestion(**suggestion) for suggestion in suggestions]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting content suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get content suggestions")

@api_router.get("/content/{content_type}/{user_id}")
async def get_content_by_type(content_type: str, user_id: str):
    """Get content by type for user"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="Multi-agent system not initialized")
        
        # Get user profile
        user_profile = await db.user_profiles.find_one({"id": user_id})
        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Get content from content agent
        content = await orchestrator.content_agent.get_content_by_type(content_type, user_profile)
        
        if not content:
            raise HTTPException(status_code=404, detail="No content found for this type")
        
        return content
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting content by type: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get content")

# Voice Personalities
@api_router.get("/voice/personalities")
async def get_voice_personalities():
    """Get available voice personalities"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="Multi-agent system not initialized")
        
        personalities = orchestrator.voice_agent.get_available_voices()
        return personalities
        
    except Exception as e:
        logger.error(f"Error getting voice personalities: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get voice personalities")

# Health Check
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agents": {
            "orchestrator": orchestrator is not None,
            "gemini_configured": GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_key_here",
            "deepgram_configured": DEEPGRAM_API_KEY and DEEPGRAM_API_KEY != "your_deepgram_key_here"
        },
        "database": "connected"
    }

# WebSocket for real-time communication
@api_router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time communication"""
    await websocket.accept()
    
    try:
        # Get user profile
        user_profile = await db.user_profiles.find_one({"id": user_id})
        if not user_profile:
            await websocket.send_text(json.dumps({"error": "User profile not found"}))
            await websocket.close()
            return
        
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "text":
                # Process text message
                result = await orchestrator.process_text_input(
                    message_data["session_id"],
                    message_data["message"],
                    user_profile
                )
                
                await websocket.send_text(json.dumps(result))
                
            elif message_data.get("type") == "voice":
                # Process voice message
                audio_data = base64.b64decode(message_data["audio_base64"])
                result = await orchestrator.process_voice_input(
                    message_data["session_id"],
                    audio_data,
                    user_profile
                )
                
                await websocket.send_text(json.dumps(result))
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user: {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.send_text(json.dumps({"error": "Connection error"}))

async def init_default_content():
    """Initialize default content if database is empty"""
    try:
        # Check if content exists
        story_count = await db.stories.count_documents({})
        
        if story_count == 0:
            logger.info("Initializing default content...")
            
            # Add default stories
            default_stories = [
                {
                    "id": "story_001",
                    "title": "The Happy Little Bear",
                    "content": "Once there was a little bear who loved to play. He played with his friends every day in the forest. The bear was always happy and kind to everyone. The end!",
                    "age_group": "toddler",
                    "language": "english",
                    "tags": ["animals", "friendship", "happiness"],
                    "difficulty_level": 1,
                    "content_type": "story",
                    "story_type": "fairy_tale",
                    "reading_time": 2
                },
                {
                    "id": "story_002", 
                    "title": "The Brave Little Mouse",
                    "content": "A small mouse lived in a big house. One day, he helped his family by being very brave and clever. Everyone was proud of him and celebrated his courage!",
                    "age_group": "child",
                    "language": "english",
                    "tags": ["courage", "family", "problem-solving"],
                    "difficulty_level": 2,
                    "content_type": "story",
                    "story_type": "moral",
                    "reading_time": 3
                }
            ]
            
            await db.stories.insert_many(default_stories)
            
            # Add default songs
            default_songs = [
                {
                    "id": "song_001",
                    "title": "Twinkle Twinkle Little Star",
                    "content": "Twinkle, twinkle, little star, How I wonder what you are! Up above the world so high, Like a diamond in the sky!",
                    "age_group": "toddler",
                    "language": "english",
                    "tags": ["stars", "wonder", "night"],
                    "difficulty_level": 1,
                    "content_type": "song",
                    "song_type": "lullaby",
                    "lyrics": "Twinkle, twinkle, little star, How I wonder what you are!",
                    "duration": 60
                }
            ]
            
            await db.songs.insert_many(default_songs)
            
            logger.info("Default content initialized successfully")
            
    except Exception as e:
        logger.error(f"Error initializing default content: {str(e)}")

# Include router in main app
app.include_router(api_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    """Cleanup on shutdown"""
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
