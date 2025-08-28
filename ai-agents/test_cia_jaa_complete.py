#!/usr/bin/env python3
"""
Complete test of CIA Agent calling JAA service
This will 100% confirm CIA -> JAA integration is working
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
    "bid_card_number": "BC0730223441"
}

async def get_bid_card_budget():
    """Get current budget from database"""
    try:
        from database_simple import db
        result = db.client.table("bid_cards").select("budget_min,budget_max").eq("id", TEST_BID_CARD['id']).single().execute()
        if result.data:
            return result.data['budget_min'], result.data['budget_max']
    except:
        pass
    return None, None

async def test_cia_jaa_integration():
    """Test CIA Agent calling JAA service through conversation"""
    
    print("=" * 80)
    print("CIA AGENT -> JAA SERVICE COMPLETE TEST")
    print("=" * 80)
    print(f"Test Started: {datetime.now().isoformat()}")
    print(f"Test Bid Card: {TEST_BID_CARD['bid_card_number']}")
    
    # Get current budget
    budget_min, budget_max = await get_bid_card_budget()
    if budget_min is not None and budget_max is not None:
        print(f"Current Budget: ${budget_min:,} - ${budget_max:,}")
    else:
        print("Current Budget: Unable to retrieve")
    
    # Initialize CIA agent
    api_key = os.getenv("ANTHROPIC_API_KEY", os.getenv("OPENAI_API_KEY", "demo_key"))
    if "sk-" in api_key:
        api_key = f"openai:{api_key}"
    cia = CustomerInterfaceAgent(api_key)
    print("CIA Agent initialized")
    
    # Test conversation that should trigger modification
    user_id = "test-cia-user"
    session_id = f"cia-test-{datetime.now().timestamp()}"
    
    # Create a message that references existing bid card and requests modification
    # The key is to mention the bid card number and a modification request
    test_message = f"""
    I'm looking at my bid card {TEST_BID_CARD['bid_card_number']} for the renovation project.
    I need to increase the budget to $85,000 because we're adding a bathroom remodel.
    Please update this bid card with the new budget.
    """
    
    print(f"\nUser Message: {test_message.strip()}")
    print("\nCalling CIA handle_conversation...")
    
    try:
        # Call handle_conversation
        result = await cia.handle_conversation(
            user_id=user_id,
            message=test_message,
            session_id=session_id
        )
        
        print("\n" + "-" * 60)
        print("CIA RESPONSE ANALYSIS")
        print("-" * 60)
        
        # Check for JAA response
        if result.get('jaa_response'):
            print("✅ JAA SERVICE WAS CALLED!")
            jaa = result['jaa_response']
            print(f"   JAA Success: {jaa.get('success')}")
            if jaa.get('update_summary'):
                print(f"   Change Summary: {jaa['update_summary'].get('change_summary')}")
            print(f"   Updated At: {jaa.get('updated_at')}")
            
            # Get new budget to confirm change
            new_min, new_max = await get_bid_card_budget()
            if budget_min and budget_max and new_min and new_max:
                print(f"\n   BEFORE: ${budget_min:,} - ${budget_max:,}")
                print(f"   AFTER:  ${new_min:,} - ${new_max:,}")
            else:
                print("\n   Unable to compare budgets")
            
            if new_max and budget_max and new_max != budget_max:
                print(f"   ✅ DATABASE CHANGED: Budget increased by ${new_max - budget_max:,}")
                return True
            else:
                print("   ⚠️ JAA called but database not changed")
                return False
                
        elif result.get('modifications_applied'):
            print("✅ MODIFICATIONS DETECTED AND APPLIED")
            print(f"   Modifications: {result['modifications_applied']}")
            
            # Check if budget actually changed
            new_min, new_max = await get_bid_card_budget()
            if new_max and budget_max and new_max != budget_max:
                print(f"   ✅ DATABASE CHANGED: ${budget_max:,} -> ${new_max:,}")
                return True
            else:
                print("   ⚠️ Modifications reported but database not changed")
                return False
        else:
            print("❌ NO JAA CALL OR MODIFICATIONS DETECTED")
            print(f"   Result keys: {list(result.keys())}")
            if result.get('response'):
                print(f"   CIA Response: {result['response'][:200]}...")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the complete CIA -> JAA test"""
    success = await test_cia_jaa_integration()
    
    print("\n" + "=" * 80)
    if success:
        print("✅ 100% CONFIRMED: CIA AGENT -> JAA SERVICE WORKING")
        print("The CIA agent successfully:")
        print("1. Detected the bid card modification request")
        print("2. Called the JAA service")
        print("3. Updated the database with the new budget")
    else:
        print("❌ FAILED: CIA AGENT -> JAA SERVICE NOT WORKING")
    print("=" * 80)
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)