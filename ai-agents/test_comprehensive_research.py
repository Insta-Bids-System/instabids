"""
Test the enhanced comprehensive research system
"""
import asyncio
from agents.coia.tools import coia_tools

async def test_comprehensive_research():
    """Test comprehensive contractor research with web scraping"""
    
    print("Testing comprehensive contractor research...")
    print("=" * 60)
    
    company_name = "JM Holiday Lighting"
    location = "Fort Lauderdale, FL"
    
    try:
        async with coia_tools as tools:
            print(f"1. Testing Google Business Search for {company_name}")
            google_data = await tools.search_google_business(company_name, location)
            print(f"   Google data success: {google_data.get('success') if google_data else 'None'}")
            if google_data and google_data.get('company_name'):
                print(f"   Found: {google_data['company_name']}")
                print(f"   Website: {google_data.get('website', 'N/A')}")
                print(f"   Phone: {google_data.get('phone', 'N/A')}")
                print(f"   Rating: {google_data.get('rating', 'N/A')}")
            
            print(f"\n2. Testing Comprehensive Web Research for {company_name}")
            web_data = await tools.web_search_company(company_name, location)
            print(f"   Web data type: {type(web_data)}")
            if web_data:
                print(f"   Data sources: {web_data.get('data_sources', [])}")
                if web_data.get('extracted_info'):
                    extracted = web_data['extracted_info']
                    print(f"   Services found: {len(extracted.get('services', []))}")
                    print(f"   Years in business: {extracted.get('years_in_business', 'N/A')}")
                    print(f"   Contact form: {extracted.get('contact_form_url', 'N/A')}")
                    print(f"   Email: {extracted.get('contact_methods', {}).get('emails', ['N/A'])[0] if extracted.get('contact_methods', {}).get('emails') else 'N/A'}")
            
            print(f"\n3. Testing Comprehensive Profile Building")
            license_data = await tools.search_contractor_licenses(company_name, "FL")
            
            comprehensive_profile = await tools.build_contractor_profile(
                company_name, google_data, web_data, license_data
            )
            
            print(f"   Profile completeness: {comprehensive_profile.get('data_completeness', 0):.1f}%")
            print(f"   Lead score: {comprehensive_profile.get('lead_score', 0):.1f}")
            print(f"   Data sources: {comprehensive_profile.get('data_sources', [])}")
            print(f"   Total profile fields: {len(comprehensive_profile)} fields")
            
            # Show key filled fields
            key_fields = [
                'business_name', 'phone', 'email', 'website', 'address', 'city', 'state',
                'years_in_business', 'specialties', 'rating', 'review_count', 'verified_business',
                'has_contact_form', 'contact_form_url', 'facebook_url', 'instagram_url'
            ]
            
            print("\n4. Key Field Status:")
            filled_count = 0
            for field in key_fields:
                value = comprehensive_profile.get(field)
                if value:  # Has meaningful value
                    if isinstance(value, list) and len(value) > 0:
                        print(f"   [YES] {field}: {value[:3]}...")  # Show first 3 items
                        filled_count += 1
                    elif isinstance(value, str) and value.strip():
                        print(f"   [YES] {field}: {value[:50]}...")  # Show first 50 chars
                        filled_count += 1
                    elif isinstance(value, (int, float)) and value > 0:
                        print(f"   [YES] {field}: {value}")
                        filled_count += 1
                    elif isinstance(value, bool) and value:
                        print(f"   [YES] {field}: {value}")
                        filled_count += 1
                else:
                    print(f"   [NO] {field}: empty")
            
            print(f"\n5. Summary:")
            print(f"   Key fields filled: {filled_count}/{len(key_fields)} ({filled_count/len(key_fields)*100:.1f}%)")
            print(f"   Total profile fields: {len(comprehensive_profile)}")
            print(f"   Data completeness score: {comprehensive_profile.get('data_completeness', 0):.1f}%")
            print(f"   Lead score: {comprehensive_profile.get('lead_score', 0):.1f}")
            
            # Show profile insights
            insights = comprehensive_profile.get('profile_insights', [])
            if insights:
                print(f"   Profile insights:")
                for insight in insights:
                    print(f"     • {insight}")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_comprehensive_research())