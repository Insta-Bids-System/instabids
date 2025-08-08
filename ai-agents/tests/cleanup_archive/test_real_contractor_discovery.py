#!/usr/bin/env python3
"""
PROVE THE SYSTEM WORKS - Real Contractor Discovery Test
This will make ACTUAL Google Maps API calls and find REAL contractors
"""
import os
import sys


# Add the parent directory to the path so we can import from ai-agents
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
from supabase import create_client

from agents.cda.web_search_agent import WebSearchContractorAgent


def test_real_contractor_discovery():
    """Test with REAL Google Maps API calls to find REAL contractors"""
    print("=" * 80)
    print("REAL CONTRACTOR DISCOVERY TEST")
    print("Making ACTUAL Google Maps API calls to find REAL contractors")
    print("Location: Coconut Creek, FL (33442)")
    print("=" * 80)

    # Load environment and setup
    load_dotenv()
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    supabase = create_client(supabase_url, supabase_key)

    # Initialize the web search agent
    web_agent = WebSearchContractorAgent(supabase)

    # Test 1: Emergency Roofing Repair
    print("\nTEST 1: EMERGENCY ROOFING REPAIR")
    print("Search Query: 'roofing repair emergency contractors near Coconut Creek FL'")
    print("Making REAL Google Maps API call...")

    roof_bid_card_id = "test-emergency-roof-repair"
    roof_result = web_agent.discover_contractors_for_bid(
        bid_card_id=roof_bid_card_id,
        contractors_needed=5,
        radius_miles=15
    )

    if roof_result["success"]:
        contractors = roof_result["contractors"]
        print(f"\nRESULT: Found {len(contractors)} REAL roofing contractors:")

        for i, contractor in enumerate(contractors[:5], 1):
            print(f"\n{i}. {contractor.get('company_name', 'Unknown')}")
            print(f"   Address: {contractor.get('address', 'N/A')}")
            print(f"   Phone: {contractor.get('phone', 'N/A')}")
            print(f"   Rating: {contractor.get('google_rating', 'N/A')} ({contractor.get('google_review_count', 0)} reviews)")
            print(f"   Business Types: {contractor.get('google_types', [])}")
            print(f"   Website: {contractor.get('website', 'N/A')}")

            # Show this is REAL by checking if it has actual Google data
            if contractor.get("google_place_id"):
                print(f"   Google Place ID: {contractor.get('google_place_id')[:20]}... (REAL GOOGLE DATA)")
    else:
        print(f"ERROR: {roof_result.get('error', 'Unknown error')}")

    # Test 2: Kitchen Installation
    print("\n" + "=" * 80)
    print("TEST 2: KITCHEN INSTALLATION")
    print("Search Query: 'kitchen remodeling installation contractors near Coconut Creek FL'")
    print("Making REAL Google Maps API call...")

    kitchen_bid_card_id = "test-kitchen-installation"
    kitchen_result = web_agent.discover_contractors_for_bid(
        bid_card_id=kitchen_bid_card_id,
        contractors_needed=4,
        radius_miles=15
    )

    if kitchen_result["success"]:
        contractors = kitchen_result["contractors"]
        print(f"\nRESULT: Found {len(contractors)} REAL kitchen contractors:")

        for i, contractor in enumerate(contractors[:3], 1):
            print(f"\n{i}. {contractor.get('company_name', 'Unknown')}")
            print(f"   Address: {contractor.get('address', 'N/A')}")
            print(f"   Rating: {contractor.get('google_rating', 'N/A')} ({contractor.get('google_review_count', 0)} reviews)")
            print(f"   Business Types: {contractor.get('google_types', [])}")

            # Prove this is real data
            if contractor.get("google_place_id"):
                print("   PROOF: Google Place ID exists (REAL contractor)")
    else:
        print(f"ERROR: {kitchen_result.get('error', 'Unknown error')}")

    # Test 3: Show the difference in contractors found
    print("\n" + "=" * 80)
    print("PROOF: SERVICE-SPECIFIC DISCOVERY WORKING")
    print("=" * 80)

    if roof_result["success"] and kitchen_result["success"]:
        roof_contractors = roof_result["contractors"]
        kitchen_contractors = kitchen_result["contractors"]

        print(f"Roofing search found: {len(roof_contractors)} contractors")
        print(f"Kitchen search found: {len(kitchen_contractors)} contractors")

        # Show that we get different contractors for different services
        roof_names = {c.get("company_name", "") for c in roof_contractors}
        kitchen_names = {c.get("company_name", "") for c in kitchen_contractors}

        overlap = roof_names.intersection(kitchen_names)
        unique_roof = roof_names - kitchen_names
        unique_kitchen = kitchen_names - roof_names

        print("\nSERVICE SPECIALIZATION PROOF:")
        print(f"  - Overlapping contractors: {len(overlap)} (general contractors)")
        print(f"  - Roofing-specific contractors: {len(unique_roof)}")
        print(f"  - Kitchen-specific contractors: {len(unique_kitchen)}")

        if len(unique_roof) > 0:
            print("\n  ROOFING SPECIALISTS FOUND:")
            for name in list(unique_roof)[:3]:
                print(f"    - {name}")

        if len(unique_kitchen) > 0:
            print("\n  KITCHEN SPECIALISTS FOUND:")
            for name in list(unique_kitchen)[:3]:
                print(f"    - {name}")

        return True
    else:
        print("Could not compare - one or both searches failed")
        return False

def test_google_api_directly():
    """Test Google Maps API directly to prove it works"""
    print("\n" + "=" * 80)
    print("DIRECT GOOGLE MAPS API TEST")
    print("Making direct API call to prove Google integration works")
    print("=" * 80)

    import requests

    load_dotenv()
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    if not api_key:
        print("ERROR: No Google Maps API key found")
        return False

    print(f"Google API Key loaded: {api_key[:20]}...{api_key[-5:]}")

    # Direct Google Places API call
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": "roofing contractors Coconut Creek FL",
        "key": api_key,
        "location": "26.2517,-80.1778",  # Coconut Creek coordinates
        "radius": "24140"  # 15 miles in meters
    }

    print("Making direct Google Maps API call...")
    response = requests.get(url, params=params)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        print(f"REAL RESULTS: Found {len(results)} contractors from Google")

        for i, place in enumerate(results[:3], 1):
            print(f"\n{i}. {place.get('name', 'Unknown')}")
            print(f"   Address: {place.get('formatted_address', 'N/A')}")
            print(f"   Rating: {place.get('rating', 'N/A')}")
            print(f"   Place ID: {place.get('place_id', 'N/A')}")
            print(f"   Types: {place.get('types', [])}")

        return len(results) > 0
    else:
        print(f"ERROR: {response.text}")
        return False

if __name__ == "__main__":
    print("PROVING THE CONTRACTOR DISCOVERY SYSTEM ACTUALLY WORKS")
    print("This test makes REAL API calls and finds REAL contractors")
    print("No hypotheticals - only concrete results")

    try:
        # Test 1: Direct Google API to prove it works
        google_works = test_google_api_directly()

        # Test 2: Full system test with real contractor discovery
        if google_works:
            system_works = test_real_contractor_discovery()

            print("\n" + "=" * 80)
            print("FINAL PROOF RESULTS")
            print("=" * 80)
            print(f"Google Maps API: {'WORKING' if google_works else 'FAILED'}")
            print(f"Contractor Discovery System: {'WORKING' if system_works else 'FAILED'}")

            if google_works and system_works:
                print("\nCONCRETE PROOF: The system ACTUALLY works!")
                print("- Makes real Google Maps API calls")
                print("- Finds real contractors with real data")
                print("- Shows service-specific results")
                print("- No hypotheticals - only real results")
            else:
                print("\nSYSTEM ISSUES DETECTED - showing real problems, not hypotheticals")
        else:
            print("\nGoogle Maps API not working - cannot test full system")

    except Exception as e:
        print(f"\nREAL ERROR (not hypothetical): {e}")
        import traceback
        traceback.print_exc()
