#!/usr/bin/env python3
"""
Simple Test of Intelligent Messaging System
Tests core functionality without Unicode emojis
"""

import asyncio
from agents.intelligent_messaging_agent import process_intelligent_message

async def test_intelligent_messaging_simple():
    """Test intelligent messaging system"""
    
    print("Testing Intelligent Messaging System...")
    print("=" * 50)
    
    # Test 1: Contact information sharing attempt
    print("\nTest 1: Contact Information Detection")
    print("-" * 40)
    result1 = await process_intelligent_message(
        content="Hi! My email is john@contractor.com and my phone is 555-123-4567. Please contact me directly.",
        sender_type="contractor",
        sender_id="test-contractor-123",
        bid_card_id="test-bid-card-123"
    )
    
    print(f"Content: 'Hi! My email is john@contractor.com...'")
    print(f"Approved: {result1['approved']}")
    print(f"Agent Decision: {result1['agent_decision']}")
    print(f"Threats Detected: {result1['threats_detected']}")
    print(f"Confidence Score: {result1['confidence_score']}")
    
    # Test 2: Legitimate project discussion
    print("\nTest 2: Legitimate Project Discussion")
    print("-" * 40)
    result2 = await process_intelligent_message(
        content="I can install kitchen cabinets for $15,000. Timeline is 2-3 weeks. Do you have color preferences?",
        sender_type="contractor", 
        sender_id="test-contractor-456",
        bid_card_id="test-bid-card-123"
    )
    
    print(f"Content: 'I can install kitchen cabinets for $15,000...'")
    print(f"Approved: {result2['approved']}")
    print(f"Agent Decision: {result2['agent_decision']}")
    print(f"Threats Detected: {result2['threats_detected']}")
    print(f"Confidence Score: {result2['confidence_score']}")
    
    print("\n" + "=" * 50)
    print("INTELLIGENT MESSAGING DIRECT TEST COMPLETE!")
    
    # Summary
    contact_blocked = not result1['approved'] or 'contact_info' in result1['threats_detected']
    legitimate_allowed = result2['approved'] and result2['agent_decision'] == 'allow'
    
    print(f"\nTest Results:")
    print(f"- Contact Info Blocked: {'PASS' if contact_blocked else 'FAIL'}")
    print(f"- Legitimate Content Allowed: {'PASS' if legitimate_allowed else 'FAIL'}")
    
    if contact_blocked and legitimate_allowed:
        print("\nSUCCESS: Intelligent messaging system working correctly!")
    else:
        print("\nWARNING: Some issues detected with messaging system")

if __name__ == "__main__":
    asyncio.run(test_intelligent_messaging_simple())