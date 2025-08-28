import requests
from config.service_urls import get_backend_url

def test_final_verification():
    """Final test to verify COIA uses real Google Places data"""
    
    print("="*80)
    print("FINAL VERIFICATION: COIA LOCATION HALLUCINATION FIX")
    print("="*80)
    
    test_data = {
        "message": "Hi, I am JM Holiday Lighting, we do Christmas lights",
        "contractor_id": "final-test",
        "session_id": "final-verification"
    }
    
    url = f"{get_backend_url()}/api/coia/landing"
    
    try:
        response = requests.post(url, json=test_data, timeout=300)
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data.get("response", "")
            
            print("AI Response:")
            print("-" * 40)
            print(ai_response)
            print("-" * 40)
            
            # Check for real vs hallucinated data
            has_pompano_beach = "Pompano Beach" in ai_response
            has_website = "jmholidaylighting.com" in ai_response  
            has_atlanta = "Atlanta" in ai_response
            
            print(f"\nVerification Results:")
            print(f"  Uses real location (Pompano Beach): {has_pompano_beach}")
            print(f"  Uses real website: {has_website}")
            print(f"  Uses old hallucinated location (Atlanta): {has_atlanta}")
            
            if has_pompano_beach and has_website and not has_atlanta:
                print(f"\nSUCCESS: COIA is using real Google Places data\!")
                return True
            else:
                print(f"\nNot fully resolved - some issues remain")
                return False
                
        else:
            print(f"Request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_final_verification()
    if success:
        print(f"\nFINAL RESULT: LOCATION HALLUCINATION FIXED")
    else:
        print(f"\nFINAL RESULT: Issue not fully resolved")
