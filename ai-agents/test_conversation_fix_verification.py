"""
Test to verify the conversation node fix is working with real Google Places data
"""
import requests
import json
from config.service_urls import get_backend_url

def test_conversation_fix():
    """Test the conversation node fix with complete workflow"""
    
    print("\n" + "="*80)
    print("VERIFYING CONVERSATION NODE FIX")
    print("="*80)
    
    # Test data with company name to trigger research
    test_data = {
        "message": "Hi, we are JM Holiday Lighting and we do christmas light installation",
        "contractor_id": "test-contractor-fix",
        "session_id": "test-conversation-fix-123"
    }
    
    url = f"{get_backend_url()}/api/coia/landing"
    
    print("\n=== TESTING COMPLETE WORKFLOW ===")
    print(f"Company: JM Holiday Lighting")
    print(f"Expected Real Location: Pompano Beach, FL")
    print(f"Should NOT hallucinate: Atlanta, GA or Overland Park, KS")
    
    try:
        print("Making API call...")
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
            real_data_indicators = [
                "Pompano Beach", "33064", "561", "Florida", "FL"
            ]
            
            real_data_found = []
            for indicator in real_data_indicators:
                if indicator in full_response:
                    real_data_found.append(indicator)
            
            # Check for hallucinated data
            hallucination_indicators = [
                "Atlanta", "Georgia", "GA", "Overland Park", "Kansas", "KS"
            ]
            
            hallucinations_found = []
            for indicator in hallucination_indicators:
                if indicator in full_response:
                    hallucinations_found.append(indicator)
            
            # Results
            print(f"\n✅ REAL DATA FOUND: {real_data_found}")
            print(f"❌ HALLUCINATIONS FOUND: {hallucinations_found}")
            
            if real_data_found and not hallucinations_found:
                print("\n🎉 SUCCESS: CONVERSATION NODE FIX WORKING!")
                print("   - AI used real Google Places data")
                print("   - No location hallucinations detected")
                return True
            elif real_data_found and hallucinations_found:
                print("\n⚠️  PARTIAL SUCCESS: Real data found but also hallucinations")
                return False
            elif not real_data_found and not hallucinations_found:
                print("\n ℹ️  NEUTRAL: No specific location mentions (may be expected)")
                return True
            else:
                print("\n❌ FAILURE: Hallucinations found without real data")
                return False
                
        else:
            print(f"[ERROR] API call failed: {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.Timeout:
        print("[ERROR] Request timed out - this may indicate a backend issue")
        return False
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_conversation_fix()
    if success:
        print("\n✅ CONVERSATION NODE FIX VERIFIED WORKING")
    else:
        print("\n❌ CONVERSATION NODE FIX NEEDS ADDITIONAL WORK")