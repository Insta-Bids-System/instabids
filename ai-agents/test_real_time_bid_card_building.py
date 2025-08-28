#!/usr/bin/env python3
"""
Test Real-Time Bid Card Building During CIA Conversations
This tests the complete end-to-end flow as a user would experience it
"""

import requests
import json
import time
import uuid
from datetime import datetime
import sys
import io

# Fix Windows encoding issues with emojis
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def create_test_user():
    """Create a test user for the conversation"""
    user_id = str(uuid.uuid4())
    print(f"Creating test user: {user_id}")
    
    try:
        from database_simple import get_client
        client = get_client()
        
        # Create homeowner record with minimal fields
        homeowner_data = {
            "user_id": user_id,
            "phone": "555-0123", 
            "email": f"test-{user_id[:8]}@example.com",
            "first_name": "Test",
            "last_name": "User"
        }
        
        result = client.table("homeowners").upsert(homeowner_data).execute()
        if result.data:
            print(f"SUCCESS: Created homeowner record")
            return user_id
        else:
            print(f"ERROR: Failed to create homeowner record")
            return user_id  # Continue anyway
            
    except Exception as e:
        print(f"WARNING: Could not create homeowner record: {e}")
        return user_id  # Continue anyway

def send_message_to_cia(conversation_id: str, user_id: str, message: str) -> dict:
    """Send a message to CIA and get the response"""
    payload = {
        "messages": [{"role": "user", "content": message}],
        "conversation_id": conversation_id,
        "user_id": user_id
    }
    
    print(f"💬 Sending: {message[:60]}...")
    
    try:
        response = requests.post(
            "http://localhost:8008/api/cia/stream",
            json=payload,
            timeout=30,
            stream=True
        )
        
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return {"error": f"HTTP {response.status_code}"}
        
        # Collect streaming response
        full_response = ""
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith("data: "):
                    try:
                        data = json.loads(line_str[6:])
                        if "choices" in data and len(data["choices"]) > 0:
                            content = data["choices"][0].get("delta", {}).get("content", "")
                            full_response += content
                    except:
                        pass
        
        print(f"🤖 CIA Response: {full_response[:100]}...")
        return {"response": full_response}
        
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return {"error": str(e)}

def check_potential_bid_card(conversation_id: str) -> dict:
    """Check if a potential bid card exists for this conversation"""
    try:
        response = requests.get(
            f"http://localhost:8008/api/cia/conversation/{conversation_id}/potential-bid-card",
            timeout=10
        )
        
        if response.status_code == 200:
            bid_card = response.json()
            print(f"🎯 Bid Card Found!")
            print(f"   ID: {bid_card.get('id', 'Unknown')}")
            print(f"   Title: {bid_card.get('title', 'Unknown')}")
            print(f"   Primary Trade: {bid_card.get('primary_trade', 'Unknown')}")
            print(f"   Completion: {bid_card.get('completion_percentage', 0)}%")
            print(f"   Ready for Conversion: {bid_card.get('ready_for_conversion', False)}")
            return bid_card
        elif response.status_code == 404:
            print("📋 No bid card found yet")
            return None
        else:
            print(f"❌ Error checking bid card: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error checking bid card: {e}")
        return None

def test_real_time_bid_card_building():
    """Test the complete real-time bid card building flow"""
    print("=" * 80)
    print("🚀 TESTING REAL-TIME BID CARD BUILDING DURING CIA CONVERSATIONS")
    print("=" * 80)
    
    # Setup
    conversation_id = str(uuid.uuid4())
    user_id = create_test_user()
    
    print(f"\n📝 Test Setup:")
    print(f"   Conversation ID: {conversation_id}")
    print(f"   User ID: {user_id}")
    
    # Conversation Flow - Multi-turn to build up project details
    conversation_flow = [
        "Hi! I need help with a kitchen renovation project.",
        "My kitchen is about 12x10 feet, and I want to replace the cabinets, countertops, and add a tile backsplash.",
        "My budget is around $25,000 to $35,000. I'm hoping to get this done within 6-8 weeks.",
        "I live in Chicago, IL 60614. I prefer working with licensed contractors who have good reviews.",
        "This is urgent - I'm hosting a family gathering in 2 months, so timing is important."
    ]
    
    print(f"\n🔄 Starting Multi-Turn Conversation...")
    
    for i, message in enumerate(conversation_flow, 1):
        print(f"\n--- Turn {i} ---")
        
        # Send message to CIA
        result = send_message_to_cia(conversation_id, user_id, message)
        
        if "error" in result:
            print(f"❌ Failed to send message {i}: {result['error']}")
            continue
        
        # Wait a moment for async processing
        print("⏳ Waiting 3 seconds for bid card processing...")
        time.sleep(3)
        
        # Check potential bid card status
        bid_card = check_potential_bid_card(conversation_id)
        
        if bid_card:
            print(f"🎯 Bid Card Status After Turn {i}:")
            
            # Show field extraction progress
            fields_found = []
            if bid_card.get('title') and bid_card.get('title') != 'New Project':
                fields_found.append(f"title: {bid_card.get('title')}")
            if bid_card.get('primary_trade') and bid_card.get('primary_trade') != 'general':
                fields_found.append(f"primary_trade: {bid_card.get('primary_trade')}")
            if bid_card.get('zip_code'):
                fields_found.append(f"zip_code: {bid_card.get('zip_code')}")
            if bid_card.get('email_address'):
                fields_found.append(f"email: {bid_card.get('email_address')}")
            if bid_card.get('urgency_level') and bid_card.get('urgency_level') != 'medium':
                fields_found.append(f"urgency: {bid_card.get('urgency_level')}")
            if bid_card.get('budget_range_min') or bid_card.get('budget_range_max'):
                fields_found.append(f"budget: ${bid_card.get('budget_range_min', 0)}-${bid_card.get('budget_range_max', 0)}")
            
            print(f"   Extracted Fields: {len(fields_found)}")
            for field in fields_found:
                print(f"     • {field}")
        else:
            print(f"❌ No bid card found after turn {i}")
        
        print("-" * 50)
    
    # Final Status Check
    print(f"\n🎉 FINAL BID CARD STATUS:")
    final_bid_card = check_potential_bid_card(conversation_id)
    
    if final_bid_card:
        print(f"✅ SUCCESS! Bid card was built during the conversation")
        print(f"   Final Completion: {final_bid_card.get('completion_percentage', 0)}%")
        print(f"   Ready for Conversion: {final_bid_card.get('ready_for_conversion', False)}")
        
        # Show all extracted data
        print(f"\n📊 ALL EXTRACTED DATA:")
        for key, value in final_bid_card.items():
            if value and key not in ['id', 'created_at', 'updated_at', 'ai_analysis']:
                print(f"   {key}: {value}")
                
    else:
        print(f"❌ FAILED: No bid card was created during the conversation")
    
    print("\n" + "=" * 80)
    return final_bid_card

if __name__ == "__main__":
    test_real_time_bid_card_building()