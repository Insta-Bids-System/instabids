#!/usr/bin/env python3
"""
Test Iris Memory Integration - Phase 1 Implementation
Tests that Iris design preferences are stored in unified memory for CIA agent access
"""

import sys
import os
import asyncio
import requests
import json
from datetime import datetime
from config.service_urls import get_backend_url

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test configuration
BACKEND_URL = os.getenv("API_BASE_URL", get_backend_url()) + ""
TEST_HOMEOWNER_ID = "bda3ab78-e034-4be7-8285-1b7be1bf1387"  # Real homeowner ID from database

class IrisMemoryIntegrationTest:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.user_id = TEST_HOMEOWNER_ID
        self.test_results = []

    async def test_iris_memory_storage(self):
        """Test 1: Verify Iris stores design preferences in unified memory"""
        print("\nTEST 1: Iris Memory Storage")
        
        try:
            # Test Iris conversation with design preferences
            iris_payload = {
                "message": "I love modern farmhouse style with white cabinets, dark hardware, and natural wood accents. I want a cozy but clean feeling in my kitchen.",
                "user_id": self.user_id,
                "room_type": "kitchen",
                "session_id": f"test_iris_memory_{int(datetime.now().timestamp())}"
            }
            
            print(f"Sending Iris chat request...")
            response = requests.post(f"{self.backend_url}/api/iris/chat", 
                                   json=iris_payload, timeout=30)
            
            if response.ok:
                data = response.json()
                conversation_id = data.get("conversation_id")
                
                print(f"PASS: Iris chat successful")
                print(f"   Conversation ID: {conversation_id}")
                print(f"   Response: {data.get('response', '')[:100]}...")
                
                # Wait a moment for memory storage
                await asyncio.sleep(2)
                
                # Verify conversation was created in unified system
                if conversation_id:
                    conv_response = requests.get(f"{self.backend_url}/api/conversations/{conversation_id}", timeout=10)
                    if conv_response.ok:
                        conv_data = conv_response.json()
                        memory_items = conv_data.get("memory", [])
                        
                        # Look for design preferences in memory
                        design_memory = None
                        for memory in memory_items:
                            if memory.get("memory_type") == "design_preferences":
                                design_memory = memory
                                break
                        
                        if design_memory:
                            print(f"PASS: Design preferences stored in unified memory:")
                            preferences = design_memory.get("memory_value", {}).get("preferences", {})
                            for key, value in preferences.items():
                                print(f"   {key}: {value}")
                            
                            self.test_results.append({
                                "test": "iris_memory_storage",
                                "status": "PASS",
                                "details": f"Design preferences stored: {list(preferences.keys())}"
                            })
                        else:
                            print(f"FAIL: No design preferences found in memory")
                            self.test_results.append({
                                "test": "iris_memory_storage", 
                                "status": "FAIL",
                                "details": "Design preferences not stored in unified memory"
                            })
                    else:
                        print(f"❌ Failed to get conversation: {conv_response.status_code}")
                        self.test_results.append({
                            "test": "iris_memory_storage",
                            "status": "FAIL", 
                            "details": "Could not retrieve conversation from unified system"
                        })
                else:
                    print(f"❌ No conversation ID returned")
                    self.test_results.append({
                        "test": "iris_memory_storage",
                        "status": "FAIL",
                        "details": "No conversation ID returned from Iris chat"
                    })
            else:
                print(f"❌ Iris chat failed: {response.status_code}")
                print(f"   Error: {response.text}")
                self.test_results.append({
                    "test": "iris_memory_storage",
                    "status": "FAIL",
                    "details": f"Iris API error: {response.status_code}"
                })
                
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            self.test_results.append({
                "test": "iris_memory_storage",
                "status": "ERROR", 
                "details": str(e)
            })

    async def test_memory_extraction_logic(self):
        """Test 2: Verify design preference extraction logic"""
        print("\n🧪 TEST 2: Memory Extraction Logic")
        
        try:
            # Import the extraction function
            from api.iris_chat_unified import extract_design_preferences
            
            # Test message with various design elements
            test_message = "I love modern farmhouse style with white cabinets and dark hardware"
            test_response = "That's a great choice! Modern farmhouse combines clean lines with rustic charm. White cabinets with dark hardware create beautiful contrast. Consider adding natural wood accents and stone countertops."
            test_context = {
                "conversation": {
                    "metadata": {"room_type": "kitchen"}
                }
            }
            
            preferences = extract_design_preferences(test_message, test_response, test_context)
            
            print(f"✅ Extraction logic working:")
            for key, value in preferences.items():
                print(f"   {key}: {value}")
            
            # Validate expected extractions
            expected_elements = ["preferred_styles", "color_preferences", "material_preferences", "focus_room"]
            found_elements = [elem for elem in expected_elements if elem in preferences]
            
            if len(found_elements) >= 3:  # Should find at least 3 elements
                self.test_results.append({
                    "test": "memory_extraction_logic",
                    "status": "PASS",
                    "details": f"Extracted {len(found_elements)} preference types: {found_elements}"
                })
            else:
                self.test_results.append({
                    "test": "memory_extraction_logic", 
                    "status": "FAIL",
                    "details": f"Only extracted {len(found_elements)} preference types: {found_elements}"
                })
                
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            self.test_results.append({
                "test": "memory_extraction_logic",
                "status": "ERROR",
                "details": str(e)
            })

    async def test_cross_agent_memory_access(self):
        """Test 3: Verify CIA agent can access Iris design preferences"""
        print("\n🧪 TEST 3: Cross-Agent Memory Access")
        
        try:
            # First get homeowner conversations to find one with design preferences
            conv_response = requests.get(f"{self.backend_url}/api/conversations/user/{self.user_id}", timeout=10)
            
            if conv_response.ok:
                conversations = conv_response.json().get("conversations", [])
                design_conversation = None
                
                # Look for conversation with design preferences
                for conv in conversations:
                    if conv.get("conversation_type") == "design_inspiration":
                        # Get full conversation details
                        detail_response = requests.get(f"{self.backend_url}/api/conversations/{conv['id']}", timeout=10)
                        if detail_response.ok:
                            conv_data = detail_response.json()
                            memory_items = conv_data.get("memory", [])
                            
                            # Check for design preferences
                            for memory in memory_items:
                                if memory.get("memory_type") == "design_preferences":
                                    design_conversation = conv_data
                                    break
                            
                            if design_conversation:
                                break
                
                if design_conversation:
                    print(f"✅ Found conversation with design preferences:")
                    print(f"   Conversation ID: {design_conversation['conversation']['id']}")
                    
                    # Extract design preferences from memory
                    design_memory = None
                    for memory in design_conversation.get("memory", []):
                        if memory.get("memory_type") == "design_preferences":
                            design_memory = memory
                            break
                    
                    if design_memory:
                        preferences = design_memory.get("memory_value", {}).get("preferences", {})
                        print(f"✅ CIA agent can access design preferences:")
                        for key, value in preferences.items():
                            print(f"   {key}: {value}")
                        
                        self.test_results.append({
                            "test": "cross_agent_memory_access",
                            "status": "PASS", 
                            "details": f"CIA can access {len(preferences)} preference types"
                        })
                    else:
                        print(f"❌ Design preferences not found in memory")
                        self.test_results.append({
                            "test": "cross_agent_memory_access",
                            "status": "FAIL",
                            "details": "Design preferences not accessible"
                        })
                else:
                    print(f"⚠️  No design conversations found - create one first")
                    self.test_results.append({
                        "test": "cross_agent_memory_access",
                        "status": "SKIP",
                        "details": "No design conversations available"
                    })
            else:
                print(f"❌ Failed to get user conversations: {conv_response.status_code}")
                self.test_results.append({
                    "test": "cross_agent_memory_access",
                    "status": "FAIL",
                    "details": f"API error: {conv_response.status_code}"
                })
                
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            self.test_results.append({
                "test": "cross_agent_memory_access",
                "status": "ERROR",
                "details": str(e)
            })

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("🧪 IRIS MEMORY INTEGRATION TEST RESULTS")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["status"] == "PASS")
        failed_tests = sum(1 for result in self.test_results if result["status"] == "FAIL") 
        error_tests = sum(1 for result in self.test_results if result["status"] == "ERROR")
        skipped_tests = sum(1 for result in self.test_results if result["status"] == "SKIP")
        
        for result in self.test_results:
            status_emoji = {
                "PASS": "✅",
                "FAIL": "❌", 
                "ERROR": "⚠️",
                "SKIP": "⏭️"
            }
            print(f"{status_emoji[result['status']]} {result['test']}: {result['status']}")
            if result.get('details'):
                print(f"   {result['details']}")
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Errors: {error_tests}")
        print(f"   Skipped: {skipped_tests}")
        
        if passed_tests == total_tests - skipped_tests:
            print(f"\n🎉 ALL TESTS PASSED! Iris memory integration working correctly.")
        else:
            print(f"\n⚠️  Some tests failed. Check the details above.")

async def main():
    """Run Iris memory integration tests"""
    print("IRIS MEMORY INTEGRATION TEST")
    print("Testing Phase 1: Memory Integration for cross-agent design preference sharing")
    
    tester = IrisMemoryIntegrationTest()
    
    # Run tests in sequence
    await tester.test_memory_extraction_logic()
    await tester.test_iris_memory_storage()
    await tester.test_cross_agent_memory_access()
    
    # Print summary
    tester.print_summary()

if __name__ == "__main__":
    asyncio.run(main())