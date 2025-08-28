#!/usr/bin/env python3
"""
Test if BSA actually pulls REAL bid cards from the database
and if the contractor AI memory system is working
"""

import asyncio
from datetime import datetime
from agents.bsa.enhanced_tools import search_available_bid_cards
from memory.contractor_ai_memory import ContractorAIMemory
from database_simple import db

async def test_real_bid_cards():
    """Test if BSA pulls real bid cards from database"""
    
    print("TESTING BSA REAL BID CARD RETRIEVAL")
    print("=" * 50)
    
    # First, check what real bid cards exist in database
    print("\n1. Checking actual bid cards in database...")
    
    result = db.client.table("bid_cards").select("id, title, project_type, location_zip, status").execute()
    
    if result.data:
        print(f"Found {len(result.data)} real bid cards in database:")
        for i, card in enumerate(result.data[:5]):  # Show first 5
            print(f"  {i+1}. {card['title']} ({card['project_type']}) - ZIP: {card['location_zip']} - Status: {card['status']}")
    else:
        print("  No bid cards found in database")
    
    # Now test BSA search function
    print("\n2. Testing BSA bid card search function...")
    
    # Use a real ZIP code from the database if available
    test_zip = "33101"  # Miami ZIP
    if result.data and result.data[0].get('location_zip'):
        test_zip = str(result.data[0]['location_zip'])
        print(f"Using ZIP {test_zip} from actual bid card")
    
    # Call the BSA search function
    search_result = search_available_bid_cards.invoke({
        "contractor_zip": test_zip,
        "radius_miles": 50,
        "project_keywords": ""
    })
    
    print(f"\nBSA Search Results:")
    print(f"  Success: {search_result.get('success')}")
    print(f"  Total found: {search_result.get('total_found')}")
    
    if search_result.get('bid_cards'):
        print(f"  Returned {len(search_result['bid_cards'])} bid cards:")
        for i, card in enumerate(search_result['bid_cards'][:3]):
            print(f"    {i+1}. {card.get('title')} - {card.get('distance_miles', 'N/A')} miles away")
    else:
        print("  No bid cards returned by BSA search")
    
    return search_result.get('success', False) and search_result.get('total_found', 0) > 0

async def test_contractor_ai_memory():
    """Test if the ContractorAIMemory system is actually working"""
    
    print("\n\nTESTING CONTRACTOR AI MEMORY SYSTEM")
    print("=" * 50)
    
    ai_memory = ContractorAIMemory()
    contractor_id = "test-contractor-ai-memory"
    
    # Test 1: Save some contractor data
    print("\n1. Testing AI memory save...")
    
    conversation_data = {
        'input': "I'm Bob from Bob's Plumbing in Tampa. We do residential and commercial plumbing.",
        'response': "Welcome Bob! I see you specialize in plumbing services.",
        'context': "Initial contractor introduction",
        'project_type': 'plumbing',
        'bid_amount': None,
        'timeline': None
    }
    
    # Save to AI memory
    success = await ai_memory.update_contractor_memory(contractor_id, conversation_data)
    print(f"  Save result: {success}")
    
    # Test 2: Retrieve contractor AI memory
    print("\n2. Testing AI memory retrieval...")
    
    retrieved = await ai_memory.get_contractor_memory(contractor_id)
    
    if retrieved:
        print(f"  Retrieved AI memory: {len(retrieved)} records")
        if retrieved.get('insights'):
            print(f"  Insights found: {retrieved['insights']}")
        if retrieved.get('company_info'):
            print(f"  Company info: {retrieved['company_info']}")
    else:
        print("  No AI memory retrieved")
    
    return bool(retrieved)

async def test_real_contractor_bids():
    """Check if there are any real contractor bids or quotes in the system"""
    
    print("\n\nTESTING REAL CONTRACTOR BIDS/QUOTES")
    print("=" * 50)
    
    # Check contractor_bids table
    print("\n1. Checking contractor_bids table...")
    bids_result = db.client.table("contractor_bids").select("*").limit(5).execute()
    
    if bids_result.data:
        print(f"  Found {len(bids_result.data)} contractor bids")
        for bid in bids_result.data:
            print(f"    Bid: ${bid.get('bid_amount')} for bid_card {bid.get('bid_card_id')[:8]}...")
    else:
        print("  No contractor bids found")
    
    # Check contractor_proposals table
    print("\n2. Checking contractor_proposals table...")
    proposals_result = db.client.table("contractor_proposals").select("*").limit(5).execute()
    
    if proposals_result.data:
        print(f"  Found {len(proposals_result.data)} contractor proposals")
    else:
        print("  No contractor proposals found")
    
    # Check bid_cards for submitted_bids in bid_document
    print("\n3. Checking bid_cards.bid_document.submitted_bids...")
    cards_with_bids = db.client.table("bid_cards").select("id, bid_document").execute()
    
    cards_with_actual_bids = 0
    for card in (cards_with_bids.data or []):
        if card.get('bid_document') and card['bid_document'].get('submitted_bids'):
            cards_with_actual_bids += 1
    
    print(f"  Found {cards_with_actual_bids} bid cards with submitted bids")
    
    return (bids_result.data or proposals_result.data or cards_with_actual_bids > 0)

async def main():
    """Run all tests"""
    
    print("BSA REAL DATA INTEGRATION TESTS")
    print("=" * 60)
    
    # Test 1: Real bid cards
    bid_cards_working = await test_real_bid_cards()
    
    # Test 2: AI memory system
    ai_memory_working = await test_contractor_ai_memory()
    
    # Test 3: Real contractor bids
    has_real_bids = await test_real_contractor_bids()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY:")
    print(f"  Real bid cards retrieved: {'YES' if bid_cards_working else 'NO'}")
    print(f"  AI memory system working: {'YES' if ai_memory_working else 'NO'}")
    print(f"  Real contractor bids exist: {'YES' if has_real_bids else 'NO'}")
    
    print("\nREALITY CHECK:")
    if not bid_cards_working:
        print("  - BSA is NOT pulling real bid cards from database")
    if not ai_memory_working:
        print("  - Contractor AI memory is NOT functioning")
    if not has_real_bids:
        print("  - No actual contractor bids/quotes exist in system")

if __name__ == "__main__":
    asyncio.run(main())