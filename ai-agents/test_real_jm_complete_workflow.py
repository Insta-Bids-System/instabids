"""
REAL END-TO-END TEST - ACTING AS JUSTIN FROM JM HOLIDAY LIGHTING
This test actually goes through the COMPLETE contractor onboarding workflow
including research, profile building, and account creation
"""

import requests
import asyncio
import json
import time
from config.service_urls import get_backend_url

async def test_real_jm_onboarding():
    """Act as Justin from JM Holiday Lighting - complete workflow"""
    
    print("=" * 80)
    print("REAL END-TO-END COIA TEST - JUSTIN FROM JM HOLIDAY LIGHTING")
    print("=" * 80)
    print("Testing COMPLETE workflow: Research -> Profile Building -> Account Creation")
    print()
    
    contractor_lead_id = "jm-holiday-real-test"
    api_url = f"{get_backend_url()}/api/coia/landing"
    
    # Session 1: Introduce as Justin from JM Holiday Lighting
    print("SESSION 1: Introducing myself as Justin from JM Holiday Lighting")
    print("-" * 60)
    
    response1 = requests.post(api_url, json={
        "message": "Hi, I'm Justin from JM Holiday Lighting. We're a professional holiday lighting installation company serving the Denver metro area. We've been in business for 8 years and specialize in residential and commercial Christmas light installations.",
        "contractor_lead_id": contractor_lead_id,
        "session_id": "session-1"
    }, timeout=60)
    
    if response1.status_code == 200:
        result1 = response1.json()
        ai_response1 = get_ai_response(result1)
        print(f"AI Response: {ai_response1[:500]}...")
        print(f"Response indicates research mode: {'research' in ai_response1.lower() or 'looking up' in ai_response1.lower()}")
    else:
        print(f"ERROR: {response1.status_code}")
        return False
    
    # Wait for research to complete
    time.sleep(3)
    
    # Session 2: Ask about what was found
    print("\nSESSION 2: Asking what information was found about my company")
    print("-" * 60)
    
    response2 = requests.post(api_url, json={
        "message": "What information did you find about JM Holiday Lighting? Can you show me what details you discovered?",
        "contractor_lead_id": contractor_lead_id,
        "session_id": "session-2"
    }, timeout=60)
    
    if response2.status_code == 200:
        result2 = response2.json()
        ai_response2 = get_ai_response(result2)
        print(f"AI Response: {ai_response2[:500]}...")
        
        # Check if research data is mentioned
        research_indicators = ['phone', 'address', 'website', 'reviews', 'rating', 'years']
        research_found = any(ind in ai_response2.lower() for ind in research_indicators)
        print(f"Research data found: {research_found}")
    else:
        print(f"ERROR: {response2.status_code}")
        return False
    
    # Session 3: Request account creation
    print("\nSESSION 3: Requesting account creation")
    print("-" * 60)
    
    response3 = requests.post(api_url, json={
        "message": "I want to create an account so I can start bidding on projects. Please set up my contractor account with all the information you've gathered.",
        "contractor_lead_id": contractor_lead_id,
        "session_id": "session-3"
    }, timeout=60)
    
    if response3.status_code == 200:
        result3 = response3.json()
        ai_response3 = get_ai_response(result3)
        print(f"AI Response: {ai_response3[:500]}...")
        
        # Check for account creation indicators
        account_indicators = ['account', 'created', 'login', 'email', 'password', 'credentials']
        account_created = any(ind in ai_response3.lower() for ind in account_indicators)
        print(f"Account creation mentioned: {account_created}")
    else:
        print(f"ERROR: {response3.status_code}")
        return False
    
    # Session 4: Ask for login details
    print("\nSESSION 4: Asking for login credentials")
    print("-" * 60)
    
    response4 = requests.post(api_url, json={
        "message": "What are my login credentials? How do I access my contractor account?",
        "contractor_lead_id": contractor_lead_id,
        "session_id": "session-4"
    }, timeout=60)
    
    if response4.status_code == 200:
        result4 = response4.json()
        ai_response4 = get_ai_response(result4)
        print(f"AI Response: {ai_response4[:500]}...")
        
        # Check for credential information
        credential_indicators = ['email', 'password', 'login', 'portal', 'sign in']
        credentials_provided = any(ind in ai_response4.lower() for ind in credential_indicators)
        print(f"Credentials provided: {credentials_provided}")
    else:
        print(f"ERROR: {response4.status_code}")
        return False
    
    # Session 5: Ask about available bid cards
    print("\nSESSION 5: Asking about available projects to bid on")
    print("-" * 60)
    
    response5 = requests.post(api_url, json={
        "message": "What projects are available for me to bid on in my area? Show me bid cards that match my holiday lighting expertise.",
        "contractor_lead_id": contractor_lead_id,
        "session_id": "session-5"
    }, timeout=60)
    
    if response5.status_code == 200:
        result5 = response5.json()
        ai_response5 = get_ai_response(result5)
        print(f"AI Response: {ai_response5[:500]}...")
        
        # Check for bid card mentions
        bid_indicators = ['project', 'bid', 'opportunity', 'budget', 'timeline']
        bids_shown = any(ind in ai_response5.lower() for ind in bid_indicators)
        print(f"Bid opportunities shown: {bids_shown}")
    else:
        print(f"ERROR: {response5.status_code}")
        return False
    
    return True

def get_ai_response(result):
    """Extract AI response from result"""
    if result.get('messages'):
        for msg in reversed(result['messages']):
            if msg.get('type') == 'ai':
                return msg.get('content', '')
    return result.get('response', 'No response')

async def verify_database_state():
    """Check if contractor was actually created in database"""
    print("\n" + "=" * 80)
    print("VERIFYING DATABASE STATE")
    print("-" * 60)
    
    # Import database module
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from database_simple import db
    
    # Check contractors table
    print("Checking contractors table for JM Holiday Lighting...")
    contractors = db.client.table("contractors").select("*").ilike("company_name", "%JM Holiday%").execute()
    
    if contractors.data:
        print(f"FOUND in contractors table: {len(contractors.data)} records")
        for contractor in contractors.data:
            print(f"  - ID: {contractor['id']}")
            print(f"  - Company: {contractor['company_name']}")
            print(f"  - Email: {contractor.get('email', 'N/A')}")
            print(f"  - Verified: {contractor.get('verified', False)}")
            print(f"  - Tier: {contractor.get('tier', 'N/A')}")
    else:
        print("NOT FOUND in contractors table")
    
    # Check contractor_leads table
    print("\nChecking contractor_leads table for JM Holiday Lighting...")
    leads = db.client.table("contractor_leads").select("*").ilike("company_name", "%JM Holiday%").execute()
    
    if leads.data:
        print(f"FOUND in contractor_leads table: {len(leads.data)} records")
        for lead in leads.data:
            print(f"  - ID: {lead['id']}")
            print(f"  - Company: {lead['company_name']}")
            print(f"  - Contact: {lead.get('contact_name', 'N/A')}")
            print(f"  - Phone: {lead.get('phone', 'N/A')}")
            print(f"  - Email: {lead.get('email', 'N/A')}")
            print(f"  - Website: {lead.get('website', 'N/A')}")
            print(f"  - Specialties: {lead.get('specialties', [])}")
            print(f"  - Years in Business: {lead.get('years_in_business', 'N/A')}")
    else:
        print("NOT FOUND in contractor_leads table")
    
    # Check langgraph_checkpoints for conversation memory
    print("\nChecking langgraph_checkpoints for conversation memory...")
    checkpoints = db.client.table("langgraph_checkpoints").select("*").eq("thread_id", "jm-holiday-real-test").execute()
    
    if checkpoints.data:
        print(f"FOUND {len(checkpoints.data)} conversation checkpoints")
    else:
        print("NO conversation checkpoints found")

if __name__ == "__main__":
    print("Starting REAL End-to-End JM Holiday Lighting Test")
    print("This test will actually try to research, build profile, and create account")
    print()
    
    try:
        # Run the main test
        success = asyncio.run(test_real_jm_onboarding())
        
        if success:
            print("\n" + "=" * 80)
            print("API CALLS COMPLETED - Checking actual database state...")
            
            # Verify what actually happened in the database
            asyncio.run(verify_database_state())
            
            print("\n" + "=" * 80)
            print("TEST COMPLETE - Check results above to see what actually happened")
        else:
            print("\nTEST FAILED - API calls did not complete successfully")
            
    except Exception as e:
        print(f"\nTEST FAILED WITH ERROR: {e}")
        import traceback
        traceback.print_exc()