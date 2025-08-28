"""
Test COIA landing page endpoint with recursion loop fixes
"""

import asyncio
import json
import requests
import time
from config.service_urls import get_backend_url

async def test_landing_page_with_jm_holiday():
    """Test the landing page endpoint with JM Holiday Lighting"""
    
    print("\n" + "="*60)
    print("TESTING COIA LANDING PAGE WITH RECURSION FIXES")
    print("="*60)
    
    # Test payload with company info
    payload = {
        "message": "Hi, I am Justin and I own JM Holiday Lighting in South Florida",
        "session_id": "test-fix-001"
    }
    
    print(f"\n[SEND] Sending to landing page endpoint:")
    print(f"   Message: {payload['message']}")
    print(f"   Session: {payload['session_id']}")
    
    try:
        # Call the landing page endpoint
        start_time = time.time()
        response = requests.post(
            f"{get_backend_url()}/api/coia/landing",
            json=payload,
            timeout=60  # 60 second timeout
        )
        elapsed = time.time() - start_time
        
        print(f"\n[TIME] Response time: {elapsed:.2f} seconds")
        print(f"[STATUS] Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n[SUCCESS] Landing page endpoint responded")
            
            # Check for mode detector visits
            if "state" in data:
                mode_visits = data["state"].get("mode_detector_visits", 0)
                print(f"   Mode detector visits: {mode_visits}")
                
                if mode_visits > 1:
                    print(f"   [WARNING] Mode detector was visited {mode_visits} times (loop prevention triggered)")
            
            # Check for research completion
            if "research_completed" in data:
                print(f"   Research completed: {data['research_completed']}")
            
            # Check for company extraction
            if "company_name" in data:
                print(f"   Company extracted: {data['company_name']}")
            
            # Check for Google data
            if "google_business" in data:
                print(f"   Google data found: Yes")
                
            # Show the response message
            if "response" in data:
                print(f"\n[RESPONSE] Response from COIA:")
                print(f"   {data['response'][:200]}...")
                
            # Check if research was triggered
            if "research_findings" in data:
                findings = data.get("research_findings", {})
                if findings.get("google_business"):
                    print(f"\n[GOOGLE] Google Business Data Found:")
                    google_data = findings["google_business"]
                    print(f"   Company: {google_data.get('company_name')}")
                    print(f"   Phone: {google_data.get('phone')}")
                    print(f"   Rating: {google_data.get('rating')}")
                    
        else:
            print(f"\n[ERROR] Status: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print("\n[TIMEOUT] Request timed out after 60 seconds")
        print("   This might indicate the recursion loop is still happening")
        
    except Exception as e:
        print(f"\n[ERROR] Error calling landing page endpoint: {e}")

async def test_chat_endpoint_as_alternative():
    """Test the chat endpoint as an alternative"""
    
    print("\n" + "="*60)
    print("TESTING CHAT ENDPOINT AS ALTERNATIVE")
    print("="*60)
    
    payload = {
        "message": "Hi, I am Justin and I own JM Holiday Lighting", 
        "session_id": "test-chat-001"
    }
    
    print(f"\n[SEND] Sending to chat endpoint:")
    print(f"   Message: {payload['message']}")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{get_backend_url()}/api/coia/chat",
            json=payload,
            timeout=30
        )
        elapsed = time.time() - start_time
        
        print(f"\n[TIME] Response time: {elapsed:.2f} seconds")
        print(f"[STATUS] Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n[SUCCESS] Chat endpoint working")
            
            if "response" in data:
                print(f"\n[RESPONSE] Response:")
                print(f"   {data['response'][:200]}...")
                
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")

async def main():
    """Run all tests"""
    
    # First test the landing page with fixes
    await test_landing_page_with_jm_holiday()
    
    # Then test chat endpoint as backup
    await test_chat_endpoint_as_alternative()
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())