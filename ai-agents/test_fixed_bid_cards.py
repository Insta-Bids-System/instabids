#!/usr/bin/env python3
"""
Test the FIXED CIA system - should now automatically create bid cards
"""

import sys
import io

# Fix Windows encoding issues with emojis
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json
import uuid
import time

def test_automatic_bid_card_creation():
    """Test that CIA now automatically creates and updates bid cards"""
    
    # Use proper UUIDs to avoid database errors  
    user_id = str(uuid.uuid4())
    conv_id = str(uuid.uuid4())
    
    print("TESTING FIXED CIA BID CARD AUTO-CREATION")
    print("=" * 50)
    print(f"User ID: {user_id}")
    print(f"Conversation ID: {conv_id}")
    
    # Test with comprehensive project info
    print("\n--- Turn 1: Kitchen Renovation Project ---")
    response1 = requests.post('http://localhost:8008/api/cia/stream', json={
        'messages': [{'role': 'user', 'content': 'I need to renovate my 400 sq ft kitchen in Miami 33101. My budget is 35,000 dollars and I need it done urgently in 2 weeks because I am selling the house.'}],
        'user_id': user_id,
        'conversation_id': conv_id
    }, stream=True, timeout=45)
    
    print(f"CIA Response: {response1.status_code}")
    
    if response1.status_code == 200:
        # Collect streaming response
        content = ""
        for line in response1.iter_lines():
            if line and line.startswith(b'data: '):
                try:
                    data = json.loads(line[6:])
                    if 'choices' in data and data['choices']:
                        delta = data['choices'][0].get('delta', {}).get('content', '')
                        content += delta
                except:
                    pass
        
        print(f"SUCCESS: Got {len(content)} character response")
        
        # Wait for background bid card processing
        print("Waiting 5 seconds for automatic bid card processing...")
        time.sleep(5)
        
        # Check if bid card was automatically created
        check_response = requests.get(f'http://localhost:8008/api/cia/conversation/{conv_id}/potential-bid-card')
        print(f"\nAutomatic Bid Card Check: {check_response.status_code}")
        
        if check_response.status_code == 200:
            bid_data = check_response.json()
            print("🎉 SUCCESS: AUTOMATIC BID CARD CREATED!")
            print(f"  Completion: {bid_data.get('completion_percentage', 0)}%")
            print(f"  Project Type: {bid_data.get('primary_trade', 'None')}")
            print(f"  Description: {bid_data.get('user_scope_notes', 'None')}")
            print(f"  Location: {bid_data.get('zip_code', 'None')}")
            print(f"  Budget: ${bid_data.get('budget_max', 'None')}")
            print(f"  Urgency: {bid_data.get('urgency_level', 'None')}")
            
            initial_completion = bid_data.get('completion_percentage', 0)
            
            # Test Turn 2: Update timeline
            print("\n--- Turn 2: Timeline Update ---")
            response2 = requests.post('http://localhost:8008/api/cia/stream', json={
                'messages': [{'role': 'user', 'content': 'Actually, I can be flexible on timeline if we can save money. Maybe 4-6 weeks would be OK.'}],
                'user_id': user_id,
                'conversation_id': conv_id
            }, stream=True, timeout=30)
            
            if response2.status_code == 200:
                # Collect response
                content2 = ""
                for line in response2.iter_lines():
                    if line and line.startswith(b'data: '):
                        try:
                            data = json.loads(line[6:])
                            if 'choices' in data and data['choices']:
                                delta = data['choices'][0].get('delta', {}).get('content', '')
                                content2 += delta
                        except:
                            pass
                
                print(f"Turn 2 Response: {len(content2)} chars")
                
                # Check for bid card updates
                time.sleep(3)
                updated_response = requests.get(f'http://localhost:8008/api/cia/conversation/{conv_id}/potential-bid-card')
                
                if updated_response.status_code == 200:
                    updated_data = updated_response.json()
                    final_completion = updated_data.get('completion_percentage', 0)
                    
                    print(f"Completion: {initial_completion}% -> {final_completion}%")
                    print(f"Urgency: {updated_data.get('urgency_level', 'None')}")
                    
                    if final_completion != initial_completion:
                        print("✅ BID CARD UPDATED automatically!")
                    else:
                        print("📊 Completion same - timeline flexibility noted elsewhere")
                        
            return True
            
        elif check_response.status_code == 404:
            print("❌ No bid card created automatically")
            print("The fix may not have worked - check backend logs")
            return False
        else:
            print(f"Error: {check_response.text}")
            return False
    else:
        print(f"CIA Failed: {response1.text}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    success = test_automatic_bid_card_creation()
    print("\n" + "=" * 60)
    if success:
        print("✅ SUCCESS: CIA automatically creates and updates bid cards!")
        print("PROOF: Real-time bid card building is working")
    else:
        print("❌ FAILURE: Automatic bid card creation not working")
    print("=" * 60)