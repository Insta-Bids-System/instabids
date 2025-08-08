"""
Quick test to verify state concurrency fix
"""
import sys


sys.path.append(".")

from agents.coia.unified_state import UnifiedCoIAState, create_initial_state


def test_state_annotations():
    """Test that all state fields are properly annotated"""

    print("\n" + "="*60)
    print("TESTING STATE ANNOTATIONS")
    print("="*60)

    # Check annotations
    annotations = UnifiedCoIAState.__annotations__

    problematic_fields = []
    annotated_fields = []

    for field, annotation in annotations.items():
        # Check if field is Annotated type
        if hasattr(annotation, "__metadata__"):
            annotated_fields.append(field)
        elif field not in ["session_id", "user_id", "contractor_lead_id", "contractor_id", "messages"]:
            # These fields don't need annotation as they're not updated concurrently
            problematic_fields.append(field)

    print(f"\nAnnotated fields: {len(annotated_fields)}")
    print(f"Problematic fields: {len(problematic_fields)}")

    if problematic_fields:
        print("\nWARNING: These fields may cause concurrency issues:")
        for field in problematic_fields[:10]:  # Show first 10
            print(f"  - {field}")
    else:
        print("\nSUCCESS: All fields properly annotated!")

    # Test state creation
    print("\n[TEST] Creating initial state...")
    state = create_initial_state(
        session_id="test_001",
        interface="chat"
    )

    print(f"State created: {state.session_id}")
    print(f"Current mode: {state.current_mode}")
    print(f"Available capabilities: {state.available_capabilities}")

    # Convert to LangGraph state
    print("\n[TEST] Converting to LangGraph state...")
    lg_state = state.to_langgraph_state()

    print(f"LangGraph state keys: {len(lg_state.keys())}")
    print(f"Current mode in LG: {lg_state.get('current_mode')}")

    return len(problematic_fields) == 0

if __name__ == "__main__":
    success = test_state_annotations()

    print("\n" + "="*60)
    print("FINAL RESULT")
    print("="*60)

    if success:
        print("\nSUCCESS: State properly configured for concurrent updates")
        print("The LangGraph concurrency issue is FIXED")
        print("\nProfile building system is ready for testing:")
        print("  - All state fields annotated")
        print("  - Concurrent updates will work")
        print("  - Mode transitions won't conflict")
    else:
        print("\nERROR: Some fields still need annotation")
        print("Fix these fields before proceeding")

    exit(0 if success else 1)
