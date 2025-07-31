#!/usr/bin/env python3
"""
Simple test of CIA -> JAA flow
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Test the API endpoints directly
import requests

def test_cia_api():
    """Test CIA agent via API"""
    print("=== TESTING CIA API ===")
    
    user_id = 'e6e47a24-95ad-4af3-9ec5-f17999917bc3'
    
    payload = {
        "user_id": user_id,
        "message": """Hi! I need help with a kitchen remodel project. I live in Tampa, Florida. 
        My budget is around $25,000 to $35,000. I want to completely renovate my kitchen:
        - Replace all cabinets with white shaker style
        - Install granite countertops 
        - Update all appliances to stainless steel
        - Replace flooring with luxury vinyl plank
        - Add under-cabinet LED lighting
        The kitchen is about 250 square feet. I'd like to start within the next month."""
    }
    
    try:
        response = requests.post('http://localhost:8008/cia/chat', json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ CIA Response: {result['response'][:200]}...")
            print(f"✅ Thread ID: {result['thread_id']}")
            return result['thread_id']
        else:
            print(f"❌ CIA API failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ CIA API error: {e}")
        return None

def test_jaa_api(thread_id):
    """Test JAA agent via API"""
    print(f"\n=== TESTING JAA API ===")
    
    payload = {
        "cia_thread_id": thread_id
    }
    
    try:
        response = requests.post('http://localhost:8008/jaa/process', json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ JAA Success: Bid card {result['bid_card_number']} created")
                print(f"✅ Project: {result['bid_card_data']['project_type']}")
                print(f"✅ Budget: ${result['bid_card_data']['budget_min']}-${result['bid_card_data']['budget_max']}")
                return result
            else:
                print(f"❌ JAA failed: {result.get('error')}")
                return None
        else:
            print(f"❌ JAA API failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ JAA API error: {e}")
        return None

def verify_database():
    """Check database for results"""
    print(f"\n=== VERIFYING DATABASE ===")
    
    try:
        from database_simple import SupabaseDB
        db = SupabaseDB()
        
        user_id = 'e6e47a24-95ad-4af3-9ec5-f17999917bc3'
        
        # Get conversations
        conversations = db.client.table('agent_conversations').select('*').eq('user_id', user_id).execute()
        print(f"✅ Conversations: {len(conversations.data) if conversations.data else 0}")
        
        # Get bid cards
        bid_cards = db.client.table('bid_cards').select('*').execute()
        print(f"✅ Total bid cards: {len(bid_cards.data) if bid_cards.data else 0}")
        
        if bid_cards.data:
            user_thread_ids = [conv['thread_id'] for conv in (conversations.data or [])]
            user_bid_cards = [card for card in bid_cards.data if card['cia_thread_id'] in user_thread_ids]
            
            print(f"✅ User's bid cards: {len(user_bid_cards)}")
            
            for card in user_bid_cards:
                print(f"   - {card['project_type']} ({card['bid_card_number']})")
                print(f"     Budget: ${card['budget_min']}-${card['budget_max']}")
                print(f"     Status: {card['status']}")
                
        return True
        
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False

def main():
    print("INSTABIDS SIMPLE FLOW TEST")
    print("=" * 50)
    print("Test User: test.homeowner@instabids.com")
    print("User ID: e6e47a24-95ad-4af3-9ec5-f17999917bc3")
    print("Password: testpass123")
    
    # Test CIA conversation
    thread_id = test_cia_api()
    if not thread_id:
        print("❌ Cannot continue without CIA thread ID")
        return
    
    # Test JAA bid card generation
    bid_card_result = test_jaa_api(thread_id)
    if not bid_card_result:
        print("❌ Cannot continue without bid card")
        return
    
    # Verify database
    if verify_database():
        print("\n" + "=" * 50)
        print("✅ SIMPLE FLOW TEST COMPLETED!")
        print("\nLOGIN TO TEST DASHBOARD:")
        print("   Email: test.homeowner@instabids.com")
        print("   Password: testpass123")
        print("   URL: http://localhost:5182/dashboard")
        print("   (You should see the bid card in the dashboard)")
    else:
        print("\n❌ DATABASE VERIFICATION FAILED")

if __name__ == "__main__":
    main()