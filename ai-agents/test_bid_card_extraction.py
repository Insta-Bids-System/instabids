#!/usr/bin/env python3
"""
Test EXACTLY what gets extracted and saved to bid card
Compare conversation content to what's actually stored
"""

import requests
import json
import uuid
import time
from datetime import datetime

def test_bid_card_extraction():
    """Send specific info and check what gets extracted"""
    print("="*80)
    print("BID CARD EXTRACTION ACCURACY TEST")
    print("="*80)
    
    # Unique IDs
    user_id = str(uuid.uuid4())
    conv_id = f"extraction-{datetime.now().strftime('%H%M%S')}"
    
    print(f"\nTracking IDs:")
    print(f"User ID: {user_id}")
    print(f"Conversation ID: {conv_id}")
    print("-"*80)
    
    # Very specific test data
    test_data = {
        "project": "artificial turf installation",
        "location": "90210", 
        "city": "Beverly Hills",
        "size": "2000 square feet",
        "timeline": "spring 2025",
        "email": "john.smith@example.com",
        "phone": "555-1234",
        "urgency": "flexible, just researching",
        "special_requirements": "need pet-friendly turf for two dogs",
        "group_interest": "5 neighbors want to do it together",
        "current_issue": "grass is dying from drought"
    }
    
    # Create message with all the specific details
    message = f"""
    I need {test_data['project']} for my backyard. I'm located in {test_data['location']} 
    in {test_data['city']}. The area is {test_data['size']}. 
    Timeline: {test_data['timeline']} - {test_data['urgency']}.
    
    Special requirements: {test_data['special_requirements']}.
    Also, {test_data['group_interest']}.
    
    Current situation: {test_data['current_issue']}.
    
    My email is {test_data['email']} and phone is {test_data['phone']}.
    """
    
    print("\nSENDING MESSAGE WITH SPECIFIC DATA:")
    print("-"*40)
    for key, value in test_data.items():
        print(f"  {key}: {value}")
    
    # Make API call
    url = "http://localhost:8008/api/cia/stream"
    payload = {
        "messages": [{"role": "user", "content": message}],
        "user_id": user_id,
        "conversation_id": conv_id
    }
    
    print("\n" + "-"*80)
    print("CALLING CIA AGENT...")
    print("-"*80)
    
    try:
        response = requests.post(url, json=payload, stream=True, timeout=30)
        
        full_response = ""
        chunks_with_tools = []
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_str = line_str[6:]
                    if data_str.strip() != '[DONE]':
                        try:
                            data = json.loads(data_str)
                            
                            # Look for tool calls in the stream
                            if 'choices' in data:
                                choice = data['choices'][0]
                                
                                # Get content
                                if 'delta' in choice and 'content' in choice['delta']:
                                    full_response += choice['delta']['content']
                                
                                # Check for tool calls
                                if 'delta' in choice and 'tool_calls' in choice['delta']:
                                    chunks_with_tools.append(data)
                                    print("\n[TOOL CALL DETECTED IN STREAM]")
                                    print(json.dumps(choice['delta']['tool_calls'], indent=2))
                                    
                        except Exception as e:
                            pass
        
        print("\nAI RESPONSE:")
        print(full_response[:500] + "..." if len(full_response) > 500 else full_response)
        
        print("\n" + "="*80)
        print("EXTRACTION ANALYSIS")
        print("="*80)
        
        # Check what the AI acknowledged
        response_lower = full_response.lower()
        
        print("\nWHAT WAS MENTIONED IN RESPONSE:")
        print("-"*40)
        
        extractions = {
            "Project Type (artificial turf)": "turf" in response_lower,
            "Location (90210)": "90210" in response_lower,
            "City (Beverly Hills)": "beverly" in response_lower,
            "Size (2000 sq ft)": "2000" in response_lower,
            "Timeline (spring)": "spring" in response_lower,
            "Email (john.smith)": "email" in response_lower or "account" in response_lower,
            "Phone (555-1234)": "555" in response_lower or "phone" in response_lower,
            "Pet-friendly requirement": "pet" in response_lower or "dog" in response_lower,
            "Group bidding (5 neighbors)": "neighbor" in response_lower or "group" in response_lower,
            "Drought issue": "drought" in response_lower or "dying" in response_lower,
        }
        
        acknowledged = 0
        not_acknowledged = []
        
        for item, found in extractions.items():
            status = "YES" if found else "NO"
            if found:
                acknowledged += 1
            else:
                not_acknowledged.append(item)
            print(f"  [{status}] {item}")
        
        print(f"\nACKNOWLEDGED: {acknowledged}/10 items in response")
        
        if not_acknowledged:
            print("\nNOT MENTIONED IN RESPONSE:")
            for item in not_acknowledged:
                print(f"  - {item}")
        
        print("\n" + "="*80)
        print("TOOL CALLING ANALYSIS")
        print("="*80)
        
        if chunks_with_tools:
            print(f"Tool calls found: {len(chunks_with_tools)}")
            print("The update_bid_card tool WAS called during processing")
        else:
            print("No tool calls visible in stream")
            print("(Tools may be called server-side but not streamed)")
        
        print("\n" + "="*80)
        print("WHAT SHOULD BE IN DATABASE:")
        print("="*80)
        
        print("\nEXPECTED bid_card fields:")
        print("  - project_type: 'artificial turf installation' or 'lawn installation'")
        print("  - location: '90210' or 'Beverly Hills, CA 90210'")
        print("  - timeline: 'spring 2025' or 'flexible'")
        print("  - scope_details: Should mention 2000 sq ft, pet-friendly, dying grass")
        print("  - email: 'john.smith@example.com'")
        print("  - phone: '555-1234' (if captured)")
        print("  - group_bidding: true or mentioned in notes")
        print("  - urgency: 'low' or 'research'")
        
        print("\nTO VERIFY IN DATABASE:")
        print(f"1. Check potential_bid_cards table for user_id: {user_id}")
        print(f"2. Check potential_bid_cards table for conversation_id: {conv_id}")
        print("3. Compare extracted fields to what was sent")
        
        print("\n" + "="*80)
        print("POTENTIAL ISSUES TO CHECK:")
        print("-"*40)
        print("1. Are fields being overwritten with defaults?")
        print("2. Is old data from other conversations leaking in?")
        print("3. Are all fields from the message being extracted?")
        print("4. Is the tool being called with the right arguments?")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_bid_card_extraction()