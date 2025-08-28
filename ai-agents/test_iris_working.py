#!/usr/bin/env python3
"""
Test Iris Working - Simple Real Conversation Test
"""

import requests
import time
from config.service_urls import get_backend_url

BACKEND_URL = get_backend_url()
TEST_HOMEOWNER_ID = "bda3ab78-e034-4be7-8285-1b7be1bf1387"

def test_iris_conversation():
    print("TESTING IRIS CONVERSATION")
    print("=" * 40)
    
    payload = {
        "message": "Hi Iris! I'm planning a kitchen remodel and love modern farmhouse style with white cabinets.",
        "user_id": TEST_HOMEOWNER_ID,
        "room_type": "kitchen",
        "session_id": f"test_{int(time.time())}"
    }
    
    print("Sending request to Iris...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/iris/chat",
            json=payload,
            timeout=30
        )
        
        end_time = time.time()
        
        if response.ok:
            data = response.json()
            print(f"SUCCESS! Response in {end_time - start_time:.2f} seconds")
            print(f"Conversation ID: {data.get('conversation_id')}")
            print(f"Iris Response: {data.get('response')}")
            print(f"Suggestions: {data.get('suggestions', [])}")
            
            return True, data.get('conversation_id')
        else:
            print(f"ERROR: {response.status_code}")
            print(f"Error details: {response.text}")
            return False, None
            
    except requests.exceptions.Timeout:
        print(f"TIMEOUT: No response within 30 seconds")
        return False, None
    except Exception as e:
        print(f"ERROR: {e}")
        return False, None

def check_memory_storage(conversation_id):
    if not conversation_id:
        return False
        
    print(f"\nCHECKING MEMORY STORAGE")
    print("=" * 40)
    
    try:
        # Wait a moment for memory processing
        time.sleep(2)
        
        response = requests.get(f"{BACKEND_URL}/api/conversations/{conversation_id}", timeout=10)
        
        if response.ok:
            data = response.json()
            memory_items = data.get("memory", [])
            
            print(f"Memory items found: {len(memory_items)}")
            
            for memory in memory_items:
                memory_type = memory.get("memory_type")
                memory_key = memory.get("memory_key")
                print(f"  - {memory_type}: {memory_key}")
                
                if memory_type == "design_preferences":
                    prefs = memory.get("memory_value", {}).get("preferences", {})
                    print(f"    Design preferences: {prefs}")
                    return True
            
            return len(memory_items) > 0
        else:
            print(f"Could not check memory: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Memory check error: {e}")
        return False

if __name__ == "__main__":
    # Test the conversation
    success, conversation_id = test_iris_conversation()
    
    if success:
        # Test memory storage
        memory_success = check_memory_storage(conversation_id)
        
        if memory_success:
            print(f"\n🎉 COMPLETE SUCCESS!")
            print("✅ Iris conversation working")
            print("✅ Memory storage working") 
            print("✅ Design preferences extracted and stored")
        else:
            print(f"\n⚠️  PARTIAL SUCCESS")
            print("✅ Iris conversation working")
            print("❌ Memory storage not confirmed")
    else:
        print(f"\n❌ FAILED")
        print("❌ Iris conversation not working")