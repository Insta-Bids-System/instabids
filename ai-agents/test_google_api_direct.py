#!/usr/bin/env python3
"""
Test Google API directly to see if it's working
"""

import requests
import time

def test_google_places_api():
    """Test Google Places API directly"""
    
    print("TESTING GOOGLE PLACES API DIRECTLY")
    print("=" * 35)
    
    api_key = "AIzaSyBacJk_H4rpExmLiG1g8-nAGZJbSgC3IaA"
    company_name = "JM Holiday Lighting"
    location = "south florida"
    
    # Test Google Places Text Search
    search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    
    params = {
        "query": f"{company_name} {location}",
        "key": api_key
    }
    
    print(f"Searching for: '{company_name}' in '{location}'")
    print(f"URL: {search_url}")
    print(f"Query: {params['query']}")
    print()
    
    start_time = time.time()
    
    try:
        response = requests.get(search_url, params=params, timeout=30)
        elapsed = time.time() - start_time
        
        print(f"Response time: {elapsed:.2f} seconds")
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"Response keys: {list(data.keys())}")
            print(f"Status: {data.get('status')}")
            
            results = data.get('results', [])
            print(f"Results count: {len(results)}")
            
            if results:
                first_result = results[0]
                print(f"\nFirst result:")
                print(f"  Name: {first_result.get('name')}")
                print(f"  Address: {first_result.get('formatted_address')}")
                print(f"  Rating: {first_result.get('rating')}")
                print(f"  Place ID: {first_result.get('place_id')}")
                return True
            else:
                print("No results found")
                if data.get('status') == 'ZERO_RESULTS':
                    print("This might be normal - company may not have Google Business listing")
                return False
        else:
            print(f"Error response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"TIMEOUT after {elapsed:.2f} seconds")
        return False
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"ERROR after {elapsed:.2f} seconds: {e}")
        return False

def test_google_places_quota():
    """Test if we're hitting quota limits"""
    
    print("\nTESTING GOOGLE API QUOTA")
    print("=" * 25)
    
    api_key = "AIzaSyBacJk_H4rpExmLiG1g8-nAGZJbSgC3IaA"
    
    # Simple test query
    search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": "test",
        "key": api_key
    }
    
    try:
        response = requests.get(search_url, params=params, timeout=10)
        data = response.json()
        
        status = data.get('status')
        print(f"API Status: {status}")
        
        if status == 'OVER_QUERY_LIMIT':
            print("PROBLEM: Google API quota exceeded")
            return False
        elif status == 'REQUEST_DENIED':
            print("PROBLEM: Google API key invalid or restricted")
            return False
        elif status in ['OK', 'ZERO_RESULTS']:
            print("Google API is working")
            return True
        else:
            print(f"Unknown status: {status}")
            return False
            
    except Exception as e:
        print(f"Error testing quota: {e}")
        return False

if __name__ == "__main__":
    print("Testing Google Places API health...")
    print()
    
    # Test quota first
    quota_ok = test_google_places_quota()
    
    if quota_ok:
        # Test actual search
        search_ok = test_google_places_api()
        
        print(f"\nFINAL RESULT:")
        print(f"  Google API Working: {quota_ok}")
        print(f"  Search Working: {search_ok}")
        
        if quota_ok and search_ok:
            print("✓ Google API is functional - problem is elsewhere")
        elif quota_ok and not search_ok:
            print("✓ Google API works but no results for test company")
        else:
            print("✗ Google API has problems - this could be causing COIA crashes")
    else:
        print("✗ Google API quota/key issues - this is likely causing COIA to hang")