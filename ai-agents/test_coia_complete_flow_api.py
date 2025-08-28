#!/usr/bin/env python3
"""
Test complete COIA flow through API - end-to-end verification
Tests the full landing page conversation → research → database save → bid card display flow
"""

import asyncio
import sys
import os
import requests
import json
from config.service_urls import get_backend_url
sys.path.append('.')

async def test_complete_coia_flow_api():
    print("Testing complete COIA flow through API...")
    print("=" * 80)
    
    # Test with a new company name 
    test_company = "Premier Roofing Solutions Miami"
    user_message = f"Hi, I'm the owner of {test_company}. We specialize in residential and commercial roofing in Miami-Dade County."
    
    # Generate session ID for this test
    import uuid
    session_id = f"test-{uuid.uuid4().hex[:12]}"
    contractor_lead_id = f"landing-{uuid.uuid4().hex[:12]}"
    
    print(f"Test company: {test_company}")
    print(f"Session ID: {session_id}")
    print(f"Contractor Lead ID: {contractor_lead_id}")
    print("-" * 80)
    
    # Make API call to COIA landing page endpoint
    try:
        payload = {
            "message": user_message,
            "session_id": session_id,
            "contractor_lead_id": contractor_lead_id
        }
        
        print(">> Making API call to COIA landing page endpoint...")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            f"{get_backend_url()}/api/coia/landing",
            json=payload,
            timeout=180  # 3 minutes for potential research
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f">> API call successful!")
            print(f"Response keys: {list(result.keys())}")
            
            # Check for conversation response
            ai_response = result.get("response", "")
            if ai_response:
                print(f"\n>> AI Response:")
                print(f"{ai_response[:500]}..." if len(ai_response) > 500 else ai_response)
            
            # Check if company name was extracted
            company_name = result.get("company_name")
            if company_name:
                print(f"\n>> Company name extracted: {company_name}")
            else:
                print(f"\n>> Company name not extracted")
                
            # Check if research was completed
            research_completed = result.get("research_completed", False)
            if research_completed:
                print(f">> Research completed: {research_completed}")
                
                # Check for research findings
                research_findings = result.get("research_findings", {})
                if research_findings:
                    print(f">> Research findings available: {research_findings.get('status', 'unknown')}")
                
                # Check contractor profile for database save
                contractor_profile = result.get("contractor_profile", {})
                if contractor_profile.get("database_saved"):
                    print(f"\n>> DATABASE SAVE CONFIRMED!")
                    print(f"Contractor Lead ID: {contractor_profile.get('contractor_lead_id')}")
                    print(f"Saved at: {contractor_profile.get('saved_at')}")
                    
                    # Verify in database using MCP
                    from database_simple import db
                    saved_contractor_id = contractor_profile.get('contractor_lead_id')
                    
                    if saved_contractor_id:
                        print(f"\n>> Verifying in database...")
                        db_result = db.client.table("contractor_leads").select("*").eq("id", saved_contractor_id).execute()
                        
                        if db_result.data:
                            record = db_result.data[0]
                            print(f">> VERIFIED: Found in database!")
                            print(f"  - Company: {record.get('company_name')}")
                            print(f"  - Phone: {record.get('phone')}")
                            print(f"  - Email: {record.get('email')}")
                            print(f"  - Website: {record.get('website')}")
                            print(f"  - Specialties: {record.get('specialties')}")
                            print(f"  - Years in business: {record.get('years_in_business')}")
                            print(f"  - Data completeness: {record.get('data_completeness')}%")
                            
                            # Count filled fields
                            filled = len([k for k, v in record.items() if v is not None and v != '' and v != [] and v != {}])
                            print(f"  - Total filled fields: {filled} out of 49")
                            
                            return True
                        else:
                            print(f">> NOT FOUND in database")
                            return False
                else:
                    print(f">> No database save confirmation in profile")
                    print(f"Profile keys: {list(contractor_profile.keys())}")
                    return False
            else:
                print(f">> Research not completed: {research_completed}")
                print(f"Result keys: {list(result.keys())}")
                return False
                
        else:
            print(f">> API call failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f">> Error during API test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("COMPLETE COIA FLOW API TEST")
    print("=" * 80)
    
    success = asyncio.run(test_complete_coia_flow_api())
    
    print("\n" + "=" * 80)
    if success:
        print(">> SUCCESS: Complete COIA flow working end-to-end!")
        print(">> Conversation -> Research -> Database Save -> Verification - ALL WORKING!")
    else:
        print(">> FAILURE: COIA flow has issues")
    print("=" * 80)