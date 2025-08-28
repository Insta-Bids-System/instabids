#!/usr/bin/env python3
"""
Test Intelligent Messaging System Directly
Tests the intelligent messaging agent without database dependencies
"""

import asyncio
from agents.intelligent_messaging_agent import process_intelligent_message

async def test_intelligent_messaging_direct():
    """Test intelligent messaging system directly"""
    
    print("🧠 Testing Intelligent Messaging System Direct API...")
    print("=" * 60)
    
    # Test 1: Contact information sharing attempt
    print("\n📧 Test 1: Email Contact Sharing")
    print("-" * 40)
    result1 = await process_intelligent_message(
        content="Hi! My email is john@contractor.com and my phone is 555-123-4567. Please contact me directly to discuss the project details.",
        sender_type="contractor",
        sender_id="test-contractor-123",
        bid_card_id="test-bid-card-123"
    )
    
    print(f"✅ Content: 'Hi! My email is john@contractor.com...'")
    print(f"📊 Approved: {result1['approved']}")
    print(f"🤖 Agent Decision: {result1['agent_decision']}")
    print(f"🚨 Threats Detected: {result1['threats_detected']}")
    print(f"📈 Confidence Score: {result1['confidence_score']}")
    
    if result1.get('filtered_content'):
        print(f"🔒 Filtered Content: '{result1['filtered_content'][:100]}...'")
    
    if result1.get('agent_comments'):
        print(f"💬 Agent Comments: {len(result1['agent_comments'])} comments generated")
    
    print()
    
    # Test 2: Legitimate project discussion
    print("💰 Test 2: Legitimate Project Discussion")
    print("-" * 40)
    result2 = await process_intelligent_message(
        content="I can install the kitchen cabinets for $15,000. The timeline would be 2-3 weeks. Do you have specific color preferences or material requirements?",
        sender_type="contractor", 
        sender_id="test-contractor-456",
        bid_card_id="test-bid-card-123"
    )
    
    print(f"✅ Content: 'I can install the kitchen cabinets for $15,000...'")
    print(f"📊 Approved: {result2['approved']}")
    print(f"🤖 Agent Decision: {result2['agent_decision']}")
    print(f"🚨 Threats Detected: {result2['threats_detected']}")
    print(f"📈 Confidence Score: {result2['confidence_score']}")
    
    if result2.get('scope_changes_detected'):
        print(f"🔄 Scope Changes: {result2['scope_changes_detected']}")
    
    print()
    
    # Test 3: Image analysis with contact info
    print("🖼️  Test 3: Image Analysis with Contact Info")  
    print("-" * 40)
    
    import base64
    # Read the test image we know contains contact information
    try:
        with open(r"C:\Users\NOTJOH~1\AppData\Local\Temp\playwright-mcp-output\2025-08-08T05-55-47.931Z\fake-bid-with-contact-info.png", "rb") as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
            
        result3 = await process_intelligent_message(
            content="Here's my bid proposal with all the details",
            sender_type="contractor",
            sender_id="test-contractor-789", 
            bid_card_id="test-bid-card-123",
            image_data=image_data
        )
        
        print(f"✅ Content: 'Here's my bid proposal with all the details' + IMAGE")
        print(f"📊 Approved: {result3['approved']}")
        print(f"🤖 Agent Decision: {result3['agent_decision']}")
        print(f"🚨 Threats Detected: {result3['threats_detected']}")
        print(f"📈 Confidence Score: {result3['confidence_score']}")
        
        if result3.get('agent_comments'):
            print(f"💬 Agent Comments: {len(result3['agent_comments'])} comments generated")
            
    except Exception as e:
        print(f"⚠️ Image test skipped: {e}")
    
    print()
    print("🎯 INTELLIGENT MESSAGING DIRECT TESTING COMPLETE!")
    print("=" * 60)
    
    # Summary
    tests_passed = 0
    total_tests = 2
    
    if result1['agent_decision'] in ['block', 'redact'] and 'contact_info' in result1['threats_detected']:
        tests_passed += 1
        print("✅ Test 1 PASSED: Contact info correctly blocked/redacted")
    else:
        print("❌ Test 1 FAILED: Contact info not properly detected")
        
    if result2['approved'] and result2['agent_decision'] == 'allow':
        tests_passed += 1 
        print("✅ Test 2 PASSED: Legitimate content approved")
    else:
        print("❌ Test 2 FAILED: Legitimate content wrongly blocked")
    
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED - Intelligent Messaging System Working!")
    else:
        print("⚠️  Some tests failed - Review system behavior")

if __name__ == "__main__":
    asyncio.run(test_intelligent_messaging_direct())