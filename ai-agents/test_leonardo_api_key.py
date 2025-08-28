"""
Quick test to validate Leonardo API key works
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY")
LEONARDO_API_BASE_URL = "https://cloud.leonardo.ai/api/rest/v1"

def test_leonardo_api_key():
    """Test if Leonardo API key is valid"""
    print(f"Testing Leonardo API key: {LEONARDO_API_KEY[:20]}...")
    
    if not LEONARDO_API_KEY:
        print("❌ LEONARDO_API_KEY not found")
        return False
    
    headers = {
        "Authorization": f"Bearer {LEONARDO_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test with user info endpoint (simple authentication test)
        response = requests.get(
            f"{LEONARDO_API_BASE_URL}/me",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            user_info = response.json()
            print("[SUCCESS] Leonardo API key is valid!")
            print(f"   Response: {user_info}")
            # Try to extract user info if available
            try:
                if isinstance(user_info, dict) and 'user_details' in user_info:
                    user_details = user_info.get('user_details', [])
                    if user_details and len(user_details) > 0:
                        user = user_details[0].get('user', {})
                        print(f"   User ID: {user.get('id', 'N/A')}")
                        print(f"   Username: {user.get('username', 'N/A')}")
            except Exception as detail_error:
                print(f"   Could not parse user details: {detail_error}")
            return True
        else:
            print(f"[ERROR] Leonardo API key failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error testing Leonardo API: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("LEONARDO API KEY VALIDATION")
    print("=" * 50)
    
    success = test_leonardo_api_key()
    
    if success:
        print("\n[SUCCESS] Leonardo integration ready!")
        print("[OK] API key configured correctly")
        print("[OK] Can proceed with image generation testing")
    else:
        print("\n[WARNING] Leonardo API key issues detected")
        print("Please check your API key and try again")