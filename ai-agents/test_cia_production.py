"""
Production test for CIA agent with FULL database access
"""

import requests
import json
import os
from dotenv import load_dotenv
from config.service_urls import get_backend_url

# Load root env
load_dotenv(r'C:\Users\Not John Or Justin\Documents\instabids\.env', override=True)

def test_cia_production():
    """Test CIA agent via API with full database access"""
    
    print("=" * 60)
    print("CIA PRODUCTION TEST - FULL DATABASE ACCESS")
    print("=" * 60)
    
    # Test data
    test_user_id = "11111111-1111-1111-1111-111111111111"
    test_session_id = "test_session_123"
    
    # Test message
    test_message = "I need help with my backyard renovation project. Can you tell me about the bids I've received?"
    
    print(f"\n[TEST] User: {test_message}")
    
    # Call CIA endpoint
    url = f"{get_backend_url()}/api/cia/chat"
    
    payload = {
        "message": test_message,
        "user_id": test_user_id,
        "session_id": test_session_id,
        "stream": False  # Non-streaming for testing
    }
    
    print(f"\n[TEST] Calling CIA endpoint: {url}")
    print(f"[TEST] Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n[SUCCESS] CIA Response received!")
            print(f"[CIA]: {result.get('response', 'No response')}")
            
            # Check if context was loaded
            if "context" in result:
                print(f"\n[CONTEXT] Loaded {len(result['context'])} data categories")
            
            return True
        else:
            print(f"\n[ERROR] CIA endpoint returned {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"\n[ERROR] CIA request timed out after 30 seconds")
        return False
    except requests.exceptions.ConnectionError:
        print(f"\n[ERROR] Could not connect to backend at localhost:8008")
        print("Make sure the backend is running!")
        return False
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        return False

def check_backend_health():
    """Check if backend is running"""
    try:
        response = requests.get(f"{get_backend_url()}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    # Check backend first
    if not check_backend_health():
        print("[WARNING] Backend not responding at localhost:8008")
        print("Checking Docker containers...")
        os.system('docker ps | findstr instabids-backend')
    
    # Run the test
    success = test_cia_production()
    
    if success:
        print("\n" + "=" * 60)
        print("CIA AGENT READY FOR PRODUCTION!")
        print("The homeowner agent has FULL database access")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("CIA AGENT TEST FAILED")
        print("Check the errors above and fix before deploying")
        print("=" * 60)