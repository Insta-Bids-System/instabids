#!/usr/bin/env python3
"""Test login credentials and verify user exists"""

from database_simple import db
import requests
import json

# Test user credentials from the tests
TEST_EMAIL = "test.homeowner@instabids.com"
TEST_PASSWORD = "testpass123"
TEST_USER_ID = "e6e47a24-95ad-4af3-9ec5-f17999917bc3"

def check_user_in_database():
    """Check if the test user exists in the database"""
    print("=== CHECKING USER IN DATABASE ===")
    
    try:
        # Check users table
        users = db.client.table('users').select('*').eq('email', TEST_EMAIL).execute()
        
        if users.data:
            user = users.data[0]
            print(f"✅ User found in database:")
            print(f"   Email: {user['email']}")
            print(f"   ID: {user['id']}")
            print(f"   Created: {user.get('created_at', 'N/A')}")
            return user
        else:
            print(f"❌ User {TEST_EMAIL} not found in database")
            return None
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return None

def check_user_bid_cards():
    """Check bid cards for the test user"""
    print(f"\n=== CHECKING BID CARDS FOR USER ===")
    
    try:
        # Get bid cards for this user
        bid_cards = db.client.table('bid_cards').select('*').order('created_at', desc=True).limit(10).execute()
        
        user_cards = [card for card in bid_cards.data if card.get('user_id') == TEST_USER_ID or 
                      (card.get('bid_document', {}).get('all_extracted_data', {}).get('user_id') == TEST_USER_ID)]
        
        if user_cards:
            print(f"✅ Found {len(user_cards)} bid cards for user:")
            for card in user_cards[:3]:
                print(f"   - {card['bid_card_number']}: {card['project_type']} (${card['budget_min']:,}-${card['budget_max']:,})")
                
                # Check for photos
                if card.get('bid_document', {}).get('all_extracted_data', {}).get('images'):
                    images = card['bid_document']['all_extracted_data']['images']
                    print(f"     📸 {len(images)} photos attached")
        else:
            print(f"❌ No bid cards found for user {TEST_USER_ID}")
            
    except Exception as e:
        print(f"❌ Error checking bid cards: {e}")

def test_auth_api():
    """Test the authentication API if it's running"""
    print(f"\n=== TESTING AUTH API ===")
    
    auth_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        # Try login API
        response = requests.post("http://localhost:8008/api/auth/login", 
                               json=auth_data, 
                               timeout=5)
        
        print(f"Auth API Status: {response.status_code}")
        
        if response.ok:
            result = response.json()
            print(f"✅ Login successful!")
            print(f"   Token type: {result.get('token_type', 'N/A')}")
            if 'access_token' in result:
                print(f"   Access token: {result['access_token'][:20]}...")
            return True
        else:
            print(f"❌ Login failed: {response.text}")
            return False
            
    except requests.exceptions.ConnectError:
        print("❌ Auth API not running at localhost:8008")
        return False
    except requests.exceptions.Timeout:
        print("❌ Auth API timeout")
        return False
    except Exception as e:
        print(f"❌ Auth API error: {e}")
        return False

def check_frontend_status():
    """Check if frontend is running"""
    print(f"\n=== CHECKING FRONTEND STATUS ===")
    
    try:
        response = requests.get("http://localhost:5173", timeout=3)
        if response.ok:
            print("✅ Frontend running at http://localhost:5173")
            return True
        else:
            print(f"❌ Frontend responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectError:
        print("❌ Frontend not running at localhost:5173")
        return False
    except Exception as e:
        print(f"❌ Frontend check error: {e}")
        return False

def main():
    print("=" * 60)
    print("LOGIN VERIFICATION TEST")
    print("=" * 60)
    
    # Check database
    user = check_user_in_database()
    
    # Check bid cards
    check_user_bid_cards()
    
    # Check auth API
    auth_working = test_auth_api()
    
    # Check frontend
    frontend_running = check_frontend_status()
    
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    if user and auth_working and frontend_running:
        print("✅ READY TO LOGIN!")
        print(f"   URL: http://localhost:5173")
        print(f"   Email: {TEST_EMAIL}")
        print(f"   Password: {TEST_PASSWORD}")
        print("   Expected: Should see bid cards with photos in dashboard")
    else:
        print("❌ LOGIN NOT READY")
        if not user:
            print("   - User not found in database")
        if not auth_working:
            print("   - Auth API not working")
        if not frontend_running:
            print("   - Frontend not running")
    
    print("=" * 60)

if __name__ == "__main__":
    main()