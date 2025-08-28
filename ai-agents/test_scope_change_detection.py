#!/usr/bin/env python3
"""
SCOPE CHANGE DETECTION TEST
Tests if the intelligent messaging system can detect scope changes 
and ask homeowner-only questions about notifying other contractors
"""

import requests
import json
import uuid
from config.service_urls import get_backend_url

def test_scope_change_detection():
    """Test scope change detection and homeowner-only questions"""
    
    print("SCOPE CHANGE DETECTION TEST")
    print("=" * 60)
    print("Testing: Homeowner changes from sod to turf in conversation")
    print("Expected: AI detects scope change, asks homeowner-only question")
    print()
    
    base_url = get_backend_url()
    
    # Test 1: Homeowner mentions scope change to contractor
    print("TEST 1: Homeowner Scope Change Message")
    print("-" * 40)
    
    scope_change_payload = {
        "content": "Actually, I've been thinking about it more and I'd like to change from regular sod to artificial turf for the backyard. What would that change in your pricing?",
        "sender_type": "homeowner",
        "sender_id": str(uuid.uuid4()),
        "bid_card_id": str(uuid.uuid4()),
        "recipient_id": str(uuid.uuid4())
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/intelligent-messages/send", 
            json=scope_change_payload, 
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"Original Message: '{scope_change_payload['content']}'")
            print()
            print("AI ANALYSIS RESULTS:")
            print(f"  Approved: {result.get('approved', False)}")
            print(f"  Decision: {result.get('agent_decision', 'unknown')}")
            print(f"  Threats: {result.get('threats_detected', [])}")
            print(f"  Confidence: {result.get('confidence_score', 0)}")
            print()
            
            # Check for scope change detection
            scope_detected = result.get('scope_change_detected', False)
            agent_comments = result.get('agent_comments', [])
            homeowner_question = result.get('homeowner_only_question', '')
            
            print("SCOPE CHANGE ANALYSIS:")
            print(f"  Scope Change Detected: {scope_detected}")
            print(f"  Agent Comments: {agent_comments}")
            print(f"  Homeowner-Only Question: '{homeowner_question}'")
            print()
            
            if scope_detected:
                print("SUCCESS: Scope change detected!")
                if homeowner_question:
                    print("SUCCESS: Homeowner-only question generated!")
                    print(f"Question: '{homeowner_question}'")
                else:
                    print("PARTIAL: Scope detected but no homeowner question")
            else:
                print("ISSUE: Scope change not detected")
                
            return scope_detected and bool(homeowner_question)
            
        else:
            print(f"HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_scope_change_variations():
    """Test different types of scope changes"""
    
    print("\n" + "=" * 60)
    print("TESTING DIFFERENT SCOPE CHANGE VARIATIONS")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Material Change",
            "content": "I want to switch from granite countertops to quartz. How does that affect the price?",
            "expected": "Material change from granite to quartz"
        },
        {
            "name": "Size Change", 
            "content": "Actually, let's expand the kitchen renovation to include the dining room too.",
            "expected": "Project scope expansion"
        },
        {
            "name": "Timeline Change",
            "content": "I need to move the start date from next month to January because of family visiting.",
            "expected": "Timeline modification"
        },
        {
            "name": "Budget Change",
            "content": "My budget has increased to $35,000, so we can do higher-end finishes now.",
            "expected": "Budget increase allowing upgrades"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTEST {i}: {test_case['name']}")
        print("-" * 40)
        
        payload = {
            "content": test_case['content'],
            "sender_type": "homeowner",
            "sender_id": str(uuid.uuid4()),
            "bid_card_id": str(uuid.uuid4())
        }
        
        try:
            response = requests.post(
                f"{get_backend_url()}/api/intelligent-messages/send",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"Message: '{test_case['content']}'")
                scope_detected = result.get('scope_change_detected', False)
                homeowner_question = result.get('homeowner_only_question', '')
                
                print(f"Scope Detected: {scope_detected}")
                if homeowner_question:
                    print(f"Homeowner Question: '{homeowner_question}'")
                else:
                    print("No homeowner-only question generated")
                
                results.append(scope_detected)
            else:
                print(f"HTTP Error: {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"Error: {e}")
            results.append(False)
    
    return results

def main():
    """Run scope change detection tests"""
    
    # Test main scope change detection
    main_result = test_scope_change_detection()
    
    # Test variations
    variation_results = test_scope_change_variations()
    
    print("\n" + "=" * 60)
    print("SCOPE CHANGE DETECTION - FINAL RESULTS")
    print("=" * 60)
    
    print(f"Main Scope Change Test: {'PASS' if main_result else 'FAIL'}")
    print(f"Variation Tests: {sum(variation_results)}/{len(variation_results)} passed")
    
    print()
    if main_result:
        print("SUCCESS: Scope change detection is working!")
        print("✅ AI can detect when homeowner changes project requirements")  
        print("✅ System can generate homeowner-only questions")
        print("✅ Ready to notify other contractors about scope changes")
    else:
        print("PARTIAL: Scope change detection needs development")
        print("The basic intelligent messaging works, but scope change")
        print("detection may need additional configuration")
    
    return main_result

if __name__ == "__main__":
    main()