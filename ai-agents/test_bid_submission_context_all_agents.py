#!/usr/bin/env python3
"""
Test Bid Submission Context Access Across All Agents
Verifies CIA, IRIS, and Messaging agents can access bid submission data
"""

import asyncio
import json
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test imports
from agents.cia.agent import CustomerInterfaceAgent
from agents.intelligent_messaging_agent import ProjectContextManager
from api.iris_chat_unified_fixed import get_bid_submissions_for_conversation, get_conversation_context_direct

# Database
from database import SupabaseDB

# Test data - using a known conversation/bid card with bid submissions
TEST_CONVERSATION_ID = "test-conversation-123"
TEST_BID_CARD_ID = "93c216f1-1e3f-490a-899d-ae2a236652a4"  # Known bid card

async def test_messaging_agent_bid_access():
    """Test that messaging agent can access bid submissions"""
    print("=" * 60)
    print("TESTING MESSAGING AGENT BID ACCESS")
    print("=" * 60)
    
    try:
        context_manager = ProjectContextManager()
        
        # Test project context with bid submissions
        project_context = await context_manager.get_project_context(TEST_BID_CARD_ID)
        
        print(f"[PASS] Project Context Retrieved: {bool(project_context)}")
        print(f"   - Bid submissions in context: {'bid_submissions' in project_context}")
        if project_context.get("bid_submissions"):
            print(f"   - Total bids found: {len(project_context['bid_submissions'])}")
            print(f"   - Bids received count: {project_context.get('bids_received_count', 0)}")
            print(f"   - Highest bid: ${project_context.get('highest_bid', 0):,.2f}")
            print(f"   - Lowest bid: ${project_context.get('lowest_bid', 0):,.2f}")
        else:
            print("   - No bid submissions found")
        
        # Test bid comparison context
        comparison_context = await context_manager.get_bid_comparison_context(TEST_BID_CARD_ID)
        print(f"[PASS] Bid Comparison Context: {comparison_context.get('has_bids', False)}")
        if comparison_context.get("has_bids"):
            print(f"   - Total bids: {comparison_context['total_bids']}")
            print(f"   - Bid range: {comparison_context['bid_range']}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] MESSAGING AGENT ERROR: {e}")
        return False

async def test_cia_agent_bid_access():
    """Test that CIA agent can access bid submissions"""
    print("=" * 60)
    print("TESTING CIA AGENT BID ACCESS")
    print("=" * 60)
    
    try:
        # Initialize CIA agent
        cia = CustomerInterfaceAgent("demo_key")  # Demo mode for testing
        
        # Test bid submission retrieval by conversation
        bid_submissions = await cia.get_bid_submissions_for_conversation(TEST_CONVERSATION_ID)
        print(f"[PASS] CIA Get Bids by Conversation: {len(bid_submissions)} bids found")
        
        # Test bid submission retrieval by bid card
        bid_card_bids = await cia.get_bid_submissions_for_bid_card(TEST_BID_CARD_ID)
        print(f"[PASS] CIA Get Bids by Bid Card: {len(bid_card_bids)} bids found")
        
        if bid_card_bids:
            for i, bid in enumerate(bid_card_bids[:3]):  # Show first 3
                amount_text = f"${bid['amount']:,.2f}" if bid['amount'] else "Amount pending"
                print(f"   - Bid {i+1}: {amount_text} from {bid['contractor_id']}")
                if bid['timeline']:
                    print(f"     Timeline: {bid['timeline']}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] CIA AGENT ERROR: {e}")
        return False

async def test_iris_agent_bid_access():
    """Test that IRIS agent can access bid submissions"""
    print("=" * 60)
    print("TESTING IRIS AGENT BID ACCESS")
    print("=" * 60)
    
    try:
        # Test IRIS bid submission retrieval
        iris_bid_submissions = await get_bid_submissions_for_conversation(TEST_CONVERSATION_ID)
        print(f"[PASS] IRIS Get Bids by Conversation: {len(iris_bid_submissions)} bids found")
        
        # Test IRIS conversation context with bid submissions
        context = await get_conversation_context_direct(TEST_CONVERSATION_ID)
        print(f"[PASS] IRIS Context Retrieved: {bool(context)}")
        print(f"   - Has bid_submissions key: {'bid_submissions' in context}")
        print(f"   - Bid submissions in context: {len(context.get('bid_submissions', []))}")
        
        if context.get("bid_submissions"):
            for i, bid in enumerate(context["bid_submissions"][:2]):  # Show first 2
                amount_text = f"${bid['amount']:,.2f}" if bid['amount'] else "Amount pending"
                print(f"   - IRIS Context Bid {i+1}: {amount_text}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] IRIS AGENT ERROR: {e}")
        return False

async def test_unified_messaging_direct():
    """Test direct unified messaging system queries"""
    print("=" * 60)
    print("TESTING UNIFIED MESSAGING SYSTEM DIRECTLY")
    print("=" * 60)
    
    try:
        db = SupabaseDB()
        
        # Direct query for bid submissions
        result = db.client.table("unified_messages").select("*").contains(
            "metadata", {"message_type": "bid_submission"}
        ).execute()
        
        print(f"[PASS] Total bid submission messages in system: {len(result.data) if result.data else 0}")
        
        # Check for test bid card specifically
        bid_card_submissions = []
        if result.data:
            for message in result.data:
                metadata = message.get("metadata", {})
                if (metadata.get("message_type") == "bid_submission" and 
                    metadata.get("bid_data", {}).get("bid_card_id") == TEST_BID_CARD_ID):
                    bid_card_submissions.append(message)
        
        print(f"[PASS] Bid submissions for test bid card: {len(bid_card_submissions)}")
        
        if bid_card_submissions:
            for i, submission in enumerate(bid_card_submissions[:2]):
                bid_data = submission["metadata"]["bid_data"]
                amount = bid_data.get("amount", 0)
                contractor = bid_data.get("contractor_id", "Unknown")
                print(f"   - Direct Query Bid {i+1}: ${amount:,.2f} from {contractor}")
        
        return len(bid_card_submissions) > 0
        
    except Exception as e:
        print(f"[FAIL] UNIFIED MESSAGING ERROR: {e}")
        return False

async def main():
    """Run all bid submission context tests"""
    print("STARTING BID SUBMISSION CONTEXT TESTS")
    print("=" * 60)
    print(f"Test Started: {datetime.now().isoformat()}")
    print(f"Test Conversation ID: {TEST_CONVERSATION_ID}")
    print(f"Test Bid Card ID: {TEST_BID_CARD_ID}")
    print()
    
    # Run all tests
    results = {}
    
    results["unified_messaging"] = await test_unified_messaging_direct()
    results["messaging_agent"] = await test_messaging_agent_bid_access()
    results["cia_agent"] = await test_cia_agent_bid_access()
    results["iris_agent"] = await test_iris_agent_bid_access()
    
    # Summary
    print()
    print("=" * 60)
    print("FINAL TEST RESULTS")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{test_name.upper()}: {status}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("ALL TESTS PASSED - All agents can access bid submission context!")
    else:
        print("SOME TESTS FAILED - Check errors above")
    
    print("=" * 60)
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)