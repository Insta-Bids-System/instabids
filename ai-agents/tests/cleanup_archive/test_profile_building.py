"""
Live test of COIA profile building capabilities
Tests website research, social media extraction, and database storage
"""
import asyncio
import os
import sys

from dotenv import load_dotenv


load_dotenv()

# Add parent directory to path
sys.path.append(".")

from agents.coia.unified_graph import app
from routers.unified_coia_api import invoke_coia_chat


async def test_profile_building():
    """Test complete profile building with website research"""

    print("\n" + "="*60)
    print("COIA PROFILE BUILDING TEST")
    print("="*60)

    # Test conversation 1: Basic info gathering
    print("\n1. Testing basic profile creation...")
    response1 = await invoke_coia_chat(
        app=app,
        user_message="Hi, I'm Mike from JM Holiday Lighting. We specialize in Christmas light installation.",
        session_id="test_profile_001"
    )
    print(f"Response: {response1.message[:200]}...")
    print(f"Mode: {response1.mode}")
    print(f"Profile completeness: {response1.profile_completeness}%")

    # Test conversation 2: Website research trigger
    print("\n2. Testing website research...")
    response2 = await invoke_coia_chat(
        app=app,
        user_message="Our website is https://jmholidaylighting.com - we've been in business for 8 years",
        session_id="test_profile_001"
    )
    print(f"Response: {response2.message[:200]}...")
    print(f"Mode: {response2.mode}")
    print(f"Profile completeness: {response2.profile_completeness}%")

    # Test conversation 3: Social media extraction
    print("\n3. Testing social media and contact extraction...")
    response3 = await invoke_coia_chat(
        app=app,
        user_message="Can you find our social media profiles and contact information from our website?",
        session_id="test_profile_001"
    )
    print(f"Response: {response3.message[:200]}...")
    print(f"Mode: {response3.mode}")
    print(f"Profile completeness: {response3.profile_completeness}%")

    # Check what got extracted
    if response3.contractor_profile:
        print("\n4. Extracted Profile Data:")
        profile = response3.contractor_profile
        print(f"- Company: {profile.get('company_name')}")
        print(f"- Website: {profile.get('website')}")
        print(f"- Email: {profile.get('email')}")
        print(f"- Phone: {profile.get('phone')}")
        print(f"- Service Areas: {profile.get('service_areas')}")
        print(f"- Years in Business: {profile.get('years_in_business')}")
        print(f"- Specialties: {profile.get('specialties')}")
        print(f"- Social Media: {profile.get('social_media')}")

    # Test database storage
    print("\n5. Checking database storage...")
    # Import Supabase client
    from supabase import create_client

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")

    if supabase_url and supabase_key:
        supabase = create_client(supabase_url, supabase_key)

        # Check if contractor was created
        result = supabase.table("contractor_leads").select("*").eq(
            "company_name", "JM Holiday Lighting"
        ).execute()

        if result.data:
            contractor = result.data[0]
            print("✅ Contractor found in database!")
            print(f"- Data completeness: {contractor.get('data_completeness')}%")
            print(f"- Lead status: {contractor.get('lead_status')}")
            print(f"- Enrichment data: {bool(contractor.get('enrichment_data'))}")

            if contractor.get("enrichment_data"):
                enrichment = contractor["enrichment_data"]
                print("\nEnrichment Details:")
                print(f"- Social Media Links: {enrichment.get('social_media', {})}")
                print(f"- Gallery Images: {len(enrichment.get('gallery_images', []))} images")
                print(f"- Business Hours: {bool(enrichment.get('business_hours'))}")
        else:
            print("❌ Contractor not found in database")
    else:
        print("❌ Supabase credentials not configured")

    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)

    return {
        "profile_completeness": response3.profile_completeness if response3 else 0,
        "mode_reached": response3.mode if response3 else None,
        "profile_created": bool(response3.contractor_profile) if response3 else False,
        "database_stored": bool(result.data) if "result" in locals() else False
    }

if __name__ == "__main__":
    # Run the test
    test_results = asyncio.run(test_profile_building())

    print("\n📊 FINAL TEST RESULTS:")
    print(f"- Profile Completeness: {test_results['profile_completeness']}%")
    print(f"- Mode Reached: {test_results['mode_reached']}")
    print(f"- Profile Created: {'✅' if test_results['profile_created'] else '❌'}")
    print(f"- Database Stored: {'✅' if test_results['database_stored'] else '❌'}")

    # Determine if profile building is ready
    if test_results["profile_completeness"] >= 80 and test_results["database_stored"]:
        print("\n🎉 PROFILE BUILDING CONFIRMED WORKING!")
        print("Ready to proceed with bid card search features.")
    else:
        print("\n⚠️ PROFILE BUILDING NEEDS FIXES")
        print("Issues to resolve before proceeding to bid card search.")
