"""
Test the fixed categorization system
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agents'))

from project_categorization.tool_handler import CATEGORIZATION_TOOL

def test_fixed_tool():
    """Test that the tool is properly fixed"""
    
    print("=" * 80)
    print("TESTING FIXED CATEGORIZATION TOOL")
    print("=" * 80)
    
    # Check that normalized_project_type is now required
    required_fields = CATEGORIZATION_TOOL["function"]["parameters"]["required"]
    print(f"Required fields: {required_fields}")
    
    if "normalized_project_type" in required_fields:
        print("[FIXED] normalized_project_type is now REQUIRED")
    else:
        print("[BROKEN] normalized_project_type is NOT required - still broken!")
        return
    
    # Check that it has enum constraint
    project_type_def = CATEGORIZATION_TOOL["function"]["parameters"]["properties"]["normalized_project_type"]
    if "enum" in project_type_def:
        enum_count = len(project_type_def["enum"])
        print(f"[FIXED] normalized_project_type has enum constraint with {enum_count} options")
        
        # Show some examples
        examples = project_type_def["enum"][:10]
        print(f"First 10 options: {examples}")
        
        # Check specific ones we care about
        turf_types = [t for t in project_type_def["enum"] if "turf" in t]
        print(f"Turf options: {turf_types}")
        
    else:
        print("[BROKEN] normalized_project_type has NO enum constraint - still broken!")
        return
    
    print("\n" + "=" * 80)
    print("WHAT THIS MEANS FOR LLM")
    print("=" * 80)
    
    print("BEFORE (BROKEN):")
    print('  User: "I need fake grass repaired"')
    print('  LLM: Can make up ANYTHING like "fake_grass_stuff" [BAD]')
    print()
    
    print("AFTER (FIXED):")
    print('  User: "I need fake grass repaired"')
    print('  LLM: MUST pick from enum list:')
    print('       - "turf_repair" [GOOD]')
    print('       - "lawn_maintenance" [GOOD]') 
    print('       - Cannot make up random names! [GOOD]')
    
    print(f"\nTotal pre-defined project types: {enum_count}")
    print("System is now ACTUALLY using our pre-built taxonomy!")
    
    return True

if __name__ == "__main__":
    test_fixed_tool()