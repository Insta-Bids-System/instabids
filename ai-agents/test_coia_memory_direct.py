"""
Direct test of COIA memory persistence system
Tests the save and restore functionality without DeepAgents
"""

import asyncio
import json
from agents.coia.memory_integration import COIAMemoryIntegrator

async def test_memory_persistence():
    """Test that COIA memory can be saved and restored"""
    
    print("=== TESTING COIA MEMORY PERSISTENCE ===\n")
    
    # Initialize memory integrator
    integrator = COIAMemoryIntegrator()
    
    # Test data
    contractor_lead_id = "test-memory-001"
    session_id = "session-test-001"
    
    # Create test state with all critical fields
    test_state = {
        "contractor_lead_id": contractor_lead_id,
        "session_id": session_id,
        "company_name": "Turf Grass Artificial Solutions",
        "staging_id": "staging-abc-123",
        "messages": [
            {"role": "user", "content": "I run Turf Grass in Boca Raton"},
            {"role": "assistant", "content": "Welcome Turf Grass!"}
        ],
        "contractor_profile": {
            "name": "Turf Grass Artificial Solutions",
            "location": "Boca Raton, FL",
            "services": ["artificial turf", "landscaping"],
            "years_in_business": 10
        },
        "radius_preferences": {
            "radius": 25,
            "zip_codes": ["33432", "33433", "33434"]
        },
        "research_findings": {
            "website": "turfgrassartificialsolutions.com",
            "phone": "561-555-0123",
            "rating": 4.5
        }
    }
    
    # Test 1: Save state
    print("TEST 1: Saving state to memory...")
    try:
        success = await integrator.save_deepagents_state(
            contractor_lead_id, 
            test_state, 
            session_id
        )
        if success:
            print("PASS: State saved successfully!")
        else:
            print("FAIL: Failed to save state")
            return False
    except Exception as e:
        print(f"FAIL: Error saving state: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Restore state
    print("\nTEST 2: Restoring state from memory...")
    try:
        restored_state = await integrator.restore_deepagents_state(
            contractor_lead_id,
            session_id
        )
        
        # Verify critical fields were restored
        print("\nVerifying restored data:")
        
        checks = [
            ("Company Name", restored_state.get("company_name"), "Turf Grass Artificial Solutions"),
            ("Staging ID", restored_state.get("staging_id"), "staging-abc-123"),
            ("Messages Count", len(restored_state.get("messages", [])), 2),
            ("Radius", restored_state.get("radius_preferences", {}).get("radius"), 25),
            ("Website", restored_state.get("research_findings", {}).get("website"), "turfgrassartificialsolutions.com")
        ]
        
        all_passed = True
        for field, actual, expected in checks:
            if actual == expected:
                print(f"  PASS: {field}: {actual}")
            else:
                print(f"  FAIL: {field}: Expected {expected}, got {actual}")
                all_passed = False
        
        if all_passed:
            print("\nPASS: ALL MEMORY TESTS PASSED!")
            print("COIA memory persistence is working correctly!")
            return True
        else:
            print("\nFAIL: Some memory tests failed")
            return False
            
    except Exception as e:
        print(f"FAIL: Error restoring state: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_memory_persistence())
    exit(0 if result else 1)