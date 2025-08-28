"""
Test COIA Account Creation Confirmation Flow
Tests the consent-based account creation as requested by the user
"""
import asyncio
import requests
import json
import time
from config.service_urls import get_backend_url

BASE_URL = get_backend_url()

async def test_coia_confirmation_flow():
    """Test the full COIA flow with account creation confirmation"""
    
    print("\n" + "="*80)
    print("TESTING COIA CONSENT-BASED ACCOUNT CREATION")
    print("="*80 + "\n")
    
    # Generate unique session ID for this test
    import uuid
    session_id = f"test-{uuid.uuid4().hex[:8]}"
    contractor_lead_id = f"lead-{uuid.uuid4().hex[:8]}"
    
    print(f"Session ID: {session_id}")
    print(f"Contractor Lead ID: {contractor_lead_id}\n")
    
    # Test conversation messages
    test_messages = [
        # Initial contact - introduce company
        "Hi, I run JM Holiday Lighting in Pompano Beach FL. We do holiday lighting installations.",
        
        # Let COIA research and respond, then wait for confirmation prompt
        # After research, we should get the "Would you like me to create your profile?" prompt
        
        # Then confirm account creation
        "Yes, create my profile"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{'='*60}")
        print(f"Turn {i}: Sending message...")
        print(f"User: {message}")
        print("-"*60)
        
        # Send message to COIA
        payload = {
            "message": message,
            "session_id": session_id,
            "contractor_lead_id": contractor_lead_id,
            "interface": "landing_page"  # Critical: Use landing_page interface
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/coia/landing",
                json=payload,
                timeout=120  # Long timeout for API calls
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get("response", "No response")
                
                # Handle Unicode safely
                try:
                    print(f"COIA: {ai_response[:500]}...")
                except UnicodeEncodeError:
                    # Use ASCII-safe version
                    safe_response = ai_response[:500].encode('ascii', 'ignore').decode('ascii')
                    print(f"COIA: {safe_response}...")
                
                # Check state information
                state_info = result.get("state", {})
                print(f"\n[STATE] State Info:")
                print(f"  - Company Name: {state_info.get('company_name', 'Not extracted')}")
                print(f"  - Research Completed: {state_info.get('research_completed', False)}")
                print(f"  - Account Creation Confirmed: {state_info.get('account_creation_confirmed', False)}")
                print(f"  - Contractor Created: {state_info.get('contractor_created', False)}")
                
                # Check if we got the confirmation prompt
                if "Would you like me to create your profile" in ai_response:
                    print("\n[SUCCESS] CONFIRMATION PROMPT DETECTED!")
                    print("System is correctly asking for user consent before creating account.")
                
                # Check if account was created after confirmation
                if i == len(test_messages) and state_info.get('contractor_created'):
                    print("\n[COMPLETE] ACCOUNT SUCCESSFULLY CREATED WITH USER CONSENT!")
                    print("The consent-based flow is working correctly.")
                
            else:
                print(f"[ERROR] Status {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.Timeout:
            print("[TIMEOUT] Request timed out (this might mean backend is processing)")
        except Exception as e:
            print(f"[ERROR] {e}")
        
        # Wait a bit between messages
        if i < len(test_messages):
            time.sleep(2)
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    # Skip health check and run test directly
    print("[INFO] Starting COIA confirmation flow test...")
    asyncio.run(test_coia_confirmation_flow())