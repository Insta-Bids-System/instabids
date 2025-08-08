#!/usr/bin/env python
"""
MEMORY PERSISTENCE TEST - SINGLE PROCESS
Tests memory persistence within same app instance (in-memory checkpointer)
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
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

from agents.coia.unified_graph import create_unified_coia_system, invoke_coia_chat

async def test_memory_single_process():
    """Test memory persistence within single process"""
    print("======================================================================")
    print("MEMORY PERSISTENCE TEST - SINGLE PROCESS")
    print("Testing in-memory checkpointer within same app instance")
    print("======================================================================")
    
    try:
        # Create COIA system ONCE
        print("\n[SETUP] Creating COIA system...")
        app = await create_unified_coia_system()
        print("COIA system created - using same app instance for all conversations")
        
        contractor_id = "memory_test_contractor"
        
        # CONVERSATION 1: Create profile
        print(f"\n[CONVERSATION 1] Creating contractor profile...")
        result1 = await invoke_coia_chat(
            app=app,  # SAME APP INSTANCE
            user_message="Hi, I'm Mike from MemoryTest HVAC. We've been in business for 12 years and specialize in emergency AC repairs in Dallas area.",
            session_id="test_session_1",
            contractor_lead_id=contractor_id
        )
        
        profile1 = result1.get("contractor_profile", {})
        messages1 = result1.get("messages", [])
        response1 = messages1[-1].content if messages1 else "No response"
        
        print(f"Profile created: {profile1}")
        print(f"Response: {response1[:100]}...")
        
        # CONVERSATION 2: Test memory - different session, same contractor
        print(f"\n[CONVERSATION 2] Testing memory (different session, same contractor)...")
        result2 = await invoke_coia_chat(
            app=app,  # SAME APP INSTANCE
            user_message="What's my company name and how many years have we been in business?",
            session_id="test_session_2",  # DIFFERENT session
            contractor_lead_id=contractor_id  # SAME contractor
        )
        
        profile2 = result2.get("contractor_profile", {})
        messages2 = result2.get("messages", [])
        response2 = messages2[-1].content if messages2 else "No response"
        
        print(f"Remembered profile: {profile2}")
        print(f"Memory response: {response2}")
        
        # CONVERSATION 3: Ask specific question to test memory
        print(f"\n[CONVERSATION 3] Testing specific memory recall...")
        result3 = await invoke_coia_chat(
            app=app,  # SAME APP INSTANCE
            user_message="I'm looking for emergency AC projects. Do you remember what I specialize in?",
            session_id="test_session_3",  # DIFFERENT session again
            contractor_lead_id=contractor_id  # SAME contractor
        )
        
        messages3 = result3.get("messages", [])
        response3 = messages3[-1].content if messages3 else "No response"
        
        print(f"Specialization recall: {response3}")
        
        # ANALYSIS
        print("\n======================================================================")
        print("MEMORY ANALYSIS")
        print("======================================================================")
        
        # Check if profile was extracted in conversation 1
        company_extracted = profile1.get("company_name") == "Memorytest Hvac"
        years_extracted = profile1.get("years_in_business") == 12
        location_extracted = "Dallas" in str(profile1.get("service_areas", []))
        
        print(f"Initial profile extraction:")
        print(f"  Company: {'PASS' if company_extracted else 'FAIL'} - {profile1.get('company_name')}")
        print(f"  Years: {'PASS' if years_extracted else 'FAIL'} - {profile1.get('years_in_business')}")
        print(f"  Location: {'PASS' if location_extracted else 'FAIL'} - {profile1.get('service_areas')}")
        
        # Check if memory persisted
        has_company_in_response2 = "MemoryTest" in response2 or "memorytest" in response2.lower()
        has_years_in_response2 = "12" in response2
        
        has_emergency_in_response3 = "emergency" in response3.lower()
        has_ac_in_response3 = "ac" in response3.lower() or "air conditioning" in response3.lower()
        
        print(f"\nMemory persistence:")
        print(f"  Company in response 2: {'PASS' if has_company_in_response2 else 'FAIL'}")
        print(f"  Years in response 2: {'PASS' if has_years_in_response2 else 'FAIL'}")
        print(f"  Emergency specialty in response 3: {'PASS' if has_emergency_in_response3 else 'FAIL'}")
        print(f"  AC specialty in response 3: {'PASS' if has_ac_in_response3 else 'FAIL'}")
        
        # Overall success
        extraction_success = company_extracted and years_extracted
        memory_success = (has_company_in_response2 or has_years_in_response2) and has_emergency_in_response3
        
        overall_success = extraction_success and memory_success
        
        print(f"\n======================================================================")
        print(f"FINAL RESULT: {'SUCCESS' if overall_success else 'PARTIAL/FAILED'}")
        print(f"======================================================================")
        
        if overall_success:
            print("PROOF: Memory persistence working within same process!")
            print("- Profile extracted from natural language")
            print("- Memory persisted across different session IDs")
            print("- Same contractor_lead_id maintains context")
            print("- In-memory checkpointer working correctly")
        elif extraction_success:
            print("PARTIAL: Profile extraction works, memory persistence needs work")
        else:
            print("FAILED: Core functionality not working")
        
        print(f"\nMemory Storage: In-memory checkpointer (Supabase fallback)")
        print(f"Contractor ID: {contractor_id}")
        print(f"Thread ID used: chat_{contractor_id}")
        
        return overall_success
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_memory_single_process())
    print(f"\nFINAL STATUS: {'SUCCESS' if success else 'FAILED'}")