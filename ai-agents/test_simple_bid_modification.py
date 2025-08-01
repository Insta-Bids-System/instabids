"""
Simple test for bid card context loading and modification
"""
import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.cia.agent import CustomerInterfaceAgent

async def test_bid_card_workflow():
    """Test basic bid card context loading and modification"""
    print("TESTING BID CARD CONTEXT AND MODIFICATION")
    print("="*50)
    
    # Initialize CIA agent
    cia = CustomerInterfaceAgent(os.getenv('ANTHROPIC_API_KEY'))
    user_id = "00000000-0000-0000-0000-000000000000"
    bid_card = "IBC-20250801030643"
    
    # Test 1: Load bid card context
    print(f"\nTEST 1: Loading bid card {bid_card}")
    result1 = await cia.handle_conversation(
        user_id=user_id,
        message=f"I want to continue working on my kitchen project (bid card {bid_card})",
        project_id=bid_card
    )
    
    print(f"Response recognized bid card: {'kitchen' in result1['response'].lower()}")
    print(f"Has bid card context: {result1.get('has_bid_card_context', False)}")
    session_id = result1.get('session_id')
    
    # Test 2: Modify the bid card
    print(f"\nTEST 2: Modifying budget")
    result2 = await cia.handle_conversation(
        user_id=user_id,
        message="I want to increase my budget to $60,000-$75,000",
        session_id=session_id
    )
    
    modification_success = (
        'updated' in result2['response'].lower() or 
        'changed' in result2['response'].lower() or
        'modification' in result2['response'].lower()
    )
    print(f"Modification response: {modification_success}")
    
    # Test 3: Check memory persistence
    print(f"\nTEST 3: Memory persistence check")
    result3 = await cia.handle_conversation(
        user_id=user_id,
        message="What's my current budget?",
        session_id=session_id
    )
    
    budget_remembered = (
        '60' in result3['response'] or 
        '75' in result3['response'] or
        'sixty' in result3['response'].lower()
    )
    print(f"Budget remembered: {budget_remembered}")
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY:")
    print(f"- Bid card context loading: {'PASS' if 'kitchen' in result1['response'].lower() else 'FAIL'}")
    print(f"- Modification capability: {'PASS' if modification_success else 'FAIL'}")
    print(f"- Memory persistence: {'PASS' if budget_remembered else 'FAIL'}")
    
    return all([
        'kitchen' in result1['response'].lower(),
        modification_success,
        budget_remembered
    ])

if __name__ == "__main__":
    success = asyncio.run(test_bid_card_workflow())
    print(f"\nOVERALL: {'PASS' if success else 'FAIL'}")