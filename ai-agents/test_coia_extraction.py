"""Test COIA company name extraction specifically"""
import requests
import json
import time
from config.service_urls import get_backend_url

def test_extraction():
    print("\n" + "="*60)
    print("TESTING COMPANY NAME EXTRACTION")
    print("="*60)
    
    # Test message with clear company name
    test_message = "Hi, I'm Justin from JM Holiday Lighting. We install Christmas lights in South Florida."
    session_id = f"test-extraction-{int(time.time())}"
    
    print(f"\nTest Message: {test_message}")
    print(f"Session ID: {session_id}")
    print(f"\nMaking API call to /api/coia/landing...")
    
    try:
        response = requests.post(
            f'{get_backend_url()}/api/coia/landing',
            json={
                'message': test_message,
                'session_id': session_id
            },
            timeout=60
        )
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Print the AI response
            print(f"\n📝 AI Response (first 300 chars):")
            print(data.get('response', 'No response')[:300])
            
            # Check the state object
            state = data.get('state', {})
            print(f"\n🔍 State Analysis:")
            print(f"  - company_name: {state.get('company_name')}")
            print(f"  - contractor_created: {state.get('contractor_created')}")
            print(f"  - research_completed: {state.get('research_completed')}")
            print(f"  - extraction_completed: {state.get('extraction_completed')}")
            
            # Check contractor_profile
            contractor_profile = state.get('contractor_profile', {})
            print(f"\n👷 Contractor Profile:")
            print(f"  - company_name: {contractor_profile.get('company_name')}")
            print(f"  - business_name: {contractor_profile.get('business_name')}")
            print(f"  - contact_name: {contractor_profile.get('contact_name')}")
            print(f"  - phone: {contractor_profile.get('phone')}")
            print(f"  - email: {contractor_profile.get('email')}")
            print(f"  - Total fields: {len(contractor_profile)}")
            
            # Check research findings
            research_findings = state.get('research_findings', {})
            print(f"\n🔬 Research Findings:")
            if research_findings:
                print(f"  - Company: {research_findings.get('company_name', 'Not found')}")
                print(f"  - Website: {research_findings.get('website', 'Not found')}")
                print(f"  - Phone: {research_findings.get('phone', 'Not found')}")
            else:
                print("  - No research findings yet")
            
            # Check if Google data was used
            if 'Pompano Beach' in data.get('response', ''):
                print("\n✅ SUCCESS: Google Places data (Pompano Beach) found in response!")
            else:
                print("\n⚠️ WARNING: Google Places data not found in response")
            
            if contractor_profile.get('company_name') == 'JM Holiday Lighting':
                print("✅ SUCCESS: Company name correctly extracted!")
            else:
                print(f"❌ FAIL: Company name not extracted (got: {contractor_profile.get('company_name')})")
                
        else:
            print(f"❌ API Error: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out after 60 seconds")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_extraction()