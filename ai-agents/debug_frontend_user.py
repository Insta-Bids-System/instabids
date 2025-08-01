#!/usr/bin/env python3
"""Debug what user ID the frontend is using"""

from database_simple import db

def debug_frontend_user():
    print("=== DEBUGGING FRONTEND USER ===")
    
    # Check profiles table for test.homeowner@instabids.com
    try:
        profiles = db.client.table('profiles').select('*').eq('email', 'test.homeowner@instabids.com').execute()
        
        if profiles.data:
            user = profiles.data[0]
            print(f"[OK] Found user in profiles table:")
            print(f"   ID: {user['id']}")
            print(f"   Email: {user['email']}")
            print(f"   Name: {user.get('full_name', 'N/A')}")
            
            # Check if this user has bid cards
            actual_user_id = user['id']
            print(f"\n=== CHECKING BID CARDS FOR ACTUAL USER ID ===")
            
            # Try different possible field names for homeowner/user reference
            possible_fields = ['user_id', 'homeowner_id', 'created_by']
            
            for field in possible_fields:
                try:
                    cards = db.client.table('bid_cards').select('id, bid_card_number, project_type').eq(field, actual_user_id).execute()
                    print(f"Field '{field}': {len(cards.data)} bid cards")
                    for card in cards.data:
                        print(f"  - {card['bid_card_number']}: {card['project_type']}")
                except Exception as e:
                    print(f"Field '{field}': Error - {e}")
            
            # Test API endpoint with actual user ID
            print(f"\n=== TESTING API WITH ACTUAL USER ID ===")
            import requests
            try:
                response = requests.get(f'http://localhost:8008/api/bid-cards/homeowner/{actual_user_id}', timeout=5)
                print(f"API Status: {response.status_code}")
                if response.ok:
                    data = response.json()
                    print(f"API Response: {len(data)} bid cards")
                else:
                    print(f"API Error: {response.text}")
            except Exception as e:
                print(f"API Connection Error: {e}")
                
        else:
            print("[ERROR] No user found with email test.homeowner@instabids.com")
            print("Checking all profiles...")
            all_profiles = db.client.table('profiles').select('id, email, full_name').limit(10).execute()
            for profile in all_profiles.data:
                print(f"  - {profile['email']}: {profile['id']}")
                
    except Exception as e:
        print(f"Database Error: {e}")

if __name__ == "__main__":
    debug_frontend_user()