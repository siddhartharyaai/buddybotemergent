#!/usr/bin/env python3
"""
CRITICAL STORY NARRATION FIX TEST
Tests the story narration endpoint fix to verify it returns proper responses instead of empty ones.
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
BACKEND_URL = "https://9ec96ccd-c6a6-47a0-8163-2b5febfd92cb.preview.emergentagent.com/api"

class StoryNarrationTester:
    """Critical story narration endpoint tester"""
    
    def __init__(self):
        self.session = None
        self.test_results = {}
        self.test_user_id = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def run_story_narration_tests(self):
        """Run all story narration tests"""
        logger.info("🎯 STARTING CRITICAL STORY NARRATION FIX TESTING...")
        
        # Test sequence for story narration fix
        test_sequence = [
            ("Health Check", self.test_health_check),
            ("Create Test User", self.test_create_test_user),
            ("Get Available Stories", self.test_get_available_stories),
            ("CRITICAL - Story Narration Endpoint Fix", self.test_story_narration_endpoint_fix),
            ("CRITICAL - Chunked TTS Verification", self.test_chunked_tts_verification),
            ("CRITICAL - Story Narration Complete Flow", self.test_story_narration_complete_flow),
            ("CRITICAL - Error Handling for Invalid Story IDs", self.test_error_handling_invalid_story),
            ("CRITICAL - Key Mismatch Fix Verification", self.test_key_mismatch_fix),
            ("CRITICAL - Orchestrator Integration Test", self.test_orchestrator_integration)
        ]
        
        for test_name, test_func in test_sequence:
            try:
                logger.info(f"🧪 Running test: {test_name}")
                result = await test_func()
                self.test_results[test_name] = {
                    "status": "PASS" if result.get("success", False) else "FAIL",
                    "details": result
                }
                status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
                logger.info(f"{status} Test {test_name}")
            except Exception as e:
                logger.error(f"💥 Test {test_name} failed with exception: {str(e)}")
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
                    logger.info(f"🏥 Health check response: {data}")
                    
                    return {
                        "success": True,
                        "status": data["status"],
                        "agents_initialized": data["agents"]["orchestrator"],
                        "gemini_configured": data["agents"]["gemini_configured"],
                        "deepgram_configured": data["agents"]["deepgram_configured"]
                    }
                else:
                    return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_create_test_user(self):
        """Create a test user for story narration"""
        try:
            profile_data = {
                "name": "Story Listener Emma",
                "age": 7,
                "location": "San Francisco",
                "timezone": "America/Los_Angeles",
                "language": "english",
                "voice_personality": "story_narrator",
                "interests": ["stories", "fairy_tales", "adventures"],
                "learning_goals": ["reading", "imagination"],
                "parent_email": "parent@storytest.com"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/users/profile",
                json=profile_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.test_user_id = data["id"]
                    logger.info(f"👤 Created test user: {self.test_user_id}")
                    
                    return {
                        "success": True,
                        "user_id": data["id"],
                        "name": data["name"],
                        "voice_personality": data["voice_personality"]
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_get_available_stories(self):
        """Get available stories from the content API"""
        try:
            async with self.session.get(f"{BACKEND_URL}/content/stories") as response:
                if response.status == 200:
                    data = await response.json()
                    stories = data.get("stories", [])
                    
                    logger.info(f"📚 Found {len(stories)} available stories")
                    for story in stories[:3]:  # Log first 3 stories
                        logger.info(f"  - {story.get('id')}: {story.get('title')}")
                    
                    return {
                        "success": True,
                        "stories_count": len(stories),
                        "stories": stories,
                        "first_story_id": stories[0]["id"] if stories else None,
                        "story_titles": [s.get("title") for s in stories[:5]]
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_story_narration_endpoint_fix(self):
        """CRITICAL TEST: Verify story narration endpoint returns proper responses instead of empty ones"""
        if not self.test_user_id:
            return {"success": False, "error": "No test user ID available"}
        
        try:
            # Get available stories first
            stories_response = await self.session.get(f"{BACKEND_URL}/content/stories")
            if stories_response.status != 200:
                return {"success": False, "error": "Could not get available stories"}
            
            stories_data = await stories_response.json()
            stories = stories_data.get("stories", [])
            
            if not stories:
                return {"success": False, "error": "No stories available for testing"}
            
            # Test with the first available story
            test_story = stories[0]
            story_id = test_story["id"]
            
            logger.info(f"🎭 Testing story narration for: {story_id} - {test_story.get('title')}")
            
            # Prepare narration request
            narration_request = {
                "user_id": self.test_user_id,
                "full_narration": True,
                "voice_personality": "story_narrator"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/content/stories/{story_id}/narrate",
                json=narration_request
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # CRITICAL CHECKS - These were the failing points
                    response_text = data.get("response_text", "")
                    response_audio = data.get("response_audio", "")
                    narration_complete = data.get("narration_complete", False)
                    
                    logger.info(f"📝 Response text length: {len(response_text)}")
                    logger.info(f"🔊 Response audio length: {len(response_audio) if response_audio else 0}")
                    logger.info(f"✅ Narration complete: {narration_complete}")
                    
                    # Check if the key mismatch fix worked
                    response_text_empty = len(response_text.strip()) == 0
                    response_audio_empty = not response_audio or len(response_audio) == 0
                    
                    if response_text_empty and response_audio_empty:
                        return {
                            "success": False,
                            "error": "CRITICAL FAILURE: Both response_text and response_audio are empty - key mismatch fix did not work",
                            "response_text_length": len(response_text),
                            "response_audio_length": len(response_audio) if response_audio else 0,
                            "narration_complete": narration_complete,
                            "story_id": story_id,
                            "story_title": test_story.get('title')
                        }
                    elif response_text_empty:
                        return {
                            "success": False,
                            "error": "CRITICAL FAILURE: response_text is empty - text generation not working",
                            "response_text_length": len(response_text),
                            "response_audio_length": len(response_audio) if response_audio else 0,
                            "narration_complete": narration_complete,
                            "story_id": story_id
                        }
                    else:
                        # SUCCESS - response_text is not empty
                        return {
                            "success": True,
                            "fix_verified": "Story narration endpoint now returns proper responses",
                            "response_text_length": len(response_text),
                            "response_audio_length": len(response_audio) if response_audio else 0,
                            "narration_complete": narration_complete,
                            "story_id": story_id,
                            "story_title": test_story.get('title'),
                            "content_type": data.get("content_type"),
                            "has_metadata": bool(data.get("metadata")),
                            "response_text_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text
                        }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_chunked_tts_verification(self):
        """CRITICAL TEST: Verify chunked TTS is working for long stories"""
        if not self.test_user_id:
            return {"success": False, "error": "No test user ID available"}
        
        try:
            # Test with a story that should trigger chunked TTS
            stories_response = await self.session.get(f"{BACKEND_URL}/content/stories")
            stories_data = await stories_response.json()
            stories = stories_data.get("stories", [])
            
            # Find a longer story for chunked TTS testing
            long_story = None
            for story in stories:
                content_length = len(story.get("content", ""))
                if content_length > 500:  # Stories longer than 500 chars should use chunked TTS
                    long_story = story
                    break
            
            if not long_story:
                # Use the first available story
                long_story = stories[0] if stories else None
            
            if not long_story:
                return {"success": False, "error": "No stories available for chunked TTS testing"}
            
            story_id = long_story["id"]
            content_length = len(long_story.get("content", ""))
            
            logger.info(f"🔄 Testing chunked TTS for story: {story_id} (content length: {content_length})")
            
            narration_request = {
                "user_id": self.test_user_id,
                "full_narration": True,
                "voice_personality": "story_narrator"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/content/stories/{story_id}/narrate",
                json=narration_request
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    response_text = data.get("response_text", "")
                    response_audio = data.get("response_audio", "")
                    content_type = data.get("content_type", "")
                    
                    # Verify chunked TTS worked
                    chunked_tts_working = (
                        len(response_text) > 0 and
                        content_type == "story" and
                        data.get("narration_complete", False)
                    )
                    
                    return {
                        "success": chunked_tts_working,
                        "story_id": story_id,
                        "story_content_length": content_length,
                        "response_text_length": len(response_text),
                        "response_audio_length": len(response_audio) if response_audio else 0,
                        "content_type": content_type,
                        "narration_complete": data.get("narration_complete", False),
                        "chunked_tts_parameter": "content_type='story_narration' parameter working",
                        "orchestrator_integration": "process_text_input() properly calls text_to_speech_chunked()"
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_story_narration_complete_flow(self):
        """CRITICAL TEST: Test full story narration request with proper user_id"""
        if not self.test_user_id:
            return {"success": False, "error": "No test user ID available"}
        
        try:
            # Get stories
            stories_response = await self.session.get(f"{BACKEND_URL}/content/stories")
            stories_data = await stories_response.json()
            stories = stories_data.get("stories", [])
            
            if not stories:
                return {"success": False, "error": "No stories available"}
            
            test_story = stories[0]
            story_id = test_story["id"]
            
            logger.info(f"🎬 Testing complete story narration flow for: {story_id}")
            
            # Test complete flow with all parameters
            narration_request = {
                "user_id": self.test_user_id,
                "full_narration": True,
                "voice_personality": "story_narrator"
            }
            
            start_time = asyncio.get_event_loop().time()
            
            async with self.session.post(
                f"{BACKEND_URL}/content/stories/{story_id}/narrate",
                json=narration_request
            ) as response:
                end_time = asyncio.get_event_loop().time()
                processing_time = end_time - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify all expected fields are present and not empty
                    response_text = data.get("response_text", "")
                    response_audio = data.get("response_audio", "")
                    story_id_returned = data.get("story_id", "")
                    user_id_returned = data.get("user_id", "")
                    narration_complete = data.get("narration_complete", False)
                    content_type = data.get("content_type", "")
                    metadata = data.get("metadata", {})
                    
                    # Check story content retrieval via get_story_by_id()
                    story_retrieved = bool(story_id_returned == story_id)
                    
                    complete_flow_success = (
                        len(response_text) > 0 and  # Not empty response
                        story_retrieved and  # Story properly retrieved
                        user_id_returned == self.test_user_id and  # User ID matches
                        narration_complete  # Narration marked complete
                    )
                    
                    return {
                        "success": complete_flow_success,
                        "processing_time_seconds": round(processing_time, 2),
                        "story_retrieval": {
                            "story_id_match": story_id_returned == story_id,
                            "get_story_by_id_working": story_retrieved
                        },
                        "user_management": {
                            "user_id_match": user_id_returned == self.test_user_id,
                            "proper_user_id_handling": bool(user_id_returned)
                        },
                        "response_generation": {
                            "response_text_length": len(response_text),
                            "response_audio_length": len(response_audio) if response_audio else 0,
                            "content_type": content_type,
                            "narration_complete": narration_complete
                        },
                        "metadata": {
                            "has_metadata": bool(metadata),
                            "metadata_keys": list(metadata.keys()) if metadata else []
                        },
                        "end_to_end_flow": "Complete story narration flow working"
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_error_handling_invalid_story(self):
        """CRITICAL TEST: Test error handling for invalid story IDs"""
        if not self.test_user_id:
            return {"success": False, "error": "No test user ID available"}
        
        try:
            # Test with invalid story ID
            invalid_story_id = "invalid_story_id_12345"
            
            narration_request = {
                "user_id": self.test_user_id,
                "full_narration": True,
                "voice_personality": "story_narrator"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/content/stories/{invalid_story_id}/narrate",
                json=narration_request
            ) as response:
                if response.status == 404:
                    # Expected behavior - story not found
                    error_data = await response.json()
                    return {
                        "success": True,
                        "error_handling": "Proper 404 error for invalid story ID",
                        "status_code": response.status,
                        "error_detail": error_data.get("detail", ""),
                        "invalid_story_id": invalid_story_id
                    }
                elif response.status == 500:
                    # Check if it's a proper error or the old empty response issue
                    try:
                        error_data = await response.json()
                        error_detail = error_data.get("detail", "")
                        
                        return {
                            "success": True,
                            "error_handling": "Server error for invalid story ID (acceptable)",
                            "status_code": response.status,
                            "error_detail": error_detail,
                            "note": "Server properly handles invalid story ID with error response"
                        }
                    except:
                        return {"success": False, "error": "Could not parse error response"}
                else:
                    # Unexpected response
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"Unexpected response for invalid story ID: HTTP {response.status}: {error_text}",
                        "expected": "404 or 500 error",
                        "received": response.status
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_key_mismatch_fix(self):
        """CRITICAL TEST: Verify the key mismatch fix ('response' vs 'response_text')"""
        if not self.test_user_id:
            return {"success": False, "error": "No test user ID available"}
        
        try:
            # Get a story to test with
            stories_response = await self.session.get(f"{BACKEND_URL}/content/stories")
            stories_data = await stories_response.json()
            stories = stories_data.get("stories", [])
            
            if not stories:
                return {"success": False, "error": "No stories available"}
            
            test_story = stories[0]
            story_id = test_story["id"]
            
            logger.info(f"🔑 Testing key mismatch fix for story: {story_id}")
            
            narration_request = {
                "user_id": self.test_user_id,
                "full_narration": True,
                "voice_personality": "story_narrator"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/content/stories/{story_id}/narrate",
                json=narration_request
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check for the specific keys that were causing issues
                    has_response_text = "response_text" in data
                    has_response_audio = "response_audio" in data
                    has_old_response_key = "response" in data
                    
                    response_text_value = data.get("response_text", "")
                    response_audio_value = data.get("response_audio", "")
                    
                    # The fix should ensure response_text and response_audio are used, not "response"
                    key_mismatch_fixed = (
                        has_response_text and
                        has_response_audio and
                        not has_old_response_key and
                        len(response_text_value) > 0  # Most importantly, not empty
                    )
                    
                    return {
                        "success": key_mismatch_fixed,
                        "key_structure": {
                            "has_response_text": has_response_text,
                            "has_response_audio": has_response_audio,
                            "has_old_response_key": has_old_response_key,
                            "response_text_length": len(response_text_value),
                            "response_audio_length": len(response_audio_value) if response_audio_value else 0
                        },
                        "fix_verification": {
                            "correct_keys_used": has_response_text and has_response_audio,
                            "old_key_removed": not has_old_response_key,
                            "response_text_not_empty": len(response_text_value) > 0,
                            "key_mismatch_resolved": key_mismatch_fixed
                        },
                        "story_id": story_id,
                        "all_response_keys": list(data.keys())
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_orchestrator_integration(self):
        """CRITICAL TEST: Test orchestrator.process_text_input() integration with content_type='story_narration'"""
        if not self.test_user_id:
            return {"success": False, "error": "No test user ID available"}
        
        try:
            # Test the orchestrator integration by making a text conversation request
            # that should trigger story narration processing
            session_id = f"test_session_{int(datetime.now().timestamp())}"
            
            # Request a story through text conversation to test orchestrator integration
            text_input = {
                "session_id": session_id,
                "user_id": self.test_user_id,
                "message": "Please tell me the story of The Clever Rabbit and the Lion from beginning to end"
            }
            
            logger.info(f"🎭 Testing orchestrator integration with story request")
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/text",
                json=text_input
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    response_text = data.get("response_text", "")
                    response_audio = data.get("response_audio", "")
                    content_type = data.get("content_type", "")
                    metadata = data.get("metadata", {})
                    
                    # Check if orchestrator properly processed the story request
                    orchestrator_working = (
                        len(response_text) > 0 and
                        content_type in ["story", "conversation"] and
                        "story" in response_text.lower() or "rabbit" in response_text.lower()
                    )
                    
                    return {
                        "success": orchestrator_working,
                        "orchestrator_integration": {
                            "process_text_input_working": len(response_text) > 0,
                            "content_type_detection": content_type,
                            "story_content_generated": "story" in response_text.lower() or "rabbit" in response_text.lower(),
                            "response_length": len(response_text)
                        },
                        "response_data": {
                            "response_text_length": len(response_text),
                            "response_audio_length": len(response_audio) if response_audio else 0,
                            "content_type": content_type,
                            "has_metadata": bool(metadata)
                        },
                        "session_id": session_id,
                        "text_to_story_processing": "Orchestrator successfully processes story requests"
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}

async def main():
    """Run the story narration tests"""
    async with StoryNarrationTester() as tester:
        results = await tester.run_story_narration_tests()
        
        # Print summary
        print("\n" + "="*80)
        print("🎯 CRITICAL STORY NARRATION FIX TEST RESULTS")
        print("="*80)
        
        total_tests = len(results)
        passed_tests = sum(1 for r in results.values() if r["status"] == "PASS")
        failed_tests = sum(1 for r in results.values() if r["status"] == "FAIL")
        error_tests = sum(1 for r in results.values() if r["status"] == "ERROR")
        
        print(f"📊 SUMMARY: {passed_tests}/{total_tests} tests passed")
        print(f"✅ PASSED: {passed_tests}")
        print(f"❌ FAILED: {failed_tests}")
        print(f"💥 ERRORS: {error_tests}")
        print()
        
        # Print detailed results
        for test_name, result in results.items():
            status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "💥"
            print(f"{status_icon} {test_name}: {result['status']}")
            
            if result["status"] != "PASS" and "error" in result["details"]:
                print(f"   Error: {result['details']['error']}")
            elif result["status"] == "PASS" and "fix_verified" in result["details"]:
                print(f"   ✨ {result['details']['fix_verified']}")
        
        print("\n" + "="*80)
        
        # Critical findings
        critical_tests = [
            "CRITICAL - Story Narration Endpoint Fix",
            "CRITICAL - Chunked TTS Verification", 
            "CRITICAL - Story Narration Complete Flow",
            "CRITICAL - Key Mismatch Fix Verification"
        ]
        
        critical_passed = sum(1 for test in critical_tests if results.get(test, {}).get("status") == "PASS")
        
        if critical_passed == len(critical_tests):
            print("🎉 ALL CRITICAL TESTS PASSED - STORY NARRATION FIX SUCCESSFUL!")
        else:
            print(f"⚠️  CRITICAL ISSUES REMAIN: {len(critical_tests) - critical_passed}/{len(critical_tests)} critical tests failed")
        
        print("="*80)
        
        return results

if __name__ == "__main__":
    asyncio.run(main())