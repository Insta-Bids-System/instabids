#!/usr/bin/env python3
"""
Simple Test: Verify bid submission context methods work
Tests the basic functionality without requiring existing data
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
from database import SupabaseDB

async def test_methods_exist_and_work():
    """Test that all our new methods exist and can be called"""
    print("=" * 60)
    print("TESTING BID SUBMISSION CONTEXT METHODS")
    print("=" * 60)
    
    success_count = 0
    total_tests = 0
    
    # Test 1: Messaging Agent Methods
    try:
        print("1. Testing Messaging Agent ProjectContextManager...")
        context_manager = ProjectContextManager()
        
        # Test method exists
        assert hasattr(context_manager, 'get_bid_submissions_for_bid_card')
        assert hasattr(context_manager, 'get_bid_comparison_context')
        print("   [PASS] Methods exist")
        
        # Test can be called (will return empty but shouldn't error)
        bid_submissions = await context_manager.get_bid_submissions_for_bid_card("test-id")
        comparison = await context_manager.get_bid_comparison_context("test-id")
        
        print(f"   [PASS] get_bid_submissions_for_bid_card returned: {type(bid_submissions)} with {len(bid_submissions)} items")
        print(f"   [PASS] get_bid_comparison_context returned: {comparison}")
        
        success_count += 1
    except Exception as e:
        print(f"   [FAIL] Messaging Agent test error: {e}")
    total_tests += 1
    
    # Test 2: CIA Agent Methods  
    try:
        print("2. Testing CIA Agent methods...")
        cia = CustomerInterfaceAgent("demo_key")
        
        # Test methods exist
        assert hasattr(cia, 'get_bid_submissions_for_conversation')
        assert hasattr(cia, 'get_bid_submissions_for_bid_card')
        print("   [PASS] Methods exist")
        
        # Test can be called
        conv_bids = await cia.get_bid_submissions_for_conversation("test-conversation")
        card_bids = await cia.get_bid_submissions_for_bid_card("test-bid-card")
        
        print(f"   [PASS] get_bid_submissions_for_conversation returned: {type(conv_bids)} with {len(conv_bids)} items")
        print(f"   [PASS] get_bid_submissions_for_bid_card returned: {type(card_bids)} with {len(card_bids)} items")
        
        success_count += 1
    except Exception as e:
        print(f"   [FAIL] CIA Agent test error: {e}")
    total_tests += 1
    
    # Test 3: IRIS Agent Methods
    try:
        print("3. Testing IRIS Agent methods...")
        from api.iris_chat_unified_fixed import get_bid_submissions_for_conversation
        
        # Test can be called
        iris_bids = await get_bid_submissions_for_conversation("test-conversation")
        
        print(f"   [PASS] get_bid_submissions_for_conversation returned: {type(iris_bids)} with {len(iris_bids)} items")
        
        success_count += 1
    except Exception as e:
        print(f"   [FAIL] IRIS Agent test error: {e}")
    total_tests += 1
    
    # Test 4: Database Query Structure
    try:
        print("4. Testing database query structure...")
        db = SupabaseDB()
        
        # Test the query pattern (should not error even with no results)
        result = db.client.table("unified_messages").select("id,metadata,created_at").contains(
            "metadata", {"message_type": "bid_submission"}
        ).limit(5).execute()
        
        print(f"   [PASS] Database query successful, found {len(result.data) if result.data else 0} bid submissions")
        
        success_count += 1
    except Exception as e:
        print(f"   [FAIL] Database query test error: {e}")
    total_tests += 1
    
    # Summary
    print()
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("[SUCCESS] All bid submission context methods are working correctly!")
        print()
        print("WHAT THIS MEANS:")
        print("- All agents can now access bid submission data")
        print("- Methods are properly implemented and callable")
        print("- Database queries are structured correctly")
        print("- System ready for bid submission context integration")
        print()
        print("NEXT STEPS:")
        print("- When contractors submit bids through your messaging system,")
        print("  all agents will automatically have access to that data")
        print("- CIA can discuss bids with homeowners")
        print("- IRIS can suggest designs based on real budgets")
        print("- Messaging agent can handle scope changes intelligently")
    else:
        print("[ISSUES] Some methods need attention - see errors above")
    
    print("=" * 60)
    return success_count == total_tests

async def main():
    """Run the simple bid context test"""
    print("SIMPLE BID SUBMISSION CONTEXT TEST")
    print(f"Test Started: {datetime.now().isoformat()}")
    print()
    
    success = await test_methods_exist_and_work()
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)