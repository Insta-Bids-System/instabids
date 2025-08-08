#!/usr/bin/env python3
"""
Isolate and test the _smart_profile_extraction bug
"""
import os
import sys
import json

sys.path.insert(0, os.path.abspath('.'))

from agents.coia.langgraph_nodes import CoIANodeWrapper

def test_isolated_extraction():
    """Test the _smart_profile_extraction method directly"""
    print("ISOLATED PROFILE EXTRACTION TEST")
    print("="*50)
    
    # Create instance
    node_wrapper = CoIANodeWrapper()
    
    # Test 1: With existing profile data
    existing_profile = {
        "primary_trade": "Electrician",
        "years_in_business": 22,
        "company_name": "TestCorp Electric", 
        "completeness": 0.2
    }
    
    user_message = "What's my company name?"
    
    print(f"Input message: '{user_message}'")
    print(f"Input profile: {json.dumps(existing_profile, indent=2)}")
    
    try:
        result = node_wrapper._smart_profile_extraction(user_message, existing_profile)
        print(f"Result type: {type(result)}")
        print(f"Result value: {result}")
        
        if isinstance(result, dict):
            non_empty = {k: v for k, v in result.items() if v}
            print(f"Result profile: {json.dumps(non_empty, indent=2)}")
            
            # Check preservation
            company_preserved = result.get('company_name') == existing_profile.get('company_name')
            years_preserved = result.get('years_in_business') == existing_profile.get('years_in_business')
            
            print(f"\nPreservation check:")
            print(f"Company name: {existing_profile.get('company_name')} -> {result.get('company_name')} = {'PRESERVED' if company_preserved else 'LOST'}")
            print(f"Years: {existing_profile.get('years_in_business')} -> {result.get('years_in_business')} = {'PRESERVED' if years_preserved else 'LOST'}")
            
            return company_preserved and years_preserved
        else:
            print("ERROR: Method returned non-dict type")
            return False
            
    except Exception as e:
        print(f"ERROR: Exception in extraction: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_isolated_extraction()
    print(f"\nFINAL: {'SUCCESS' if success else 'FAILED'}")