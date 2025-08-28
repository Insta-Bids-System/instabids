"""
Test the fixed conversation node with real Google Places data
"""
import requests
import json
from config.service_urls import get_backend_url

def test_conversation_fix():
    """Test that conversation node uses real Google Places data"""
    
    print("\n" + "="*80)
    print("TESTING FIXED CONVERSATION NODE")
    print("="*80)
    
    # Use a fresh session to avoid any cached state
    test_data = {
        "message": "Hello, I'm with JM Holiday Lighting, we install christmas lights in South Florida",
        "contractor_id": "coia-fix-test",
        "session_id": "fix-test-session-123"
    }
    
    url = f"{get_backend_url()}/api/coia/landing"
    
    print("\nStep 1: Test conversation with Google Places data")
    print("Company: JM Holiday Lighting")
    print("Location: South Florida") 
    print("Expected: Research should return real Google data, conversation should use it")
    
    try:
        # Make the request
        response = requests.post(url, json=test_data, timeout=300)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"[SUCCESS] Response received")
            
            # Check key fields
            research_completed = data.get("research_completed")
            research_findings = data.get("research_findings")
            ai_response = data.get("response", "")
            
            print("\n" + "="*60)
            print("RESEARCH DATA ANALYSIS")
            print("="*60)
            print(f"research_completed: {research_completed}")
            print(f"research_findings present: {research_findings is not None}")
            
            if research_findings:
                print(f"research_findings status: {research_findings.get('status')}")
                raw_data = research_findings.get("raw_data", {})
                google_data = raw_data.get("google_business", {})
                
                print(f"Google data present: {bool(google_data)}")
                if google_data:
                    print(f"  Company: {google_data.get('company_name')}")
                    print(f"  Address: {google_data.get('address')}")
                    print(f"  Phone: {google_data.get('phone')}")
                    print(f"  Website: {google_data.get('website')}")
                    print(f"  Rating: {google_data.get('rating')}")
            
            print("\n" + "="*60)
            print("AI RESPONSE ANALYSIS")
            print("="*60)
            print(f"AI Response length: {len(ai_response)} characters")
            print("AI Response excerpt:")
            print(ai_response[:500] + "..." if len(ai_response) > 500 else ai_response)
            
            # Test if AI is using real data
            if research_findings and research_findings.get("status") == "research_complete_with_real_data":
                raw_data = research_findings.get("raw_data", {})
                google_data = raw_data.get("google_business", {})
                
                if google_data:
                    website = google_data.get('website', '')
                    phone = google_data.get('phone', '')
                    address = google_data.get('address', '')
                    rating = google_data.get('rating', '')
                    
                    print("\n" + "="*60)
                    print("REAL DATA USAGE TEST")
                    print("="*60)
                    
                    # Check if AI mentions the real website
                    if website and "jmholidaylighting.com" in website:
                        if "jmholidaylighting.com" in ai_response:
                            print("SUCCESS WEBSITE: AI correctly used real website data")
                        else:
                            print("FAIL WEBSITE: AI ignored real website data")
                            print(f"   Expected: {website}")
                            print(f"   AI said: Website info not found in response")
                    
                    # Check if AI mentions real phone number
                    if phone:
                        if phone in ai_response or "phone" in ai_response.lower():
                            print("SUCCESS PHONE: AI mentioned phone information")
                        else:
                            print("FAIL PHONE: AI ignored real phone data")
                            print(f"   Expected: {phone}")
                    
                    # Check if AI mentions real location
                    if address and "Pompano Beach" in address:
                        if "Pompano Beach" in ai_response:
                            print("SUCCESS LOCATION: AI correctly used real location (Pompano Beach)")
                        else:
                            print("FAIL LOCATION: AI ignored real location data")
                            print(f"   Expected: {address}")
                    
                    # Check if AI mentions real rating
                    if rating:
                        if str(rating) in ai_response or "rating" in ai_response.lower():
                            print("SUCCESS RATING: AI mentioned rating information")
                        else:
                            print("FAIL RATING: AI ignored real rating data")
                            print(f"   Expected: {rating}")
                    
                    # Overall assessment
                    if ("jmholidaylighting.com" in ai_response and 
                        "Pompano Beach" in ai_response):
                        print("\nSUCCESS: AI is using real Google Places data!")
                        return True
                    else:
                        print("\nFAILURE: AI is still ignoring real Google Places data")
                        return False
                else:
                    print("FAIL: No Google data in research findings")
                    return False
            else:
                print("FAIL: Research not completed or no real data")
                return False
                
        else:
            print(f"[ERROR] Request failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_conversation_fix()
    if success:
        print(f"\nCONVERSATION FIX TEST: SUCCESS")
    else:
        print(f"\nCONVERSATION FIX TEST: FAILED")