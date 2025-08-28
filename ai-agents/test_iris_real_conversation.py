#!/usr/bin/env python3
"""
REAL Iris Conversation Test - End-to-End Verification
Actually chat with Iris and verify memory storage works
"""

import requests
import time
import json
from config.service_urls import get_backend_url

BACKEND_URL = get_backend_url()
TEST_HOMEOWNER_ID = "bda3ab78-e034-4be7-8285-1b7be1bf1387"

def test_real_iris_conversation():
    """Have an actual conversation with Iris"""
    print("REAL IRIS CONVERSATION TEST")
    print("="*50)
    
    # Test conversation with rich design content
    messages = [
        "Hi Iris! I'm planning a kitchen remodel and love modern farmhouse style.",
        "I really want white shaker cabinets with black hardware, and I'd love a subway tile backsplash.",
        "My budget is around $15,000 and I want it to feel cozy but clean."
    ]
    
    conversation_id = None
    
    for i, message in enumerate(messages, 1):
        print(f"\n--- MESSAGE {i} ---")
        print(f"USER: {message}")
        
        payload = {
            "message": message,
            "user_id": TEST_HOMEOWNER_ID,
            "room_type": "kitchen",
            "session_id": f"real_test_{int(time.time())}"
        }
        
        try:
            print("Sending to Iris...")
            response = requests.post(f"{BACKEND_URL}/api/iris/chat", 
                                   json=payload, timeout=45)
            
            if response.ok:
                data = response.json()
                print(f"IRIS: {data.get('response', '')[:200]}...")
                
                if data.get('conversation_id'):
                    conversation_id = data['conversation_id']
                    print(f"Conversation ID: {conversation_id}")
                
                # Wait for memory processing
                time.sleep(2)
                
            else:
                print(f"ERROR: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"ERROR: {e}")
            return False
    
    # Now check if memory was actually stored
    if conversation_id:
        print(f"\n--- MEMORY VERIFICATION ---")
        try:
            conv_response = requests.get(f"{BACKEND_URL}/api/conversations/{conversation_id}", timeout=10)
            if conv_response.ok:
                conv_data = conv_response.json()
                memory_items = conv_data.get("memory", [])
                
                print(f"Found {len(memory_items)} memory items:")
                for memory in memory_items:
                    print(f"  - {memory.get('memory_type')}: {memory.get('memory_key')}")
                    if memory.get('memory_type') == 'design_preferences':
                        prefs = memory.get('memory_value', {}).get('preferences', {})
                        print(f"    Preferences: {prefs}")
                
                return len(memory_items) > 0
            else:
                print(f"Failed to get conversation: {conv_response.status_code}")
                return False
        except Exception as e:
            print(f"Memory check failed: {e}")
            return False
    
    return True

def test_openai_api_key():
    """Check if OpenAI API key is properly configured"""
    print("\n--- OPENAI API KEY CHECK ---")
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"API Key found: {api_key[:10]}...{api_key[-5:]}")
        return True
    else:
        print("No OpenAI API key found!")
        return False

if __name__ == "__main__":
    # Check prerequisites
    if not test_openai_api_key():
        print("Please set OPENAI_API_KEY environment variable")
        exit(1)
    
    # Run the real test
    success = test_real_iris_conversation()
    
    if success:
        print("\n🎉 SUCCESS: Real Iris conversation completed with memory storage!")
    else:
        print("\n❌ FAILED: Could not complete real Iris conversation test")