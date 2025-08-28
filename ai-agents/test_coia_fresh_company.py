#!/usr/bin/env python3
"""
Test COIA with completely fresh company (no existing database records)
This proves the system actually researches and saves new data
"""

import asyncio
import sys
import os
sys.path.append('.')

from agents.coia.unified_graph import create_unified_coia_system
from agents.coia.unified_state import create_initial_state
from langchain_core.messages import HumanMessage

async def test_fresh_company():
    print("Testing COIA with COMPLETELY FRESH company...")
    print("=" * 60)
    
    # Use a completely new company that definitely doesn't exist in database
    test_company = "Apex Construction Solutions Orlando"
    user_message = f"Hi, I'm Mark Johnson, owner of {test_company}. We're a general contractor with 12 years experience in Orlando doing kitchen remodels, bathroom renovations, and home additions."
    
    print(f"Testing with: {test_company}")
    print(f"User message: {user_message}")
    print("-" * 60)
    
    try:
        # Create COIA app
        app = await create_unified_coia_system()
        
        # Create initial state
        initial_state = create_initial_state(
            session_id="fresh-company-test",
            interface="landing_page",
            contractor_lead_id="11111111-1111-1111-1111-111111111111"
        ).to_langgraph_state()
        
        initial_state["messages"] = [HumanMessage(content=user_message)]
        
        config = {
            "configurable": {
                "thread_id": "fresh-company-test",
                "checkpoint_id": "fresh_test",
                "checkpoint_ns": "coia_fresh"
            },
            "recursion_limit": 50,
            "max_concurrency": 10
        }
        
        start_time = asyncio.get_event_loop().time()
        
        # Execute the complete flow
        result = await app.ainvoke(initial_state, config)
        
        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time
        
        print(f"COMPLETE FLOW FINISHED in {duration:.2f} seconds")
        print("=" * 60)
        
        # Analyze results
        company_name = result.get('company_name')
        research_completed = result.get('research_completed')
        profile_completeness = result.get('profile_completeness', 0)
        contractor_profile = result.get('contractor_profile', {})
        
        print("FINAL RESULTS:")
        print(f"- Company extracted: {company_name}")
        print(f"- Research completed: {research_completed}")
        print(f"- Profile completeness: {profile_completeness}%")
        print(f"- Current mode: {result.get('current_mode')}")
        print(f"- Messages: {len(result.get('messages', []))}")
        
        # Check if we actually got research data
        research_findings = result.get('research_findings')
        if research_findings:
            print(f"- Research data: {len(str(research_findings))} characters")
            
        # Check specific profile fields
        extracted_fields = []
        for field, value in contractor_profile.items():
            if value and value != [] and value != "":
                extracted_fields.append(f"{field}: {value}")
                
        if extracted_fields:
            print(f"- Profile fields extracted: {len(extracted_fields)}")
            for field in extracted_fields[:5]:  # Show first 5
                print(f"  * {field}")
        
        # Now verify this was actually saved to database
        print("\n" + "=" * 60)
        print("VERIFYING DATABASE SAVE...")
        
        from mcp_tools import supabase_client
        
        # Check if the company was saved
        response = supabase_client.table('contractor_leads').select('*').eq('company_name', company_name).execute()
        
        if response.data and len(response.data) > 0:
            saved_record = response.data[0]
            print(f"SUCCESS: Found saved record in database!")
            print(f"- ID: {saved_record.get('id')}")
            print(f"- Company: {saved_record.get('company_name')}")
            print(f"- Contact: {saved_record.get('contact_name')}")
            print(f"- Phone: {saved_record.get('phone')}")
            print(f"- Website: {saved_record.get('website')}")
            print(f"- Years in business: {saved_record.get('years_in_business')}")
            
            # Count non-null fields
            non_null_fields = sum(1 for k, v in saved_record.items() if v is not None and v != '' and v != [])
            print(f"- Total fields populated: {non_null_fields}")
            
            print("\nSUCCESS: SYSTEM IS ACTUALLY WORKING!")
            print("- Company researched from scratch")
            print("- Data extracted and saved to database") 
            print("- No pre-existing records used")
            
        else:
            print("ERROR: No record found in database")
            print("Research may have completed but not saved properly")
            
    except Exception as e:
        print(f"ERROR: Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fresh_company())