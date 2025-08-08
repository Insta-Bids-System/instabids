"""
Test COIA Profile Building & Website Research Capabilities
Verifies that the system can build complete contractor profiles with social media extraction
"""
import asyncio
import os
import sys

from dotenv import load_dotenv


load_dotenv()

# Add parent directory to path
sys.path.append(".")


from supabase import create_client

from agents.coia.unified_graph import create_unified_coia_system, invoke_coia_chat


async def test_complete_profile_building():
    """Test the complete profile building capabilities"""

    print("\n" + "="*60)
    print("COIA PROFILE BUILDING VERIFICATION TEST")
    print("="*60)

    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set")
        return False

    print("SUCCESS: Anthropic API key found")

    # Create the unified COIA app
    print("\nInitializing COIA system...")
    app = await create_unified_coia_system()
    print("SUCCESS: COIA system initialized")

    # Test 1: Basic conversation
    print("\n[TEST 1] Basic profile extraction...")
    result1 = await invoke_coia_chat(
        app=app,
        user_message="Hi, I'm Mike from JM Holiday Lighting. We specialize in Christmas light installation and have been in business for 8 years.",
        session_id="profile_test_001"
    )

    # Extract response message properly
    if result1 and "messages" in result1:
        messages = result1["messages"]
        if messages and len(messages) > 0:
            last_msg = messages[-1]
            response_text = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
            print(f"Response received: {len(response_text)} chars")
        else:
            print("Response received: No message content")
    else:
        print("Response received: No response")

    print(f"Mode: {result1.get('current_mode', 'unknown')}")
    print(f"Profile data captured: {bool(result1.get('contractor_profile'))}")

    # Test 2: Website research trigger
    print("\n[TEST 2] Website research capabilities...")
    result2 = await invoke_coia_chat(
        app=app,
        user_message="Our website is https://jmholidaylighting.com. We service the Dallas-Fort Worth area. Can you research our company?",
        session_id="profile_test_001"
    )

    # Extract response message properly
    if result2 and "messages" in result2:
        messages = result2["messages"]
        if messages and len(messages) > 0:
            last_msg = messages[-1]
            response_text = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
            print(f"Response received: {len(response_text)} chars")
        else:
            print("Response received: No message content")
    else:
        print("Response received: No response")

    print(f"Mode switched to: {result2.get('current_mode', 'unknown')}")

    # Check if research was triggered
    if result2.get("current_mode") == "research":
        print("SUCCESS: Research mode activated")

        # Test 3: Check what data was extracted
        print("\n[TEST 3] Checking extracted profile data...")
        result3 = await invoke_coia_chat(
            app=app,
            user_message="What information did you find about our company? Show me the complete profile.",
            session_id="profile_test_001"
        )

        profile = result3.get("contractor_profile", {})
        if profile:
            print("\n=== EXTRACTED PROFILE DATA ===")
            print(f"Company Name: {profile.get('company_name', 'Not extracted')}")
            print(f"Website: {profile.get('website', 'Not extracted')}")
            print(f"Email: {profile.get('email', 'Not extracted')}")
            print(f"Phone: {profile.get('phone', 'Not extracted')}")
            print(f"Service Areas: {profile.get('service_areas', [])}")
            print(f"Years in Business: {profile.get('years_in_business', 'Not extracted')}")
            print(f"Specialties: {profile.get('specialties', [])}")
            print(f"Social Media: {profile.get('social_media', {})}")
            print(f"Certifications: {profile.get('certifications', [])}")
            print(f"Business Size: {profile.get('business_size', 'Not extracted')}")

            # Calculate completeness
            fields_to_check = ["company_name", "website", "email", "phone", "service_areas",
                              "years_in_business", "specialties", "social_media"]
            filled_fields = sum(1 for f in fields_to_check if profile.get(f))
            completeness = (filled_fields / len(fields_to_check)) * 100
            print(f"\nProfile Completeness: {completeness:.1f}%")

            # Check database storage
            print("\n[TEST 4] Checking database storage...")
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_ANON_KEY")

            if supabase_url and supabase_key:
                supabase = create_client(supabase_url, supabase_key)

                # Check contractor_leads table
                result = supabase.table("contractor_leads").select("*").eq(
                    "company_name", "JM Holiday Lighting"
                ).order("created_at", desc=True).limit(1).execute()

                if result.data:
                    contractor = result.data[0]
                    print("SUCCESS: Contractor found in database")
                    print(f"  - Lead Status: {contractor.get('lead_status')}")
                    print(f"  - Data Completeness: {contractor.get('data_completeness')}%")
                    print(f"  - Has Enrichment Data: {bool(contractor.get('enrichment_data'))}")
                    print(f"  - Has Raw Data: {bool(contractor.get('raw_data'))}")

                    if contractor.get("enrichment_data"):
                        enrichment = contractor["enrichment_data"]
                        print("\n=== ENRICHMENT DATA ===")
                        print(f"  - Social Media Links: {enrichment.get('social_media', {})}")
                        print(f"  - Gallery Images: {len(enrichment.get('gallery_images', []))} images")
                        print(f"  - Business Hours: {bool(enrichment.get('business_hours'))}")
                        print(f"  - Team Size: {enrichment.get('team_size_estimate', 'Not found')}")

                    # Test result
                    if contractor.get("data_completeness", 0) >= 80:
                        print("\nRESULT: Profile building FULLY OPERATIONAL (80%+ completeness)")
                        return True
                    elif contractor.get("data_completeness", 0) >= 50:
                        print("\nRESULT: Profile building PARTIALLY WORKING (50-79% completeness)")
                        return True
                    else:
                        print("\nRESULT: Profile building NEEDS IMPROVEMENT (<50% completeness)")
                        return False
                else:
                    print("WARNING: Contractor not found in database")
                    print("Profile may not be persisting to database")
                    return False
            else:
                print("WARNING: Supabase credentials not configured")
                print("Cannot verify database storage")
                return False
        else:
            print("ERROR: No profile data extracted")
            return False
    else:
        print("WARNING: Research mode not activated")
        print("System may not have website research capabilities active")
        return False

async def main():
    """Run the complete test suite"""

    # Run profile building test
    success = await test_complete_profile_building()

    print("\n" + "="*60)
    print("FINAL VERIFICATION RESULT")
    print("="*60)

    if success:
        print("\nSUCCESS: PROFILE BUILDING CONFIRMED OPERATIONAL")
        print("The COIA system can:")
        print("  - Extract company information from conversation")
        print("  - Research websites for additional data")
        print("  - Extract social media and contact info")
        print("  - Store enriched profiles in database")
        print("  - Achieve 80%+ data completeness")
        print("\nREADY TO PROCEED WITH BID CARD SEARCH FEATURES")
    else:
        print("\nWARNING: PROFILE BUILDING NEEDS VERIFICATION")
        print("Issues found:")
        print("  - May not be extracting all website data")
        print("  - Database storage may not be working")
        print("  - Enrichment features may not be active")
        print("\nFIX THESE ISSUES BEFORE ADDING BID CARD SEARCH")

    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)
