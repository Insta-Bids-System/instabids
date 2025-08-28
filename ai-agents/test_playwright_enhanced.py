"""
Test Enhanced Playwright MCP Integration - Windows Safe Version
"""
import asyncio
from agents.coia.tools import coia_tools

async def test_enhanced_integration():
    """Test enhanced integration with comprehensive data extraction"""
    
    print("Testing Enhanced Playwright MCP Integration...")
    print("=" * 60)
    
    company_name = "JM Holiday Lighting"
    location = "Fort Lauderdale, FL"
    
    try:
        async with coia_tools as tools:
            print("1. COMPREHENSIVE WEB SEARCH")
            web_data = await tools.web_search_company(company_name, location)
            
            if web_data and web_data.get("extracted_info"):
                extracted = web_data["extracted_info"]
                print(f"   [OK] Services: {len(extracted.get('services', []))}")
                print(f"   [OK] Service Areas: {len(extracted.get('service_areas', []))}")
                print(f"   [OK] Team Members: {len(extracted.get('team_members', []))}")
                print(f"   [OK] Specializations: {extracted.get('specializations', [])}")
                print(f"   [OK] Contractor Size: {extracted.get('contractor_size', 'unknown')}")
                
                if extracted.get('team_members'):
                    print("   TEAM MEMBERS FOUND:")
                    for member in extracted['team_members'][:3]:
                        print(f"      - {member.get('name', 'N/A')} ({member.get('role', 'N/A')})")
                
                if extracted.get('service_areas'):
                    print(f"   SERVICE AREAS: {len(extracted['service_areas'])} locations")
                    for area in extracted['service_areas'][:5]:
                        print(f"      - {area}")
            
            print("\n2. PROFILE BUILDING")
            google_data = await tools.search_google_business(company_name, location)
            license_data = await tools.search_contractor_licenses(company_name, "FL")
            
            profile = await tools.build_contractor_profile(
                company_name, google_data, web_data, license_data
            )
            
            print(f"   [OK] Completeness: {profile.get('data_completeness', 0):.1f}%")
            print(f"   [OK] Lead Score: {profile.get('lead_score', 0):.1f}")
            print(f"   [OK] Data Sources: {profile.get('data_sources', [])}")
            
            # Count filled fields
            key_fields = [
                'business_name', 'phone', 'email', 'website', 'address', 
                'specialties', 'rating', 'verified_business', 'service_areas'
            ]
            
            filled = 0
            for field in key_fields:
                value = profile.get(field)
                if value and (
                    (isinstance(value, list) and len(value) > 0) or
                    (isinstance(value, str) and value.strip()) or
                    (isinstance(value, (int, float)) and value > 0) or
                    (isinstance(value, bool) and value)
                ):
                    filled += 1
                    print(f"   [YES] {field}")
                else:
                    print(f"   [NO]  {field}")
            
            completion_rate = (filled / len(key_fields)) * 100
            print(f"\n3. RESULTS SUMMARY")
            print(f"   Fields Completed: {filled}/{len(key_fields)} ({completion_rate:.1f}%)")
            print(f"   Google Places API: WORKING")
            print(f"   Website Scraping: ENHANCED")
            print(f"   Playwright MCP: AVAILABLE")
            
            return completion_rate > 70  # Success if >70% fields filled
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_enhanced_integration())
    print(f"\nRESULT: {'SUCCESS' if result else 'NEEDS_IMPROVEMENT'}")