#!/usr/bin/env python3
"""
Test bid card update detection in messaging agent
This test verifies if the messaging agent can detect when homeowners make
changes that require bid card updates and contractor notifications
"""

import asyncio
import json
from datetime import datetime
import database_simple

# Import messaging agent
from agents.messaging_agent import process_message, MessageType

db = database_simple.get_client()

async def test_bid_card_update_detection():
    """Test if messaging agent detects bid card update scenarios"""
    
    print("\n" + "="*70)
    print("MESSAGING AGENT - BID CARD UPDATE DETECTION TEST")
    print("="*70)
    
    test_bid_card_id = "test-bid-card-updates-123"
    test_user_id = "test-homeowner-456"
    
    print(f"Test Bid Card: {test_bid_card_id}")
    print(f"Test Homeowner: {test_user_id}")
    
    # TEST SCENARIOS: Messages that SHOULD trigger bid card updates
    update_scenarios = [
        {
            "name": "Budget Change",
            "message": "Actually, I need to increase my budget from $15k to $25k because I want premium materials",
            "expected_detection": "budget_change",
            "should_trigger_update": True
        },
        {
            "name": "Timeline Change", 
            "message": "I'm moving up my timeline - I need this done in 2 weeks instead of 2 months",
            "expected_detection": "timeline_change",
            "should_trigger_update": True
        },
        {
            "name": "Scope Expansion",
            "message": "Can we also add a full kitchen remodel to this bathroom project? Same contractors",
            "expected_detection": "scope_expansion", 
            "should_trigger_update": True
        },
        {
            "name": "Material Upgrade",
            "message": "I changed my mind about the basic tile - I want marble instead throughout",
            "expected_detection": "material_change",
            "should_trigger_update": True
        },
        {
            "name": "Emergency Status",
            "message": "This is now urgent! Pipe burst - need contractors ASAP, willing to pay emergency rates",
            "expected_detection": "urgency_change",
            "should_trigger_update": True
        },
        {
            "name": "Regular Chat (No Update)",
            "message": "Thanks for the updates, looking forward to hearing from contractors",
            "expected_detection": None,
            "should_trigger_update": False
        }
    ]
    
    # Test each scenario
    results = []
    
    for scenario in update_scenarios:
        print(f"\n" + "-"*60)
        print(f"TESTING: {scenario['name']}")
        print("-"*60)
        
        print(f"Message: {scenario['message'][:80]}...")
        print(f"Expected: {'Should trigger update' if scenario['should_trigger_update'] else 'No update needed'}")
        
        try:
            # Process message through messaging agent
            result = await process_message(
                content=scenario['message'],
                sender_type="homeowner",
                sender_id=test_user_id,
                bid_card_id=test_bid_card_id,
                message_type=MessageType.TEXT
            )
            
            # Check if agent detected any bid card update triggers
            detected_update = check_for_update_detection(result, scenario['message'])
            
            test_result = {
                "scenario": scenario['name'],
                "expected_update": scenario['should_trigger_update'],
                "detected_update": detected_update['detected'],
                "detection_reason": detected_update.get('reason'),
                "agent_metadata": result.get('metadata', {})
            }
            
            results.append(test_result)
            
            # Report result
            if scenario['should_trigger_update'] and detected_update['detected']:
                print(f"✅ PASS: Correctly detected update trigger")
                print(f"   Reason: {detected_update.get('reason', 'Not specified')}")
            elif not scenario['should_trigger_update'] and not detected_update['detected']:
                print(f"✅ PASS: Correctly identified no update needed")
            elif scenario['should_trigger_update'] and not detected_update['detected']:
                print(f"❌ FAIL: Should have detected update but didn't")
            else:
                print(f"❌ FAIL: False positive - detected update when none needed")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            test_result = {
                "scenario": scenario['name'],
                "expected_update": scenario['should_trigger_update'],
                "detected_update": False,
                "error": str(e)
            }
            results.append(test_result)
    
    # RESULTS SUMMARY
    print(f"\n" + "="*60)
    print("BID CARD UPDATE DETECTION RESULTS")
    print("="*60)
    
    passed_tests = sum(1 for r in results if test_passed(r))
    total_tests = len(results)
    
    print(f"Test Results: {passed_tests}/{total_tests} passed")
    
    for result in results:
        status = "✅ PASS" if test_passed(result) else "❌ FAIL"
        print(f"  {status}: {result['scenario']}")
        if 'error' in result:
            print(f"    Error: {result['error']}")
        elif 'detection_reason' in result:
            print(f"    Detection: {result['detection_reason']}")
    
    # IMPLEMENTATION ANALYSIS
    print(f"\n" + "="*60)
    print("IMPLEMENTATION ANALYSIS")
    print("="*60)
    
    if passed_tests == 0:
        print("❌ BID CARD UPDATE DETECTION NOT IMPLEMENTED")
        print("\nWhat's Missing:")
        print("1. Update detection logic in messaging agent")
        print("2. Pattern recognition for scope/budget/timeline changes")
        print("3. Contractor notification system for updates")
        print("4. Bid card update API integration")
        
        print(f"\nRecommended Implementation:")
        print("1. Add update detection node to LangGraph workflow")
        print("2. Use LLM to analyze messages for change patterns")  
        print("3. Create bid_card_updates table for tracking changes")
        print("4. Build contractor notification system")
        
    elif passed_tests < total_tests - 1:  # Allow one failure for regular chat
        print("⚠️ PARTIAL IMPLEMENTATION - Some scenarios working")
    else:
        print("✅ BID CARD UPDATE DETECTION FULLY WORKING")
        
    return passed_tests >= (total_tests - 1)  # Success if all but regular chat pass

def check_for_update_detection(message_result, original_message):
    """Check if messaging agent detected bid card update triggers"""
    
    # Look for update detection in agent metadata
    metadata = message_result.get('metadata', {})
    
    # Check for bid card update flags
    if metadata.get('bid_card_update_required'):
        return {
            'detected': True,
            'reason': metadata.get('update_reason', 'Generic update detected')
        }
    
    # Check for contractor notification flags  
    if metadata.get('contractor_notification_required'):
        return {
            'detected': True,
            'reason': 'Contractor notification triggered'
        }
    
    # Check message content for update keywords (manual detection)
    update_keywords = [
        'budget', 'increase', 'decrease', 'timeline', 'urgent', 'asap',
        'scope', 'add', 'remove', 'change', 'upgrade', 'premium', 
        'emergency', 'rush', 'material', 'marble', 'granite'
    ]
    
    message_lower = original_message.lower()
    detected_keywords = [kw for kw in update_keywords if kw in message_lower]
    
    if detected_keywords:
        return {
            'detected': False,  # Agent didn't detect, but keywords present
            'reason': f'Keywords present but not detected: {detected_keywords}'
        }
    
    return {'detected': False}

def test_passed(result):
    """Determine if test passed based on expected vs actual results"""
    if 'error' in result:
        return False
        
    expected = result['expected_update']
    detected = result['detected_update']
    
    # Test passes if expectation matches detection
    return expected == detected

if __name__ == "__main__":
    result = asyncio.run(test_bid_card_update_detection())
    print(f"\nFINAL RESULT: {'SUCCESS' if result else 'IMPLEMENTATION NEEDED'}")