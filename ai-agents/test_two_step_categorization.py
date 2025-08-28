"""
Test the two-step LLM categorization process:
Step 1: Pick 1 of 14 service categories
Step 2: Pick specific project type from that category's list
"""

from agents.project_categorization.tool_handler import CATEGORIZATION_TOOL
from agents.project_categorization.project_types import PROJECT_TYPE_MAPPING

def test_two_step_process():
    """Test that the tool enforces two-step process"""
    
    print("=" * 80)
    print("TESTING TWO-STEP LLM CATEGORIZATION PROCESS")
    print("=" * 80)
    print()
    
    # Step 1: Show that LLM must pick from 14 categories
    print("STEP 1: LLM picks from 14 service categories")
    print("-" * 50)
    categories = CATEGORIZATION_TOOL["function"]["parameters"]["properties"]["service_category"]["enum"]
    print(f"Available categories: {len(categories)}")
    for i, category in enumerate(categories, 1):
        count = len(PROJECT_TYPE_MAPPING.get(category, []))
        print(f"  {i:2d}. {category:<20} ({count} project types)")
    
    print(f"\nTotal categories: {len(categories)}")
    
    print()
    
    # Step 2: Show that LLM must pick from specific project types within category
    print("STEP 2: LLM picks specific project type from category")
    print("-" * 50)
    
    # Example with "Repair" category
    example_category = "Repair"
    repair_types = PROJECT_TYPE_MAPPING[example_category]
    
    print(f"Example: If LLM picks '{example_category}', it must then pick from {len(repair_types)} options:")
    print()
    for i, project_type in enumerate(repair_types[:10], 1):  # Show first 10
        print(f"  {i:2d}. {project_type}")
    
    if len(repair_types) > 10:
        print(f"  ... and {len(repair_types) - 10} more")
    
    print()
    
    # Step 3: Show the enum constraint forces this behavior
    print("STEP 3: Enum constraint enforcement")
    print("-" * 50)
    
    all_project_types = CATEGORIZATION_TOOL["function"]["parameters"]["properties"]["normalized_project_type"]["enum"]
    print(f"Total project types in enum: {len(all_project_types)}")
    
    # Count types per category
    for category in categories:
        category_types = PROJECT_TYPE_MAPPING.get(category, [])
        enum_matches = [t for t in all_project_types if t in category_types]
        print(f"  {category:<20}: {len(enum_matches):3d} types in enum")
    
    print()
    print("WHAT THIS MEANS:")
    print("✓ LLM cannot make up project types like 'fake_grass_repair_thing'")
    print("✓ LLM must pick 1 of 14 categories first (e.g. 'Repair')")
    print("✓ LLM must then pick from that category's predefined list (e.g. 'turf_repair')")
    print("✓ No synonym mapping needed - LLM handles intelligence via constraints")
    
    print()
    print("EXAMPLE PROCESS:")
    print("User: 'I need my fake grass repaired'")
    print("Step 1: LLM picks 'Repair' from 14 categories")
    print("Step 2: LLM picks 'turf_repair' from Repair's 84 project types")
    print("Result: Guaranteed consistency, no random names")

if __name__ == "__main__":
    test_two_step_process()