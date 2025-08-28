#!/usr/bin/env python3
"""
REAL END-TO-END TEST: COIA with REAL Tavily API (not simulations)
This test proves the integration actually works with real API calls
"""
import asyncio
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.coia.tools import COIATools
from database_simple import db

async def test_real_tavily_integration():
    """Test COIA with REAL Tavily API calls"""
    print("\n" + "="*60)
    print("REAL TAVILY API INTEGRATION TEST")
    print("This uses ACTUAL API calls, not simulations")
    print("="*60 + "\n")
    
    # Initialize tools
    tools = COIATools()
    
    # Test with a real company
    test_company = "JM Holiday Lighting"
    test_location = "Fort Lauderdale, FL"
    
    print(f"[TEST] Researching real company: {test_company}")
    print(f"[TEST] Location: {test_location}\n")
    
    try:
        # 1. Test web search with REAL Tavily API
        print("[STEP 1] Calling web_search_company with REAL Tavily API...")
        web_data = await tools.web_search_company(test_company, test_location)
        
        if web_data:
            print("[SUCCESS] Web search returned data!")
            
            # Check if Tavily was actually used
            if "tavily_discovery_data" in web_data:
                tavily_data = web_data["tavily_discovery_data"]
                
                # Check for proof of real API usage
                if tavily_data.get("api_used") == "REAL_TAVILY_API":
                    print("[VERIFIED] REAL Tavily API was used (not simulation)")
                    
                    discovered_pages = tavily_data.get("discovered_pages", [])
                    print(f"[RESULT] Discovered {len(discovered_pages)} pages")
                    
                    for i, page in enumerate(discovered_pages[:5], 1):
                        print(f"  {i}. {page.get('url', 'Unknown URL')}")
                        print(f"     Type: {page.get('type', 'unknown')}")
                        print(f"     Priority: {page.get('priority', 'unknown')}")
                else:
                    print("[WARNING] Tavily data present but no API confirmation")
            else:
                print("[WARNING] No Tavily discovery data in response")
            
            # 2. Build comprehensive profile
            print("\n[STEP 2] Building comprehensive contractor profile...")
            profile = await tools.build_contractor_profile(
                test_company,
                web_data.get("google_data"),
                web_data,
                None  # No license data for now
            )
            
            if profile:
                print(f"[SUCCESS] Profile created!")
                print(f"  Completeness: {profile.get('data_completeness', 0):.1f}%")
                print(f"  Lead Score: {profile.get('lead_score', 0):.1f}")
                
                # Count filled fields
                filled_count = sum(1 for k, v in profile.items() 
                                 if v and k not in ['raw_data', 'enrichment_data'])
                print(f"  Fields Filled: {filled_count}/66")
                
                # Show some key fields
                print("\n[KEY FIELDS]:")
                key_fields = [
                    "company_name", "email", "phone", "website",
                    "rating", "review_count", "years_in_business",
                    "estimated_employees", "specialties", "service_areas"
                ]
                
                for field in key_fields:
                    value = profile.get(field)
                    if value:
                        print(f"  {field}: {value}")
                
                # 3. Create contractor account (without password fields)
                print("\n[STEP 3] Creating contractor account...")
                account_result = await tools.create_contractor_account(profile)
                
                if account_result.get("success"):
                    contractor_id = account_result.get("account", {}).get("id")
                    print(f"[SUCCESS] Contractor created with ID: {contractor_id}")
                    
                    # 4. Verify in database
                    print("\n[STEP 4] Verifying in database...")
                    contractor = db.client.table("contractors").select("*").eq("id", contractor_id).execute()
                    
                    if contractor.data:
                        print("[SUCCESS] Contractor found in database!")
                        
                        # Check no password fields
                        if 'password' in contractor.data[0] or 'temporary_password' in contractor.data[0]:
                            print("[ERROR] Password fields found in database!")
                        else:
                            print("[VERIFIED] No password fields in database")
                        
                        # Show database fields
                        print("\n[DATABASE FIELDS]:")
                        db_data = contractor.data[0]
                        for field in ["company_name", "email", "tier", "availability_status", "source"]:
                            print(f"  {field}: {db_data.get(field)}")
                    else:
                        print("[ERROR] Contractor not found in database")
                else:
                    print(f"[ERROR] Failed to create account: {account_result.get('error')}")
            else:
                print("[ERROR] Failed to build profile")
        else:
            print("[ERROR] Web search returned no data")
            
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("END OF TEST")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_real_tavily_integration())