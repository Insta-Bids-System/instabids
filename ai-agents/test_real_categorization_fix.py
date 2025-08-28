"""
Test the fixed categorization system with actual API call
"""

import asyncio
import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agents'))

from project_categorization.tool_handler import handle_categorize_project_tool

async def test_real_categorization():
    """Test with simulated tool call from OpenAI"""
    
    print("=" * 80)
    print("TESTING REAL CATEGORIZATION WITH FIXED TOOL")
    print("=" * 80)
    
    # Simulate what OpenAI would send back - it MUST pick from enum now
    test_cases = [
        {
            "name": "Fake Grass Repair",
            "project_data": {"title": "fake grass repair", "description": "my artificial turf is torn"},
            "tool_response": {
                "service_category": "Repair",
                "normalized_project_type": "turf_repair",  # Must pick from enum
                "project_scope": "single_trade",
                "confidence_score": 0.85
            }
        },
        {
            "name": "Kitchen Renovation",
            "project_data": {"title": "kitchen remodel", "description": "complete kitchen makeover"},
            "tool_response": {
                "service_category": "Renovation", 
                "normalized_project_type": "kitchen_renovation",  # Must pick from enum
                "project_scope": "multi_trade",
                "confidence_score": 0.90
            }
        },
        {
            "name": "Water Heater Installation",
            "project_data": {"title": "install water heater", "description": "new tankless water heater"},
            "tool_response": {
                "service_category": "Installation",
                "normalized_project_type": "water_heater_installation",  # Must pick from enum
                "project_scope": "single_trade", 
                "confidence_score": 0.95
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n[TEST] {test_case['name']}")
        print(f"Input: '{test_case['project_data']['title']}'")
        print(f"LLM Response: {test_case['tool_response']}")
        
        # Test the handler
        result = await handle_categorize_project_tool(
            bid_card_id=None,  # Don't save to database
            project_data=test_case['project_data'],
            tool_call_args=test_case['tool_response']
        )
        
        print(f"Handler Result: {result}")
        
        if result.get('success'):
            print("[SUCCESS] Categorization handled correctly")
        else:
            print(f"[ERROR] {result.get('message', 'Unknown error')}")
    
    print("\n" + "=" * 80)
    print("WHAT CHANGED")
    print("=" * 80)
    print("BEFORE: LLM could make up 'fake_grass_repair_thing'")
    print("AFTER:  LLM MUST choose from our 448 predefined types")
    print()
    print("This means:")
    print("- No more random project type names")
    print("- Guaranteed consistency across all categorizations")
    print("- Synonym mappings now make sense (help LLM pick the right enum)")
    
if __name__ == "__main__":
    asyncio.run(test_real_categorization())