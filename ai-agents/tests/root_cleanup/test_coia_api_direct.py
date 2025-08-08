"""
Test COIA API directly via HTTP requests
Check if research mode actually works
"""

import asyncio
import requests
import json

def test_coia_api():
    """Test COIA API directly"""
    
    print("TESTING COIA API DIRECTLY")
    print("=" * 50)
    
    # Backend URL
    base_url = "http://localhost:8008"
    
    # Test message that should trigger research
    payload = {
        "message": "Hi, I'm from Turf Grass Artificial Solutions. We're a landscaping company based in South Florida. We do artificial turf installation.",
        "session_id": "test_direct_api",
        "contractor_lead_id": "test_lead_123"
    }
    
    try:
        print("1. Sending to COIA Landing Page API...")
        print(f"Payload: {payload}")
        
        response = requests.post(
            f"{base_url}/api/coia/landing",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n2. RESPONSE DATA:")
            print(f"Success: {data.get('success')}")
            print(f"Current Mode: {data.get('current_mode')}")
            print(f"Interface: {data.get('interface')}")
            print(f"Response: {data.get('response', 'No response')[:200]}...")
            
            # Check contractor profile
            profile = data.get("contractor_profile", {})
            print(f"\n3. CONTRACTOR PROFILE:")
            if profile:
                critical_fields = [
                    "company_name", "main_service_type", "business_size_category",
                    "service_subtypes", "zip_codes", "website", "phone"
                ]
                
                for field in critical_fields:
                    value = profile.get(field)
                    if value:
                        print(f"  {field}: {value}")
                
                # Show all profile fields
                print(f"\n4. ALL PROFILE FIELDS:")
                for key, value in profile.items():
                    if value:  # Only show non-empty fields
                        print(f"  {key}: {value}")
            else:
                print("  No profile data found")
            
            # Check research status
            research_completed = data.get("research_completed")
            research_status = data.get("website_research_status")
            
            print(f"\n5. RESEARCH STATUS:")
            print(f"  Research Completed: {research_completed}")
            print(f"  Website Research Status: {research_status}")
            
            if data.get("research_findings"):
                print(f"  Research Findings: {data['research_findings']}")
            
            return data
            
        else:
            print(f"ERROR: API returned {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"ERROR: {e}")
        return None

if __name__ == "__main__":
    result = test_coia_api()
    
    if result:
        print("\n" + "=" * 50)
        print("SUMMARY")
        print("=" * 50)
        
        profile = result.get("contractor_profile", {})
        has_company = bool(profile.get("company_name"))
        has_service = bool(profile.get("main_service_type"))
        has_size = bool(profile.get("business_size_category"))
        
        if has_company and has_service and has_size:
            print("SUCCESS: Critical fields extracted")
            print("COIA can build contractor profiles!")
        else:
            print("PARTIAL: Some fields missing")
            print("More work needed for complete profiles")
    else:
        print("FAILED: No response from COIA API")