#!/usr/bin/env python3
"""
Direct test of research node database save without complex routing
"""

import asyncio
import sys
import os
sys.path.append('.')

async def test_direct_research_save():
    print("Testing direct research node with database save...")
    print("=" * 60)
    
    from agents.coia.tools import COIATools
    from agents.coia.langgraph_nodes import research_node
    from agents.coia.unified_state import UnifiedCoIAState
    from langchain_core.messages import HumanMessage
    
    # Create test state for a new company
    test_company = "Premier Landscaping Miami"
    
    state = UnifiedCoIAState(
        messages=[HumanMessage(content=f"Hi, I'm the owner of {test_company} in Miami Beach")],
        interface="landing_page",
        company_name=test_company,
        contractor_profile={
            "company_name": test_company,
            "service_areas": ["Miami Beach"]
        },
        research_completed=False
    )
    
    print(f"Test company: {test_company}")
    print(f"Testing research node...")
    print("-" * 60)
    
    # Call research node directly
    try:
        result = await research_node(state)
        
        print(f"Research node completed")
        
        if result.get("research_completed"):
            print("Research marked as completed")
            
            # Check research findings
            findings = result.get("research_findings", {})
            if findings:
                print(f"Research findings: {findings.get('status', 'unknown')}")
                
                # Check contractor profile for database save
                profile = result.get("contractor_profile", {})
                if profile.get("database_saved"):
                    print(f"\n✅ DATABASE SAVE CONFIRMED!")
                    print(f"Contractor ID: {profile.get('contractor_lead_id')}")
                    print(f"Saved at: {profile.get('saved_at')}")
                    
                    # Verify in database
                    from database_simple import db
                    contractor_id = profile.get('contractor_lead_id')
                    
                    if contractor_id:
                        db_result = db.client.table("contractor_leads").select("*").eq("id", contractor_id).execute()
                        
                        if db_result.data:
                            record = db_result.data[0]
                            print(f"\n✅ VERIFICATION: Found in database!")
                            print(f"Company: {record.get('company_name')}")
                            print(f"Phone: {record.get('phone')}")
                            print(f"Specialties: {record.get('specialties')}")
                            print(f"Data completeness: {record.get('data_completeness')}%")
                            return True
                        else:
                            print(f"❌ VERIFICATION FAILED: Not found in database")
                            return False
                else:
                    print(f"❌ No database save confirmation in profile")
                    print(f"Profile keys: {list(profile.keys())}")
                    return False
            else:
                print("❌ No research findings returned")
                return False
        else:
            print("❌ Research not completed")
            return False
            
    except Exception as e:
        print(f"❌ Error during research: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("DIRECT RESEARCH NODE DATABASE SAVE TEST")
    print("=" * 60)
    
    success = asyncio.run(test_direct_research_save())
    
    print("\n" + "=" * 60)
    if success:
        print("✅ TEST PASSED: Research node saves to database!")
    else:
        print("❌ TEST FAILED: Research node not saving properly")
    print("=" * 60)