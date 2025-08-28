"""
Direct test of COIA account creation functionality
"""

import asyncio
import requests
import json
from config.service_urls import get_backend_url

async def test_direct_account_creation():
    """Test account creation directly via COIA chat"""
    
    print("="*60)
    print("TESTING DIRECT COIA ACCOUNT CREATION")
    print("="*60)
    
    # First establish the profile
    session_id = "direct-account-test"
    
    # Step 1: Introduction
    payload1 = {
        "message": "Hi, I'm Justin from JM Holiday Lighting in South Florida, and I want to create my contractor account on InstaBids.",
        "session_id": session_id
    }
    
    print("[STEP 1] Initial contact...")
    response1 = requests.post(f"{get_backend_url()}/api/coia/chat", json=payload1, timeout=30)
    if response1.status_code == 200:
        data1 = response1.json()
        print(f"[RESPONSE 1] {data1.get('response', '')[:150]}...")
    
    # Step 2: Provide complete details 
    payload2 = {
        "message": "My company is JM Holiday Lighting, email is justin@jmholidaylighting.com, phone (954) 555-0123, we do holiday lighting installations. I've been in business 8 years and I'm ready to create my account now.",
        "session_id": session_id
    }
    
    print("\n[STEP 2] Providing complete details...")
    response2 = requests.post(f"{get_backend_url()}/api/coia/chat", json=payload2, timeout=30)
    if response2.status_code == 200:
        data2 = response2.json()
        print(f"[RESPONSE 2] {data2.get('response', '')[:150]}...")
        
        # Check if account was created
        if 'account_data' in data2:
            account = data2['account_data']
            print(f"\n[SUCCESS] Account created!")
            print(f"  Username: {account.get('username')}")
            print(f"  Password: {account.get('password')}")
            return account
    
    # Step 3: Explicit account creation request
    payload3 = {
        "message": "Please create my contractor account now with all the information I provided. I want to get my username and password.",
        "session_id": session_id
    }
    
    print("\n[STEP 3] Explicit account creation request...")
    response3 = requests.post(f"{get_backend_url()}/api/coia/chat", json=payload3, timeout=30)
    if response3.status_code == 200:
        data3 = response3.json()
        print(f"[RESPONSE 3] {data3.get('response', '')[:200]}...")
        
        # Check if account was created
        if 'account_data' in data3:
            account = data3['account_data']
            print(f"\n[SUCCESS] Account created!")
            print(f"  Username: {account.get('username')}")
            print(f"  Password: {account.get('password')}")
            return account
    
    print("\n[ERROR] Account creation was not triggered")
    return None

async def test_direct_bid_search():
    """Test bid card search directly"""
    
    print("\n" + "="*60)
    print("TESTING DIRECT BID CARD SEARCH")
    print("="*60)
    
    payload = {
        "message": "I'm a holiday lighting contractor in South Florida. Show me electrical projects I can bid on.",
        "session_id": "bid-search-test"
    }
    
    print("[SEARCH] Searching for electrical bid cards...")
    response = requests.post(f"{get_backend_url()}/api/coia/chat", json=payload, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        print(f"[RESPONSE] {data.get('response', '')[:200]}...")
        
        # Check if bid cards were found
        if 'bid_cards_attached' in data:
            cards = data['bid_cards_attached'] 
            print(f"\n[SUCCESS] Found {len(cards)} bid cards")
            for card in cards:
                print(f"  - {card.get('bid_card_number')}: {card.get('project_type')}")
            return cards
        else:
            print("\n[INFO] No bid cards found in response")
    
    return []

async def main():
    """Run direct tests"""
    
    # Test account creation
    account = await test_direct_account_creation()
    
    # Test bid search
    bid_cards = await test_direct_bid_search()
    
    print("\n" + "="*60)
    print("DIRECT TEST SUMMARY")
    print("="*60)
    print(f"Account Creation: {'SUCCESS' if account else 'FAILED'}")
    print(f"Bid Card Search: {'SUCCESS' if bid_cards else 'FAILED'}")
    
    if account:
        print(f"\nAccount Details:")
        print(f"  Username: {account.get('username')}")
        print(f"  Password: {account.get('password')}")
        print(f"  Company: {account.get('company_name')}")

if __name__ == "__main__":
    asyncio.run(main())