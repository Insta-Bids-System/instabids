"""
Complete COIA Landing Page Flow Test
Tests the entire flow from initial contact to account creation
Follows the design in LANDING_PAGE_CONTRACTOR_FLOW_DESIGN.md
"""
import asyncio
import requests
import json
import time
import uuid
from config.service_urls import get_backend_url

BASE_URL = get_backend_url()

async def test_complete_coia_flow():
    """Test the complete COIA flow following the design document stages"""
    
    print("\n" + "="*80)
    print("TESTING COMPLETE COIA LANDING PAGE FLOW")
    print("Following stages from LANDING_PAGE_CONTRACTOR_FLOW_DESIGN.md")
    print("="*80 + "\n")
    
    # Generate unique session ID for this test
    session_id = f"test-{uuid.uuid4().hex[:8]}"
    contractor_lead_id = f"lead-{uuid.uuid4().hex[:8]}"
    
    print(f"Session ID: {session_id}")
    print(f"Contractor Lead ID: {contractor_lead_id}\n")
    
    # Test conversation following the design stages
    test_stages = [
        {
            "stage": "STAGE 1: Initial Contact & Business Identification",
            "message": "Hi, I run JM Holiday Lighting in Pompano Beach FL. We do holiday lighting installations.",
            "expected": ["JM Holiday Lighting", "look up", "business information"]
        },
        {
            "stage": "STAGE 2: Business Confirmation (after research)",
            "message": "Yes that's my business! We're at the Pompano Beach location.",
            "expected": ["found", "profile", "create"]
        },
        {
            "stage": "STAGE 3: Account Creation Confirmation",
            "message": "Yes, create my profile please!",
            "expected": ["account", "created", "password"]
        }
    ]
    
    conversation_state = None
    
    for i, stage_data in enumerate(test_stages, 1):
        print(f"\n{'='*60}")
        print(f"{stage_data['stage']}")
        print(f"Turn {i}: {stage_data['message']}")
        print("-"*60)
        
        # Send message to COIA
        payload = {
            "message": stage_data["message"],
            "session_id": session_id,
            "contractor_lead_id": contractor_lead_id,
            "interface": "landing_page"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/coia/landing",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get("response", "No response")
                
                # Handle Unicode safely
                try:
                    print(f"COIA Response Preview:")
                    print(ai_response[:400] + "..." if len(ai_response) > 400 else ai_response)
                except UnicodeEncodeError:
                    safe_response = ai_response[:400].encode('ascii', 'ignore').decode('ascii')
                    print(f"COIA Response Preview:")
                    print(safe_response + "...")
                
                # Check state information
                state_info = result.get("state", {})
                conversation_state = state_info  # Save for analysis
                
                print(f"\n[STATE] Analysis:")
                print(f"  - Company Name: {state_info.get('company_name', 'Not extracted')}")
                print(f"  - Research Completed: {state_info.get('research_completed', False)}")
                print(f"  - Account Creation Confirmed: {state_info.get('account_creation_confirmed', False)}")
                print(f"  - Contractor Created: {state_info.get('contractor_created', False)}")
                print(f"  - Contractor ID: {state_info.get('contractor_id', 'None')}")
                
                # Check for expected content
                response_lower = ai_response.lower()
                found_expected = [exp for exp in stage_data["expected"] if exp.lower() in response_lower]
                print(f"\n[VALIDATION] Expected keywords found: {found_expected}")
                
                # Stage-specific checks
                if i == 1:  # After Stage 1
                    if state_info.get('company_name') == 'JM Holiday Lighting':
                        print("[SUCCESS] Company name correctly extracted!")
                    else:
                        print(f"[WARNING] Company name not extracted correctly: {state_info.get('company_name')}")
                
                elif i == 2:  # After Stage 2
                    if "Would you like me to create your profile" in ai_response:
                        print("[SUCCESS] Account creation confirmation prompt detected!")
                    
                elif i == 3:  # After Stage 3
                    if state_info.get('contractor_created'):
                        print("[SUCCESS] CONTRACTOR ACCOUNT CREATED!")
                        print(f"[SUCCESS] Contractor ID: {state_info.get('contractor_id')}")
                    else:
                        print("[FAILURE] Contractor account NOT created - flag still False")
                
            else:
                print(f"[ERROR] Status {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
        except requests.Timeout:
            print("[TIMEOUT] Request timed out (backend processing)")
        except Exception as e:
            print(f"[ERROR] {str(e)[:200]}")
        
        # Wait between stages
        if i < len(test_stages):
            print(f"\nWaiting 3 seconds before next stage...")
            time.sleep(3)
    
    # Final Summary
    print("\n" + "="*80)
    print("TEST COMPLETE - FINAL ANALYSIS")
    print("="*80)
    
    if conversation_state:
        print("\nFinal State Summary:")
        print(f"  - Company Extracted: {'Yes' if conversation_state.get('company_name') else 'No'}")
        print(f"  - Research Completed: {'Yes' if conversation_state.get('research_completed') else 'No'}")
        print(f"  - Account Created: {'Yes' if conversation_state.get('contractor_created') else 'No'}")
        print(f"  - Contractor ID: {conversation_state.get('contractor_id', 'None')}")
        
        if conversation_state.get('contractor_created'):
            print("\n[OVERALL RESULT] SUCCESS - Full flow completed with account creation!")
        else:
            print("\n[OVERALL RESULT] FAILURE - contractor_created flag never set to True")
    else:
        print("\n[OVERALL RESULT] ERROR - No state information available")

if __name__ == "__main__":
    print("[INFO] Starting complete COIA flow test...")
    asyncio.run(test_complete_coia_flow())