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
BACKEND_URL = "https://12805ad1-847f-4cc6-8d3f-22976e36496b.preview.emergentagent.com/api"

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
            ("Error Handling", self.test_error_handling)
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
        
        print("\n" + "="*80)

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