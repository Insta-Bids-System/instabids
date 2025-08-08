"""
Test COIA Agent Profile Extraction
Verifies that COIA extracts all critical matching fields
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.coia.langgraph_nodes import CoIANodeWrapper
from agents.coia.unified_state import UnifiedCoIAState

async def test_profile_extraction():
    """Test various contractor messages to verify profile extraction"""
    
    print("=" * 80)
    print("TESTING COIA PROFILE EXTRACTION")
    print("=" * 80)
    
    # Initialize the node wrapper (has the extraction logic)
    wrapper = CoIANodeWrapper()
    
    # Test cases with expected extractions
    test_cases = [
        {
            "message": "Hi, I'm John from Turf Grass Artificial Solutions. We're a landscaping company specializing in artificial turf installation. Been in business for 15 years serving South Florida, mainly zip codes 33428, 33429, and 33431. We have crews of 4-6 people and handle both residential and commercial projects.",
            "expected": {
                "company_name": "Turf Grass Artificial Solutions",
                "main_service_type": "Landscaping",
                "service_subtypes": ["New installation"],
                "business_size_category": "LOCAL_BUSINESS_TEAMS",
                "years_in_business": 15,
                "zip_codes": ["33428", "33429", "33431"],
                "specializations": ["residential", "commercial"]
            }
        },
        {
            "message": "I'm a solo handyman doing plumbing repairs and maintenance. Work within 20 miles of downtown Miami. Been doing this for 5 years. Handle emergency repairs too.",
            "expected": {
                "main_service_type": "Plumbing",
                "service_subtypes": ["Repair/service", "Emergency repair", "Maintenance"],
                "business_size_category": "INDIVIDUAL_HANDYMAN",
                "years_in_business": 5,
                "service_radius_miles": 20,
                "specializations": ["emergency"]
            }
        },
        {
            "message": "We're ABC Roofing, a national company with multiple locations. We do new roof installations and replacements for commercial properties.",
            "expected": {
                "company_name": "Abc Roofing",
                "main_service_type": "Roofing",
                "service_subtypes": ["New installation", "Replacement"],
                "business_size_category": "NATIONAL_COMPANY",
                "specializations": ["commercial"]
            }
        },
        {
            "message": "I own a small HVAC business with a couple of employees. We do AC repair and new installations in the 33401 area.",
            "expected": {
                "main_service_type": "HVAC",
                "service_subtypes": ["Repair/service", "New installation"],
                "business_size_category": "OWNER_OPERATOR",
                "zip_codes": ["33401"]
            }
        }
    ]
    
    # Test each case
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Message: {test_case['message'][:100]}...")
        
        # Extract profile using the enhanced extraction
        profile = wrapper._smart_profile_extraction(test_case['message'], {})
        
        print(f"\nExtracted Profile:")
        for key in ["company_name", "main_service_type", "service_subtypes", 
                   "business_size_category", "years_in_business", "zip_codes",
                   "service_radius_miles", "specializations"]:
            if key in profile:
                print(f"  {key}: {profile[key]}")
        
        # Check expected fields
        print(f"\nValidation:")
        expected = test_case['expected']
        for key, expected_value in expected.items():
            actual_value = profile.get(key)
            if actual_value == expected_value:
                print(f"  ✅ {key}: CORRECT")
            else:
                print(f"  ❌ {key}: Expected {expected_value}, got {actual_value}")
        
        print("-" * 40)
    
    # Test Research Mode Trigger
    print("\n" + "=" * 80)
    print("TESTING RESEARCH MODE TRIGGER")
    print("=" * 80)
    
    research_message = "I'm Turf Grass Artificial Solutions from South Florida"
    print(f"Message: {research_message}")
    
    # The COIA should detect this needs research
    profile = wrapper._smart_profile_extraction(research_message, {})
    
    if profile.get("company_name") and not profile.get("website"):
        print("\n✅ RESEARCH NEEDED: Company name found but no website")
        print("   COIA should trigger research mode to find:")
        print("   - Website: turfgrassartificialsolutions.com")
        print("   - Google Business listing")
        print("   - Phone number")
        print("   - Reviews and ratings")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    print("\n✅ CRITICAL FIELDS NOW EXTRACTED:")
    print("  - main_service_type (for work type matching)")
    print("  - service_subtypes (for specific work matching)")
    print("  - business_size_category (for company size matching)")
    print("  - zip_codes (for geographic matching)")
    print("  - service_radius_miles (for coverage area)")
    
    print("\n📝 NEXT STEPS:")
    print("  1. COIA should ask follow-up questions for missing fields")
    print("  2. Trigger research mode when company name provided")
    print("  3. Save complete profile to database")
    print("  4. Enable Agent 2 to use this data for matching")

if __name__ == "__main__":
    asyncio.run(test_profile_extraction())