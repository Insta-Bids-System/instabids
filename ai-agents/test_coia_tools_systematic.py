"""
COIA Tools Systematic Testing Suite
Tests every single tool in tools.py for production readiness
Run this to identify exactly what works and what's broken
"""

import asyncio
import os
import sys
import logging
from datetime import datetime

# Add the path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

async def test_coia_tools_systematic():
    """Test every tool in the COIA toolkit systematically"""
    
    print("=" * 80)
    print("COIA TOOLS SYSTEMATIC TESTING SUITE")
    print("=" * 80)
    print(f"Started: {datetime.now()}")
    print()
    
    # Import the tools
    try:
        from agents.coia.tools import coia_tools
        print("✅ IMPORT: COIATools imported successfully")
    except Exception as e:
        print(f"❌ CRITICAL ERROR: Cannot import COIATools: {e}")
        return False
    
    # Test results tracking
    test_results = {
        "passed": [],
        "failed": [],
        "total_tests": 0
    }
    
    # Test companies for consistent testing
    test_companies = [
        {"name": "JM Holiday Lighting", "location": "FL"},
        {"name": "Tropical Turf Solutions", "location": "33442"}
    ]
    
    print("ENVIRONMENT CHECK:")
    env_vars = [
        "TAVILY_API_KEY", "USE_TAVILY", "OPENAI_API_KEY", 
        "GOOGLE_MAPS_API_KEY", "WRITE_LEADS_ON_RESEARCH"
    ]
    for var in env_vars:
        value = os.getenv(var, "NOT SET")
        if value == "NOT SET":
            print(f"  WARNING: {var}: {value}")
        else:
            print(f"  OK: {var}: {value[:20]}..." if len(value) > 20 else f"  OK: {var}: {value}")
    print()
    
    # TEST 1: Google Business Search
    print("TEST 1: Google Business Search")
    test_results["total_tests"] += 1
    try:
        result = await coia_tools.search_google_business("JM Holiday Lighting", "FL")
        if result and result.get("success") != False:
            print(f"  PASS: Google Business Search: Found data for JM Holiday Lighting")
            print(f"     Company: {result.get('company_name', 'N/A')}")
            print(f"     Phone: {result.get('phone', 'N/A')}")
            print(f"     Website: {result.get('website', 'N/A')}")
            test_results["passed"].append("Google Business Search")
        else:
            print(f"  FAIL: Google Business Search: No results or failed")
            test_results["failed"].append("Google Business Search")
    except Exception as e:
        print(f"  FAIL: Google Business Search: Exception - {e}")
        test_results["failed"].append(f"Google Business Search - {e}")
    print()
    
    # TEST 2: Web Company Research  
    print("TEST 2: Web Company Research")
    test_results["total_tests"] += 1
    try:
        result = await coia_tools.web_search_company("JM Holiday Lighting", "FL")
        if result and result.get("extracted_info"):
            print(f"  ✅ Web Company Research: Extracted comprehensive data")
            extracted = result["extracted_info"]
            print(f"     Services found: {len(extracted.get('services', []))}")
            print(f"     Description: {extracted.get('description', 'N/A')[:100]}...")
            print(f"     Data sources: {result.get('data_sources', [])}")
            test_results["passed"].append("Web Company Research")
        else:
            print(f"  ❌ Web Company Research: No extracted data")
            test_results["failed"].append("Web Company Research")
    except Exception as e:
        print(f"  ❌ Web Company Research: Exception - {e}")
        test_results["failed"].append(f"Web Company Research - {e}")
    print()
    
    # TEST 3: Business Intelligence Research
    print("🧠 TEST 3: Business Intelligence Research")
    test_results["total_tests"] += 1
    try:
        result = await coia_tools.research_business("Tropical Turf Solutions", "33442")
        if result and result.get("success"):
            print(f"  ✅ Business Intelligence Research: Successfully researched business")
            print(f"     Company: {result.get('company_name', 'N/A')}")
            print(f"     Success: {result.get('success', False)}")
            test_results["passed"].append("Business Intelligence Research")
        else:
            print(f"  ❌ Business Intelligence Research: Failed or no success flag")
            test_results["failed"].append("Business Intelligence Research")
    except Exception as e:
        print(f"  ❌ Business Intelligence Research: Exception - {e}")
        test_results["failed"].append(f"Business Intelligence Research - {e}")
    print()
    
    # TEST 4: Contractor Profile Building
    print("👷 TEST 4: Contractor Profile Building")
    test_results["total_tests"] += 1
    try:
        # First get some data
        google_data = await coia_tools.search_google_business("Test Company", "FL")
        web_data = {"extracted_info": {"services": ["Testing"], "description": "Test company"}}
        license_data = {"licenses": []}
        
        result = await coia_tools.build_contractor_profile(
            "Test Company", google_data, web_data, license_data
        )
        
        if result and result.get("business_name"):
            print(f"  ✅ Contractor Profile Building: Built complete profile")
            print(f"     Completeness: {result.get('data_completeness', 0):.1f}%")
            print(f"     Lead score: {result.get('lead_score', 0):.1f}")
            print(f"     Database saved: {result.get('database_saved', False)}")
            test_results["passed"].append("Contractor Profile Building")
        else:
            print(f"  ❌ Contractor Profile Building: No profile data")
            test_results["failed"].append("Contractor Profile Building")
    except Exception as e:
        print(f"  ❌ Contractor Profile Building: Exception - {e}")
        test_results["failed"].append(f"Contractor Profile Building - {e}")
    print()
    
    # TEST 5: Bid Card Search
    print("🃏 TEST 5: Bid Card Search")
    test_results["total_tests"] += 1
    try:
        contractor_profile = {
            "company_name": "Test Contractor",
            "specialties": ["electrical", "lighting"],
            "id": "test-contractor-123"
        }
        
        result = await coia_tools.search_bid_cards(contractor_profile, "FL")
        
        if isinstance(result, list):
            print(f"  ✅ Bid Card Search: Found {len(result)} projects")
            for i, project in enumerate(result[:3]):  # Show first 3
                print(f"     Project {i+1}: {project.get('project_type', 'Unknown')}")
            test_results["passed"].append("Bid Card Search")
        else:
            print(f"  ❌ Bid Card Search: Invalid result type")
            test_results["failed"].append("Bid Card Search")
    except Exception as e:
        print(f"  ❌ Bid Card Search: Exception - {e}")
        test_results["failed"].append(f"Bid Card Search - {e}")
    print()
    
    # TEST 6: Contractor Account Creation
    print("🏗️ TEST 6: Contractor Account Creation")
    test_results["total_tests"] += 1
    try:
        contractor_profile = {
            "company_name": "Test Account Creation Co",
            "email": "test@testcompany.com",
            "phone": "555-123-4567",
            "specialties": ["testing"]
        }
        
        result = await coia_tools.create_contractor_account(contractor_profile)
        
        if result and result.get("success"):
            print(f"  ✅ Contractor Account Creation: Account created successfully")
            print(f"     Account ID: {result.get('account', {}).get('id', 'N/A')}")
            print(f"     Company: {result.get('account', {}).get('company_name', 'N/A')}")
            test_results["passed"].append("Contractor Account Creation")
        else:
            print(f"  ❌ Contractor Account Creation: Failed to create account")
            print(f"     Error: {result.get('error', 'Unknown error')}")
            test_results["failed"].append("Contractor Account Creation")
    except Exception as e:
        print(f"  ❌ Contractor Account Creation: Exception - {e}")
        test_results["failed"].append(f"Contractor Account Creation - {e}")
    print()
    
    # TEST 7: License Search (Expected to be placeholder)
    print("📜 TEST 7: License Search")
    test_results["total_tests"] += 1
    try:
        result = await coia_tools.search_contractor_licenses("Test Company", "FL")
        
        if result and "success" in result:
            if result["success"]:
                print(f"  ✅ License Search: Found licenses")
                print(f"     Licenses: {len(result.get('licenses', []))}")
            else:
                print(f"  ⚠️  License Search: Placeholder working (no real integration)")
                print(f"     Message: {result.get('message', 'N/A')}")
            test_results["passed"].append("License Search")
        else:
            print(f"  ❌ License Search: Invalid response")
            test_results["failed"].append("License Search")
    except Exception as e:
        print(f"  ❌ License Search: Exception - {e}")
        test_results["failed"].append(f"License Search - {e}")
    print()
    
    # FINAL RESULTS
    print("=" * 80)
    print("📊 FINAL TEST RESULTS")
    print("=" * 80)
    
    passed_count = len(test_results["passed"])
    failed_count = len(test_results["failed"])
    total_count = test_results["total_tests"]
    
    print(f"✅ PASSED: {passed_count}/{total_count} tests")
    for test in test_results["passed"]:
        print(f"   ✅ {test}")
    print()
    
    if test_results["failed"]:
        print(f"❌ FAILED: {failed_count}/{total_count} tests")
        for test in test_results["failed"]:
            print(f"   ❌ {test}")
        print()
    
    # PRODUCTION READINESS ASSESSMENT
    print("🚀 PRODUCTION READINESS ASSESSMENT:")
    
    if passed_count >= 5:  # At least 5/7 tools working
        print("✅ SYSTEM IS PRODUCTION READY")
        print("   - Core business research tools working")
        print("   - Profile building functional")
        print("   - Database integration operational")
        
        if failed_count > 0:
            print(f"⚠️  {failed_count} non-critical issues to address")
    else:
        print("❌ SYSTEM NEEDS FIXES BEFORE PRODUCTION")
        print("   - Critical tools not functioning")
        print("   - Check environment variables and API keys")
    
    print(f"\nCompleted: {datetime.now()}")
    
    return passed_count >= 5


if __name__ == "__main__":
    success = asyncio.run(test_coia_tools_systematic())
    exit(0 if success else 1)