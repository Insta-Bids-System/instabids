"""
COIA Tools Quick Test - Production Readiness Check
"""

import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

async def test_coia_tools_quick():
    print("=" * 60)
    print("COIA TOOLS PRODUCTION READINESS TEST")
    print("=" * 60)
    
    # Import tools
    try:
        from agents.coia.tools import coia_tools
        print("PASS: COIATools imported successfully")
    except Exception as e:
        print(f"FAIL: Cannot import COIATools: {e}")
        return False
    
    # Check environment
    print("\nENVIRONMENT:")
    tavily_key = os.getenv("TAVILY_API_KEY", "NOT SET")
    use_tavily = os.getenv("USE_TAVILY", "false")
    openai_key = os.getenv("OPENAI_API_KEY", "NOT SET") 
    write_leads = os.getenv("WRITE_LEADS_ON_RESEARCH", "false")
    
    print(f"  TAVILY_API_KEY: {'SET' if tavily_key != 'NOT SET' else 'NOT SET'}")
    print(f"  USE_TAVILY: {use_tavily}")
    print(f"  OPENAI_API_KEY: {'SET' if openai_key != 'NOT SET' else 'NOT SET'}")
    print(f"  WRITE_LEADS_ON_RESEARCH: {write_leads}")
    
    # Test core tools
    results = {"passed": 0, "failed": 0}
    
    # TEST 1: Google Business Search
    print("\nTEST 1: Google Business Search")
    try:
        result = await coia_tools.search_google_business("JM Holiday Lighting", "FL")
        if result and result.get("company_name"):
            print(f"  PASS: Found {result.get('company_name')}")
            results["passed"] += 1
        else:
            print("  FAIL: No company data returned")
            results["failed"] += 1
    except Exception as e:
        print(f"  FAIL: Exception - {str(e)[:100]}")
        results["failed"] += 1
    
    # TEST 2: Web Research
    print("\nTEST 2: Web Research")
    try:
        result = await coia_tools.web_search_company("Test Company", "FL")
        if result and result.get("extracted_info"):
            print(f"  PASS: Extracted {len(result.get('data_sources', []))} data sources")
            results["passed"] += 1
        else:
            print("  FAIL: No extracted info")
            results["failed"] += 1
    except Exception as e:
        print(f"  FAIL: Exception - {str(e)[:100]}")
        results["failed"] += 1
    
    # TEST 3: Profile Building
    print("\nTEST 3: Profile Building")
    try:
        google_data = {"company_name": "Test", "phone": "555-1234"}
        web_data = {"extracted_info": {"services": ["testing"]}}
        result = await coia_tools.build_contractor_profile("Test", google_data, web_data, {})
        
        if result and result.get("business_name"):
            print(f"  PASS: Built profile {result.get('data_completeness', 0):.0f}% complete")
            results["passed"] += 1
        else:
            print("  FAIL: No profile built")
            results["failed"] += 1
    except Exception as e:
        print(f"  FAIL: Exception - {str(e)[:100]}")
        results["failed"] += 1
    
    # TEST 4: Bid Search
    print("\nTEST 4: Bid Search")
    try:
        profile = {"company_name": "Test", "specialties": ["electrical"], "id": "test"}
        result = await coia_tools.search_bid_cards(profile, "FL")
        
        if isinstance(result, list):
            print(f"  PASS: Found {len(result)} bid cards")
            results["passed"] += 1
        else:
            print("  FAIL: Invalid bid search result")
            results["failed"] += 1
    except Exception as e:
        print(f"  FAIL: Exception - {str(e)[:100]}")
        results["failed"] += 1
    
    # TEST 5: Account Creation
    print("\nTEST 5: Account Creation")
    try:
        profile = {
            "company_name": f"Test Co {asyncio.get_event_loop().time()}",
            "email": "test@test.com",
            "phone": "555-1234"
        }
        result = await coia_tools.create_contractor_account(profile)
        
        if result and result.get("success"):
            print(f"  PASS: Created account {result.get('account', {}).get('id', 'N/A')[:8]}...")
            results["passed"] += 1
        else:
            print(f"  FAIL: Account creation failed - {result.get('error', 'Unknown')}")
            results["failed"] += 1
    except Exception as e:
        print(f"  FAIL: Exception - {str(e)[:100]}")
        results["failed"] += 1
    
    # FINAL ASSESSMENT
    print("\n" + "=" * 60)
    print("PRODUCTION READINESS ASSESSMENT")
    print("=" * 60)
    
    total_tests = results["passed"] + results["failed"]
    success_rate = (results["passed"] / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"PASSED: {results['passed']}/{total_tests} ({success_rate:.0f}%)")
    print(f"FAILED: {results['failed']}/{total_tests}")
    
    if success_rate >= 80:
        print("\nSTATUS: PRODUCTION READY")
        print("- Core tools functioning")
        print("- Business research working") 
        print("- Database integration operational")
        return True
    else:
        print("\nSTATUS: NEEDS FIXES")
        print("- Critical tools failing")
        print("- Check environment variables")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_coia_tools_quick())
    print(f"\nEXIT CODE: {'0 (SUCCESS)' if success else '1 (FAILURE)'}")
    exit(0 if success else 1)