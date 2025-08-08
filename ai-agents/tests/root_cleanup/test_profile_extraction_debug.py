#!/usr/bin/env python3
"""
Debug the profile extraction specifically
"""
import re
import json

def debug_smart_profile_extraction():
    """Test the profile extraction logic directly"""
    print("Profile extraction debug test")
    print("="*50)
    
    # Simulate existing profile from conversation 1
    existing_profile = {
        "primary_trade": "Plumber",
        "years_in_business": 25,
        "company_name": "Statedebug Plumbing",
        "completeness": 0.2
    }
    
    print(f"Existing profile: {json.dumps(existing_profile, indent=2)}")
    
    # Test message from conversation 2
    user_message = "What's my company name?"
    user_input = user_message.lower().strip()
    
    print(f"New message: '{user_message}'")
    print(f"Processed input: '{user_input}'")
    
    # Start with current profile (this is what the code does)
    profile = existing_profile.copy()
    print(f"Profile after copy: {json.dumps(profile, indent=2)}")
    
    # Test company name extraction (should not find anything)
    company_patterns = [
        r"i'm\s+([^.,!]+?)\s*[.,!]",  # "I'm StateDebug Plumbing." or "I'm HVAC Solutions!"
        r"i'm\s+(\w+)\s+from\s+([^.,]+)",  # "I'm John from HVAC Solutions"
        r"from\s+([^.,]+)",  # "from HVAC Solutions"
        r"company\s+is\s+([^.,]+)",  # "company is HVAC Solutions"
        r"business\s+is\s+([^.,]+)",  # "business is HVAC Solutions"
        r"i\s+own\s+([^.,]+)",  # "I own HVAC Solutions"
        r"we're\s+([^.,]+)",  # "We're HVAC Solutions"
    ]
    
    company_found = False
    for i, pattern in enumerate(company_patterns):
        match = re.search(pattern, user_input)
        if match:
            print(f"  Company pattern {i} matched: {pattern}")
            groups = match.groups()
            if groups:
                if i == 0:
                    potential_company = groups[0].strip()
                else:
                    potential_company = groups[-1].strip()
                
                if not any(word in potential_company for word in ["doing", "been", "years", "work", "specialize", "usually"]):
                    profile["company_name"] = potential_company.title()
                    company_found = True
                    print(f"  Set company_name to: {potential_company.title()}")
                    break
    
    if not company_found:
        print("  No company name patterns matched - existing name should be preserved")
    
    # Test years extraction (should not find anything)
    if not profile.get("years_in_business"):  # This condition should be FALSE
        print(f"  Checking years in business (current: {profile.get('years_in_business')})")
        # ... years extraction logic would run here
    else:
        print(f"  Skipping years extraction - already have: {profile.get('years_in_business')}")
    
    print(f"Final profile: {json.dumps(profile, indent=2)}")
    
    # Check if data was preserved
    name_preserved = profile.get("company_name") == existing_profile.get("company_name")
    years_preserved = profile.get("years_in_business") == existing_profile.get("years_in_business")
    
    print(f"\nResults:")
    print(f"Company name preserved: {name_preserved}")
    print(f"Years preserved: {years_preserved}")
    
    if name_preserved and years_preserved:
        print("✅ Profile extraction correctly preserves existing data")
    else:
        print("❌ Profile extraction is losing data")
        
    return name_preserved and years_preserved

if __name__ == "__main__":
    success = debug_smart_profile_extraction()
    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")