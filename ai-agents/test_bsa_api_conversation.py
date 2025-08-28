#!/usr/bin/env python3
"""
Test BSA API endpoint with real conversation scenarios
"""

import asyncio
import requests
import time
import json

def test_bsa_api_conversation():
    """Test BSA API with realistic contractor conversations"""
    
    print("TESTING BSA API CONVERSATION ENDPOINTS")
    print("=" * 50)
    
    base_url = "http://localhost:8008/api/bsa"
    
    # Test 1: Initial contractor conversation
    print("TEST 1: Initial contractor conversation")
    
    payload_1 = {
        "contractor_id": "test-contractor-api-001",
        "message": "Hello, I'm Sarah from Green Thumb Landscaping. We specialize in lawn care and garden design in Orlando.",
        "session_id": "session-api-001"
    }
    
    try:
        print("Sending request to BSA API...")
        start_time = time.time()
        
        response = requests.post(
            f"{base_url}/fast-stream",
            json=payload_1,
            timeout=45  # Increased timeout for BSA processing
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"Response time: {response_time:.2f} seconds")
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("SUCCESS: BSA API responded")
            
            # Try to parse response
            try:
                response_data = response.json()
                print(f"Response type: {type(response_data)}")
                print(f"Response preview: {str(response_data)[:200]}...")
            except json.JSONDecodeError:
                print("Response is not JSON, checking if it's streaming...")
                print(f"Response text preview: {response.text[:200]}...")
                
        else:
            print(f"ERROR: BSA API returned status {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("ERROR: BSA API request timed out")
        return False
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to BSA API")
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        return False
    
    # Test 2: Follow-up conversation
    print("\nTEST 2: Follow-up conversation with same contractor")
    
    payload_2 = {
        "contractor_id": "test-contractor-api-001",  # Same contractor
        "message": "Can you show me any lawn maintenance projects available in the Orlando area?",
        "session_id": "session-api-002"  # Different session
    }
    
    try:
        print("Sending follow-up request...")
        start_time = time.time()
        
        response = requests.post(
            f"{base_url}/fast-stream",
            json=payload_2,
            timeout=45
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"Follow-up response time: {response_time:.2f} seconds")
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("SUCCESS: BSA API handled follow-up conversation")
            return True
        else:
            print(f"ERROR: Follow-up request failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"ERROR in follow-up test: {e}")
        return False

def test_bsa_api_health():
    """Test if BSA API is accessible"""
    
    print("TESTING BSA API HEALTH")
    print("=" * 30)
    
    try:
        # Test basic backend health
        response = requests.get("http://localhost:8008", timeout=5)
        if response.status_code == 200:
            print("Backend is running")
            
            # Check if BSA endpoints are listed
            data = response.json()
            endpoints = data.get('endpoints', [])
            bsa_available = any('bsa' in endpoint.lower() for endpoint in endpoints)
            print(f"BSA endpoints listed: {bsa_available}")
            
            return True
        else:
            print(f"Backend responded with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Backend health check failed: {e}")
        return False

def main():
    """Run all BSA API tests"""
    
    print("STARTING BSA API INTEGRATION TESTS")
    print("=" * 40)
    
    # Health check first
    health_ok = test_bsa_api_health()
    if not health_ok:
        print("STOPPING: Backend health check failed")
        return
    
    # API conversation test
    conversation_ok = test_bsa_api_conversation()
    
    print("\n" + "=" * 40)
    print("BSA API TEST RESULTS:")
    print(f"  Backend health: {'PASS' if health_ok else 'FAIL'}")
    print(f"  API conversations: {'PASS' if conversation_ok else 'FAIL'}")
    
    if health_ok and conversation_ok:
        print("\nSUCCESS: BSA API is working for contractor conversations!")
    elif health_ok:
        print("\nPARTIAL: Backend is running but BSA API has issues")
    else:
        print("\nFAILED: Backend or BSA API is not working")

if __name__ == "__main__":
    main()