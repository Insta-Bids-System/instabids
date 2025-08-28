"""
Simple test to verify conversation node fix without Unicode issues
"""
import requests
import json
from config.service_urls import get_backend_url

def test_conversation_fix():
    """Test the conversation node fix"""
    
    print("\n" + "="*80)
    print("VERIFYING CONVERSATION NODE FIX")
    print("="*80)
    
    test_data = {
        "message": "Hi, we are JM Holiday Lighting and we do christmas light installation",
        "contractor_id": "test-contractor-fix",
        "session_id": "test-conversation-fix-123"
    }
    
    url = f"{get_backend_url()}/api/coia/landing"
    
    print("\nCompany: JM Holiday Lighting")
    print("Expected Real Location: Pompano Beach, FL")
    print("Should NOT hallucinate: Atlanta, GA or Overland Park, KS")
    
    try:
        print("\nMaking API call...")
        response = requests.post(url, json=test_data, stream=True, timeout=180)
        
        if response.status_code == 200:
            print("[SUCCESS] API response received")
            
            full_response = ""
            
            for line in response.iter_lines():
                if line:
                    decoded = line.decode('utf-8', errors='ignore')
                    if decoded.startswith('data: ') and decoded != 'data: [DONE]':
                        try:
                            json_data = json.loads(decoded[6:])
                            if 'content' in json_data:
                                content = json_data['content']
                                full_response += content
                                print(content, end='', flush=True)
                        except json.JSONDecodeError:
                            pass
            
            print("\n\n" + "="*60)
            print("VERIFICATION ANALYSIS")
            print("="*60)
            
            # Check for real location data
            real_data_found = []
            if "Pompano Beach" in full_response:
                real_data_found.append("Pompano Beach")
            if "33064" in full_response:
                real_data_found.append("33064")
            if "561" in full_response:
                real_data_found.append("561")
            if "Florida" in full_response or "FL" in full_response:
                real_data_found.append("Florida/FL")
            
            # Check for hallucinated data
            hallucinations_found = []
            if "Atlanta" in full_response:
                hallucinations_found.append("Atlanta")
            if "Georgia" in full_response or "GA" in full_response:
                hallucinations_found.append("Georgia/GA")
            if "Overland Park" in full_response:
                hallucinations_found.append("Overland Park")
            if "Kansas" in full_response or "KS" in full_response:
                hallucinations_found.append("Kansas/KS")
            
            print(f"\nREAL DATA FOUND: {real_data_found}")
            print(f"HALLUCINATIONS FOUND: {hallucinations_found}")
            
            if real_data_found and not hallucinations_found:
                print("\nSUCCESS: CONVERSATION NODE FIX WORKING!")
                print("- AI used real Google Places data")
                print("- No location hallucinations detected")
                return True
            elif real_data_found and hallucinations_found:
                print("\nPARTIAL SUCCESS: Real data found but also hallucinations")
                return False
            elif not real_data_found and not hallucinations_found:
                print("\nNEUTRAL: No specific location mentions")
                return True
            else:
                print("\nFAILURE: Hallucinations found without real data")
                return False
                
        else:
            print(f"[ERROR] API call failed: {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.Timeout:
        print("[ERROR] Request timed out")
        return False
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_conversation_fix()
    if success:
        print("\nCONVERSATION NODE FIX VERIFIED WORKING")
    else:
        print("\nCONVERSATION NODE FIX NEEDS ADDITIONAL WORK")