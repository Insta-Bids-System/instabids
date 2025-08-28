#!/usr/bin/env python3
"""
Simple long conversation test without Unicode issues
"""

import requests
import json
import time
import uuid

def test_conversation(scenario_name, messages_sequence, user_id=None):
    """Test a multi-turn conversation scenario"""
    if not user_id:
        user_id = str(uuid.uuid4())
        
    conv_id = f"{scenario_name}-{int(time.time())}"
    url = "http://localhost:8008/api/cia/stream"
    
    print(f"\n{'='*50}")
    print(f"TESTING: {scenario_name.upper()}")
    print('='*50)
    
    conversation = []
    all_responses = []
    
    for i, user_msg in enumerate(messages_sequence):
        print(f"\nTurn {i+1}")
        print(f"User: {user_msg}")
        
        conversation.append({"role": "user", "content": user_msg})
        
        # Add previous AI responses to conversation
        if i > 0:
            for j in range(i):
                conversation.insert(-1, {"role": "assistant", "content": all_responses[j]})
        
        payload = {
            "messages": conversation,
            "user_id": user_id,
            "conversation_id": conv_id
        }
        
        try:
            response = requests.post(url, json=payload, stream=True, timeout=30)
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
            all_responses.append(full_response)
            conversation.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            print(f"ERROR: {e}")
            return False, []
        
        time.sleep(1)  # Brief pause between turns
    
    return True, all_responses

def analyze_group_bidding():
    """Test group bidding logic"""
    messages = [
        "I want to install artificial turf in my backyard",
        "I'm in 90210 and flexible on timing",
        "My neighbors have been asking about doing the same thing",
        "Would it save money if we coordinate with neighbors?"
    ]
    
    success, responses = test_conversation("group_bidding", messages)
    
    if success:
        full_text = " ".join(responses).lower()
        group_words = ['group', 'neighbors', 'coordinate', 'bulk', 'savings', '15-25%']
        found = [w for w in group_words if w in full_text]
        
        print(f"\nGROUP BIDDING ANALYSIS:")
        print(f"Keywords found: {found}")
        return len(found) > 0
    return False

def analyze_emergency_handling():
    """Test emergency vs planned handling"""
    messages = [
        "My pipe burst in the basement and water is everywhere!",
        "This is an emergency in 60601 Chicago",
        "I need someone RIGHT NOW before more damage happens"
    ]
    
    success, responses = test_conversation("emergency_handling", messages)
    
    if success:
        full_text = " ".join(responses).lower()
        emergency_words = ['emergency', 'urgent', 'right away', 'immediately', 'asap']
        group_words = ['group', 'neighbors', 'flexible']  # Should NOT appear
        
        emergency_found = [w for w in emergency_words if w in full_text]
        group_found = [w for w in group_words if w in full_text]
        
        print(f"\nEMERGENCY HANDLING ANALYSIS:")
        print(f"Emergency keywords: {emergency_found}")
        print(f"Group keywords (bad): {group_found}")
        return len(emergency_found) > 0 and len(group_found) == 0
    return False

def analyze_budget_context():
    """Test budget context exploration without asking amounts"""
    messages = [
        "I want to remodel my kitchen",
        "New cabinets and countertops for a 12x14 room", 
        "I'm just starting to research what this might cost",
        "Do you need to know my budget?"
    ]
    
    success, responses = test_conversation("budget_context", messages)
    
    if success:
        full_text = " ".join(responses).lower()
        good_words = ['research', 'quotes', 'contractors provide', 'accurate pricing']
        bad_words = ['your budget', 'budget range', 'how much', 'dollar amount']
        
        good_found = [w for w in good_words if w in full_text]
        bad_found = [w for w in bad_words if w in full_text]
        
        print(f"\nBUDGET CONTEXT ANALYSIS:")
        print(f"Good budget exploration: {good_found}")
        print(f"Bad budget questions: {bad_found}")
        return len(good_found) > 0 and len(bad_found) == 0
    return False

def analyze_service_types():
    """Test service type classification"""
    messages = [
        "My dishwasher stopped working completely",
        "It's only 2 years old, just stopped draining",
        "Should I repair it or replace it?"
    ]
    
    success, responses = test_conversation("service_types", messages)
    
    if success:
        full_text = " ".join(responses).lower()
        repair_words = ['repair', 'fix', 'appliance']
        
        repair_found = [w for w in repair_words if w in full_text]
        
        print(f"\nSERVICE TYPE ANALYSIS:")
        print(f"Repair classification: {repair_found}")
        return len(repair_found) > 0
    return False

def run_business_logic_tests():
    """Run all business logic tests"""
    print("TESTING CIA AGENT BUSINESS LOGIC")
    print("Testing real conversations across multiple turns...")
    
    results = {}
    
    print("\n1. Testing Group Bidding Logic...")
    results['group_bidding'] = analyze_group_bidding()
    
    print("\n2. Testing Emergency Handling...")
    results['emergency'] = analyze_emergency_handling()
    
    print("\n3. Testing Budget Context...")
    results['budget'] = analyze_budget_context()
    
    print("\n4. Testing Service Type Classification...")
    results['service_types'] = analyze_service_types()
    
    # Final results
    print(f"\n{'='*50}")
    print("BUSINESS LOGIC TEST RESULTS")
    print('='*50)
    
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nSUCCESS: All business logic working in long conversations!")
    else:
        print(f"\nISSUES: {total-passed} business logic problems detected")
    
    return results

if __name__ == "__main__":
    run_business_logic_tests()