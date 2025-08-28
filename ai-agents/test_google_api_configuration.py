#!/usr/bin/env python3
"""
Test Google Places API Configuration
Verifies API key and identifies configuration issues
"""

import os
import requests
import json
from dotenv import load_dotenv

def test_google_api_configuration():
    """Test Google API configuration and identify issues"""
    
    print("GOOGLE PLACES API CONFIGURATION TEST")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        print("[ERROR] No Google API key found in environment variables")
        print("   Fix: Add GOOGLE_MAPS_API_KEY to .env file")
        return False
    
    print(f"[OK] API Key found: {api_key[:20]}...")
    print()
    
    # Test 1: Check API key validity with simple request
    print("Test 1: Checking API key validity...")
    test_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        "input": "test",
        "inputtype": "textquery",
        "key": api_key
    }
    
    try:
        response = requests.get(test_url, params=params, timeout=10)
        data = response.json()
        
        status = data.get("status")
        print(f"  Status: {status}")
        
        if status == "REQUEST_DENIED":
            error_message = data.get("error_message", "No error message provided")
            print(f"  [X] API Key Problem: {error_message}")
            
            # Common issues
            print("\n  Possible fixes:")
            print("  1. Enable Places API in Google Cloud Console")
            print("  2. Check API key restrictions (HTTP referrers, IP addresses)")
            print("  3. Verify billing account is active")
            print("  4. Create a new unrestricted API key for testing")
            
            return False
            
        elif status == "OVER_QUERY_LIMIT":
            print("  [X] Quota exceeded - check Google Cloud Console")
            return False
            
        elif status in ["OK", "ZERO_RESULTS"]:
            print("  [X] API key is valid and working!")
            
        else:
            print(f"  [X] Unknown status: {status}")
            
    except Exception as e:
        print(f"  [X] Error testing API: {e}")
        return False
    
    print()
    
    # Test 2: Try new Places API (v1)
    print("Test 2: Testing new Places API (v1)...")
    new_api_url = "https://places.googleapis.com/v1/places:searchText"
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress"
    }
    
    data = {
        "textQuery": "JM Holiday Lighting south florida",
        "languageCode": "en",
        "maxResultCount": 1
    }
    
    try:
        response = requests.post(new_api_url, json=data, headers=headers, timeout=10)
        
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("places"):
                print("  [X] New Places API working!")
                place = result["places"][0]
                print(f"    Found: {place.get('displayName', {}).get('text', 'Unknown')}")
            else:
                print("  [X] API working but no results for test query")
        else:
            print(f"  [X] Error: {response.text}")
            
            # Parse error for more details
            try:
                error_data = response.json()
                if "error" in error_data:
                    error_msg = error_data["error"].get("message", "")
                    print(f"    Error details: {error_msg}")
            except:
                pass
                
    except Exception as e:
        print(f"  [X] Error with new API: {e}")
    
    print()
    
    # Test 3: Check what APIs are enabled
    print("Test 3: API Key Analysis...")
    print("  Current key:", api_key)
    print()
    print("  To fix REQUEST_DENIED:")
    print("  1. Go to: https://console.cloud.google.com/apis/credentials")
    print("  2. Find your API key")
    print("  3. Remove all restrictions (for testing)")
    print("  4. Enable these APIs:")
    print("     - Places API")
    print("     - Places API (New)")
    print("     - Maps JavaScript API")
    print("  5. Ensure billing is enabled")
    print()
    print("  OR create a new unrestricted key for development")
    
    return True

if __name__ == "__main__":
    test_google_api_configuration()