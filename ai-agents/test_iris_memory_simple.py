#!/usr/bin/env python3
"""
Test Iris Memory Integration - Simple Version
Tests that Iris design preferences are stored in unified memory for CIA agent access
"""

import sys
import os
import asyncio
import requests
from datetime import datetime
from config.service_urls import get_backend_url

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test configuration
BACKEND_URL = os.getenv("API_BASE_URL", get_backend_url()) + ""
TEST_HOMEOWNER_ID = "bda3ab78-e034-4be7-8285-1b7be1bf1387"

async def test_memory_extraction():
    """Test design preference extraction logic"""
    print("\nTEST: Memory Extraction Logic")
    
    try:
        # Import the extraction function
        from api.iris_chat_unified import extract_design_preferences
        
        # Test message with various design elements
        test_message = "I love modern farmhouse style with white cabinets and dark hardware"
        test_response = "That's great! Modern farmhouse combines clean lines with rustic charm. White cabinets with dark hardware create beautiful contrast."
        test_context = {
            "conversation": {
                "metadata": {"room_type": "kitchen"}
            }
        }
        
        preferences = extract_design_preferences(test_message, test_response, test_context)
        
        print("PASS: Extraction logic working:")
        for key, value in preferences.items():
            print(f"   {key}: {value}")
        
        return len(preferences) >= 3  # Should extract at least 3 types
        
    except Exception as e:
        print(f"FAIL: Test failed with exception: {e}")
        return False

async def test_iris_conversation():
    """Test Iris conversation with memory storage"""
    print("\nTEST: Iris Conversation with Memory Storage")
    
    try:
        iris_payload = {
            "message": "I love modern farmhouse style with white cabinets, dark hardware, and natural wood accents. I want a cozy but clean feeling in my kitchen.",
            "user_id": TEST_HOMEOWNER_ID,
            "room_type": "kitchen",
            "session_id": f"test_iris_memory_{int(datetime.now().timestamp())}"
        }
        
        print("Sending Iris chat request...")
        response = requests.post(f"{BACKEND_URL}/api/iris/chat", 
                               json=iris_payload, timeout=30)
        
        if response.ok:
            data = response.json()
            conversation_id = data.get("conversation_id")
            
            print(f"PASS: Iris chat successful")
            print(f"   Conversation ID: {conversation_id}")
            print(f"   Response: {data.get('response', '')[:100]}...")
            
            # Wait for memory storage
            await asyncio.sleep(2)
            
            if conversation_id:
                # Check unified system
                conv_response = requests.get(f"{BACKEND_URL}/api/conversations/{conversation_id}", timeout=10)
                if conv_response.ok:
                    conv_data = conv_response.json()
                    memory_items = conv_data.get("memory", [])
                    
                    # Look for design preferences
                    design_memory = None
                    for memory in memory_items:
                        if memory.get("memory_type") == "design_preferences":
                            design_memory = memory
                            break
                    
                    if design_memory:
                        preferences = design_memory.get("memory_value", {}).get("preferences", {})
                        print(f"PASS: Design preferences stored:")
                        for key, value in preferences.items():
                            print(f"   {key}: {value}")
                        return True
                    else:
                        print("FAIL: No design preferences found in memory")
                        return False
                else:
                    print(f"FAIL: Could not retrieve conversation: {conv_response.status_code}")
                    return False
            else:
                print("FAIL: No conversation ID returned")
                return False
        else:
            print(f"FAIL: Iris chat failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"FAIL: Test failed with exception: {e}")
        return False

async def main():
    """Run tests"""
    print("IRIS MEMORY INTEGRATION TEST")
    print("Testing Phase 1: Memory Integration for cross-agent design preference sharing")
    
    results = []
    
    # Test 1: Memory extraction logic
    result1 = await test_memory_extraction()
    results.append(("Memory Extraction", result1))
    
    # Test 2: Iris conversation with memory
    result2 = await test_iris_conversation()
    results.append(("Iris Memory Storage", result2))
    
    # Print results
    print("\n" + "="*50)
    print("TEST RESULTS")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nSUMMARY: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("SUCCESS: All tests passed! Iris memory integration working.")
    else:
        print("NOTICE: Some tests failed. Check details above.")

if __name__ == "__main__":
    asyncio.run(main())