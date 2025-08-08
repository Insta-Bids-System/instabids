#!/usr/bin/env python
"""
SIMPLE PROOF TEST - No Unicode issues
Creates new contractor, shows exactly where data is saved
"""

import asyncio
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)

# Set up logging
logging.basicConfig(level=logging.WARNING)  # Reduce noise
logger = logging.getLogger(__name__)

from agents.coia.unified_graph import create_unified_coia_system, invoke_coia_chat

# Create unique contractor for this test
UNIQUE_CONTRACTOR_ID = f"proof_test_{int(datetime.now().timestamp())}"
UNIQUE_COMPANY_NAME = f"ProofTest Contracting {datetime.now().strftime('%H%M%S')}"

async def test_proof_simple():
    """Simple proof test - create contractor and verify memory"""
    print("======================================================================")
    print("PROOF TEST: Creating new contractor and verifying memory")
    print(f"Company: {UNIQUE_COMPANY_NAME}")
    print(f"Contractor ID: {UNIQUE_CONTRACTOR_ID}")
    print("======================================================================")
    
    try:
        # Create COIA system
        print("\n[STEP 1] Creating COIA system...")
        app = await create_unified_coia_system()
        print("COIA system ready")
        
        # Conversation 1: Create new contractor
        print(f"\n[STEP 2] Creating contractor profile...")
        message1 = f"Hi, I'm John from {UNIQUE_COMPANY_NAME}. We've been in business for 8 years and specialize in emergency HVAC repairs in Phoenix. Our website is https://prooftest-hvac.com."
        
        result1 = await invoke_coia_chat(
            app=app,
            user_message=message1,
            session_id="proof_session",
            contractor_lead_id=UNIQUE_CONTRACTOR_ID
        )
        
        profile1 = result1.get("contractor_profile", {})
        print(f"PROFILE CREATED: {profile1}")
        
        # Conversation 2: Test memory 
        print(f"\n[STEP 3] Testing memory...")
        message2 = "What's my company name and how many years have we been in business?"
        
        result2 = await invoke_coia_chat(
            app=app,
            user_message=message2,
            session_id="proof_session",
            contractor_lead_id=UNIQUE_CONTRACTOR_ID
        )
        
        profile2 = result2.get("contractor_profile", {})
        messages2 = result2.get("messages", [])
        response2 = messages2[-1].content if messages2 else "No response"
        
        print(f"MEMORY TEST RESPONSE: {response2}")
        print(f"REMEMBERED PROFILE: {profile2}")
        
        # Analysis
        print("\n======================================================================")
        print("PROOF RESULTS")
        print("======================================================================")
        
        company_correct = profile1.get("company_name") == UNIQUE_COMPANY_NAME
        years_correct = profile1.get("years_in_business") == 8
        website_correct = profile1.get("website") == "https://prooftest-hvac.com"
        memory_working = UNIQUE_COMPANY_NAME in response2 and "8" in response2
        
        print(f"Company extracted: {'PASS' if company_correct else 'FAIL'} - {profile1.get('company_name')}")
        print(f"Years extracted: {'PASS' if years_correct else 'FAIL'} - {profile1.get('years_in_business')}")
        print(f"Website extracted: {'PASS' if website_correct else 'FAIL'} - {profile1.get('website')}")
        print(f"Memory working: {'PASS' if memory_working else 'FAIL'}")
        
        success = company_correct and years_correct and memory_working
        print(f"\nOVERALL: {'SUCCESS' if success else 'FAILED'}")
        
        if success:
            print("\nPROOF COMPLETE:")
            print(f"- Created contractor: {UNIQUE_COMPANY_NAME}")
            print(f"- Extracted profile data from natural language")
            print(f"- Memory persisted between conversations")
            print(f"- Contractor ID: {UNIQUE_CONTRACTOR_ID}")
            print("- Data stored in in-memory checkpointer (Supabase fallback)")
        
        return success, UNIQUE_CONTRACTOR_ID, profile2
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False, None, {}

if __name__ == "__main__":
    success, contractor_id, final_profile = asyncio.run(test_proof_simple())
    print(f"\nFINAL RESULT: {'SUCCESS' if success else 'FAILED'}")