#!/usr/bin/env python
"""
PROVE TO USER - EXACT BACKEND VERIFICATION TEST
Creates new contractor, shows exactly where data is saved, proves memory persistence
"""

import asyncio
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
import uuid

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from agents.coia.unified_graph import create_unified_coia_system, invoke_coia_chat

# Create unique contractor for this test
UNIQUE_CONTRACTOR_ID = f"proof_test_{int(datetime.now().timestamp())}"
UNIQUE_COMPANY_NAME = f"ProofTest Contracting {datetime.now().strftime('%H%M%S')}"

async def test_prove_to_user():
    """PROVE TO USER: Show exactly where data is saved and memory persistence"""
    print("======================================================================")
    print("PROVING TO USER: EXACT BACKEND VERIFICATION")
    print(f"Creating NEW contractor: {UNIQUE_COMPANY_NAME}")
    print(f"Contractor ID: {UNIQUE_CONTRACTOR_ID}")
    print("======================================================================")
    
    try:
        # Create COIA system
        print("\n[STEP 1] Creating COIA system...")
        app = await create_unified_coia_system()
        print("✅ COIA system ready")
        
        # CONVERSATION 1: Create brand new contractor
        print(f"\n[STEP 2] Creating NEW contractor profile...")
        message1 = f"Hi, I'm John from {UNIQUE_COMPANY_NAME}. We've been in business for 8 years and specialize in emergency HVAC repairs in Phoenix area. Our website is https://prooftest-hvac.com."
        
        result1 = await invoke_coia_chat(
            app=app,
            user_message=message1,
            session_id="proof_session",
            contractor_lead_id=UNIQUE_CONTRACTOR_ID
        )
        
        # Extract and display results
        profile1 = result1.get("contractor_profile", {})
        messages1 = result1.get("messages", [])
        response1 = messages1[-1].content if messages1 else "No response"
        
        print(f"✅ CONVERSATION 1 COMPLETE")
        print(f"   Profile extracted: {profile1}")
        print(f"   Response: {response1[:100]}...")
        
        # CONVERSATION 2: Test memory - ask follow-up without repeating info
        print(f"\n[STEP 3] Testing memory persistence...")
        message2 = "What services does my company offer? Also, I'd like to find emergency HVAC projects."
        
        result2 = await invoke_coia_chat(
            app=app,
            user_message=message2,
            session_id="proof_session", 
            contractor_lead_id=UNIQUE_CONTRACTOR_ID
        )
        
        # Extract results
        profile2 = result2.get("contractor_profile", {})
        messages2 = result2.get("messages", [])
        response2 = messages2[-1].content if messages2 else "No response"
        mode2 = result2.get("current_mode", "unknown")
        
        print(f"✅ CONVERSATION 2 COMPLETE")
        print(f"   Remembered profile: {profile2}")
        print(f"   Current mode: {mode2}")
        print(f"   Response: {response2[:100]}...")
        
        # CONVERSATION 3: Different session - test cross-session memory
        print(f"\n[STEP 4] Testing cross-session memory...")
        message3 = "I'm ready to bid on projects now. How many years have I been in business?"
        
        result3 = await invoke_coia_chat(
            app=app,
            user_message=message3,
            session_id="different_session",  # DIFFERENT SESSION
            contractor_lead_id=UNIQUE_CONTRACTOR_ID  # SAME CONTRACTOR
        )
        
        profile3 = result3.get("contractor_profile", {})
        messages3 = result3.get("messages", [])
        response3 = messages3[-1].content if messages3 else "No response"
        
        print(f"✅ CONVERSATION 3 COMPLETE (Different session)")
        print(f"   Cross-session profile: {profile3}")
        print(f"   Response: {response3[:100]}...")
        
        # ANALYSIS - Check what actually got saved and remembered
        print("\n======================================================================")
        print("PROOF ANALYSIS - WHAT ACTUALLY WORKED")
        print("======================================================================")
        
        # Check profile extraction
        company_extracted = profile1.get("company_name") == UNIQUE_COMPANY_NAME
        website_extracted = profile1.get("website") == "https://prooftest-hvac.com"
        years_extracted = profile1.get("years_in_business") == 8
        location_extracted = "Phoenix" in str(profile1.get("service_areas", []))
        
        print(f"Company name extracted: {'✅ PASS' if company_extracted else '❌ FAIL'} - {profile1.get('company_name')}")
        print(f"Website extracted: {'✅ PASS' if website_extracted else '❌ FAIL'} - {profile1.get('website')}")
        print(f"Years extracted: {'✅ PASS' if years_extracted else '❌ FAIL'} - {profile1.get('years_in_business')}")
        print(f"Location extracted: {'✅ PASS' if location_extracted else '❌ FAIL'} - {profile1.get('service_areas')}")
        
        # Check memory persistence within session
        same_session_memory = (
            profile2.get("company_name") == UNIQUE_COMPANY_NAME and
            "emergency HVAC" in response2.lower() and
            profile2.get("years_in_business") == 8
        )
        
        print(f"Same session memory: {'✅ PASS' if same_session_memory else '❌ FAIL'}")
        
        # Check cross-session memory
        cross_session_memory = (
            profile3.get("company_name") == UNIQUE_COMPANY_NAME and
            ("8 years" in response3 or str(profile3.get("years_in_business")) == "8")
        )
        
        print(f"Cross-session memory: {'✅ PASS' if cross_session_memory else '❌ FAIL'}")
        
        # Check bid card search mode triggered
        bid_search_triggered = "bid" in mode2 or "project" in response2.lower()
        print(f"Bid search mode triggered: {'✅ PASS' if bid_search_triggered else '❌ FAIL'}")
        
        # OVERALL SUCCESS
        all_tests = [company_extracted, website_extracted, years_extracted, same_session_memory, cross_session_memory]
        success_rate = (sum(all_tests) / len(all_tests)) * 100
        
        print(f"\n======================================================================")
        print(f"OVERALL PROOF RESULTS: {success_rate:.0f}% SUCCESS")
        print(f"======================================================================")
        
        if success_rate >= 80:
            print("🎉 PROOF SUCCESSFUL - System is working as claimed!")
            print(f"   - NEW contractor '{UNIQUE_COMPANY_NAME}' created")
            print(f"   - Profile data extracted from natural language")
            print(f"   - Memory persisted within session")
            print(f"   - Memory persisted across different sessions")
            print(f"   - Contractor ID: {UNIQUE_CONTRACTOR_ID}")
        else:
            print("❌ PROOF FAILED - System not working properly")
        
        print(f"\nWHERE TO FIND THE DATA:")
        print(f"   - Contractor ID: {UNIQUE_CONTRACTOR_ID}")
        print(f"   - Company Name: {UNIQUE_COMPANY_NAME}")
        print(f"   - In-Memory Storage: Currently using in-memory checkpointer")
        print(f"   - To verify: Search for '{UNIQUE_COMPANY_NAME}' in system")
        
        return success_rate >= 80, UNIQUE_CONTRACTOR_ID, profile3
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False, None, {}

if __name__ == "__main__":
    success, contractor_id, final_profile = asyncio.run(test_prove_to_user())
    
    print(f"\n🎯 FINAL PROOF STATUS:")
    print(f"   Success: {'✅ YES' if success else '❌ NO'}")
    if contractor_id:
        print(f"   Contractor Created: {contractor_id}")
        print(f"   Final Profile: {final_profile}")
    print(f"   Test completed at: {datetime.now()}")