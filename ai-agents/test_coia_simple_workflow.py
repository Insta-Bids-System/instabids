#!/usr/bin/env python3
"""
Simple COIA Workflow Test - Multi-turn conversations with key result summaries
"""
import requests
import json
import time
from datetime import datetime
from config.service_urls import get_backend_url

def test_contractor_conversation(contractor_name, messages, session_id):
    """Test multi-turn conversation with a contractor"""
    url = f"{get_backend_url()}/ai/coia/chat/stream"
    results = []
    
    print(f"\n=== TESTING {contractor_name.upper()} ===")
    
    for i, message in enumerate(messages, 1):
        print(f"\n🔄 Conversation Turn {i}:")
        print(f"   Message: {message[:60]}...")
        
        payload = {
            "message": message,
            "session_id": session_id,
            "interface": "chat"
        }
        
        try:
            with requests.post(url, json=payload, stream=True, timeout=25) as response:
                if response.status_code == 200:
                    # Parse key data from stream
                    tool_calls = 0
                    tokens = 0
                    profile_found = False
                    bid_cards_found = 0
                    connected = False
                    
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
                                elif msg_type == 'metadata':
                                    metadata = data.get('metadata', {})
                                    if metadata.get('profile'):
                                        profile_found = True
                                    bid_cards_found = len(metadata.get('bid_cards', []))
                                elif msg_type == 'complete':
                                    break
                            except:
                                continue
                    
                    results.append({
                        'turn': i,
                        'connected': connected,
                        'tool_calls': tool_calls,
                        'tokens': tokens,
                        'profile_found': profile_found,
                        'bid_cards_found': bid_cards_found
                    })
                    
                    print(f"   ✅ Connected: {connected}, Tools: {tool_calls}, Tokens: {tokens}")
                    if profile_found:
                        print(f"   📋 Profile created")
                    if bid_cards_found > 0:
                        print(f"   🗂️ Found {bid_cards_found} bid cards")
                        
                else:
                    print(f"   ❌ Error: {response.status_code}")
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(2)  # Brief pause between messages
    
    return results

def main():
    """Run the complete workflow test"""
    print("🚀 COIA MULTI-TURN CONVERSATION TEST")
    print(f"⏰ Started: {datetime.now().strftime('%H:%M:%S')}")
    
    # Test TurfGrass with multiple conversation turns
    turfgrass_session = f"turfgrass_{int(time.time())}"
    turfgrass_messages = [
        "Hi, I own TurfGrass Artificial Solutions in South Florida. We specialize in artificial grass installation and landscaping services.",
        "That sounds right! We also do putting greens and commercial landscaping. Can you show me more details about those projects?",
        "What's the process for submitting bids? Do you need any additional information from us?"
    ]
    
    turfgrass_results = test_contractor_conversation("TurfGrass Artificial Solutions", turfgrass_messages, turfgrass_session)
    
    # Test JM Holiday Lighting with multiple turns  
    jm_session = f"jm_holiday_{int(time.time())}"
    jm_messages = [
        "Hello, I'm with JM Holiday Lighting. We provide professional holiday lighting installation and electrical services in South Florida.",
        "Perfect! We do both residential and commercial displays. Can you tell me more about the commercial project?",
        "We have all necessary electrical licenses. What's the timeline for these holiday projects?"
    ]
    
    jm_results = test_contractor_conversation("JM Holiday Lighting", jm_messages, jm_session)
    
    # Session persistence test
    print(f"\n=== TESTING SESSION PERSISTENCE ===")
    time.sleep(3)
    
    # Test if TurfGrass session remembers previous conversation
    persistence_payload = {
        "message": "Can you remind me what projects you found for my landscaping business?",
        "session_id": turfgrass_session,
        "interface": "chat"
    }
    
    try:
        with requests.post(f"{get_backend_url()}/ai/coia/chat/stream", 
                          json=persistence_payload, stream=True, timeout=15) as response:
            if response.status_code == 200:
                conversation_text = ""
                for line in response.iter_lines():
                    if line and 'token' in line.decode('utf-8'):
                        try:
                            data = json.loads(line.decode('utf-8')[6:])
                            if data.get('type') == 'token':
                                conversation_text += data.get('content', '')
                        except:
                            continue
                
                if "turfgrass" in conversation_text.lower() or "artificial" in conversation_text.lower():
                    print("✅ Session persistence: COIA remembered TurfGrass")
                else:
                    print("⚠️ Session persistence: Memory unclear")
            else:
                print(f"❌ Persistence test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Persistence test error: {e}")
    
    # Final summary
    print(f"\n=== FINAL RESULTS ===")
    print(f"⏰ Completed: {datetime.now().strftime('%H:%M:%S')}")
    
    turfgrass_success = len([r for r in turfgrass_results if r['connected'] and r['tool_calls'] > 0]) >= 2
    jm_success = len([r for r in jm_results if r['connected'] and r['tool_calls'] > 0]) >= 2
    
    print(f"✅ TurfGrass workflow: {'PASSED' if turfgrass_success else 'FAILED'}")
    print(f"✅ JM Holiday workflow: {'PASSED' if jm_success else 'FAILED'}")
    
    if turfgrass_success and jm_success:
        print(f"\n🎉 COMPLETE SUCCESS - COIA MULTI-TURN CONVERSATIONS WORKING!")
    else:
        print(f"\n⚠️ SOME ISSUES DETECTED")

if __name__ == "__main__":
    main()