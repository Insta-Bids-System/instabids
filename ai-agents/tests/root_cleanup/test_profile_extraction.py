"""
Test profile extraction to see what's being extracted
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.coia.langgraph_nodes import CoIANodeWrapper

def test_profile_extraction():
    """Test profile extraction logic"""
    
    wrapper = CoIANodeWrapper()
    
    test_messages = [
        "Hi, I'm from Turf Grass Artificial Solutions. We're a landscaping company based in South Florida.",
        "I'm John from ABC Plumbing Services",
        "My company is Elite Kitchen Designs", 
        "We're Premium Construction Group"
    ]
    
    for msg in test_messages:
        print(f"\nTesting: {msg}")
        profile = wrapper._smart_profile_extraction(msg, {})
        print(f"Extracted profile: {profile}")
        
        company_name = profile.get("company_name")
        print(f"Company name: {company_name}")

if __name__ == "__main__":
    test_profile_extraction()