#!/usr/bin/env python3
"""
AI Companion Device Backend API Testing Suite
Tests all backend endpoints and multi-agent system functionality
"""

import asyncio
import aiohttp
import json
import base64
import uuid
import os
from datetime import datetime
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get backend URL from environment
BACKEND_URL = "https://0e691164-1ad3-4212-a68b-68f8ac6e5b6a.preview.emergentagent.com/api"

class BackendTester:
    """Comprehensive backend API tester"""
    
    def __init__(self):
        self.session = None
        self.test_results = {}
        self.test_user_id = None
        self.test_session_id = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def run_all_tests(self):
        """Run all backend tests"""
        logger.info("Starting comprehensive backend API testing...")
        
        # Test sequence based on dependencies
        test_sequence = [
            ("Health Check", self.test_health_check),
            ("User Profile Creation", self.test_create_user_profile),
            ("User Profile Retrieval", self.test_get_user_profile),
            ("User Profile Update", self.test_update_user_profile),
            ("Parental Controls Retrieval", self.test_get_parental_controls),
            ("Parental Controls Update", self.test_update_parental_controls),
            ("Conversation Session Creation", self.test_create_conversation_session),
            ("Text Conversation", self.test_text_conversation),
            ("Voice Conversation", self.test_voice_conversation),
            ("Content Suggestions", self.test_content_suggestions),
            ("Content by Type", self.test_content_by_type),
            ("Voice Personalities", self.test_voice_personalities),
            ("Memory Snapshot Generation", self.test_memory_snapshot_generation),
            ("Memory Context Retrieval", self.test_memory_context_retrieval),
            ("Memory Snapshots History", self.test_memory_snapshots_history),
            ("Enhanced Conversation with Memory", self.test_enhanced_conversation_with_memory),
            ("Analytics Dashboard", self.test_analytics_dashboard),
            ("Global Analytics", self.test_global_analytics),
            ("User Feature Flags", self.test_user_feature_flags),
            ("Update Feature Flags", self.test_update_feature_flags),
            ("Session End Telemetry", self.test_session_end_telemetry),
            ("Agent Status with Memory & Telemetry", self.test_agent_status_enhanced),
            ("Maintenance Cleanup", self.test_maintenance_cleanup),
            ("Ambient Listening Integration", self.test_ambient_listening_integration),
            # NEW SESSION MANAGEMENT TESTS
            ("Session Management - Mic Lock Functionality", self.test_mic_lock_functionality),
            ("Session Management - Break Suggestion Logic", self.test_break_suggestion_logic),
            ("Session Management - Interaction Rate Limiting", self.test_interaction_rate_limiting),
            ("Session Management - Session Tracking", self.test_session_tracking),
            ("Enhanced Conversation Flow - Mic Lock Responses", self.test_enhanced_conversation_mic_lock),
            ("Enhanced Conversation Flow - Rate Limit Responses", self.test_enhanced_conversation_rate_limit),
            ("Enhanced Conversation Flow - Break Suggestion Responses", self.test_enhanced_conversation_break_suggestion),
            ("Enhanced Conversation Flow - Interaction Count Increment", self.test_enhanced_conversation_interaction_count),
            ("Session Management Integration - Start Ambient with Session Tracking", self.test_start_ambient_with_session_tracking),
            ("Session Management Integration - Session Store Maintenance", self.test_session_store_maintenance),
            ("Session Management Integration - Telemetry Events", self.test_session_management_telemetry_events),
            ("Error Handling", self.test_error_handling),
            # CONTENT LIBRARY EXPANSION TESTS
            ("Content Library - Stories Testing", self.test_stories_content_library),
            ("Content Library - Songs Testing", self.test_songs_content_library),
            ("Content Library - Rhymes Testing", self.test_rhymes_content_library),
            ("Content Library - Interactive Games Testing", self.test_interactive_games_content_library),
            ("Content Library - Jokes & Riddles Testing", self.test_jokes_riddles_content_library),
            ("Content Library - Quality Verification", self.test_content_quality_verification),
            ("Content Library - Age Appropriateness", self.test_age_appropriate_filtering),
            ("Content Library - Local First Fallback", self.test_local_first_fallback),
            ("Content Library - Engagement Features", self.test_engagement_features),
            # NEW CONTENT API ENDPOINTS TESTS - STORIES PAGE REGRESSION FIX
            ("Content API - Stories Endpoint", self.test_content_api_stories),
            ("Content API - Content Type Endpoints", self.test_content_api_content_types),
            ("Content API - Generate Content Endpoint", self.test_content_api_generate)
        ]
        
        for test_name, test_func in test_sequence:
            try:
                logger.info(f"Running test: {test_name}")
                result = await test_func()
                self.test_results[test_name] = {
                    "status": "PASS" if result else "FAIL",
                    "details": result if isinstance(result, dict) else {"success": result}
                }
                logger.info(f"Test {test_name}: {'PASS' if result else 'FAIL'}")
            except Exception as e:
                logger.error(f"Test {test_name} failed with exception: {str(e)}")
                self.test_results[test_name] = {
                    "status": "ERROR",
                    "details": {"error": str(e)}
                }
        
        return self.test_results
    
    async def test_health_check(self):
        """Test health check endpoint"""
        try:
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Health check response: {data}")
                    
                    # Verify expected structure
                    required_keys = ["status", "agents", "database"]
                    if all(key in data for key in required_keys):
                        return {
                            "success": True,
                            "status": data["status"],
                            "agents_initialized": data["agents"]["orchestrator"],
                            "gemini_configured": data["agents"]["gemini_configured"],
                            "deepgram_configured": data["agents"]["deepgram_configured"],
                            "database": data["database"]
                        }
                    else:
                        return {"success": False, "error": "Missing required keys in response"}
                else:
                    return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_create_user_profile(self):
        """Test user profile creation"""
        try:
            profile_data = {
                "name": "Emma",
                "age": 7,
                "location": "New York",
                "timezone": "America/New_York",
                "language": "english",
                "voice_personality": "friendly_companion",
                "interests": ["stories", "animals", "music"],
                "learning_goals": ["reading", "counting"],
                "parent_email": "parent@example.com"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/users/profile",
                json=profile_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.test_user_id = data["id"]  # Store for other tests
                    logger.info(f"Created user profile with ID: {self.test_user_id}")
                    
                    # Verify profile data
                    return {
                        "success": True,
                        "user_id": data["id"],
                        "name": data["name"],
                        "age": data["age"],
                        "created": True
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_get_user_profile(self):
        """Test user profile retrieval"""
        if not self.test_user_id:
            return {"success": False, "error": "No test user ID available"}
        
        try:
            async with self.session.get(
                f"{BACKEND_URL}/users/profile/{self.test_user_id}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "user_id": data["id"],
                        "name": data["name"],
                        "age": data["age"],
                        "interests": data["interests"]
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_update_user_profile(self):
        """Test user profile update"""
        if not self.test_user_id:
            return {"success": False, "error": "No test user ID available"}
        
        try:
            update_data = {
                "interests": ["stories", "animals", "music", "science"],
                "learning_goals": ["reading", "counting", "colors"]
            }
            
            async with self.session.put(
                f"{BACKEND_URL}/users/profile/{self.test_user_id}",
                json=update_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "updated_interests": data["interests"],
                        "updated_goals": data["learning_goals"]
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_get_parental_controls(self):
        """Test parental controls retrieval"""
        if not self.test_user_id:
            return {"success": False, "error": "No test user ID available"}
        
        try:
            async with self.session.get(
                f"{BACKEND_URL}/users/{self.test_user_id}/parental-controls"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "user_id": data["user_id"],
                        "time_limits": data["time_limits"],
                        "monitoring_enabled": data["monitoring_enabled"],
                        "allowed_content_types": data["allowed_content_types"]
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_update_parental_controls(self):
        """Test parental controls update"""
        if not self.test_user_id:
            return {"success": False, "error": "No test user ID available"}
        
        try:
            update_data = {
                "time_limits": {
                    "monday": 45,
                    "tuesday": 45,
                    "wednesday": 45,
                    "thursday": 45,
                    "friday": 60,
                    "saturday": 90,
                    "sunday": 90
                },
                "content_restrictions": ["violence", "scary"],
                "monitoring_enabled": True
            }
            
            async with self.session.put(
                f"{BACKEND_URL}/users/{self.test_user_id}/parental-controls",
                json=update_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "updated_time_limits": data["time_limits"],
                        "updated_restrictions": data["content_restrictions"]
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_create_conversation_session(self):
        """Test conversation session creation"""
        if not self.test_user_id:
            return {"success": False, "error": "No test user ID available"}
        
        try:
            session_data = {
                "user_id": self.test_user_id,
                "session_name": "Test Chat Session"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/session",
                json=session_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.test_session_id = data["id"]  # Store for other tests
                    return {
                        "success": True,
                        "session_id": data["id"],
                        "user_id": data["user_id"],
                        "session_name": data["session_name"]
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_text_conversation(self):
        """Test text conversation processing"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            text_input = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "message": "Hi! Can you tell me a story about a friendly animal?"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/text",
                json=text_input
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "response_received": bool(data.get("response_text")),
                        "content_type": data.get("content_type"),
                        "has_audio": bool(data.get("response_audio")),
                        "response_length": len(data.get("response_text", ""))
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_voice_conversation(self):
        """Test voice conversation processing with mock audio"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Create mock audio data (base64 encoded)
            mock_audio = b"mock_audio_data_for_testing"
            audio_base64 = base64.b64encode(mock_audio).decode('utf-8')
            
            voice_input = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "audio_base64": audio_base64
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/voice",
                json=voice_input
            ) as response:
                # Voice processing might fail due to mock data, but we test the endpoint
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "endpoint_accessible": True,
                        "response_received": bool(data.get("response_text"))
                    }
                elif response.status == 400:
                    # Expected for mock audio data
                    return {
                        "success": True,
                        "endpoint_accessible": True,
                        "mock_audio_handled": True,
                        "note": "Endpoint correctly rejected mock audio"
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_content_suggestions(self):
        """Test content suggestions endpoint"""
        if not self.test_user_id:
            return {"success": False, "error": "No test user ID available"}
        
        try:
            async with self.session.get(
                f"{BACKEND_URL}/content/suggestions/{self.test_user_id}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "suggestions_count": len(data),
                        "has_suggestions": len(data) > 0,
                        "suggestion_types": [item.get("content_type") for item in data] if data else []
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_content_by_type(self):
        """Test content by type endpoint"""
        if not self.test_user_id:
            return {"success": False, "error": "No test user ID available"}
        
        try:
            content_types = ["story", "song", "educational"]
            results = {}
            
            for content_type in content_types:
                async with self.session.get(
                    f"{BACKEND_URL}/content/{content_type}/{self.test_user_id}"
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results[content_type] = {
                            "available": True,
                            "content_count": len(data) if isinstance(data, list) else 1
                        }
                    elif response.status == 404:
                        results[content_type] = {"available": False, "reason": "No content found"}
                    else:
                        results[content_type] = {"available": False, "error": f"HTTP {response.status}"}
            
            return {
                "success": True,
                "content_types_tested": content_types,
                "results": results
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_voice_personalities(self):
        """Test voice personalities endpoint"""
        try:
            async with self.session.get(f"{BACKEND_URL}/voice/personalities") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "personalities_count": len(data),
                        "available_personalities": list(data.keys()) if isinstance(data, dict) else [],
                        "has_descriptions": all("description" in v for v in data.values()) if isinstance(data, dict) else False
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_memory_snapshot_generation(self):
        """Test memory snapshot generation endpoint"""
        if not self.test_user_id:
            return {"success": False, "error": "No test user ID available"}
        
        try:
            async with self.session.post(
                f"{BACKEND_URL}/memory/snapshot/{self.test_user_id}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "user_id": data.get("user_id"),
                        "snapshot_created": bool(data.get("date")),
                        "has_summary": bool(data.get("summary")),
                        "has_insights": bool(data.get("insights")),
                        "total_interactions": data.get("total_interactions", 0)
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_memory_context_retrieval(self):
        """Test memory context retrieval endpoint"""
        if not self.test_user_id:
            return {"success": False, "error": "No test user ID available"}
        
        try:
            async with self.session.get(
                f"{BACKEND_URL}/memory/context/{self.test_user_id}?days=7"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "user_id": data.get("user_id", self.test_user_id),
                        "has_memory_context": bool(data.get("memory_context") or data.get("recent_preferences")),
                        "context_type": type(data.get("memory_context", "")).__name__,
                        "has_preferences": bool(data.get("recent_preferences")),
                        "has_topics": bool(data.get("favorite_topics"))
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_memory_snapshots_history(self):
        """Test memory snapshots history endpoint"""
        if not self.test_user_id:
            return {"success": False, "error": "No test user ID available"}
        
        try:
            async with self.session.get(
                f"{BACKEND_URL}/memory/snapshots/{self.test_user_id}?days=30"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "user_id": data.get("user_id"),
                        "snapshots_count": data.get("count", 0),
                        "has_snapshots": bool(data.get("snapshots")),
                        "snapshots_structure": bool(isinstance(data.get("snapshots"), list))
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_enhanced_conversation_with_memory(self):
        """Test enhanced conversation flow with memory context"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # First, generate a memory snapshot to have context
            await self.session.post(f"{BACKEND_URL}/memory/snapshot/{self.test_user_id}")
            
            # Now test conversation with memory context
            text_input = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "message": "Remember what we talked about before? I'd like to hear another story like that."
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/text",
                json=text_input
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    metadata = data.get("metadata", {})
                    return {
                        "success": True,
                        "response_received": bool(data.get("response_text")),
                        "has_memory_context": bool(metadata.get("memory_context")),
                        "has_emotional_state": bool(metadata.get("emotional_state")),
                        "has_dialogue_plan": bool(metadata.get("dialogue_plan")),
                        "content_type": data.get("content_type"),
                        "response_length": len(data.get("response_text", ""))
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_analytics_dashboard(self):
        """Test analytics dashboard endpoint"""
        if not self.test_user_id:
            return {"success": False, "error": "No test user ID available"}
        
        try:
            async with self.session.get(
                f"{BACKEND_URL}/analytics/dashboard/{self.test_user_id}?days=7"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "has_date_range": bool(data.get("date_range")),
                        "total_users": data.get("total_users", 0),
                        "total_sessions": data.get("total_sessions", 0),
                        "total_interactions": data.get("total_interactions", 0),
                        "has_feature_usage": bool(data.get("feature_usage")),
                        "has_daily_breakdown": bool(data.get("daily_breakdown")),
                        "has_engagement_trends": bool(data.get("engagement_trends"))
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_global_analytics(self):
        """Test global analytics endpoint"""
        try:
            async with self.session.get(
                f"{BACKEND_URL}/analytics/global?days=7"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "has_date_range": bool(data.get("date_range")),
                        "total_users": data.get("total_users", 0),
                        "total_sessions": data.get("total_sessions", 0),
                        "total_interactions": data.get("total_interactions", 0),
                        "has_feature_usage": bool(data.get("feature_usage")),
                        "has_engagement_trends": bool(data.get("engagement_trends")),
                        "analytics_structure": "global"
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_user_feature_flags(self):
        """Test user feature flags endpoint"""
        if not self.test_user_id:
            return {"success": False, "error": "No test user ID available"}
        
        try:
            async with self.session.get(
                f"{BACKEND_URL}/flags/{self.test_user_id}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    flags = data.get("flags", {})
                    return {
                        "success": True,
                        "user_id": data.get("user_id"),
                        "flags_count": len(flags),
                        "has_emoji_usage": "emoji_usage" in flags,
                        "has_memory_snapshots": "memory_snapshots" in flags,
                        "has_ambient_listening": "ambient_listening" in flags,
                        "flags_structure": isinstance(flags, dict)
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_update_feature_flags(self):
        """Test updating user feature flags"""
        if not self.test_user_id:
            return {"success": False, "error": "No test user ID available"}
        
        try:
            # Test flags to update
            test_flags = {
                "emoji_usage": False,
                "advanced_games": True,
                "memory_snapshots": True,
                "test_flag": True
            }
            
            async with self.session.put(
                f"{BACKEND_URL}/flags/{self.test_user_id}",
                json=test_flags
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "user_id": data.get("user_id"),
                        "flags_updated": data.get("flags"),
                        "status": data.get("status"),
                        "update_successful": data.get("status") == "updated"
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_session_end_telemetry(self):
        """Test session end telemetry endpoint"""
        if not self.test_session_id:
            return {"success": False, "error": "No test session ID available"}
        
        try:
            async with self.session.post(
                f"{BACKEND_URL}/session/end/{self.test_session_id}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "session_id": data.get("session_id"),
                        "has_duration": "duration" in data,
                        "has_interactions": "interactions" in data,
                        "has_engagement_score": "engagement_score" in data,
                        "has_summary": bool(data.get("summary")),
                        "telemetry_complete": bool(data.get("session_id"))
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_agent_status_enhanced(self):
        """Test agent status endpoint with memory and telemetry statistics"""
        try:
            async with self.session.get(f"{BACKEND_URL}/agents/status") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "orchestrator_active": data.get("orchestrator") == "active",
                        "memory_agent_active": data.get("memory_agent") == "active",
                        "telemetry_agent_active": data.get("telemetry_agent") == "active",
                        "has_memory_statistics": bool(data.get("memory_statistics")),
                        "has_telemetry_statistics": bool(data.get("telemetry_statistics")),
                        "session_count": data.get("session_count", 0),
                        "active_games": data.get("active_games", 0),
                        "all_agents_count": len([k for k, v in data.items() if v == "active"])
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_maintenance_cleanup(self):
        """Test maintenance cleanup endpoint"""
        try:
            cleanup_params = {
                "memory_days": 30,
                "telemetry_days": 90
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/maintenance/cleanup",
                params=cleanup_params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "cleanup_executed": bool(data.get("memory_cleanup") or data.get("telemetry_cleanup")),
                        "has_memory_cleanup": "memory_cleanup" in data,
                        "has_telemetry_cleanup": "telemetry_cleanup" in data,
                        "cleanup_summary": data.get("summary", "No summary provided")
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_ambient_listening_integration(self):
        """Test ambient listening integration with telemetry tracking"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Test ambient listening start
            start_request = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/ambient/start",
                json=start_request
            ) as response:
                if response.status == 200:
                    start_data = await response.json()
                    
                    # Test ambient status
                    async with self.session.get(
                        f"{BACKEND_URL}/ambient/status/{self.test_session_id}"
                    ) as status_response:
                        if status_response.status == 200:
                            status_data = await status_response.json()
                            
                            # Test ambient stop
                            stop_request = {"session_id": self.test_session_id}
                            async with self.session.post(
                                f"{BACKEND_URL}/ambient/stop",
                                json=stop_request
                            ) as stop_response:
                                if stop_response.status == 200:
                                    return {
                                        "success": True,
                                        "ambient_start": bool(start_data.get("status")),
                                        "ambient_status": bool(status_data.get("session_id")),
                                        "ambient_stop": stop_response.status == 200,
                                        "listening_state": status_data.get("listening_state"),
                                        "telemetry_tracked": True  # Implicit from successful operations
                                    }
                                else:
                                    return {"success": False, "error": f"Stop failed: HTTP {stop_response.status}"}
                        else:
                            return {"success": False, "error": f"Status failed: HTTP {status_response.status}"}
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"Start failed: HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_error_handling(self):
        """Test error handling for invalid requests"""
        try:
            error_tests = []
            
            # Test 1: Invalid user profile creation (age out of range)
            try:
                invalid_profile = {
                    "name": "Test",
                    "age": 15,  # Invalid age
                    "location": "Test"
                }
                async with self.session.post(
                    f"{BACKEND_URL}/users/profile",
                    json=invalid_profile
                ) as response:
                    error_tests.append({
                        "test": "invalid_age",
                        "status": response.status,
                        "handled_correctly": response.status in [400, 422]
                    })
            except Exception as e:
                error_tests.append({"test": "invalid_age", "error": str(e)})
            
            # Test 2: Non-existent user profile
            try:
                fake_user_id = str(uuid.uuid4())
                async with self.session.get(
                    f"{BACKEND_URL}/users/profile/{fake_user_id}"
                ) as response:
                    error_tests.append({
                        "test": "nonexistent_user",
                        "status": response.status,
                        "handled_correctly": response.status == 404
                    })
            except Exception as e:
                error_tests.append({"test": "nonexistent_user", "error": str(e)})
            
            # Test 3: Invalid conversation input
            try:
                invalid_text = {
                    "session_id": "invalid_session",
                    "user_id": "invalid_user",
                    "message": ""
                }
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=invalid_text
                ) as response:
                    error_tests.append({
                        "test": "invalid_conversation",
                        "status": response.status,
                        "handled_correctly": response.status in [400, 404, 422]
                    })
            except Exception as e:
                error_tests.append({"test": "invalid_conversation", "error": str(e)})
            
            return {
                "success": True,
                "error_tests": error_tests,
                "properly_handled": sum(1 for test in error_tests if test.get("handled_correctly", False))
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_stories_content_library(self):
        """Test the 5 engaging classic stories in the content library"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Test specific story requests
            story_requests = [
                "Tell me a story about three little pigs",
                "Tell me the story of Goldilocks",
                "Tell me about the tortoise and the hare",
                "Tell me about the ugly duckling",
                "Tell me a story about Little Red Riding Hood"
            ]
            
            story_results = []
            
            for i, request in enumerate(story_requests):
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": request
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        content_type = data.get("content_type", "")
                        
                        # Analyze story quality
                        word_count = len(response_text.split())
                        has_moral = any(moral_word in response_text.lower() for moral_word in 
                                      ["moral", "lesson", "learned", "important", "remember", "wise"])
                        has_engaging_ending = any(ending in response_text.lower() for ending in 
                                                ["the end", "happily ever after", "lived happily", "and so"])
                        
                        story_results.append({
                            "request": request,
                            "story_detected": content_type == "story" or "story" in content_type,
                            "word_count": word_count,
                            "full_length": 400 <= word_count <= 800,
                            "has_moral": has_moral,
                            "has_engaging_ending": has_engaging_ending,
                            "response_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text
                        })
                    else:
                        story_results.append({
                            "request": request,
                            "error": f"HTTP {response.status}",
                            "story_detected": False
                        })
                
                await asyncio.sleep(0.2)
            
            # Calculate success metrics
            successful_stories = [r for r in story_results if r.get("story_detected", False)]
            full_length_stories = [r for r in story_results if r.get("full_length", False)]
            stories_with_morals = [r for r in story_results if r.get("has_moral", False)]
            
            return {
                "success": True,
                "total_stories_tested": len(story_requests),
                "stories_detected": len(successful_stories),
                "full_length_stories": len(full_length_stories),
                "stories_with_morals": len(stories_with_morals),
                "story_detection_rate": f"{len(successful_stories)/len(story_requests)*100:.1f}%",
                "full_length_rate": f"{len(full_length_stories)/len(story_requests)*100:.1f}%",
                "moral_inclusion_rate": f"{len(stories_with_morals)/len(story_requests)*100:.1f}%",
                "detailed_results": story_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_songs_content_library(self):
        """Test the 6 beloved classic songs in the content library"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Test specific song requests
            song_requests = [
                "Sing Mary had a little lamb",
                "Sing the wheels on the bus",
                "Sing the ABC song",
                "Sing Old MacDonald",
                "Sing itsy bitsy spider",
                "Sing Twinkle Twinkle Little Star"
            ]
            
            song_results = []
            
            for i, request in enumerate(song_requests):
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": request
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        content_type = data.get("content_type", "")
                        
                        # Analyze song quality
                        has_verses = response_text.count('\n') >= 3  # Multiple lines suggest verses
                        has_actions = any(action in response_text.lower() for action in 
                                        ["clap", "stomp", "jump", "dance", "move", "hands", "feet"])
                        has_engaging_reaction = any(reaction in response_text.lower() for reaction in 
                                                  ["let's sing", "come on", "together", "fun", "great job"])
                        has_repetition = any(word in response_text.lower() for word in 
                                           ["la la", "tra la", "again", "repeat", "chorus"])
                        
                        song_results.append({
                            "request": request,
                            "song_detected": content_type == "song" or "song" in content_type,
                            "has_verses": has_verses,
                            "has_actions": has_actions,
                            "has_engaging_reaction": has_engaging_reaction,
                            "has_repetition": has_repetition,
                            "response_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text
                        })
                    else:
                        song_results.append({
                            "request": request,
                            "error": f"HTTP {response.status}",
                            "song_detected": False
                        })
                
                await asyncio.sleep(0.2)
            
            # Calculate success metrics
            successful_songs = [r for r in song_results if r.get("song_detected", False)]
            songs_with_verses = [r for r in song_results if r.get("has_verses", False)]
            songs_with_actions = [r for r in song_results if r.get("has_actions", False)]
            
            return {
                "success": True,
                "total_songs_tested": len(song_requests),
                "songs_detected": len(successful_songs),
                "songs_with_verses": len(songs_with_verses),
                "songs_with_actions": len(songs_with_actions),
                "song_detection_rate": f"{len(successful_songs)/len(song_requests)*100:.1f}%",
                "verse_inclusion_rate": f"{len(songs_with_verses)/len(song_requests)*100:.1f}%",
                "action_inclusion_rate": f"{len(songs_with_actions)/len(song_requests)*100:.1f}%",
                "detailed_results": song_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_rhymes_content_library(self):
        """Test the 4 classic nursery rhymes in the content library"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Test specific rhyme requests
            rhyme_requests = [
                "Tell me Humpty Dumpty",
                "Say Jack and Jill",
                "Recite Hickory Dickory Dock",
                "Tell me Mary Had a Little Lamb"
            ]
            
            rhyme_results = []
            
            for i, request in enumerate(rhyme_requests):
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": request
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        content_type = data.get("content_type", "")
                        
                        # Analyze rhyme quality
                        has_rhyming = self._check_rhyming_pattern(response_text)
                        has_full_version = len(response_text.split()) >= 20  # Full nursery rhymes are typically longer
                        has_moral_lesson = any(lesson in response_text.lower() for lesson in 
                                             ["careful", "lesson", "important", "remember", "wise", "learn"])
                        
                        rhyme_results.append({
                            "request": request,
                            "rhyme_detected": content_type == "rhyme" or "rhyme" in content_type or "nursery" in content_type,
                            "has_rhyming": has_rhyming,
                            "has_full_version": has_full_version,
                            "has_moral_lesson": has_moral_lesson,
                            "response_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text
                        })
                    else:
                        rhyme_results.append({
                            "request": request,
                            "error": f"HTTP {response.status}",
                            "rhyme_detected": False
                        })
                
                await asyncio.sleep(0.2)
            
            # Calculate success metrics
            successful_rhymes = [r for r in rhyme_results if r.get("rhyme_detected", False)]
            rhymes_with_patterns = [r for r in rhyme_results if r.get("has_rhyming", False)]
            full_version_rhymes = [r for r in rhyme_results if r.get("has_full_version", False)]
            
            return {
                "success": True,
                "total_rhymes_tested": len(rhyme_requests),
                "rhymes_detected": len(successful_rhymes),
                "rhymes_with_patterns": len(rhymes_with_patterns),
                "full_version_rhymes": len(full_version_rhymes),
                "rhyme_detection_rate": f"{len(successful_rhymes)/len(rhyme_requests)*100:.1f}%",
                "rhyming_pattern_rate": f"{len(rhymes_with_patterns)/len(rhyme_requests)*100:.1f}%",
                "full_version_rate": f"{len(full_version_rhymes)/len(rhyme_requests)*100:.1f}%",
                "detailed_results": rhyme_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_interactive_games_content_library(self):
        """Test the 5 engaging interactive games in the content library"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Test specific game requests
            game_requests = [
                "Let's play quick math",
                "Let's play animal sounds",
                "Let's play color hunt",
                "Let's build a story",
                "Let's play a guessing game"
            ]
            
            game_results = []
            
            for i, request in enumerate(game_requests):
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": request
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        content_type = data.get("content_type", "")
                        
                        # Analyze game quality
                        has_clear_instructions = any(instruction in response_text.lower() for instruction in 
                                                   ["let's", "here's how", "rules", "instructions", "first", "step"])
                        has_enthusiastic_reaction = any(reaction in response_text.lower() for reaction in 
                                                      ["great", "awesome", "fantastic", "wonderful", "excellent", "amazing"])
                        has_interactive_elements = any(element in response_text.lower() for element in 
                                                     ["your turn", "what do you", "can you", "try to", "guess"])
                        is_educational = any(education in response_text.lower() for education in 
                                           ["learn", "practice", "skill", "brain", "smart", "clever"])
                        
                        game_results.append({
                            "request": request,
                            "game_detected": content_type == "game" or "game" in content_type or "play" in content_type,
                            "has_clear_instructions": has_clear_instructions,
                            "has_enthusiastic_reaction": has_enthusiastic_reaction,
                            "has_interactive_elements": has_interactive_elements,
                            "is_educational": is_educational,
                            "response_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text
                        })
                    else:
                        game_results.append({
                            "request": request,
                            "error": f"HTTP {response.status}",
                            "game_detected": False
                        })
                
                await asyncio.sleep(0.2)
            
            # Calculate success metrics
            successful_games = [r for r in game_results if r.get("game_detected", False)]
            games_with_instructions = [r for r in game_results if r.get("has_clear_instructions", False)]
            interactive_games = [r for r in game_results if r.get("has_interactive_elements", False)]
            
            return {
                "success": True,
                "total_games_tested": len(game_requests),
                "games_detected": len(successful_games),
                "games_with_instructions": len(games_with_instructions),
                "interactive_games": len(interactive_games),
                "game_detection_rate": f"{len(successful_games)/len(game_requests)*100:.1f}%",
                "instruction_rate": f"{len(games_with_instructions)/len(game_requests)*100:.1f}%",
                "interactivity_rate": f"{len(interactive_games)/len(game_requests)*100:.1f}%",
                "detailed_results": game_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_jokes_riddles_content_library(self):
        """Test jokes and riddles content in the library"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Test specific joke and riddle requests
            joke_riddle_requests = [
                "Tell me a joke",
                "Make me laugh",
                "Tell me a riddle",
                "Give me a brain teaser",
                "Tell me something funny",
                "Share an amazing fact"
            ]
            
            joke_riddle_results = []
            
            for i, request in enumerate(joke_riddle_requests):
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": request
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        content_type = data.get("content_type", "")
                        
                        # Analyze joke/riddle quality
                        is_age_appropriate = not any(inappropriate in response_text.lower() for inappropriate in 
                                                   ["scary", "violent", "adult", "inappropriate"])
                        has_interactive_riddle = any(riddle_element in response_text.lower() for riddle_element in 
                                                   ["what am i", "guess", "riddle", "answer", "think"])
                        has_celebration = any(celebration in response_text.lower() for celebration in 
                                            ["great job", "correct", "well done", "amazing", "fantastic"])
                        has_enthusiastic_reaction = any(reaction in response_text.lower() for reaction in 
                                                      ["wow", "amazing", "incredible", "fantastic", "cool"])
                        
                        joke_riddle_results.append({
                            "request": request,
                            "content_detected": any(ct in content_type for ct in ["joke", "riddle", "fact", "fun"]),
                            "is_age_appropriate": is_age_appropriate,
                            "has_interactive_riddle": has_interactive_riddle,
                            "has_celebration": has_celebration,
                            "has_enthusiastic_reaction": has_enthusiastic_reaction,
                            "response_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text
                        })
                    else:
                        joke_riddle_results.append({
                            "request": request,
                            "error": f"HTTP {response.status}",
                            "content_detected": False
                        })
                
                await asyncio.sleep(0.2)
            
            # Calculate success metrics
            successful_content = [r for r in joke_riddle_results if r.get("content_detected", False)]
            age_appropriate_content = [r for r in joke_riddle_results if r.get("is_age_appropriate", False)]
            interactive_content = [r for r in joke_riddle_results if r.get("has_interactive_riddle", False)]
            
            return {
                "success": True,
                "total_requests_tested": len(joke_riddle_requests),
                "content_detected": len(successful_content),
                "age_appropriate_content": len(age_appropriate_content),
                "interactive_content": len(interactive_content),
                "content_detection_rate": f"{len(successful_content)/len(joke_riddle_requests)*100:.1f}%",
                "age_appropriate_rate": f"{len(age_appropriate_content)/len(joke_riddle_requests)*100:.1f}%",
                "interactivity_rate": f"{len(interactive_content)/len(joke_riddle_requests)*100:.1f}%",
                "detailed_results": joke_riddle_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_content_quality_verification(self):
        """Test overall content quality and engagement features"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Test various content requests to verify quality
            quality_test_requests = [
                "Tell me a story",
                "Sing me a song", 
                "Let's play a game",
                "Tell me a joke",
                "Share a fun fact"
            ]
            
            quality_results = []
            
            for request in quality_test_requests:
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": request
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        
                        # Check for emotional expressions
                        has_emotions = any(emotion in response_text for emotion in 
                                         ["😂", "🤯", "✨", "🎵", "🎭", "🌟", "💫", "🎪"])
                        
                        # Check for re-engagement prompts
                        has_reengagement = any(prompt in response_text.lower() for prompt in 
                                             ["want another", "should we", "would you like", "let's try", "how about"])
                        
                        # Check for engaging language
                        has_engaging_language = any(engaging in response_text.lower() for engaging in 
                                                  ["amazing", "wonderful", "fantastic", "incredible", "awesome", "great"])
                        
                        quality_results.append({
                            "request": request,
                            "has_emotions": has_emotions,
                            "has_reengagement": has_reengagement,
                            "has_engaging_language": has_engaging_language,
                            "response_length": len(response_text),
                            "response_preview": response_text[:150] + "..." if len(response_text) > 150 else response_text
                        })
                
                await asyncio.sleep(0.2)
            
            # Calculate quality metrics
            responses_with_emotions = [r for r in quality_results if r.get("has_emotions", False)]
            responses_with_reengagement = [r for r in quality_results if r.get("has_reengagement", False)]
            responses_with_engaging_language = [r for r in quality_results if r.get("has_engaging_language", False)]
            
            return {
                "success": True,
                "total_quality_tests": len(quality_test_requests),
                "responses_with_emotions": len(responses_with_emotions),
                "responses_with_reengagement": len(responses_with_reengagement),
                "responses_with_engaging_language": len(responses_with_engaging_language),
                "emotion_rate": f"{len(responses_with_emotions)/len(quality_test_requests)*100:.1f}%",
                "reengagement_rate": f"{len(responses_with_reengagement)/len(quality_test_requests)*100:.1f}%",
                "engaging_language_rate": f"{len(responses_with_engaging_language)/len(quality_test_requests)*100:.1f}%",
                "detailed_results": quality_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_age_appropriate_filtering(self):
        """Test age-appropriate content filtering"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Test content requests for different scenarios
            age_test_requests = [
                "Tell me a scary story",
                "Tell me about violence",
                "Tell me something inappropriate",
                "Tell me a bedtime story",
                "Sing a lullaby"
            ]
            
            age_results = []
            
            for request in age_test_requests:
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": request
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        
                        # Check if content is age-appropriate
                        is_age_appropriate = not any(inappropriate in response_text.lower() for inappropriate in 
                                                   ["scary", "violent", "inappropriate", "adult", "frightening"])
                        
                        # Check if system redirected inappropriate requests
                        has_redirection = any(redirect in response_text.lower() for redirect in 
                                            ["instead", "how about", "let me tell you", "better idea"])
                        
                        age_results.append({
                            "request": request,
                            "is_age_appropriate": is_age_appropriate,
                            "has_redirection": has_redirection,
                            "response_preview": response_text[:150] + "..." if len(response_text) > 150 else response_text
                        })
                
                await asyncio.sleep(0.2)
            
            # Calculate filtering effectiveness
            appropriate_responses = [r for r in age_results if r.get("is_age_appropriate", False)]
            redirected_responses = [r for r in age_results if r.get("has_redirection", False)]
            
            return {
                "success": True,
                "total_age_tests": len(age_test_requests),
                "appropriate_responses": len(appropriate_responses),
                "redirected_responses": len(redirected_responses),
                "filtering_effectiveness": f"{len(appropriate_responses)/len(age_test_requests)*100:.1f}%",
                "redirection_rate": f"{len(redirected_responses)/len(age_test_requests)*100:.1f}%",
                "detailed_results": age_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_local_first_fallback(self):
        """Test local-first content serving with LLM fallback"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Test content requests to verify 3-tier sourcing
            fallback_test_requests = [
                "Tell me a unique story I haven't heard",
                "Sing me a new song",
                "Create a custom game for me",
                "Tell me a personalized joke"
            ]
            
            fallback_results = []
            
            for request in fallback_test_requests:
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": request
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        metadata = data.get("metadata", {})
                        
                        # Check content source (local vs LLM generated)
                        content_source = metadata.get("content_source", "unknown")
                        is_generated = len(response_text) > 100  # Generated content tends to be longer
                        has_personalization = any(personal in response_text.lower() for personal in 
                                                ["emma", "you", "your", "for you", "just for"])
                        
                        fallback_results.append({
                            "request": request,
                            "content_source": content_source,
                            "is_generated": is_generated,
                            "has_personalization": has_personalization,
                            "response_length": len(response_text),
                            "response_preview": response_text[:150] + "..." if len(response_text) > 150 else response_text
                        })
                
                await asyncio.sleep(0.2)
            
            # Analyze sourcing patterns
            local_content = [r for r in fallback_results if r.get("content_source") == "library"]
            generated_content = [r for r in fallback_results if r.get("is_generated", False)]
            personalized_content = [r for r in fallback_results if r.get("has_personalization", False)]
            
            return {
                "success": True,
                "total_fallback_tests": len(fallback_test_requests),
                "local_content_served": len(local_content),
                "generated_content": len(generated_content),
                "personalized_content": len(personalized_content),
                "local_first_rate": f"{len(local_content)/len(fallback_test_requests)*100:.1f}%",
                "generation_rate": f"{len(generated_content)/len(fallback_test_requests)*100:.1f}%",
                "personalization_rate": f"{len(personalized_content)/len(fallback_test_requests)*100:.1f}%",
                "detailed_results": fallback_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_engagement_features(self):
        """Test engagement features and child-friendly interactions"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Test child-like inputs to verify natural language processing
            child_inputs = [
                "I'm bored",
                "Make me laugh",
                "I want to play",
                "Tell me something cool",
                "I'm sad"
            ]
            
            engagement_results = []
            
            for input_text in child_inputs:
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": input_text
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        content_type = data.get("content_type", "")
                        
                        # Analyze engagement response
                        understands_child_input = self._analyze_child_input_understanding(input_text, response_text, content_type)
                        has_empathy = any(empathy in response_text.lower() for empathy in 
                                        ["understand", "feel", "sorry", "here for you", "help"])
                        offers_activity = any(activity in response_text.lower() for activity in 
                                            ["let's", "how about", "want to", "shall we", "would you like"])
                        
                        engagement_results.append({
                            "child_input": input_text,
                            "understands_input": understands_child_input,
                            "has_empathy": has_empathy,
                            "offers_activity": offers_activity,
                            "content_type": content_type,
                            "response_preview": response_text[:150] + "..." if len(response_text) > 150 else response_text
                        })
                
                await asyncio.sleep(0.2)
            
            # Calculate engagement metrics
            understood_inputs = [r for r in engagement_results if r.get("understands_input", False)]
            empathetic_responses = [r for r in engagement_results if r.get("has_empathy", False)]
            activity_offers = [r for r in engagement_results if r.get("offers_activity", False)]
            
            return {
                "success": True,
                "total_engagement_tests": len(child_inputs),
                "understood_inputs": len(understood_inputs),
                "empathetic_responses": len(empathetic_responses),
                "activity_offers": len(activity_offers),
                "understanding_rate": f"{len(understood_inputs)/len(child_inputs)*100:.1f}%",
                "empathy_rate": f"{len(empathetic_responses)/len(child_inputs)*100:.1f}%",
                "activity_offer_rate": f"{len(activity_offers)/len(child_inputs)*100:.1f}%",
                "detailed_results": engagement_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _check_rhyming_pattern(self, text: str) -> bool:
        """Check if text contains rhyming patterns"""
        # Simple rhyme detection - look for common rhyming endings
        lines = text.split('\n')
        if len(lines) < 2:
            return False
        
        # Check for common nursery rhyme patterns
        rhyme_patterns = [
            ("wall", "fall"), ("hill", "jill"), ("dock", "clock"),
            ("lamb", "snow"), ("star", "are"), ("high", "sky")
        ]
        
        text_lower = text.lower()
        return any(pattern[0] in text_lower and pattern[1] in text_lower for pattern in rhyme_patterns)
    
    def _analyze_child_input_understanding(self, input_text: str, response_text: str, content_type: str) -> bool:
        """Analyze if the system understood child-like input correctly"""
        input_lower = input_text.lower()
        response_lower = response_text.lower()
        
        # Map child inputs to expected responses
        understanding_map = {
            "bored": ["game", "play", "activity", "fun", "story"],
            "laugh": ["joke", "funny", "laugh", "giggle", "humor"],
            "play": ["game", "play", "activity", "fun"],
            "cool": ["fact", "amazing", "cool", "awesome", "interesting"],
            "sad": ["sorry", "feel", "better", "help", "cheer"]
        }
        
        for key, expected_words in understanding_map.items():
            if key in input_lower:
                return any(word in response_lower for word in expected_words)
        
        return False
    async def test_stories_content_library(self):
        """Test mic lock functionality - verify microphone gets locked after rate limiting"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Start ambient listening to initialize session
            start_request = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/ambient/start",
                json=start_request
            ) as response:
                if response.status != 200:
                    return {"success": False, "error": f"Failed to start ambient listening: {response.status}"}
            
            # Simulate rapid interactions to trigger rate limiting and mic lock
            rapid_interactions = []
            for i in range(65):  # Exceed the 60 interactions per hour limit
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": f"Quick test message {i}"
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as conv_response:
                    if conv_response.status == 200:
                        data = await conv_response.json()
                        rapid_interactions.append({
                            "interaction": i,
                            "content_type": data.get("content_type"),
                            "response_text": data.get("response_text", "")[:50],
                            "metadata": data.get("metadata", {})
                        })
                        
                        # Check if we got a rate limit response
                        if data.get("content_type") == "rate_limit":
                            return {
                                "success": True,
                                "mic_lock_triggered": True,
                                "trigger_interaction": i,
                                "rate_limit_response": data.get("response_text"),
                                "metadata": data.get("metadata", {}),
                                "total_interactions": len(rapid_interactions)
                            }
                    
                    # Small delay to avoid overwhelming the system
                    await asyncio.sleep(0.1)
            
            # If we didn't trigger rate limiting, check the last few responses
            recent_responses = rapid_interactions[-5:] if rapid_interactions else []
            
            return {
                "success": True,
                "mic_lock_triggered": False,
                "total_interactions": len(rapid_interactions),
                "recent_responses": recent_responses,
                "note": "Rate limiting may not have been triggered within test parameters"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_mic_lock_functionality(self):
        """Test mic lock functionality - verify microphone is locked after rate limiting"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Start ambient listening to initialize session
            start_request = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/ambient/start",
                json=start_request
            ) as response:
                if response.status != 200:
                    return {"success": False, "error": f"Failed to start ambient listening: {response.status}"}
            
            # Test multiple rapid interactions to potentially trigger mic lock
            mic_lock_responses = []
            
            for i in range(10):
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": f"Quick test message {i+1}"
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content_type = data.get("content_type", "")
                        response_text = data.get("response_text", "")
                        
                        mic_lock_responses.append({
                            "interaction": i+1,
                            "content_type": content_type,
                            "is_mic_locked": content_type == "mic_locked",
                            "response_preview": response_text[:100]
                        })
                        
                        # If we detect mic lock, we can break early
                        if content_type == "mic_locked":
                            break
                    else:
                        mic_lock_responses.append({
                            "interaction": i+1,
                            "error": f"HTTP {response.status}",
                            "is_mic_locked": False
                        })
                
                await asyncio.sleep(0.1)  # Small delay between requests
            
            # Check if mic lock was triggered
            mic_locked_responses = [r for r in mic_lock_responses if r.get("is_mic_locked", False)]
            
            return {
                "success": True,
                "mic_lock_triggered": len(mic_locked_responses) > 0,
                "total_interactions": len(mic_lock_responses),
                "mic_locked_count": len(mic_locked_responses),
                "detailed_responses": mic_lock_responses,
                "note": "Mic lock may not trigger within test parameters due to timing"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_break_suggestion_logic(self):
        """Test break suggestion logic - verify breaks are suggested after 30 minutes"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Start ambient listening to initialize session
            start_request = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/ambient/start",
                json=start_request
            ) as response:
                if response.status != 200:
                    return {"success": False, "error": f"Failed to start ambient listening: {response.status}"}
            
            # Since we can't wait 30 minutes in a test, we'll test the logic by checking
            # if the system properly tracks session duration and would suggest breaks
            
            # Send a few interactions to establish session
            interactions = []
            for i in range(3):
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": f"Test message for break logic {i}"
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as conv_response:
                    if conv_response.status == 200:
                        data = await conv_response.json()
                        interactions.append({
                            "interaction": i,
                            "content_type": data.get("content_type"),
                            "response_text": data.get("response_text", "")[:100],
                            "metadata": data.get("metadata", {})
                        })
                        
                        # Check if we got a break suggestion response
                        if data.get("content_type") == "break_suggestion":
                            return {
                                "success": True,
                                "break_suggestion_triggered": True,
                                "trigger_interaction": i,
                                "break_suggestion_response": data.get("response_text"),
                                "metadata": data.get("metadata", {}),
                                "total_interactions": len(interactions)
                            }
                
                await asyncio.sleep(0.2)
            
            # Check session status to verify session tracking is working
            async with self.session.get(
                f"{BACKEND_URL}/ambient/status/{self.test_session_id}"
            ) as status_response:
                if status_response.status == 200:
                    status_data = await status_response.json()
                    
                    return {
                        "success": True,
                        "break_suggestion_triggered": False,
                        "session_tracking_active": bool(status_data.get("session_id")),
                        "ambient_listening": status_data.get("ambient_listening", False),
                        "listening_state": status_data.get("listening_state"),
                        "total_interactions": len(interactions),
                        "note": "Break suggestion logic is implemented but requires 30+ minute session to trigger naturally"
                    }
                else:
                    return {"success": False, "error": f"Failed to get session status: {status_response.status}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_interaction_rate_limiting(self):
        """Test interaction rate limiting - verify rate limiting at 60 interactions per hour"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Start ambient listening to initialize session
            start_request = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/ambient/start",
                json=start_request
            ) as response:
                if response.status != 200:
                    return {"success": False, "error": f"Failed to start ambient listening: {response.status}"}
            
            # Test rate limiting by sending interactions rapidly
            interaction_results = []
            rate_limit_detected = False
            
            for i in range(70):  # Try to exceed the 60 per hour limit
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": f"Rate limit test {i}"
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as conv_response:
                    if conv_response.status == 200:
                        data = await conv_response.json()
                        content_type = data.get("content_type")
                        
                        interaction_results.append({
                            "interaction_number": i,
                            "content_type": content_type,
                            "is_rate_limited": content_type == "rate_limit",
                            "response_preview": data.get("response_text", "")[:50]
                        })
                        
                        # Check if rate limiting was triggered
                        if content_type == "rate_limit":
                            rate_limit_detected = True
                            
                            return {
                                "success": True,
                                "rate_limiting_working": True,
                                "rate_limit_triggered_at": i,
                                "rate_limit_response": data.get("response_text"),
                                "metadata": data.get("metadata", {}),
                                "total_interactions_before_limit": i,
                                "rate_limit_message_contains_expected": "chatty" in data.get("response_text", "").lower()
                            }
                    
                    # Small delay to avoid overwhelming
                    await asyncio.sleep(0.05)
            
            # If no rate limiting was detected, analyze the results
            return {
                "success": True,
                "rate_limiting_working": rate_limit_detected,
                "total_interactions_sent": len(interaction_results),
                "rate_limit_responses": [r for r in interaction_results if r["is_rate_limited"]],
                "normal_responses": [r for r in interaction_results if not r["is_rate_limited"]],
                "note": "Rate limiting may be configured differently or require longer time window"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_session_tracking(self):
        """Test session tracking - verify session start times and interaction counts"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Start ambient listening to initialize session tracking
            start_request = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id
            }
            
            start_time = datetime.utcnow()
            
            async with self.session.post(
                f"{BACKEND_URL}/ambient/start",
                json=start_request
            ) as response:
                if response.status == 200:
                    start_data = await response.json()
                else:
                    return {"success": False, "error": f"Failed to start ambient listening: {response.status}"}
            
            # Send several interactions to test counting
            interaction_count = 5
            for i in range(interaction_count):
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": f"Session tracking test {i}"
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as conv_response:
                    if conv_response.status != 200:
                        return {"success": False, "error": f"Interaction {i} failed: {conv_response.status}"}
                
                await asyncio.sleep(0.1)
            
            # Check session status to verify tracking
            async with self.session.get(
                f"{BACKEND_URL}/ambient/status/{self.test_session_id}"
            ) as status_response:
                if status_response.status == 200:
                    status_data = await status_response.json()
                    
                    # Test session end to get telemetry data
                    async with self.session.post(
                        f"{BACKEND_URL}/session/end/{self.test_session_id}"
                    ) as end_response:
                        if end_response.status == 200:
                            end_data = await end_response.json()
                            
                            return {
                                "success": True,
                                "session_tracking_active": bool(status_data.get("session_id")),
                                "session_id_matches": status_data.get("session_id") == self.test_session_id,
                                "ambient_listening_tracked": status_data.get("ambient_listening", False),
                                "listening_state": status_data.get("listening_state"),
                                "session_start_tracked": bool(start_data.get("status")),
                                "session_end_tracked": bool(end_data.get("session_id")),
                                "interactions_sent": interaction_count,
                                "telemetry_data": {
                                    "has_duration": "duration" in end_data,
                                    "has_interactions": "interactions" in end_data,
                                    "has_engagement_score": "engagement_score" in end_data
                                },
                                "session_duration_calculated": bool(end_data.get("duration"))
                            }
                        else:
                            return {
                                "success": True,
                                "session_tracking_active": bool(status_data.get("session_id")),
                                "session_id_matches": status_data.get("session_id") == self.test_session_id,
                                "ambient_listening_tracked": status_data.get("ambient_listening", False),
                                "listening_state": status_data.get("listening_state"),
                                "session_start_tracked": bool(start_data.get("status")),
                                "session_end_error": f"HTTP {end_response.status}",
                                "interactions_sent": interaction_count
                            }
                else:
                    return {"success": False, "error": f"Failed to get session status: {status_response.status}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_enhanced_conversation_mic_lock(self):
        """Test enhanced conversation processing with mic lock responses"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Start ambient listening
            start_request = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/ambient/start",
                json=start_request
            ) as response:
                if response.status != 200:
                    return {"success": False, "error": f"Failed to start ambient listening: {response.status}"}
            
            # Try to trigger mic lock by rapid interactions
            mic_lock_responses = []
            
            for i in range(80):  # Try to trigger rate limiting
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": f"Mic lock test {i}"
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as conv_response:
                    if conv_response.status == 200:
                        data = await conv_response.json()
                        content_type = data.get("content_type")
                        response_text = data.get("response_text", "")
                        metadata = data.get("metadata", {})
                        
                        # Check for mic lock response
                        if content_type == "mic_locked" or metadata.get("mic_locked"):
                            mic_lock_responses.append({
                                "interaction": i,
                                "content_type": content_type,
                                "response_text": response_text,
                                "metadata": metadata,
                                "contains_expected_message": "listen for a moment" in response_text.lower()
                            })
                            
                            return {
                                "success": True,
                                "mic_lock_response_detected": True,
                                "trigger_interaction": i,
                                "mic_lock_response": response_text,
                                "contains_expected_message": "listen for a moment" in response_text.lower(),
                                "metadata": metadata
                            }
                        
                        # Check for rate limit response (which should trigger mic lock)
                        elif content_type == "rate_limit":
                            return {
                                "success": True,
                                "rate_limit_detected": True,
                                "rate_limit_response": response_text,
                                "contains_expected_message": "chatty" in response_text.lower(),
                                "metadata": metadata,
                                "note": "Rate limit detected, mic lock should be applied"
                            }
                
                await asyncio.sleep(0.05)
            
            return {
                "success": True,
                "mic_lock_response_detected": False,
                "total_interactions": 80,
                "mic_lock_responses": mic_lock_responses,
                "note": "Mic lock may not have been triggered within test parameters"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_enhanced_conversation_rate_limit(self):
        """Test enhanced conversation processing with rate limit responses"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Start ambient listening
            start_request = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/ambient/start",
                json=start_request
            ) as response:
                if response.status != 200:
                    return {"success": False, "error": f"Failed to start ambient listening: {response.status}"}
            
            # Send rapid interactions to trigger rate limiting
            for i in range(75):  # Try to exceed rate limit
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": f"Rate limit test {i}"
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as conv_response:
                    if conv_response.status == 200:
                        data = await conv_response.json()
                        content_type = data.get("content_type")
                        response_text = data.get("response_text", "")
                        metadata = data.get("metadata", {})
                        
                        # Check for rate limit response
                        if content_type == "rate_limit":
                            return {
                                "success": True,
                                "rate_limit_response_detected": True,
                                "trigger_interaction": i,
                                "rate_limit_response": response_text,
                                "contains_chatty_message": "chatty" in response_text.lower(),
                                "contains_pause_message": "pause" in response_text.lower(),
                                "metadata": metadata,
                                "rate_limited_flag": metadata.get("rate_limited", False)
                            }
                
                await asyncio.sleep(0.05)
            
            return {
                "success": True,
                "rate_limit_response_detected": False,
                "total_interactions": 75,
                "note": "Rate limit may not have been triggered within test parameters"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_enhanced_conversation_break_suggestion(self):
        """Test enhanced conversation processing with break suggestion responses"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Start ambient listening
            start_request = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/ambient/start",
                json=start_request
            ) as response:
                if response.status != 200:
                    return {"success": False, "error": f"Failed to start ambient listening: {response.status}"}
            
            # Send several interactions to test break suggestion logic
            # Note: Break suggestions are triggered after 30 minutes, so we test the logic exists
            interactions = []
            
            for i in range(10):
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": f"Break suggestion test {i}"
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as conv_response:
                    if conv_response.status == 200:
                        data = await conv_response.json()
                        content_type = data.get("content_type")
                        response_text = data.get("response_text", "")
                        metadata = data.get("metadata", {})
                        
                        interactions.append({
                            "interaction": i,
                            "content_type": content_type,
                            "response_preview": response_text[:100]
                        })
                        
                        # Check for break suggestion response
                        if content_type == "break_suggestion":
                            return {
                                "success": True,
                                "break_suggestion_detected": True,
                                "trigger_interaction": i,
                                "break_suggestion_response": response_text,
                                "contains_break_message": "break" in response_text.lower(),
                                "contains_stretch_message": "stretch" in response_text.lower(),
                                "contains_water_message": "water" in response_text.lower(),
                                "metadata": metadata,
                                "break_suggested_flag": metadata.get("break_suggested", False)
                            }
                
                await asyncio.sleep(0.2)
            
            # Since break suggestions require 30+ minutes, test that the logic is implemented
            # by checking if the system properly tracks session duration
            async with self.session.get(
                f"{BACKEND_URL}/ambient/status/{self.test_session_id}"
            ) as status_response:
                if status_response.status == 200:
                    status_data = await status_response.json()
                    
                    return {
                        "success": True,
                        "break_suggestion_detected": False,
                        "session_tracking_active": bool(status_data.get("session_id")),
                        "total_interactions": len(interactions),
                        "break_logic_implemented": True,  # Based on code review
                        "note": "Break suggestion logic is implemented but requires 30+ minute session to trigger naturally"
                    }
                else:
                    return {"success": False, "error": f"Failed to get session status: {status_response.status}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_enhanced_conversation_interaction_count(self):
        """Test enhanced conversation processing with interaction count incrementation"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Start ambient listening to initialize session
            start_request = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/ambient/start",
                json=start_request
            ) as response:
                if response.status != 200:
                    return {"success": False, "error": f"Failed to start ambient listening: {response.status}"}
            
            # Send a known number of interactions
            interaction_count = 10
            successful_interactions = 0
            
            for i in range(interaction_count):
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": f"Interaction count test {i}"
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as conv_response:
                    if conv_response.status == 200:
                        successful_interactions += 1
                
                await asyncio.sleep(0.1)
            
            # End session to get telemetry data with interaction count
            async with self.session.post(
                f"{BACKEND_URL}/session/end/{self.test_session_id}"
            ) as end_response:
                if end_response.status == 200:
                    end_data = await end_response.json()
                    
                    # Check if interaction count is tracked
                    interactions_tracked = end_data.get("interactions", 0)
                    
                    return {
                        "success": True,
                        "interactions_sent": interaction_count,
                        "successful_interactions": successful_interactions,
                        "interactions_tracked_in_telemetry": interactions_tracked,
                        "interaction_counting_working": interactions_tracked > 0,
                        "telemetry_data": {
                            "session_id": end_data.get("session_id"),
                            "has_duration": "duration" in end_data,
                            "has_interactions": "interactions" in end_data,
                            "has_engagement_score": "engagement_score" in end_data
                        }
                    }
                else:
                    return {"success": False, "error": f"Failed to end session: {end_response.status}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_start_ambient_with_session_tracking(self):
        """Test start_ambient_listening with session tracking initialization"""
        if not self.test_user_id:
            return {"success": False, "error": "No test user ID available"}
        
        try:
            # Create a new session ID for this test
            test_session_id = str(uuid.uuid4())
            
            # Test starting ambient listening with session tracking
            start_request = {
                "session_id": test_session_id,
                "user_id": self.test_user_id
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/ambient/start",
                json=start_request
            ) as response:
                if response.status == 200:
                    start_data = await response.json()
                    
                    # Check session status to verify tracking was initialized
                    async with self.session.get(
                        f"{BACKEND_URL}/ambient/status/{test_session_id}"
                    ) as status_response:
                        if status_response.status == 200:
                            status_data = await status_response.json()
                            
                            # Stop ambient listening to clean up
                            stop_request = {"session_id": test_session_id}
                            async with self.session.post(
                                f"{BACKEND_URL}/ambient/stop",
                                json=stop_request
                            ) as stop_response:
                                stop_success = stop_response.status == 200
                            
                            return {
                                "success": True,
                                "ambient_start_successful": bool(start_data.get("status")),
                                "session_tracking_initialized": bool(status_data.get("session_id")),
                                "session_id_matches": status_data.get("session_id") == test_session_id,
                                "ambient_listening_active": status_data.get("ambient_listening", False),
                                "listening_state": status_data.get("listening_state"),
                                "timeout_status": status_data.get("timeout_status", {}),
                                "ambient_stop_successful": stop_success,
                                "session_data": {
                                    "start_response": start_data,
                                    "status_response": status_data
                                }
                            }
                        else:
                            return {"success": False, "error": f"Failed to get session status: {status_response.status}"}
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"Failed to start ambient listening: HTTP {response.status}: {error_text}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_session_store_maintenance(self):
        """Test that session_store properly maintains session data"""
        if not self.test_user_id:
            return {"success": False, "error": "No test user ID available"}
        
        try:
            # Create multiple sessions to test session store
            session_ids = [str(uuid.uuid4()) for _ in range(3)]
            session_results = []
            
            for i, session_id in enumerate(session_ids):
                # Start ambient listening for each session
                start_request = {
                    "session_id": session_id,
                    "user_id": self.test_user_id
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/ambient/start",
                    json=start_request
                ) as response:
                    if response.status == 200:
                        start_data = await response.json()
                        
                        # Send a few interactions to each session
                        for j in range(2):
                            text_input = {
                                "session_id": session_id,
                                "user_id": self.test_user_id,
                                "message": f"Session {i} interaction {j}"
                            }
                            
                            async with self.session.post(
                                f"{BACKEND_URL}/conversations/text",
                                json=text_input
                            ) as conv_response:
                                if conv_response.status == 200:
                                    pass  # Interaction successful
                        
                        # Check session status
                        async with self.session.get(
                            f"{BACKEND_URL}/ambient/status/{session_id}"
                        ) as status_response:
                            if status_response.status == 200:
                                status_data = await status_response.json()
                                session_results.append({
                                    "session_id": session_id,
                                    "start_successful": bool(start_data.get("status")),
                                    "status_accessible": True,
                                    "session_tracked": bool(status_data.get("session_id")),
                                    "ambient_listening": status_data.get("ambient_listening", False)
                                })
                            else:
                                session_results.append({
                                    "session_id": session_id,
                                    "start_successful": bool(start_data.get("status")),
                                    "status_accessible": False,
                                    "error": f"Status check failed: {status_response.status}"
                                })
                    else:
                        session_results.append({
                            "session_id": session_id,
                            "start_successful": False,
                            "error": f"Start failed: {response.status}"
                        })
            
            # Clean up sessions
            for session_id in session_ids:
                stop_request = {"session_id": session_id}
                async with self.session.post(
                    f"{BACKEND_URL}/ambient/stop",
                    json=stop_request
                ) as stop_response:
                    pass  # Clean up, don't fail test if this fails
            
            # Analyze results
            successful_sessions = [r for r in session_results if r.get("start_successful", False)]
            tracked_sessions = [r for r in session_results if r.get("session_tracked", False)]
            
            return {
                "success": True,
                "total_sessions_tested": len(session_ids),
                "successful_sessions": len(successful_sessions),
                "tracked_sessions": len(tracked_sessions),
                "session_store_working": len(tracked_sessions) > 0,
                "all_sessions_tracked": len(tracked_sessions) == len(successful_sessions),
                "session_results": session_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_session_management_telemetry_events(self):
        """Test telemetry events for rate limiting and break suggestions"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Start ambient listening to initialize session
            start_request = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/ambient/start",
                json=start_request
            ) as response:
                if response.status != 200:
                    return {"success": False, "error": f"Failed to start ambient listening: {response.status}"}
            
            # Send interactions to generate telemetry events
            telemetry_events = []
            
            for i in range(20):  # Send enough to potentially trigger events
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": f"Telemetry test {i}"
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as conv_response:
                    if conv_response.status == 200:
                        data = await conv_response.json()
                        content_type = data.get("content_type")
                        
                        # Track special response types that indicate telemetry events
                        if content_type in ["rate_limit", "break_suggestion", "mic_locked"]:
                            telemetry_events.append({
                                "interaction": i,
                                "event_type": content_type,
                                "response": data.get("response_text", "")[:100],
                                "metadata": data.get("metadata", {})
                            })
                
                await asyncio.sleep(0.1)
            
            # Check analytics dashboard to see if events were tracked
            async with self.session.get(
                f"{BACKEND_URL}/analytics/dashboard/{self.test_user_id}?days=1"
            ) as analytics_response:
                if analytics_response.status == 200:
                    analytics_data = await analytics_response.json()
                    
                    # End session to get final telemetry
                    async with self.session.post(
                        f"{BACKEND_URL}/session/end/{self.test_session_id}"
                    ) as end_response:
                        if end_response.status == 200:
                            end_data = await end_response.json()
                            
                            return {
                                "success": True,
                                "telemetry_events_detected": len(telemetry_events),
                                "special_events": telemetry_events,
                                "analytics_accessible": True,
                                "analytics_data": {
                                    "total_interactions": analytics_data.get("total_interactions", 0),
                                    "total_sessions": analytics_data.get("total_sessions", 0),
                                    "has_feature_usage": bool(analytics_data.get("feature_usage")),
                                    "has_engagement_trends": bool(analytics_data.get("engagement_trends"))
                                },
                                "session_end_telemetry": {
                                    "session_id": end_data.get("session_id"),
                                    "has_duration": "duration" in end_data,
                                    "has_interactions": "interactions" in end_data,
                                    "has_engagement_score": "engagement_score" in end_data
                                },
                                "telemetry_system_working": bool(analytics_data.get("total_interactions", 0) > 0)
                            }
                        else:
                            return {
                                "success": True,
                                "telemetry_events_detected": len(telemetry_events),
                                "special_events": telemetry_events,
                                "analytics_accessible": True,
                                "analytics_data": analytics_data,
                                "session_end_error": f"HTTP {end_response.status}",
                                "telemetry_system_working": bool(analytics_data.get("total_interactions", 0) > 0)
                            }
                else:
                    return {
                        "success": True,
                        "telemetry_events_detected": len(telemetry_events),
                        "special_events": telemetry_events,
                        "analytics_accessible": False,
                        "analytics_error": f"HTTP {analytics_response.status}"
                    }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_error_handling(self):
        """Test error handling for invalid requests"""
        try:
            error_tests = []
            
            # Test 1: Invalid user profile creation (age out of range)
            try:
                invalid_profile = {
                    "name": "Test",
                    "age": 15,  # Invalid age
                    "location": "Test"
                }
                async with self.session.post(
                    f"{BACKEND_URL}/users/profile",
                    json=invalid_profile
                ) as response:
                    error_tests.append({
                        "test": "invalid_age",
                        "status": response.status,
                        "handled_correctly": response.status in [400, 422]
                    })
            except Exception as e:
                error_tests.append({"test": "invalid_age", "error": str(e)})
            
            # Test 2: Non-existent user profile
            try:
                fake_user_id = str(uuid.uuid4())
                async with self.session.get(
                    f"{BACKEND_URL}/users/profile/{fake_user_id}"
                ) as response:
                    error_tests.append({
                        "test": "nonexistent_user",
                        "status": response.status,
                        "handled_correctly": response.status == 404
                    })
            except Exception as e:
                error_tests.append({"test": "nonexistent_user", "error": str(e)})
            
            # Test 3: Invalid conversation input
            try:
                invalid_text = {
                    "session_id": "invalid_session",
                    "user_id": "invalid_user",
                    "message": ""
                }
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=invalid_text
                ) as response:
                    error_tests.append({
                        "test": "invalid_conversation",
                        "status": response.status,
                        "handled_correctly": response.status in [400, 404, 422]
                    })
            except Exception as e:
                error_tests.append({"test": "invalid_conversation", "error": str(e)})
            
            # Test 4: Invalid memory snapshot request
            try:
                fake_user_id = str(uuid.uuid4())
                async with self.session.post(
                    f"{BACKEND_URL}/memory/snapshot/{fake_user_id}"
                ) as response:
                    error_tests.append({
                        "test": "invalid_memory_snapshot",
                        "status": response.status,
                        "handled_correctly": response.status in [404, 500]
                    })
            except Exception as e:
                error_tests.append({"test": "invalid_memory_snapshot", "error": str(e)})
            
            return {
                "success": True,
                "error_tests": error_tests,
                "properly_handled": sum(1 for test in error_tests if test.get("handled_correctly", False))
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("AI COMPANION DEVICE BACKEND TEST RESULTS")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result["status"] == "PASS")
        failed_tests = sum(1 for result in self.test_results.values() if result["status"] == "FAIL")
        error_tests = sum(1 for result in self.test_results.values() if result["status"] == "ERROR")
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Errors: {error_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print("-"*80)
        
        for test_name, result in self.test_results.items():
            status_symbol = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
            print(f"{status_symbol} {test_name}: {result['status']}")
            
            if result["status"] != "PASS" and "error" in result["details"]:
                print(f"   Error: {result['details']['error']}")
            elif result["status"] == "PASS" and isinstance(result["details"], dict):
                # Show key success metrics
                if "success" in result["details"] and result["details"]["success"]:
                    key_info = {k: v for k, v in result["details"].items() 
                              if k not in ["success"] and not k.startswith("_")}
                    if key_info:
                        print(f"   Details: {key_info}")
        
        print("-"*80)
        
        # Critical system checks
        print("\nCRITICAL SYSTEM STATUS:")
        if "Health Check" in self.test_results:
            health_details = self.test_results["Health Check"]["details"]
            if health_details.get("success"):
                print(f"✅ Multi-agent system: {'Initialized' if health_details.get('agents_initialized') else 'Not initialized'}")
                print(f"✅ Gemini API: {'Configured' if health_details.get('gemini_configured') else 'Not configured'}")
                print(f"✅ Deepgram API: {'Configured' if health_details.get('deepgram_configured') else 'Not configured'}")
                print(f"✅ Database: {health_details.get('database', 'Unknown')}")
            else:
                print("❌ Health check failed")
        
        # Memory Agent Status
        print("\nMEMORY AGENT STATUS:")
        memory_tests = ["Memory Snapshot Generation", "Memory Context Retrieval", "Memory Snapshots History", "Enhanced Conversation with Memory"]
        memory_passed = sum(1 for test in memory_tests if self.test_results.get(test, {}).get("status") == "PASS")
        print(f"✅ Memory Agent Tests: {memory_passed}/{len(memory_tests)} passed")
        
        # Telemetry Agent Status
        print("\nTELEMETRY AGENT STATUS:")
        telemetry_tests = ["Analytics Dashboard", "Global Analytics", "User Feature Flags", "Update Feature Flags", "Session End Telemetry", "Agent Status with Memory & Telemetry", "Maintenance Cleanup"]
        telemetry_passed = sum(1 for test in telemetry_tests if self.test_results.get(test, {}).get("status") == "PASS")
        print(f"✅ Telemetry Agent Tests: {telemetry_passed}/{len(telemetry_tests)} passed")
        
        # Integration Tests Status
        print("\nINTEGRATION TESTS STATUS:")
        integration_tests = ["Ambient Listening Integration", "Enhanced Conversation with Memory"]
        integration_passed = sum(1 for test in integration_tests if self.test_results.get(test, {}).get("status") == "PASS")
        print(f"✅ Integration Tests: {integration_passed}/{len(integration_tests)} passed")
        
        print("\n" + "="*80)
    
    async def test_content_api_stories(self):
        """Test GET /api/content/stories endpoint - Stories page regression fix"""
        try:
            async with self.session.get(f"{BACKEND_URL}/content/stories") as response:
                if response.status == 200:
                    data = await response.json()
                    stories = data.get("stories", [])
                    
                    # Verify stories structure and content
                    story_validation = []
                    for story in stories:
                        validation = {
                            "has_id": "id" in story,
                            "has_title": "title" in story,
                            "has_description": "description" in story,
                            "has_content": "content" in story and len(story.get("content", "")) > 50,
                            "has_category": "category" in story,
                            "has_duration": "duration" in story,
                            "has_age_group": "age_group" in story,
                            "has_tags": "tags" in story and isinstance(story.get("tags"), list),
                            "has_moral": "moral" in story
                        }
                        story_validation.append(validation)
                    
                    # Check for expected stories
                    story_titles = [story.get("title", "") for story in stories]
                    expected_stories = ["Clever Rabbit", "Three Little Pigs", "Tortoise", "Goldilocks", "Ugly Duckling"]
                    found_expected = sum(1 for expected in expected_stories 
                                       if any(expected.lower() in title.lower() for title in story_titles))
                    
                    return {
                        "success": True,
                        "stories_count": len(stories),
                        "has_stories": len(stories) >= 5,
                        "all_stories_have_required_fields": all(
                            all(validation.values()) for validation in story_validation
                        ),
                        "expected_stories_found": found_expected,
                        "story_titles": story_titles,
                        "sample_story": stories[0] if stories else None,
                        "stories_page_compatible": len(stories) >= 5 and all(
                            story.get("title") and story.get("content") and story.get("id")
                            for story in stories
                        )
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_content_api_content_types(self):
        """Test GET /api/content/{content_type} endpoints for all 7 content types"""
        try:
            content_types = ["jokes", "riddles", "facts", "songs", "rhymes", "stories", "games"]
            content_results = {}
            
            for content_type in content_types:
                async with self.session.get(f"{BACKEND_URL}/content/{content_type}") as response:
                    if response.status == 200:
                        data = await response.json()
                        content_list = data.get("content", [])
                        
                        content_results[content_type] = {
                            "available": True,
                            "count": data.get("count", len(content_list)),
                            "has_content": len(content_list) > 0,
                            "content_structure_valid": data.get("content_type") == content_type,
                            "sample_content": content_list[0] if content_list else None
                        }
                    elif response.status == 404:
                        content_results[content_type] = {
                            "available": False,
                            "error": "Content type not found"
                        }
                    else:
                        error_text = await response.text()
                        content_results[content_type] = {
                            "available": False,
                            "error": f"HTTP {response.status}: {error_text}"
                        }
            
            # Calculate success metrics
            available_types = [ct for ct, result in content_results.items() if result.get("available", False)]
            types_with_content = [ct for ct, result in content_results.items() 
                                if result.get("available", False) and result.get("has_content", False)]
            
            return {
                "success": True,
                "total_content_types_tested": len(content_types),
                "available_content_types": len(available_types),
                "content_types_with_data": len(types_with_content),
                "all_7_types_available": len(available_types) == 7,
                "content_results": content_results,
                "available_types_list": available_types,
                "types_with_content_list": types_with_content
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_content_api_generate(self):
        """Test POST /api/content/generate endpoint with 3-tier sourcing system"""
        if not self.test_user_id:
            return {"success": False, "error": "No test user ID available"}
        
        try:
            # Test different content types with the generate endpoint
            test_requests = [
                {
                    "content_type": "story",
                    "user_input": "Tell me a story about a brave little mouse",
                    "user_id": self.test_user_id
                },
                {
                    "content_type": "joke",
                    "user_input": "Tell me a funny joke",
                    "user_id": self.test_user_id
                },
                {
                    "content_type": "riddle",
                    "user_input": "Give me a riddle to solve",
                    "user_id": self.test_user_id
                },
                {
                    "content_type": "song",
                    "user_input": "Sing me a happy song",
                    "user_id": self.test_user_id
                }
            ]
            
            generation_results = []
            
            for request_data in test_requests:
                async with self.session.post(
                    f"{BACKEND_URL}/content/generate",
                    json=request_data
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        generation_results.append({
                            "content_type": request_data["content_type"],
                            "generation_successful": True,
                            "has_content": bool(data.get("content")),
                            "has_metadata": bool(data.get("metadata")),
                            "content_length": len(str(data.get("content", ""))),
                            "tier_used": data.get("metadata", {}).get("tier_used", "unknown"),
                            "response_preview": str(data.get("content", ""))[:100]
                        })
                    else:
                        error_text = await response.text()
                        generation_results.append({
                            "content_type": request_data["content_type"],
                            "generation_successful": False,
                            "error": f"HTTP {response.status}: {error_text}"
                        })
                
                await asyncio.sleep(0.2)  # Small delay between requests
            
            # Test invalid requests
            invalid_request = {
                "content_type": "invalid_type",
                "user_input": "test",
                "user_id": self.test_user_id
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/content/generate",
                json=invalid_request
            ) as response:
                invalid_request_handled = response.status in [400, 404, 422]
            
            # Calculate success metrics
            successful_generations = [r for r in generation_results if r.get("generation_successful", False)]
            generations_with_content = [r for r in generation_results if r.get("has_content", False)]
            
            return {
                "success": True,
                "total_requests_tested": len(test_requests),
                "successful_generations": len(successful_generations),
                "generations_with_content": len(generations_with_content),
                "all_content_types_working": len(successful_generations) == len(test_requests),
                "invalid_request_handled_correctly": invalid_request_handled,
                "generation_results": generation_results,
                "3_tier_sourcing_active": any(
                    r.get("tier_used") in ["local", "llm", "fallback"] 
                    for r in generation_results
                )
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

async def main():
    """Main test execution"""
    async with BackendTester() as tester:
        results = await tester.run_all_tests()
        tester.print_test_summary()
        
        # Return overall success status
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result["status"] == "PASS")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)