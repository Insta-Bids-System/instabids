#!/usr/bin/env python3
"""
Debug CIA streaming and potential bid card creation
"""

import requests
import json
import time
import asyncio
from datetime import datetime

def test_cia_streaming():
    """Test CIA streaming endpoint with debug output"""
    
    print("=" * 60)
    print("CIA STREAMING DEBUG TEST")
    print("=" * 60)
    
    # Test payload with proper UUIDs
    import uuid
    conversation_id = str(uuid.uuid4())  # Valid UUID for conversation
    user_id = str(uuid.uuid4())  # Valid UUID for user
    
    # Create test homeowner record
    print(f"Creating test homeowner record for user_id: {user_id}")
    try:
        import os
        import sys
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from database_simple import get_client
        
        client = get_client()
        
        # Create homeowner record
        homeowner_data = {
            "user_id": user_id,
            "phone": "555-0123", 
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "address": "123 Test St",
            "city": "Test City",
            "state": "TS",
            "zip": "12345",
            "preferences": {},
            "total_projects": 0
        }
        
        result = client.table("homeowners").insert(homeowner_data).execute()
        if result.data:
            print(f"✅ Created homeowner record: {result.data[0]['id']}")
        else:
            print("❌ Failed to create homeowner record")
            
    except Exception as e:
        print(f"Warning: Could not create homeowner record: {e}")
        print("Continuing with test anyway...")
    
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "I need help with a kitchen remodel. My cabinets are old and the countertops are cracked."
            }
        ],
        "conversation_id": conversation_id,
        "user_id": user_id
    }
    
    print(f"\nTest Details:")
    print(f"Conversation ID: {conversation_id}")
    print(f"User ID: {user_id}")
    print(f"Message: {payload['messages'][0]['content']}")
    
    # Make request
    print("\nSending request to CIA streaming endpoint...")
    start_time = time.time()
    
    try:
        response = requests.post(
            "http://localhost:8008/api/cia/stream",
            json=payload,
            timeout=30,
            stream=True
        )
        
        elapsed = time.time() - start_time
        print(f"Response received in {elapsed:.2f} seconds")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        # Collect streaming response
        full_response = ""
        chunk_count = 0
        for line in response.iter_lines():
            if line:
                chunk_count += 1
                line_str = line.decode('utf-8')
                if line_str.startswith("data: "):
                    try:
                        data = json.loads(line_str[6:])
                        if "choices" in data and len(data["choices"]) > 0:
                            content = data["choices"][0].get("delta", {}).get("content", "")
                            full_response += content
                    except:
                        pass
        
        print(f"\nReceived {chunk_count} chunks")
        print(f"Full response length: {len(full_response)} chars")
        print(f"Response preview: {full_response[:200]}...")
        
    except Exception as e:
        print(f"ERROR: {e}")
        return None
    
    # Wait a moment for async processing
    print("\nWaiting 3 seconds for async potential bid card creation...")
    time.sleep(3)
    
    # Check if potential bid card was created
    print("\nChecking for potential bid card creation...")
    
    # Use Supabase client
    import os
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from database_simple import get_client
    
    try:
        # Get Supabase client
        client = get_client()
        
        # Check using session_id (which is also used as cia_conversation_id)
        result = client.table("potential_bid_cards").select("*").eq("cia_conversation_id", conversation_id).execute()
        
        if result.data and len(result.data) > 0:
            bid_card = result.data[0]
            print(f"\n✅ POTENTIAL BID CARD CREATED!")
            print(f"ID: {bid_card.get('id')}")
            print(f"Title: {bid_card.get('title')}")
            print(f"Primary Trade: {bid_card.get('primary_trade')}")
            print(f"User Scope Notes: {bid_card.get('user_scope_notes')}")
            print(f"Completion %: {bid_card.get('completion_percentage')}")
            print(f"Status: {bid_card.get('status')}")
            
            # Show all fields that were extracted
            extracted_fields = []
            for field, value in bid_card.items():
                if value and field not in ['id', 'created_at', 'updated_at']:
                    extracted_fields.append(f"  - {field}: {value}")
            
            if extracted_fields:
                print("\nExtracted Fields:")
                for field in extracted_fields[:10]:  # Show first 10
                    print(field)
                    
        else:
            print("\n❌ No potential bid card found")
            
            # Check if there's any with the user_id
            user_result = client.table("potential_bid_cards").select("*").eq("user_id", user_id).limit(5).execute()
            if user_result.data:
                print(f"Found {len(user_result.data)} bid cards for user {user_id}")
                for card in user_result.data:
                    print(f"  - {card.get('id')}: {card.get('title')} (conversation: {card.get('cia_conversation_id')})")
                    
    except Exception as e:
        print(f"Database check error: {e}")
    
    return conversation_id

if __name__ == "__main__":
    test_cia_streaming()