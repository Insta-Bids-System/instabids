"""
COMPLETE END-TO-END TEST OF BID SUBMISSION CONTACT FILTERING
This verifies the entire system works from submission to storage
"""

import asyncio
import uuid
from datetime import datetime
from agents.intelligent_messaging_agent import intelligent_messaging_agent, MessageType

async def test_filtering_system():
    """Complete test of contact information filtering"""
    
    print("=" * 70)
    print("COMPLETE BID SUBMISSION FILTERING TEST")
    print("=" * 70)
    
    # Test cases with different types of contact information
    test_cases = [
        {
            "name": "Phone and Email",
            "message": """I can complete your project for $5000.
Please call me at 555-123-4567 or email contractor@email.com
I have 10 years experience and can start immediately.""",
            "should_filter": ["555-123-4567", "contractor@email.com"]
        },
        {
            "name": "Clean Message",
            "message": """I can complete your project for $5000.
I have 10 years experience and can start immediately.
Looking forward to working with you.""",
            "should_filter": []
        },
        {
            "name": "Social Media",
            "message": """Check out my work on Instagram @contractor123
or Facebook at facebook.com/contractorpage
I do great work!""",
            "should_filter": ["@contractor123", "facebook.com"]
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"TEST: {test_case['name']}")
        print("-" * 60)
        print("ORIGINAL:")
        print(test_case['message'])
        
        # Create state with valid UUIDs
        initial_state = {
            'original_content': test_case['message'],
            'sender_type': 'contractor',
            'sender_id': str(uuid.uuid4()),
            'bid_card_id': str(uuid.uuid4()),
            'conversation_id': str(uuid.uuid4()),
            'message_type': MessageType.TEXT,
            'attachments': [],
            'has_attachments': False,
            'threats_detected': [],
            'agent_comments': {},
            'timestamp': datetime.now().isoformat()
        }
        
        config = {
            'configurable': {
                'thread_id': f'test-{uuid.uuid4()}',
                'checkpoint_ns': ''
            }
        }
        
        try:
            # Process the message
            result = await intelligent_messaging_agent.ainvoke(initial_state, config)
            
            filtered = result.get('filtered_content', '')
            threats = result.get('threats_detected', [])
            action = result.get('agent_decision', 'UNKNOWN')
            
            print("\nFILTERED:")
            print(filtered if filtered else "[NO CONTENT]")
            
            # Check if filtering worked correctly
            passed = True
            for contact_info in test_case['should_filter']:
                if contact_info in filtered:
                    print(f"  FAILED: {contact_info} not filtered")
                    passed = False
                else:
                    print(f"  OK: {contact_info} removed")
            
            if not test_case['should_filter'] and filtered:
                print("  OK: Clean message passed through")
            
            results.append({
                "test": test_case['name'],
                "passed": passed,
                "action": str(action),
                "threats": len(threats)
            })
            
        except Exception as e:
            print(f"  ERROR: {str(e)}")
            results.append({
                "test": test_case['name'],
                "passed": False,
                "action": "ERROR",
                "threats": 0
            })
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    total_passed = sum(1 for r in results if r['passed'])
    total_tests = len(results)
    
    for result in results:
        status = "PASS" if result['passed'] else "FAIL"
        print(f"{result['test']}: {status} (Action: {result['action']}, Threats: {result['threats']})")
    
    print("-" * 70)
    print(f"TOTAL: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n*** ALL TESTS PASSED - SYSTEM IS WORKING ***")
        return True
    else:
        print(f"\n*** {total_tests - total_passed} TESTS FAILED - SYSTEM NEEDS FIXES ***")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_filtering_system())
    exit(0 if success else 1)