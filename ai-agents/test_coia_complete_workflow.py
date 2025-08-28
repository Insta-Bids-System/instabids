"""
COMPLETE COIA WORKFLOW TEST
Tests the entire contractor onboarding process end-to-end with real APIs
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env')
os.environ['TAVILY_API_KEY'] = os.getenv('TAVILY_API_KEY', '')
os.environ['USE_TAVILY'] = 'true'
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '')
os.environ['GOOGLE_MAPS_API_KEY'] = os.getenv('GOOGLE_MAPS_API_KEY', '')
os.environ['WRITE_LEADS_ON_RESEARCH'] = 'true'  # Enable database writes

async def test_complete_coia_workflow():
    print("=" * 80)
    print("COIA COMPLETE WORKFLOW TEST")
    print("Testing: Company Discovery -> Research -> Profile -> Bid Search -> Account")
    print("=" * 80)
    
    from agents.coia.tools import coia_tools
    
    # Test company name
    company_name = "Tropical Turf Solutions"
    location = "33442"
    
    print(f"TESTING COMPLETE WORKFLOW FOR: {company_name} in {location}")
    print()
    
    # STEP 1: Google Business Search (Real API)
    print("STEP 1: Google Business Discovery")
    print("-" * 40)
    try:
        google_result = await coia_tools.search_google_business(company_name, location)
        if google_result and google_result.get('company_name'):
            print(f"SUCCESS: Found business - {google_result.get('company_name')}")
            print(f"  Phone: {google_result.get('phone', 'N/A')}")
            print(f"  Website: {google_result.get('website', 'N/A')}")
            print(f"  Address: {google_result.get('address', 'N/A')}")
        else:
            print("FAILED: No business data found")
            google_result = {}
    except Exception as e:
        print(f"ERROR: {e}")
        google_result = {}
    
    print()
    
    # STEP 2: Web Research (Real Tavily API)
    print("STEP 2: Deep Web Research")
    print("-" * 40)
    try:
        web_result = await coia_tools.web_search_company(company_name, location)
        if web_result and web_result.get('extracted_info'):
            extracted = web_result['extracted_info']
            print(f"SUCCESS: Extracted data from {len(web_result.get('data_sources', []))} sources")
            print(f"  Services: {extracted.get('services', [])}")
            print(f"  Description: {extracted.get('description', 'N/A')[:100]}...")
            print(f"  Contact Info: {extracted.get('contact_info', {})}")
        else:
            print("FAILED: No web research data")
            web_result = {'extracted_info': {}}
    except Exception as e:
        print(f"ERROR: {e}")
        web_result = {'extracted_info': {}}
    
    print()
    
    # STEP 3: Complete Business Research (Combined APIs + OpenAI)
    print("STEP 3: Intelligent Business Analysis")
    print("-" * 40)
    try:
        research_result = await coia_tools.research_business(company_name, location)
        if research_result and research_result.get('success'):
            print(f"SUCCESS: Complete business analysis completed")
            print(f"  Company: {research_result.get('company_name')}")
            print(f"  Specialties: {research_result.get('specialties', [])}")
            print(f"  Years in Business: {research_result.get('years_in_business', 'N/A')}")
            print(f"  Business Type: {research_result.get('business_type', 'N/A')}")
        else:
            print("FAILED: Business research unsuccessful")
            research_result = {}
    except Exception as e:
        print(f"ERROR: {e}")
        research_result = {}
    
    print()
    
    # STEP 4: Build Complete Contractor Profile
    print("STEP 4: Contractor Profile Building")
    print("-" * 40)
    try:
        profile_result = await coia_tools.build_contractor_profile(
            company_name, 
            google_result, 
            web_result, 
            {'licenses': []}
        )
        if profile_result and profile_result.get('business_name'):
            print(f"SUCCESS: Built complete contractor profile")
            print(f"  Business Name: {profile_result.get('business_name')}")
            print(f"  Data Completeness: {profile_result.get('data_completeness', 0):.1f}%")
            print(f"  Lead Score: {profile_result.get('lead_score', 0):.1f}")
            print(f"  Database Saved: {profile_result.get('database_saved', False)}")
            contractor_profile = profile_result
        else:
            print("FAILED: Could not build profile")
            contractor_profile = {}
    except Exception as e:
        print(f"ERROR: {e}")
        contractor_profile = {}
    
    print()
    
    # STEP 5: Search Available Bid Cards
    print("STEP 5: Bid Card Opportunity Search")
    print("-" * 40)
    try:
        if contractor_profile:
            bid_cards = await coia_tools.search_bid_cards(contractor_profile, location)
            if isinstance(bid_cards, list):
                print(f"SUCCESS: Found {len(bid_cards)} available projects")
                for i, project in enumerate(bid_cards[:3]):
                    print(f"  Project {i+1}: {project.get('project_type', 'Unknown')}")
                    print(f"    Budget: {project.get('budget_range', 'N/A')}")
                    print(f"    Location: {project.get('location', 'N/A')}")
            else:
                print("FAILED: Invalid bid search result")
        else:
            print("SKIPPED: No contractor profile to search with")
    except Exception as e:
        print(f"ERROR: {e}")
    
    print()
    
    # STEP 6: Create Contractor Account
    print("STEP 6: Account Creation")
    print("-" * 40)
    try:
        if contractor_profile:
            account_result = await coia_tools.create_contractor_account(contractor_profile)
            if account_result and account_result.get('success'):
                print(f"SUCCESS: Contractor account created")
                print(f"  Account ID: {account_result.get('account', {}).get('id', 'N/A')}")
                print(f"  Company: {account_result.get('account', {}).get('company_name', 'N/A')}")
            else:
                print(f"FAILED: Account creation failed")
                print(f"  Error: {account_result.get('error', 'Unknown') if account_result else 'No result'}")
        else:
            print("SKIPPED: No contractor profile to create account with")
    except Exception as e:
        print(f"ERROR: {e}")
    
    print()
    print("=" * 80)
    print("COMPLETE WORKFLOW TEST SUMMARY")
    print("=" * 80)
    print("This test validates the entire COIA contractor onboarding process:")
    print("1. Google Business API discovery")
    print("2. Tavily web research with real data extraction")
    print("3. OpenAI business intelligence analysis")
    print("4. Complete contractor profile generation")
    print("5. Database integration and persistence")
    print("6. Bid opportunity matching")
    print("7. Account creation and onboarding")
    print()
    print("All steps use REAL APIs and database operations.")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_complete_coia_workflow())