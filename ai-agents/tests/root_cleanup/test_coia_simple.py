"""
Simple COIA Profile Extraction Test
Verify the COIA agent extracts all critical matching fields
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.coia.langgraph_nodes import CoIANodeWrapper

def test_profile_extraction():
    """Test COIA profile extraction"""
    
    print("TESTING COIA PROFILE EXTRACTION")
    print("=" * 50)
    
    wrapper = CoIANodeWrapper()
    
    # Test contractor message
    message = "Hi, I'm from Turf Grass Artificial Solutions. We're a landscaping company specializing in artificial turf installation. Been in business for 15 years serving South Florida, zip codes 33428, 33429, and 33431. We have crews and handle both residential and commercial projects."
    
    profile = wrapper._smart_profile_extraction(message, {})
    
    print(f"CONTRACTOR MESSAGE:")
    print(f"{message}\n")
    
    print("EXTRACTED PROFILE DATA:")
    critical_fields = [
        "main_service_type",
        "service_subtypes", 
        "business_size_category",
        "zip_codes",
        "years_in_business",
        "specializations"
    ]
    
    for field in critical_fields:
        if field in profile:
            print(f"  {field}: {profile[field]}")
        else:
            print(f"  {field}: NOT FOUND")
    
    print("\nOTHER FIELDS:")
    for key, value in profile.items():
        if key not in critical_fields:
            print(f"  {key}: {value}")
    
    print("\nCRITICAL FIELDS CHECK:")
    required_for_matching = [
        "main_service_type", 
        "business_size_category", 
        "zip_codes"
    ]
    
    all_present = True
    for field in required_for_matching:
        if field in profile and profile[field]:
            print(f"  PASS: {field}")
        else:
            print(f"  FAIL: {field}")
            all_present = False
    
    if all_present:
        print("\nSUCCESS: All critical matching fields extracted!")
        print("Agent 2 backend can now match this contractor to bid cards!")
    else:
        print("\nNEEDS WORK: Missing critical fields")
    
    return profile

if __name__ == "__main__":
    test_profile_extraction()