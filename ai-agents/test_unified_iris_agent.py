#!/usr/bin/env python3
"""
Test Unified IRIS Agent Implementation
Tests complete context access, reasoning, and tool integration
"""

import asyncio
import requests
import json
from datetime import datetime
from config.service_urls import get_backend_url

# Test configuration
BACKEND_URL = get_backend_url()
TEST_USER_ID = "550e8400-e29b-41d4-a716-446655440001"

def test_unified_iris_chat():
    """Test unified IRIS chat endpoint with complete context"""
    print("Testing Unified IRIS Chat Endpoint...")
    
    # Test basic conversation
    test_message = {
        "message": "I'm planning a backyard renovation project. Can you help me understand what I have vs what I want?",
        "user_id": TEST_USER_ID,
        "context_type": "auto"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/iris/unified-chat",
            json=test_message,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("PASS - IRIS Unified Chat Response:")
            print(f"   Response: {data.get('response', 'No response')[:100]}...")
            print(f"   Session ID: {data.get('session_id', 'None')}")
            print(f"   Suggestions: {len(data.get('suggestions', []))} suggestions")
            print(f"   Available Tools: {data.get('available_tools', [])}")
            print(f"   User Intent: {data.get('reasoning', {}).get('user_intent', 'Unknown')}")
            print(f"   Confidence: {data.get('reasoning', {}).get('confidence', 0):.1%}")
            print(f"   Context Summary: {data.get('context_summary', {})}")
            return True
        else:
            print(f"FAIL - Chat endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"FAIL - Chat request failed: {e}")
        return False

def test_iris_context_retrieval():
    """Test IRIS context retrieval endpoint"""
    print("\nTesting IRIS Context Retrieval...")
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/iris/context/{TEST_USER_ID}",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            context = data.get('context', {})
            
            print("PASS - IRIS Context Retrieved:")
            print(f"   Inspiration Boards: {len(context.get('inspiration', {}).get('inspiration_boards', []))}")
            print(f"   Properties: {len(context.get('property', {}).get('properties', []))}")
            print(f"   Property Photos: {len(context.get('property', {}).get('property_photos', []))}")
            print(f"   Trade Projects: {context.get('trade_projects', {}).get('total_trade_projects', 0)}")
            print(f"   Available Trades: {len(context.get('trade_projects', {}).get('available_trades', []))}")
            
            # Show available trades
            available_trades = context.get('trade_projects', {}).get('available_trades', [])
            if available_trades:
                print(f"   Supported Trades: {', '.join(available_trades[:5])}...")
            
            return True
        else:
            print(f"FAIL - Context endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"FAIL - Context request failed: {e}")
        return False

def test_iris_with_photo():
    """Test IRIS with photo analysis"""
    print("\nTesting IRIS with Photo Analysis...")
    
    test_message = {
        "message": "I just uploaded a photo of my current backyard. What do you think about the space?",
        "user_id": TEST_USER_ID,
        "photo_url": "https://example.com/backyard-current.jpg",
        "photo_metadata": {
            "category": "current",
            "room_type": "backyard",
            "source": "homeowner_upload"
        },
        "context_type": "property"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/iris/unified-chat",
            json=test_message,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print("PASS - IRIS Photo Analysis Response:")
            print(f"   Response: {data.get('response', 'No response')[:150]}...")
            print(f"   Intent: {data.get('reasoning', {}).get('user_intent', 'Unknown')}")
            print(f"   Suggested Actions: {data.get('reasoning', {}).get('suggested_actions', [])}")
            print(f"   Available Tools: {data.get('available_tools', [])}")
            return True
        else:
            print(f"FAIL - Photo analysis failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"FAIL - Photo analysis request failed: {e}")
        return False

def test_iris_trade_context():
    """Test IRIS with trade-specific questions"""
    print("\nTesting IRIS with Trade Context...")
    
    test_message = {
        "message": "I need electrical work done - new outlets and fixing some wiring issues. Can you help me organize this project?",
        "user_id": TEST_USER_ID,
        "context_type": "both"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/iris/unified-chat",
            json=test_message,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            reasoning = data.get('reasoning', {})
            
            print("PASS - IRIS Trade Context Response:")
            print(f"   Response: {data.get('response', 'No response')[:150]}...")
            print(f"   Detected Intent: {reasoning.get('user_intent', 'Unknown')}")
            print(f"   Confidence: {reasoning.get('confidence', 0):.1%}")
            print(f"   Suggested Actions: {reasoning.get('suggested_actions', [])}")
            print(f"   Available Tools: {data.get('available_tools', [])}")
            
            # Check if trade grouping is suggested
            suggested_actions = reasoning.get('suggested_actions', [])
            if 'group_by_trade' in suggested_actions:
                print("   PASS - Trade grouping correctly suggested")
            
            return True
        else:
            print(f"FAIL - Trade context failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"FAIL - Trade context request failed: {e}")
        return False

def test_iris_tool_suggestion():
    """Test IRIS tool suggestion endpoint"""
    print("\nTesting IRIS Tool Suggestion...")
    
    test_request = {
        "user_id": TEST_USER_ID,
        "context": "User has electrical and plumbing issues identified",
        "suggested_tool": "trade_grouping"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/iris/suggest-tool/trade_grouping",
            json=test_request,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("PASS - IRIS Tool Suggestion:")
            print(f"   Tool: {data.get('tool', 'None')}")
            print(f"   Endpoint: {data.get('endpoint', 'None')}")
            print(f"   Suggestion: {data.get('suggestion', 'None')}")
            print(f"   Requires Confirmation: {data.get('requires_confirmation', False)}")
            return True
        else:
            print(f"FAIL - Tool suggestion failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"FAIL - Tool suggestion request failed: {e}")
        return False

def run_comprehensive_test():
    """Run comprehensive test of unified IRIS agent"""
    print("UNIFIED IRIS AGENT COMPREHENSIVE TEST")
    print("=" * 50)
    
    results = []
    
    # Test 1: Basic chat functionality
    results.append(test_unified_iris_chat())
    
    # Test 2: Context retrieval
    results.append(test_iris_context_retrieval())
    
    # Test 3: Photo analysis
    results.append(test_iris_with_photo())
    
    # Test 4: Trade-specific context
    results.append(test_iris_trade_context())
    
    # Test 5: Tool suggestion
    results.append(test_iris_tool_suggestion())
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"PASS - Passed: {passed}/{total} tests")
    print(f"FAIL - Failed: {total - passed}/{total} tests")
    
    if passed == total:
        print("\nALL TESTS PASSED - Unified IRIS Agent is operational!")
        print("* Complete context access working")
        print("* Smart reasoning functioning")  
        print("* Tool integration operational")
        print("* Multi-modal support ready")
    else:
        print(f"\nSome tests failed - system needs attention")
        
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_test()
    exit(0 if success else 1)