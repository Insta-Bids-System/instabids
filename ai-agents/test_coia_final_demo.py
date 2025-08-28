#!/usr/bin/env python3
"""
Final COIA Demo - Multi-turn contractor conversations
"""
import requests
import json
import time
import sys
from datetime import datetime
from config.service_urls import get_backend_url

# Fix Windows Unicode
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

def test_single_conversation(contractor_name, message, session_id):
    """Test a single conversation turn"""
    url = f"{get_backend_url()}/ai/coia/chat/stream"
    
    payload = {
        "message": message,
        "session_id": session_id,
        "interface": "chat"
    }
    
    try:
        with requests.post(url, json=payload, stream=True, timeout=20) as response:
            if response.status_code == 200:
                tool_calls = 0
                tokens = 0
                profile_data = None
                bid_cards = 0
                connected = False
                conversation_text = ""
                
                for line in response.iter_lines():
                    if line and line.decode('utf-8').startswith('data: '):
                        try:
                            data = json.loads(line.decode('utf-8')[6:])
                            msg_type = data.get('type', '')
                            
                            if msg_type == 'connected':
                                connected = True
                            elif msg_type == 'tool_call':
                                tool_calls += 1
                            elif msg_type == 'token':
                                tokens += 1
                                conversation_text += data.get('content', '')
                            elif msg_type == 'metadata':
                                metadata = data.get('metadata', {})
                                profile_data = metadata.get('profile', {})
                                bid_cards = len(metadata.get('bid_cards', []))
                            elif msg_type == 'complete':
                                break
                        except:
                            continue
                
                return {
                    'success': True,
                    'connected': connected,
                    'tool_calls': tool_calls,
                    'tokens': tokens,
                    'profile': profile_data,
                    'bid_cards': bid_cards,
                    'conversation': conversation_text[:100] + "..." if len(conversation_text) > 100 else conversation_text
                }
            else:
                return {'success': False, 'error': f"HTTP {response.status_code}"}
                
    except Exception as e:
        return {'success': False, 'error': str(e)}

def main():
    print("COIA MULTI-TURN CONVERSATION TEST")
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
    
    # Test 1: TurfGrass Initial Conversation
    print(f"\n=== TURFGRASS CONVERSATION 1 ===")
    turfgrass_session = f"turfgrass_{int(time.time())}"
    result1 = test_single_conversation(
        "TurfGrass", 
        "Hi, I own TurfGrass Artificial Solutions in South Florida. We specialize in artificial grass installation.",
        turfgrass_session
    )
    
    if result1['success']:
        print(f"Connected: {result1['connected']}")
        print(f"Tool calls: {result1['tool_calls']}")
        print(f"Tokens: {result1['tokens']}")
        print(f"Profile created: {result1['profile'] is not None}")
        print(f"Bid cards found: {result1['bid_cards']}")
        if result1['profile']:
            print(f"Company: {result1['profile'].get('company_name', 'Unknown')}")
    else:
        print(f"ERROR: {result1['error']}")
    
    time.sleep(3)
    
    # Test 2: TurfGrass Follow-up Conversation (same session)
    print(f"\n=== TURFGRASS CONVERSATION 2 (Same Session) ===")
    result2 = test_single_conversation(
        "TurfGrass", 
        "That looks great! We also do putting greens. Can you show me more about those landscaping projects?",
        turfgrass_session  # Same session ID
    )
    
    if result2['success']:
        print(f"Connected: {result2['connected']}")
        print(f"Tool calls: {result2['tool_calls']}")
        print(f"Tokens: {result2['tokens']}")
        print(f"Conversation sample: {result2['conversation']}")
    else:
        print(f"ERROR: {result2['error']}")
    
    time.sleep(3)
    
    # Test 3: JM Holiday Lighting
    print(f"\n=== JM HOLIDAY LIGHTING CONVERSATION ===")
    jm_session = f"jm_holiday_{int(time.time())}"
    result3 = test_single_conversation(
        "JM Holiday", 
        "Hello, I'm with JM Holiday Lighting. We provide holiday lighting installation and electrical services in South Florida.",
        jm_session
    )
    
    if result3['success']:
        print(f"Connected: {result3['connected']}")
        print(f"Tool calls: {result3['tool_calls']}")
        print(f"Tokens: {result3['tokens']}")
        print(f"Profile created: {result3['profile'] is not None}")
        print(f"Bid cards found: {result3['bid_cards']}")
        if result3['profile']:
            print(f"Company: {result3['profile'].get('company_name', 'Unknown')}")
    else:
        print(f"ERROR: {result3['error']}")
    
    # Summary
    print(f"\n=== FINAL SUMMARY ===")
    success_count = sum([1 for r in [result1, result2, result3] if r.get('success')])
    print(f"Successful conversations: {success_count}/3")
    
    if success_count >= 2:
        print("SUCCESS: COIA multi-turn conversations working!")
    else:
        print("ISSUES: Some conversations failed")

if __name__ == "__main__":
    main()