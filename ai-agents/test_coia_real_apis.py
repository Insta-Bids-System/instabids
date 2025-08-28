"""
Test COIA Tools with Real API Keys from .env file
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Load .env from parent directory
load_dotenv('../.env')

# Set environment variables for this test
os.environ['TAVILY_API_KEY'] = os.getenv('TAVILY_API_KEY', '')
os.environ['USE_TAVILY'] = 'true'
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '')
os.environ['GOOGLE_MAPS_API_KEY'] = os.getenv('GOOGLE_MAPS_API_KEY', '')
os.environ['WRITE_LEADS_ON_RESEARCH'] = 'false'

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

async def test_coia_real_apis():
    print("=" * 60)
    print("COIA TOOLS - REAL API TESTING")
    print("=" * 60)
    
    # Import tools after setting environment
    try:
        from agents.coia.tools import coia_tools
        print("✅ COIA Tools imported successfully")
    except Exception as e:
        print(f"❌ FAILED to import COIA Tools: {e}")
        return False
    
    # Check environment
    print("\nENVIRONMENT CHECK:")
    print(f"  TAVILY_API_KEY: {'SET' if os.getenv('TAVILY_API_KEY') else 'NOT SET'}")
    print(f"  USE_TAVILY: {os.getenv('USE_TAVILY')}")
    print(f"  OPENAI_API_KEY: {'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET'}")
    print(f"  GOOGLE_MAPS_API_KEY: {'SET' if os.getenv('GOOGLE_MAPS_API_KEY') else 'NOT SET'}")
    
    print("\n" + "=" * 60)
    print("REAL API TESTS")
    print("=" * 60)
    
    # TEST 1: Google Business Search (Real API)
    print("\n🔍 TEST 1: Google Business Search with Real API")
    try:
        result = await coia_tools.search_google_business("JM Holiday Lighting", "FL")
        if result and result.get("company_name"):
            print(f"  ✅ SUCCESS: Found {result.get('company_name')}")
            print(f"     Phone: {result.get('phone', 'N/A')}")
            print(f"     Website: {result.get('website', 'N/A')}")
            print(f"     Address: {result.get('address', 'N/A')}")
        else:
            print(f"  ❌ FAILED: No valid company data returned")
            print(f"     Result: {result}")
    except Exception as e:
        print(f"  ❌ FAILED: Exception - {e}")
    
    # TEST 2: Web Research with Real Tavily API
    print("\n🌐 TEST 2: Web Research with Real Tavily API")
    try:
        result = await coia_tools.web_search_company("JM Holiday Lighting", "FL")
        if result and result.get("extracted_info"):
            print(f"  ✅ SUCCESS: Extracted data from web research")
            extracted = result["extracted_info"]
            print(f"     Services: {extracted.get('services', [])}")
            print(f"     Description: {extracted.get('description', 'N/A')[:100]}...")
            print(f"     Contact Info: {extracted.get('contact_info', {})}")
            print(f"     Data Sources: {len(result.get('data_sources', []))} sources")
        else:
            print(f"  ❌ FAILED: No extracted info returned")
            print(f"     Result keys: {list(result.keys()) if result else 'None'}")
    except Exception as e:
        print(f"  ❌ FAILED: Exception - {e}")
    
    # TEST 3: Business Research (Combined APIs)
    print("\n🧠 TEST 3: Full Business Research (Google + Tavily + OpenAI)")
    try:
        result = await coia_tools.research_business("Tropical Turf Solutions", "33442")
        if result and result.get("success"):
            print(f"  ✅ SUCCESS: Complete business research completed")
            print(f"     Company: {result.get('company_name', 'N/A')}")
            print(f"     Research Success: {result.get('success')}")
            print(f"     Data Quality: {result.get('data_quality', 'N/A')}")
        else:
            print(f"  ❌ FAILED: Business research unsuccessful")
            print(f"     Result: {result}")
    except Exception as e:
        print(f"  ❌ FAILED: Exception - {e}")
    
    print("\n" + "=" * 60)
    print("REAL API TEST SUMMARY")
    print("=" * 60)
    print("These tests verify if COIA is actually making real API calls")
    print("to external services (Tavily, OpenAI, Google Maps) vs using")
    print("fallback/simulation methods.")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_coia_real_apis())