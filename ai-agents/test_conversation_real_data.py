"""
Test COIA conversation node specifically to verify it uses REAL Google Places data
and does not hallucinate location information
"""
import requests
import json
from config.service_urls import get_backend_url

def test_coia_conversation_real_data():
    """Test that conversation node uses real Google Places data"""
    
    print("\n" + "="*80)
    print("TESTING CONVERSATION NODE: REAL DATA VS HALLUCINATION")
    print("="*80)
    
    # Test data for JM Holiday Lighting (known to be in Pompano Beach, FL)
    test_data = {
        "message": "What services do you offer? I'm interested in your holiday lighting options.",
        "contractor_id": "test-contractor-id",
        "session_id": "test-conversation-data-123"
    }
    
    url = f"{get_backend_url()}/api/coia/landing"
    
    print("\n=== TESTING CONVERSATION WITH FOLLOW-UP QUESTION ===")
    print(f"Testing follow-up message after company extraction")
    
    response = requests.post(url, json=test_data, stream=True, timeout=60)
    
    if response.status_code == 200:
        print("[SUCCESS] Conversation response received")
        
        conversation_content = ""
        
        for line in response.iter_lines():
            if line:
                decoded = line.decode('utf-8')
                if decoded.startswith('data: ') and decoded != 'data: [DONE]':
                    try:
                        json_data = json.loads(decoded[6:])
                        if 'content' in json_data:
                            conversation_content += json_data['content']
                    except:
                        pass
        
        print("\n=== CONVERSATION CONTENT ANALYSIS ===")
        print("-" * 40)
        print("AI Response:")
        print(conversation_content)
        print("-" * 40)
        
        # Check for real data usage vs hallucination
        print("\n=== LOCATION DATA VERIFICATION ===")
        
        if "Pompano Beach" in conversation_content or "33064" in conversation_content or "561" in conversation_content:
            print("[PASS] Real Location Data: AI used real Pompano Beach, FL data ✅")
        else:
            print("[FAIL] Real Location Data: AI did not use real Pompano Beach data ❌")
        
        # Check for common hallucinations
        hallucination_locations = ["Atlanta", "Overland Park", "Kansas", "Georgia"]
        hallucination_found = False
        for location in hallucination_locations:
            if location in conversation_content:
                print(f"[FAIL] Hallucination Detected: AI mentioned '{location}' (not real) ❌")
                hallucination_found = True
        
        if not hallucination_found:
            print("[PASS] No Hallucinations: AI did not make up fake locations ✅")
        
        # Check if research data is being referenced
        if "research" in conversation_content.lower() or "found" in conversation_content.lower():
            print("[PASS] Research Reference: AI referenced research findings ✅")
        else:
            print("[INFO] Research Reference: AI may not be explicitly mentioning research")
        
        print("\n" + "="*80)
        if "Pompano Beach" in conversation_content and not hallucination_found:
            print("✅ SUCCESS: CONVERSATION USES REAL DATA - NO HALLUCINATIONS!")
            print("The conversation node fix is working correctly.")
        else:
            print("❌ ISSUE: Conversation still has problems with real data usage")
        print("="*80)
        
    else:
        print(f"[ERROR] Conversation failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_coia_conversation_real_data()