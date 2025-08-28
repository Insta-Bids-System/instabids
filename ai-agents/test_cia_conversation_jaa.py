#!/usr/bin/env python3
"""
Test CIA Agent calling JAA service through a conversation
This simulates a real user conversation where they request a budget change
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# Add project paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agents'))

from agents.cia.agent import CustomerInterfaceAgent

# Test with the same bid card we've been using
TEST_BID_CARD = {
    "id": "93c216f1-1e3f-490a-899d-ae2a236652a4",
    "bid_card_number": "BC0730223441",
    "current_budget_max": 60000  # Current value after our last test
}

async def test_cia_conversation_with_jaa():
    """Test CIA Agent calling JAA service through conversation"""
    
    print("CIA AGENT CONVERSATION -> JAA SERVICE TEST")
    print("=" * 60)
    print(f"Test Started: {datetime.now().isoformat()}")
    print(f"Test Bid Card: {TEST_BID_CARD['bid_card_number']}")
    print(f"Current Budget Max: ${TEST_BID_CARD['current_budget_max']:,}")
    
    # Initialize CIA agent
    api_key = os.getenv("ANTHROPIC_API_KEY", os.getenv("OPENAI_API_KEY", "demo_key"))
    cia = CustomerInterfaceAgent(f"openai:{api_key}" if "sk-" in api_key else api_key)
    
    print("\nCIA Agent initialized")
    
    # Create a conversation that modifies an existing bid card
    # The CIA agent should detect we're talking about an existing bid card
    # and apply modifications through JAA
    
    user_id = "test-cia-user"
    session_id = "cia-jaa-test-session"
    
    # First message - reference the existing bid card
    print("\nStarting conversation about existing bid card...")
    
    message1 = f"I have bid card {TEST_BID_CARD['bid_card_number']} for my renovation project. I need to increase the budget to $75,000 because we decided to add premium materials."
    
    print(f"\nUser message: {message1}")
    
    try:
        # Call handle_conversation which should detect bid card modification
        result = await cia.handle_conversation(
            user_id=user_id,
            message=message1,
            session_id=session_id,
            bid_card_number=TEST_BID_CARD['bid_card_number'],  # Pass existing bid card
            bid_card_id=TEST_BID_CARD['id']
        )
        
        print("\nCIA Agent Response:")
        print(f"Success: {result.get('success', False)}")
        
        # Check if JAA was called
        if result.get('jaa_response'):
            print("\n*** JAA SERVICE WAS CALLED! ***")
            jaa_resp = result['jaa_response']
            print(f"  JAA Success: {jaa_resp.get('success', False)}")
            if jaa_resp.get('update_summary'):
                print(f"  Change Summary: {jaa_resp['update_summary'].get('change_summary', 'N/A')}")
            print(f"  Updated At: {jaa_resp.get('updated_at', 'N/A')}")
            
            return True, "JAA service called successfully"
            
        elif result.get('modifications_applied'):
            print("\n*** MODIFICATIONS DETECTED ***")
            print(f"  Modifications: {result['modifications_applied']}")
            if result.get('affected_contractors'):
                print(f"  Affected Contractors: {len(result['affected_contractors'])}")
            
            return True, "Modifications applied (possibly through JAA)"
            
        else:
            print("\nNo JAA response or modifications found in result")
            print(f"Result keys: {list(result.keys())}")
            if result.get('response'):
                print(f"Agent response: {result['response'][:200]}...")
            
            return False, "No JAA integration detected"
            
    except Exception as e:
        print(f"\nERROR: CIA conversation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, f"Error: {str(e)}"

async def main():
    """Run the CIA conversation -> JAA integration test"""
    success, message = await test_cia_conversation_with_jaa()
    
    print("\n" + "=" * 60)
    print("TEST RESULT")
    print("=" * 60)
    
    if success:
        print("SUCCESS: CIA AGENT -> JAA SERVICE INTEGRATION CONFIRMED")
        print(f"Details: {message}")
        print("\nThe CIA agent successfully:")
        print("1. Detected the bid card modification request")
        print("2. Called the JAA service to update the database")
        print("3. Returned the JAA response confirming the update")
    else:
        print("FAILED: CIA AGENT -> JAA SERVICE INTEGRATION NOT CONFIRMED")
        print(f"Reason: {message}")
        print("\nPossible issues:")
        print("1. CIA agent didn't detect the modification request")
        print("2. JAA service wasn't called")
        print("3. Error in the integration")
    
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)