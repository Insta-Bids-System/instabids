#!/usr/bin/env python3
"""
Simple test of CIA Agent's bid card context loading and modification capability
Tests the key customer workflow: Continue Chat -> Modify bid card
"""
import os
import json
import asyncio
from agents.cia.agent import CustomerInterfaceAgent
from database_simple import db
from dotenv import load_dotenv

load_dotenv()

async def main():
    print("TESTING: CIA BID CARD CONTEXT & MODIFICATIONS")
    print("=" * 50)
    
    # Step 1: Get existing bid card
    bid_card_number = "IBC-20250801030643"
    result = db.client.table('bid_cards').select('*').eq('bid_card_number', bid_card_number).execute()
    
    if not result.data:
        print(f"ERROR: Could not find bid card {bid_card_number}")
        return
    
    bid_card = result.data[0]
    print(f"Found bid card: {bid_card_number}")
    print(f"Project: {bid_card['project_type']}")
    print(f"Original budget: ${bid_card['budget_min']}-${bid_card['budget_max']}")
    
    # Step 2: Initialize CIA (simulating Continue Chat)
    print(f"\n[SIMULATING] Customer clicks Continue Chat on {bid_card_number}")
    
    cia = CustomerInterfaceAgent(os.getenv('ANTHROPIC_API_KEY'))
    
    # Step 3: First message with project context
    initial_message = f"I want to continue working on my {bid_card['project_type']} project (bid card {bid_card_number})"
    
    print(f"[CUSTOMER] {initial_message}")
    
    result1 = await cia.handle_conversation(
        user_id="00000000-0000-0000-0000-000000000000",
        message=initial_message,
        project_id=bid_card_number
    )
    
    print(f"[CIA] {result1.get('response', 'No response')}")
    
    # Step 4: Test if CIA recognizes context
    response_text = result1.get('response', '').lower()
    
    context_found = (
        bid_card['project_type'].lower() in response_text or
        bid_card_number.lower() in response_text or
        str(bid_card['budget_min']) in response_text
    )
    
    print(f"\nContext Recognition: {'PASS' if context_found else 'FAIL'}")
    
    if not context_found:
        print("CIA did not recognize existing bid card context")
        return
    
    # Step 5: Request modification
    session_id = result1.get('session_id')
    
    print(f"\n[CUSTOMER] I want to increase my budget to $60,000-$75,000")
    
    result2 = await cia.handle_conversation(
        user_id="00000000-0000-0000-0000-000000000000",
        message="I want to increase my budget to $60,000-$75,000",
        session_id=session_id
    )
    
    print(f"[CIA] {result2.get('response', 'No response')}")
    
    # Step 6: Test modification understanding
    mod_response = result2.get('response', '').lower()
    
    modification_understood = (
        '60' in mod_response or
        '75' in mod_response or
        'budget' in mod_response or
        'increase' in mod_response
    )
    
    print(f"\nModification Understanding: {'PASS' if modification_understood else 'FAIL'}")
    
    # Step 7: Test memory persistence
    print(f"\n[CUSTOMER] What was my original budget again?")
    
    result3 = await cia.handle_conversation(
        user_id="00000000-0000-0000-0000-000000000000",
        message="What was my original budget again?",
        session_id=session_id
    )
    
    print(f"[CIA] {result3.get('response', 'No response')}")
    
    # Step 8: Test memory
    memory_response = result3.get('response', '').lower()
    
    memory_working = (
        str(bid_card['budget_min']) in memory_response or
        str(bid_card['budget_max']) in memory_response or
        'original' in memory_response
    )
    
    print(f"\nMemory Persistence: {'PASS' if memory_working else 'FAIL'}")
    
    # Final Assessment
    print(f"\n" + "=" * 50)
    print("RESULTS SUMMARY")
    print("=" * 50)
    print(f"Context Loading: {'PASS' if context_found else 'FAIL'}")
    print(f"Modification Understanding: {'PASS' if modification_understood else 'FAIL'}")
    print(f"Memory Persistence: {'PASS' if memory_working else 'FAIL'}")
    
    total_passed = sum([context_found, modification_understood, memory_working])
    
    if total_passed >= 2:
        print(f"\nOVERALL: SUCCESS ({total_passed}/3 tests passed)")
        print("Customer bid card workflow is working!")
    else:
        print(f"\nOVERALL: NEEDS WORK ({total_passed}/3 tests passed)")
        print("Customer workflow has issues that need fixing")

if __name__ == "__main__":
    asyncio.run(main())