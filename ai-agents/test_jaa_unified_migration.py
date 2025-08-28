#!/usr/bin/env python3
"""
Test JAA Agent with Unified Conversation System
Tests Phase 1 JAA migration to unified conversations
"""
import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from agents.jaa.agent import JobAssessmentAgent

async def test_jaa_unified_conversation():
    """Test JAA agent reading from unified conversation system"""
    print("=== Testing JAA Agent with Unified Conversation System ===")
    
    # Initialize JAA agent
    jaa = JobAssessmentAgent()
    
    # Test with existing unified conversation
    test_session_id = "test-unified-bathroom-final"
    print(f"Testing with session ID: {test_session_id}")
    
    try:
        result = await jaa.process_conversation(test_session_id)
        
        if result["success"]:
            print("SUCCESS: JAA UNIFIED MIGRATION SUCCESS!")
            print(f"Created bid card: {result['bid_card_number']}")
            print(f"Project type: {result['bid_card_data']['project_type']}")
            print(f"Budget: ${result['bid_card_data']['budget_min']}-${result['bid_card_data']['budget_max']}")
            print(f"Database ID: {result['database_id']}")
            return True
        else:
            print(f"FAILED: JAA Test Failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"ERROR: JAA Test Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_jaa_unified_conversation())
    
    if success:
        print("\nSUCCESS: PHASE 1 JAA MIGRATION COMPLETE!")
        print("JAA agent successfully reading from unified conversation system")
    else:
        print("\nFAILED: PHASE 1 JAA MIGRATION FAILED")
        print("JAA agent unable to read from unified system")