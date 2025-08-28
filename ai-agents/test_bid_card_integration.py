#!/usr/bin/env python3
"""
Test Bid Card Messaging Integration
Tests the complete integration of intelligent messaging with bid card system
"""

import asyncio
import base64
import requests
import json
from pathlib import Path
from config.service_urls import get_backend_url

async def test_bid_card_messaging():
    """Test bid card messaging with intelligent filtering"""
    
    print("=== TESTING BID CARD MESSAGING INTEGRATION ===")
    
    # Backend API base URL
    api_base = f"{get_backend_url()}/api/bid-cards"
    
    # Test data
    test_bid_card_id = "test-bid-card-123"
    test_recipient_id = "test-recipient-456"
    
    # Test cases with different security scenarios
    test_messages = [
        {
            "name": "SAFE_MESSAGE",
            "content": "Hi! I'm excited about your kitchen renovation project. I have 15 years of experience with cabinet installations and would love to work with you. What's your timeline?",
            "expected_blocked": False
        },
        {
            "name": "CONTACT_INFO_MESSAGE", 
            "content": "I'd love to discuss this project with you! Please call me at (555) 123-4567 or email me at contractor@example.com so we can talk details.",
            "expected_blocked": True
        },
        {
            "name": "SCOPE_CHANGE_MESSAGE",
            "content": "After reviewing your project, I think we should use granite countertops instead of quartz. This would increase the budget to $18,000. Also, let's add crown molding to the upper cabinets.",
            "expected_blocked": False
        }
    ]
    
    # Test with image containing contact info
    image_test = {
        "name": "IMAGE_WITH_CONTACT",
        "content": "Here's my detailed proposal for your project",
        "expected_blocked": True
    }
    
    results = {}
    
    # Test text messages
    for test_case in test_messages:
        print(f"\nTesting: {test_case['name']}")
        
        try:
            # Prepare request payload
            payload = {
                "bid_card_id": test_bid_card_id,
                "recipient_id": test_recipient_id,
                "content": test_case["content"],
                "attachments": []
            }
            
            # Send request to bid card messaging API
            response = requests.post(f"{api_base}/messages", json=payload, timeout=30)
            
            print(f"  Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                blocked = result.get("blocked", False)
                agent_decision = result.get("agent_decision", "unknown")
                threats = result.get("threats_detected", [])
                confidence = result.get("confidence_score", 0)
                
                print(f"  Blocked: {blocked}")
                print(f"  Agent Decision: {agent_decision}")
                print(f"  Threats: {threats}")
                print(f"  Confidence: {confidence}")
                
                # Check if result matches expectation
                expected_blocked = test_case["expected_blocked"]
                test_passed = (blocked == expected_blocked)
                
                results[test_case["name"]] = {
                    "passed": test_passed,
                    "blocked": blocked,
                    "expected_blocked": expected_blocked,
                    "agent_decision": agent_decision,
                    "threats": threats,
                    "confidence": confidence
                }
                
                print(f"  Test Result: {'PASS' if test_passed else 'FAIL'}")
                
            else:
                print(f"  API Error: {response.status_code}")
                print(f"  Response: {response.text}")
                results[test_case["name"]] = {
                    "passed": False,
                    "error": f"HTTP {response.status_code}",
                    "response": response.text
                }
        
        except Exception as e:
            print(f"  Exception: {e}")
            results[test_case["name"]] = {
                "passed": False,
                "error": str(e)
            }
    
    # Test image message
    print(f"\nTesting: {image_test['name']}")
    
    try:
        # Use the fake bid document image we created earlier
        image_path = Path("C:/Users/NOTJOH~1/AppData/Local/Temp/playwright-mcp-output/2025-08-08T05-55-47.931Z/fake-bid-with-contact-info.png")
        
        if image_path.exists():
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            payload = {
                "bid_card_id": test_bid_card_id,
                "recipient_id": test_recipient_id,
                "content": image_test["content"],
                "attachments": [],
                "image_data": image_data
            }
            
            response = requests.post(f"{api_base}/messages", json=payload, timeout=45)
            
            print(f"  Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                blocked = result.get("blocked", False)
                agent_decision = result.get("agent_decision", "unknown")
                threats = result.get("threats_detected", [])
                confidence = result.get("confidence_score", 0)
                
                print(f"  Blocked: {blocked}")
                print(f"  Agent Decision: {agent_decision}")
                print(f"  Threats: {threats}")
                print(f"  Confidence: {confidence}")
                
                # Should be blocked due to contact info in image
                test_passed = (blocked == image_test["expected_blocked"])
                
                results[image_test["name"]] = {
                    "passed": test_passed,
                    "blocked": blocked,
                    "expected_blocked": image_test["expected_blocked"],
                    "agent_decision": agent_decision,
                    "threats": threats,
                    "confidence": confidence
                }
                
                print(f"  Test Result: {'PASS' if test_passed else 'FAIL'}")
                
            else:
                print(f"  API Error: {response.status_code}")
                print(f"  Response: {response.text}")
                results[image_test["name"]] = {
                    "passed": False,
                    "error": f"HTTP {response.status_code}"
                }
        else:
            print(f"  Image file not found: {image_path}")
            results[image_test["name"]] = {
                "passed": False,
                "error": "Image file not found"
            }
    
    except Exception as e:
        print(f"  Exception: {e}")
        results[image_test["name"]] = {
            "passed": False,
            "error": str(e)
        }
    
    # Summary
    print("\n=== INTEGRATION TEST RESULTS ===")
    
    passed_count = 0
    total_count = len(results)
    
    for test_name, result in results.items():
        status = "PASS" if result.get("passed", False) else "FAIL"
        print(f"{test_name}: {status}")
        
        if result.get("passed", False):
            passed_count += 1
    
    print(f"\nPassed: {passed_count}/{total_count}")
    
    if passed_count == total_count:
        print("SUCCESS: All bid card messaging integration tests passed!")
        print("Intelligent messaging is fully integrated with bid card system")
        return True
    else:
        print("PARTIAL: Some integration tests failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_bid_card_messaging())
    
    if success:
        print("\nFINAL: Bid card messaging integration is WORKING")
    else:
        print("\nFINAL: Integration needs fixes")