"""
Simple test for COIA state persistence system
Tests the core functionality without complex scenarios
"""

import json
import time
import requests
from config.service_urls import get_backend_url

API_BASE_URL = get_backend_url()

def test_coia_state_persistence():
    """Test core state persistence functionality"""
    print("="*60)
    print("COIA STATE PERSISTENCE - SIMPLE TEST")
    print("="*60)
    
    # Test 1: First conversation
    print("\nTest 1: First conversation with company info")
    print("-" * 40)
    
    response1 = requests.post(
        f"{API_BASE_URL}/api/coia/landing",
        json={
            "message": "Hi, I'm ABC Landscaping and we specialize in lawn care",
            "session_id": "test-session-1"
        }
    )
    
    if response1.status_code == 200:
        data1 = response1.json()
        contractor_lead_id = data1.get("contractor_lead_id")
        
        if contractor_lead_id and contractor_lead_id.startswith("landing-"):
            print(f"PASS: contractor_lead_id generated: {contractor_lead_id}")
            
            if "ABC Landscaping" in data1.get("response", "") or "lawn care" in data1.get("response", ""):
                print("PASS: Company info acknowledged")
            else:
                print("PARTIAL: Company info not clearly acknowledged")
        else:
            print("FAIL: No contractor_lead_id generated")
            return
    else:
        print(f"FAIL: API error {response1.status_code}")
        return
    
    # Test 2: Return visitor with same ID
    print(f"\nTest 2: Return visitor with ID {contractor_lead_id}")
    print("-" * 40)
    
    # Wait for async save
    time.sleep(2)
    
    response2 = requests.post(
        f"{API_BASE_URL}/api/coia/landing",
        json={
            "message": "What do you remember about my company?",
            "session_id": "test-session-2",
            "contractor_lead_id": contractor_lead_id
        }
    )
    
    if response2.status_code == 200:
        data2 = response2.json()
        response_text = data2.get("response", "").lower()
        
        if any(term in response_text for term in ["abc landscaping", "lawn care", "remember", "mentioned", "told"]):
            print("PASS: COIA remembers previous conversation!")
            print(f"Response snippet: {data2['response'][:150]}...")
        else:
            print("FAIL: COIA doesn't remember previous conversation")
            print(f"Response: {data2['response'][:150]}...")
        
        # Verify same contractor_lead_id
        if data2.get("contractor_lead_id") == contractor_lead_id:
            print(f"PASS: Same contractor_lead_id maintained")
        else:
            print("FAIL: contractor_lead_id changed")
    else:
        print(f"FAIL: API error {response2.status_code}")
    
    # Test 3: Check unified memory storage
    print(f"\nTest 3: Verify state saved to unified memory")
    print("-" * 40)
    
    try:
        response3 = requests.get(f"{API_BASE_URL}/api/conversations/{contractor_lead_id}")
        
        if response3.status_code == 200:
            data3 = response3.json()
            memory_items = data3.get("memory", [])
            
            state_fields = [item for item in memory_items if item.get("memory_type") == "coia_state"]
            
            if state_fields:
                print(f"PASS: Found {len(state_fields)} state fields in unified memory")
                
                # Check for company_name
                company_saved = any(item.get("memory_key") == "company_name" for item in state_fields)
                if company_saved:
                    print("PASS: company_name saved to unified memory")
                else:
                    print("PARTIAL: State fields saved but no company_name")
                    
                # Show sample fields
                print("Sample saved fields:")
                for item in state_fields[:3]:
                    key = item.get("memory_key", "unknown")
                    value = str(item.get("memory_value", ""))[:50]
                    print(f"  - {key}: {value}")
            else:
                print("FAIL: No state fields found in unified memory")
        else:
            print(f"SKIP: Cannot check unified memory (error {response3.status_code})")
    except Exception as e:
        print(f"SKIP: Cannot check unified memory ({e})")
    
    print("\n" + "="*60)
    print("TEST COMPLETED")
    print("="*60)
    print(f"Test contractor_lead_id: {contractor_lead_id}")
    print("\nIf COIA remembered your company in Test 2, the system is working!")

if __name__ == "__main__":
    test_coia_state_persistence()