"""Reality check test - what's ACTUALLY working with IRIS"""

import requests
import json
from datetime import datetime
from config.service_urls import get_backend_url

BASE_URL = get_backend_url()
TEST_USER_ID = "550e8400-e29b-41d4-a716-446655440001"

def print_section(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)

def test_reality_check():
    """Test what's REALLY working"""
    
    print_section("IRIS REALITY CHECK - WHAT'S ACTUALLY WORKING")
    
    session_id = f"reality_check_{int(datetime.now().timestamp())}"
    
    # Test 1: Is IRIS making real LLM calls?
    print_section("TEST 1: Real LLM Calls?")
    
    response1 = requests.post(
        f"{BASE_URL}/api/iris/unified-chat",
        json={
            "user_id": TEST_USER_ID,
            "message": "Explain quantum physics in one sentence",
            "session_id": session_id
        }
    )
    
    if response1.status_code == 200:
        data = response1.json()
        response_text = data.get('response', '')
        
        # Check if response is intelligent (not a fallback)
        if len(response_text) > 100 and "quantum" in response_text.lower():
            print("[YES] Real LLM call to Anthropic Claude working!")
            print(f"Response: {response_text[:200]}...")
        else:
            print("[NO] Might be using fallback responses")
            print(f"Response: {response_text}")
    else:
        print(f"[ERROR] Status {response1.status_code}")
    
    # Test 2: What does IRIS call the prebuilt projects?
    print_section("TEST 2: What does IRIS call prebuilt projects/cards?")
    
    response2 = requests.post(
        f"{BASE_URL}/api/iris/unified-chat",
        json={
            "user_id": TEST_USER_ID,
            "message": "What are inspiration boards and how are they different from property maintenance projects?",
            "session_id": session_id
        }
    )
    
    if response2.status_code == 200:
        data = response2.json()
        response_text = data.get('response', '')
        print(f"IRIS explains: {response_text[:400]}...")
        
        # Check what terminology IRIS uses
        terms_found = []
        if "inspiration board" in response_text.lower():
            terms_found.append("inspiration boards")
        if "bid card" in response_text.lower():
            terms_found.append("bid cards")
        if "trade group" in response_text.lower():
            terms_found.append("trade groups")
        if "project" in response_text.lower():
            terms_found.append("projects")
        
        print(f"\nTerms IRIS uses: {', '.join(terms_found) if terms_found else 'None detected'}")
    
    # Test 3: Does IRIS understand its context?
    print_section("TEST 3: Context Understanding")
    
    test_questions = [
        "Can you see my property photos?",
        "How many properties do I have documented?",
        "Can you group maintenance issues by trade?",
        "Can you create a bid card directly?"
    ]
    
    for question in test_questions:
        response = requests.post(
            f"{BASE_URL}/api/iris/unified-chat",
            json={
                "user_id": TEST_USER_ID,
                "message": question,
                "session_id": session_id
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get('response', '')[:150]
            
            # Check context awareness
            context_summary = data.get('context_summary', {})
            
            print(f"\nQ: {question}")
            print(f"A: {answer}...")
            print(f"Context: Photos={context_summary.get('property_photos', 0)}, "
                  f"Boards={context_summary.get('inspiration_boards', 0)}, "
                  f"Projects={context_summary.get('trade_projects', 0)}")
    
    # Test 4: Available tools and reasoning
    print_section("TEST 4: IRIS Tools & Reasoning")
    
    response4 = requests.post(
        f"{BASE_URL}/api/iris/unified-chat",
        json={
            "user_id": TEST_USER_ID,
            "message": "I need to fix some electrical issues and plumbing problems",
            "session_id": session_id
        }
    )
    
    if response4.status_code == 200:
        data = response4.json()
        
        print("Available Tools:")
        for tool in data.get('available_tools', []):
            print(f"  - {tool}")
        
        print("\nReasoning:")
        reasoning = data.get('reasoning', {})
        print(f"  Intent: {reasoning.get('user_intent', 'unknown')}")
        print(f"  Confidence: {reasoning.get('confidence', 0) * 100:.0f}%")
        print(f"  Suggested Actions: {reasoning.get('suggested_actions', [])}")
    
    # Test 5: Persistence check
    print_section("TEST 5: Memory Persistence")
    
    # Tell IRIS something specific
    response5a = requests.post(
        f"{BASE_URL}/api/iris/unified-chat",
        json={
            "user_id": TEST_USER_ID,
            "message": "My favorite color is purple and I have 3 dogs",
            "session_id": session_id
        }
    )
    
    # Ask about it
    response5b = requests.post(
        f"{BASE_URL}/api/iris/unified-chat",
        json={
            "user_id": TEST_USER_ID,
            "message": "What personal details did I just share?",
            "session_id": session_id
        }
    )
    
    if response5b.status_code == 200:
        data = response5b.json()
        response_text = data.get('response', '')
        
        if "purple" in response_text.lower() and "dogs" in response_text.lower():
            print("[SUCCESS] Memory working perfectly!")
        else:
            print("[PARTIAL] Memory may be working but not perfectly")
        
        print(f"IRIS recalls: {response_text[:200]}...")

if __name__ == "__main__":
    test_reality_check()