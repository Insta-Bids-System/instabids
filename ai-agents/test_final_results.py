#!/usr/bin/env python3
"""
Final Results Test - Simple Version
Tests core functionality without Unicode issues
"""

import asyncio
from agents.intelligent_messaging_agent import process_intelligent_message

async def test_final_results():
    """Test final results"""
    
    print("INTELLIGENT MESSAGING SYSTEM - FINAL VERIFICATION")
    print("=" * 55)
    
    tests = [
        {
            "name": "Contact Info Block",
            "content": "My email is john@contractor.com and phone is 555-123-4567",
            "sender_type": "contractor",
            "expected_blocked": True
        },
        {
            "name": "Platform Bypass Block", 
            "content": "Let's take this off-platform and meet for coffee",
            "sender_type": "contractor",
            "expected_blocked": True
        },
        {
            "name": "Legitimate Content Allow",
            "content": "I can install kitchen cabinets for $15,000 in 2-3 weeks",
            "sender_type": "contractor",
            "expected_blocked": False
        },
        {
            "name": "Scope Change Detection",
            "content": "Let's use granite instead of quartz and add a backsplash",
            "sender_type": "homeowner",
            "expected_blocked": False
        }
    ]
    
    passed = 0
    total = len(tests)
    
    for i, test in enumerate(tests, 1):
        print(f"\nTest {i}: {test['name']}")
        print("-" * 30)
        
        result = await process_intelligent_message(
            content=test["content"],
            sender_type=test["sender_type"],
            sender_id="test-user-123",
            bid_card_id="test-bid-card"
        )
        
        blocked = not result['approved']
        expected = test["expected_blocked"]
        
        print(f"Content: '{test['content'][:50]}...'")
        print(f"Blocked: {blocked} (Expected: {expected})")
        print(f"Decision: {result['agent_decision']}")
        print(f"Threats: {result['threats_detected']}")
        
        if blocked == expected:
            print("PASS")
            passed += 1
        else:
            print("FAIL")
    
    print(f"\n" + "=" * 55)
    print(f"FINAL RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: All tests passed - System ready for production!")
    else:
        print(f"WARNING: {total - passed} tests failed")

if __name__ == "__main__":
    asyncio.run(test_final_results())