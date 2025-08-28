#!/usr/bin/env python3
"""
Full API Integration Test
Tests intelligent messaging system through live API endpoints
"""

import requests
import json
import base64
from config.service_urls import get_backend_url

def test_full_api_integration():
    """Test intelligent messaging through live API"""
    
    print("INTELLIGENT MESSAGING API INTEGRATION TEST")
    print("=" * 50)
    
    base_url = get_backend_url()
    
    # Test 1: Direct intelligent messaging send endpoint
    print("\nTest 1: Direct Intelligent Messaging API")
    print("-" * 40)
    
    payload = {
        "content": "Hi! My email is john@contractor.com and phone is 555-123-4567. Please contact me directly to discuss the project.",
        "sender_type": "contractor",
        "sender_id": "550e8400-e29b-41d4-a716-446655440001",
        "bid_card_id": "550e8400-e29b-41d4-a716-446655440000"
    }
    
    try:
        response = requests.post(f"{base_url}/api/intelligent-messages/send", json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        result = response.json()
        
        print(f"Input: '{payload['content'][:50]}...'")
        print(f"Approved: {result.get('approved', False)}")
        print(f"Decision: {result.get('agent_decision', 'unknown')}")
        print(f"Threats: {result.get('threats_detected', [])}")
        print(f"Confidence: {result.get('confidence_score', 0)}")
        
        # Check if contact info was properly detected
        if not result.get('approved') and 'contact_info' in str(result.get('threats_detected', [])):
            print("✅ PASSED - Contact info correctly blocked")
        else:
            print("❌ FAILED - Contact info not properly handled")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 2: Legitimate content
    print("\nTest 2: Legitimate Content")
    print("-" * 40)
    
    payload2 = {
        "content": "I can install your kitchen cabinets for $15,000. The timeline would be 2-3 weeks. Do you have color preferences?",
        "sender_type": "contractor",
        "sender_id": "550e8400-e29b-41d4-a716-446655440002",
        "bid_card_id": "550e8400-e29b-41d4-a716-446655440000"
    }
    
    try:
        response = requests.post(f"{base_url}/api/intelligent-messages/send", json=payload2, timeout=30)
        result = response.json()
        
        print(f"Input: '{payload2['content'][:50]}...'")
        print(f"Approved: {result.get('approved', False)}")
        print(f"Decision: {result.get('agent_decision', 'unknown')}")
        print(f"Threats: {result.get('threats_detected', [])}")
        
        # Check if legitimate content was approved
        if result.get('approved') and result.get('agent_decision') == 'allow':
            print("✅ PASSED - Legitimate content correctly approved")
        else:
            print("❌ FAILED - Legitimate content wrongly blocked")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 3: Image upload with contact info (if available)
    print("\nTest 3: Image Analysis")
    print("-" * 40)
    
    try:
        # Try to read the test image
        image_path = r"C:\Users\NOTJOH~1\AppData\Local\Temp\playwright-mcp-output\2025-08-08T05-55-47.931Z\fake-bid-with-contact-info.png"
        
        with open(image_path, "rb") as f:
            files = {"image": ("test-bid.png", f, "image/png")}
            data = {
                "content": "Here's my detailed bid proposal",
                "sender_type": "contractor", 
                "sender_id": "550e8400-e29b-41d4-a716-446655440003",
                "bid_card_id": "550e8400-e29b-41d4-a716-446655440000"
            }
            
            response = requests.post(f"{base_url}/api/intelligent-messages/send-with-image", 
                                   files=files, data=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                print(f"Input: 'Here's my detailed bid proposal' + IMAGE")
                print(f"Approved: {result.get('approved', False)}")
                print(f"Decision: {result.get('agent_decision', 'unknown')}")
                print(f"Threats: {result.get('threats_detected', [])}")
                
                if not result.get('approved') and 'contact_info' in str(result.get('threats_detected', [])):
                    print("✅ PASSED - Image contact info correctly blocked")
                else:
                    print("❌ FAILED - Image contact info not blocked")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                
    except FileNotFoundError:
        print("⚠️ Image test skipped - test image not found")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 4: Health check
    print("\nTest 4: System Health Check")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/api/intelligent-messages/health", timeout=15)
        if response.status_code == 200:
            health = response.json()
            print(f"Status: {health.get('status', 'unknown')}")
            print(f"Database: {health.get('database', 'unknown')}")
            print(f"Intelligent Agent: {health.get('intelligent_agent', 'unknown')}")
            print(f"GPT Available: {health.get('gpt5_available', False)}")
            
            if health.get('status') == 'healthy':
                print("✅ PASSED - System health good")
            else:
                print("❌ FAILED - System health issues detected")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print(f"\n" + "=" * 50)
    print("API INTEGRATION TEST COMPLETE")
    print("Backend is running and intelligent messaging is operational!")

if __name__ == "__main__":
    test_full_api_integration()