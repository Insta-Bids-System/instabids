#!/usr/bin/env python3
"""
Test CIA Agent calling JAA service with real bid card
This will prove CIA -> JAA integration is working
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

async def test_cia_jaa_integration():
    """Test CIA Agent calling JAA service"""
    
    print("CIA AGENT -> JAA SERVICE INTEGRATION TEST")
    print("=" * 60)
    print(f"Test Started: {datetime.now().isoformat()}")
    print(f"Test Bid Card: {TEST_BID_CARD['bid_card_number']}")
    print(f"Current Budget Max: ${TEST_BID_CARD['current_budget_max']:,}")
    
    # Initialize CIA agent
    api_key = os.getenv("ANTHROPIC_API_KEY", os.getenv("OPENAI_API_KEY", "demo_key"))
    cia = CustomerInterfaceAgent(f"openai:{api_key}" if "sk-" in api_key else api_key)
    
    print("\nCIA Agent initialized")
    
    # Test modification request - increase budget to $70,000
    new_budget = 70000
    print(f"\nRequesting budget change to ${new_budget:,}")
    
    try:
        # Call CIA's handle_modification which should call JAA
        result = await cia.handle_modification(
            message=f"Please increase the budget to ${new_budget:,} for this renovation project",
            bid_card_number=TEST_BID_CARD['bid_card_number'],
            bid_card_id=TEST_BID_CARD['id'],
            user_id="test-cia-user",
            session_id="cia-jaa-test-session"
        )
        
        print("\nCIA Agent Response:")
        print(f"Success: {result.get('success', False)}")
        
        if result.get('jaa_response'):
            print("\nJAA Response received:")
            jaa_resp = result['jaa_response']
            print(f"  JAA Success: {jaa_resp.get('success', False)}")
            if jaa_resp.get('update_summary'):
                print(f"  Change Summary: {jaa_resp['update_summary'].get('change_summary', 'N/A')}")
            print(f"  Updated At: {jaa_resp.get('updated_at', 'N/A')}")
            
            return True
        else:
            print("ERROR: No JAA response in CIA result")
            if result.get('error'):
                print(f"Error: {result['error']}")
            return False
            
    except Exception as e:
        print(f"ERROR: CIA Agent test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the CIA -> JAA integration test"""
    success = await test_cia_jaa_integration()
    
    print("\n" + "=" * 60)
    if success:
        print("SUCCESS: CIA AGENT -> JAA SERVICE INTEGRATION WORKING")
        print("The CIA agent successfully called the JAA service")
        print("to update the bid card in the database.")
    else:
        print("FAILED: CIA AGENT -> JAA SERVICE INTEGRATION NOT WORKING")
        print("The CIA agent failed to call the JAA service.")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)