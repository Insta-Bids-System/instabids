"""
Test unified conversation API endpoints directly to verify they work
This will help debug why COIA conversations aren't saving
"""

import requests
import json
from datetime import datetime
import uuid
from config.service_urls import get_backend_url

def test_unified_api_endpoints():
    """Test all unified API endpoints directly"""
    base_url = get_backend_url()
    
    print("Testing Unified Conversation API Endpoints")
    print("=" * 60)
    
    # Test 1: Check if backend is running
    print("1. Testing backend connection...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.ok:
            print("   PASS - Backend is running")
        else:
            print("   FAIL - Backend connection failed")
            return False
    except Exception as e:
        print(f"   ERROR - Backend connection ERROR: {e}")
        return False
    
    print()
    
    # Test 2: Create conversation
    print("2. Testing conversation creation...")
    create_payload = {
        "user_id": "test-contractor-123",
        "agent_type": "COIA", 
        "title": "Test COIA Conversation",
        "context_type": "contractor_onboarding",
        "metadata": {
            "session_id": "test-session-123",
            "contractor_lead_id": "test-lead-456",
            "agent_type": "COIA"
        }
    }
    
    try:
        response = requests.post(f"{base_url}/conversations/create", json=create_payload, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.ok:
            response_data = response.json()
            conversation_id = response_data.get("conversation_id")
            print(f"   PASS - Conversation created: {conversation_id}")
        else:
            print("   FAIL - Conversation creation FAILED")
            return False
    except Exception as e:
        print(f"   ERROR - Conversation creation ERROR: {e}")
        return False
    
    print()
    
    # Test 3: Send message
    print("3. Testing message sending...")
    message_payload = {
        "conversation_id": conversation_id,
        "sender_type": "agent",
        "sender_id": None,
        "agent_type": "COIA",
        "content": "Welcome to contractor onboarding! This is a test message.",
        "content_type": "text",
        "metadata": {
            "stage": "welcome",
            "timestamp": datetime.now().isoformat()
        }
    }
    
    try:
        response = requests.post(f"{base_url}/conversations/message", json=message_payload, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.ok:
            response_data = response.json()
            message_id = response_data.get("message_id")
            print(f"   PASS - Message sent: {message_id}")
        else:
            print("   FAIL - Message sending FAILED")
            return False
    except Exception as e:
        print(f"   ERROR - Message sending ERROR: {e}")
        return False
    
    print()
    
    # Test 4: Store memory
    print("4. Testing memory storage...")
    memory_payload = {
        "conversation_id": conversation_id,
        "memory_type": "agent_state",
        "key": "coia_test_state",
        "value": {
            "current_stage": "test",
            "test_data": "This is test memory data",
            "timestamp": datetime.now().isoformat()
        }
    }
    
    try:
        response = requests.post(f"{base_url}/conversations/memory", json=memory_payload, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.ok:
            response_data = response.json()
            memory_id = response_data.get("memory_id")
            print(f"   PASS - Memory stored: {memory_id}")
        else:
            print("   FAIL - Memory storage FAILED")
            return False
    except Exception as e:
        print(f"   ERROR - Memory storage ERROR: {e}")
        return False
    
    print()
    
    # Test 5: Get conversation
    print("5. Testing conversation retrieval...")
    try:
        response = requests.get(f"{base_url}/conversations/{conversation_id}", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.ok:
            response_data = response.json()
            messages = response_data.get("messages", [])
            memory = response_data.get("memory", [])
            print(f"   PASS - Conversation retrieved")
            print(f"   Messages: {len(messages)}")
            print(f"   Memory records: {len(memory)}")
            
            # Show some details
            if messages:
                print(f"   First message: {messages[0].get('content', '')[:50]}...")
            if memory:
                print(f"   Memory keys: {[m.get('key') for m in memory]}")
        else:
            print(f"   FAIL - Conversation retrieval FAILED: {response.text}")
            return False
    except Exception as e:
        print(f"   ERROR - Conversation retrieval ERROR: {e}")
        return False
    
    print()
    print("ALL UNIFIED API TESTS PASSED!")
    print(f"Test conversation ID: {conversation_id}")
    return True

if __name__ == "__main__":
    success = test_unified_api_endpoints()
    if success:
        print("\nPASS - Unified API is working correctly")
        print("Issue must be in COIA integration or save triggers")
    else:
        print("\nFAIL - Unified API has issues")
        print("Need to fix API before debugging COIA integration")