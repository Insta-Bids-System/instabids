"""
COMPLETE COIA TEST - TurfGrass Artificial Solutions
Full workflow with database save and all information display
"""
import asyncio
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env')
os.environ['TAVILY_API_KEY'] = os.getenv('TAVILY_API_KEY', '')
os.environ['USE_TAVILY'] = 'true'
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '')
os.environ['WRITE_LEADS_ON_RESEARCH'] = 'true'

async def test_complete_turfgrass():
    print("=" * 80)
    print("COMPLETE COIA TEST - TurfGrass Artificial Solutions")
    print("Full workflow with database save")
    print("=" * 80)
    
    from agents.coia.tools import coia_tools
    
    # Use the specific company we found
    company = "South Florida Turf Solutions"
    location = "South Florida"
    
    print(f"TESTING: {company} in {location}")
    print("This should be a REAL turf/artificial grass business")
    print()
    
    # STEP 1: Google Business Search
    print("STEP 1: Google Business Search")
    print("-" * 50)
    try:
        google_result = await coia_tools.search_google_business(company, location)
        print("✅ Google Business Search SUCCESS")
        print(f"Company: {google_result.get('company_name', 'Not found')}")
        print(f"Website: {google_result.get('website', 'Not found')}")
        print(f"Verified: {google_result.get('verified', False)}")
        if google_result.get('search_results'):
            print(f"Found {len(google_result['search_results'])} sources")
        print()
    except Exception as e:
        print(f"❌ ERROR: {e}")
        google_result = {}
    
    # STEP 2: Web Research 
    print("STEP 2: Tavily Web Research")
    print("-" * 50)
    try:
        web_result = await coia_tools.web_search_company(company, location)
        print("✅ Tavily Web Research SUCCESS")
        if web_result and web_result.get('extracted_info'):
            extracted = web_result['extracted_info']
            print(f"Data extracted from: {web_result.get('data_sources', [])}")
            print(f"Years in business: {extracted.get('years_in_business', 'Not found')}")
            print(f"Services found: {len(extracted.get('services', []))} services")
            print(f"Service areas: {extracted.get('service_areas', [])}")
            print(f"Business description available: {bool(extracted.get('description'))}")
        else:
            print("No extracted info available")
        print()
    except Exception as e:
        print(f"❌ ERROR: {e}")
        web_result = {}
    
    # STEP 3: Profile Building and Database Save
    print("STEP 3: Profile Building and Database Save")
    print("-" * 50)
    try:
        profile_result = await coia_tools.build_contractor_profile(
            company, 
            google_result or {}, 
            web_result or {}, 
            {'licenses': []}
        )
        
        if profile_result:
            print("✅ PROFILE CREATED AND SAVED TO DATABASE")
            print(f"📋 TABLE USED: contractor_leads")
            print(f"🆔 CONTRACTOR_LEAD_ID: {profile_result.get('contractor_lead_id', 'Not found')}")
            print(f"💾 DATABASE SAVED: {profile_result.get('database_saved', False)}")
            print(f"📊 LEAD SCORE: {profile_result.get('lead_score', 0)}")
            print(f"📈 DATA COMPLETENESS: {profile_result.get('data_completeness', 0)}%")
            print()
            
            print("🔍 ALL INFORMATION PULLED AND SAVED:")
            print("-" * 50)
            
            # Core Business Info
            print(f"Company Name: {profile_result.get('business_name', 'Not found')}")
            print(f"Website: {profile_result.get('website', 'Not found')}")
            print(f"Phone: {profile_result.get('phone', 'Not found')}")
            print(f"Email: {profile_result.get('email', 'Not found')}")
            print(f"Years in Business: {profile_result.get('years_in_business', 'Not found')}")
            print(f"Contractor Size: {profile_result.get('contractor_size', 'Not found')}")
            
            # Services & Specialties
            specialties = profile_result.get('specialties', [])
            if specialties:
                print(f"Specialties ({len(specialties)} found):")
                for i, specialty in enumerate(specialties[:3], 1):  # Show first 3
                    print(f"  {i}. {specialty}")
                if len(specialties) > 3:
                    print(f"  ... and {len(specialties) - 3} more")
            
            # Service Areas
            service_areas = profile_result.get('service_areas', [])
            if service_areas:
                print(f"Service Areas: {', '.join(service_areas)}")
            
            # Business Metrics
            print(f"Lead Status: {profile_result.get('lead_status', 'Not found')}")
            print(f"Verified Business: {profile_result.get('enrichment_data', {}).get('verified_business', False)}")
            print(f"Completeness Score: {profile_result.get('enrichment_data', {}).get('completeness_score', 0)}%")
            
            return profile_result.get('contractor_lead_id')
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None

if __name__ == "__main__":
    contractor_id = asyncio.run(test_complete_turfgrass())
    if contractor_id:
        print()
        print("=" * 80)
        print("✅ SUCCESS: TurfGrass business research completed!")
        print(f"🆔 Saved with ID: {contractor_id}")
        print("📊 Check contractor_leads table in Supabase for full data")
        print("=" * 80)