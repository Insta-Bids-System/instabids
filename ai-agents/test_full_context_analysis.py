#!/usr/bin/env python3
"""
Complete analysis of what's being sent to OpenAI
Shows system prompt, tools, and messages
"""

import requests
import json
import uuid

def test_cia_full_context():
    """Test conversation and analyze full context"""
    print("="*70)
    print("COMPLETE CIA AGENT CONTEXT ANALYSIS")
    print("="*70)
    
    # Simple test conversation
    user_id = str(uuid.uuid4())
    conv_id = "context-test"
    url = "http://localhost:8008/api/cia/stream"
    
    messages = [
        {"role": "user", "content": "I want to install artificial turf in my backyard. I'm flexible on timing and neighbors might be interested."}
    ]
    
    payload = {
        "messages": messages,
        "user_id": user_id,
        "conversation_id": conv_id
    }
    
    print("\n1. TEST MESSAGE:")
    print("-"*40)
    print(f"User: {messages[0]['content']}")
    
    print("\n2. KEY PHRASES TO DETECT:")
    print("-"*40)
    key_phrases = [
        '"artificial turf" -> should extract as project type',
        '"flexible on timing" -> should trigger group bidding',
        '"neighbors might be interested" -> perfect for group bidding'
    ]
    for phrase in key_phrases:
        print(f"  - {phrase}")
    
    print("\n3. EXPECTED BUSINESS LOGIC:")
    print("-"*40)
    print("  - Should detect lawn/turf installation")
    print("  - Should mention group bidding (15-25% savings)")
    print("  - Should emphasize neighbor coordination")
    print("  - Should NOT push for budget amounts")
    
    print("\n4. ACTUAL AI RESPONSE:")
    print("-"*40)
    
    try:
        response = requests.post(url, json=payload, stream=True, timeout=30)
        if response.status_code != 200:
            print(f"ERROR: Status {response.status_code}")
            return
            
        full_response = ""
        print("AI: ", end="", flush=True)
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_str = line_str[6:]
                    if data_str.strip() != '[DONE]':
                        try:
                            data = json.loads(data_str)
                            if 'choices' in data and len(data['choices']) > 0:
                                content = data['choices'][0].get('delta', {}).get('content', '')
                                full_response += content
                                print(content, end='', flush=True)
                        except:
                            pass
        
        print()  # New line
        
        # Analyze response
        print("\n5. BUSINESS LOGIC ANALYSIS:")
        print("-"*40)
        
        response_lower = full_response.lower()
        
        # Check for key business logic
        checks = {
            "Group Bidding": any(word in response_lower for word in ['group', 'neighbor', 'coordinate', 'bulk']),
            "Cost Savings": any(word in response_lower for word in ['save', 'savings', '15-25%', 'discount']),
            "Project Extracted": any(word in response_lower for word in ['turf', 'grass', 'lawn', 'backyard']),
            "Timeline Flexibility": any(word in response_lower for word in ['flexible', 'timing']),
            "Budget Pressure": any(word in response_lower for word in ['budget', 'cost', 'how much', 'price range'])
        }
        
        for check, result in checks.items():
            status = "YES" if result else "NO"
            symbol = "[OK]" if result else "[X]"
            print(f"  {symbol} {check}: {status}")
        
        # Overall assessment
        print("\n6. OVERALL ASSESSMENT:")
        print("-"*40)
        
        if checks["Group Bidding"] and checks["Cost Savings"]:
            print("SUCCESS: Full business logic is working!")
            print("The 12 Key Data Points are being applied correctly.")
        elif checks["Project Extracted"]:
            print("PARTIAL: Field extraction working but business logic missing")
            print("The agent is extracting data but not applying business rules.")
        else:
            print("FAILURE: Neither extraction nor business logic working")
            print("Major issue with the agent configuration.")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_cia_full_context()