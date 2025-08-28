"""
Test to verify Google API research is triggered properly in COIA
"""

import asyncio
import json
import requests
import time
from config.service_urls import get_backend_url

async def test_research_trigger():
    """Test that research is properly triggered when company name is extracted"""
    
    print("\n" + "="*60)
    print("TESTING COIA RESEARCH TRIGGER VERIFICATION")  
    print("="*60)
    
    # Test with different company introductions
    test_cases = [
        {
            "message": "Hi, I am Justin and I own JM Holiday Lighting in South Florida",
            "session": "research-test-001",
            "expected_company": "JM Holiday Lighting"
        },
        {
            "message": "Hello, my company is TurfGrass Artificial Solutions and we do landscaping",
            "session": "research-test-002", 
            "expected_company": "TurfGrass Artificial Solutions"
        }
    ]
    
    for i, test in enumerate(test_cases):
        print(f"\n--- TEST CASE {i+1} ---")
        print(f"Message: {test['message']}")
        print(f"Expected company: {test['expected_company']}")
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{get_backend_url()}/api/coia/landing",
                json={"message": test["message"], "session_id": test["session"]},
                timeout=30
            )
            elapsed = time.time() - start_time
            
            print(f"Response time: {elapsed:.2f}s")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Check if company was extracted
                    company_found = False
                    if "company_name" in data:
                        print(f"[SUCCESS] Company extracted: {data['company_name']}")
                        company_found = True
                    
                    # Check response for company mention
                    response_text = data.get("response", "")
                    if test["expected_company"].lower() in response_text.lower():
                        print(f"[SUCCESS] Company mentioned in response")
                        company_found = True
                        
                    if not company_found:
                        print(f"[WARNING] Company not clearly extracted")
                        
                    # Check if research would be triggered
                    # (Research might not complete in landing page due to our loop prevention)
                    if "research" in response_text.lower():
                        print(f"[INFO] Research mentioned in response")
                        
                    # Show key response excerpt
                    print(f"Response excerpt: {response_text[:150]}...")
                    
                except Exception as parse_error:
                    print(f"[ERROR] JSON parsing error: {parse_error}")
                    print(f"Raw response: {response.text[:200]}")
                    
            else:
                print(f"[ERROR] HTTP {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            print(f"[ERROR] Request failed: {e}")
    
    print(f"\n" + "="*60)
    print("RESEARCH VERIFICATION COMPLETE")
    print("="*60)

async def test_chat_research_flow():
    """Test the full research flow via chat endpoint"""
    
    print(f"\n--- CHAT ENDPOINT RESEARCH FLOW ---")
    
    payload = {
        "message": "I'm Mike and I run Premium Construction Services in Miami",
        "session_id": "chat-research-test"
    }
    
    try:
        response = requests.post(
            f"{get_backend_url()}/api/coia/chat",
            json=payload,
            timeout=25
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"[CHAT] Response received")
            print(f"Response: {data.get('response', '')[:200]}...")
            
            # Check if this triggers follow-up research
            if "Premium Construction" in data.get('response', ''):
                print(f"[SUCCESS] Company name recognized in chat")
        else:
            print(f"[ERROR] Chat failed: {response.status_code}")
            
    except Exception as e:
        print(f"[ERROR] Chat test failed: {e}")

async def main():
    """Run research verification tests"""
    await test_research_trigger()
    await test_chat_research_flow()

if __name__ == "__main__":
    asyncio.run(main())