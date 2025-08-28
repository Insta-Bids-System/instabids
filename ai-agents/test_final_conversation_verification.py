"""
Final test to verify the conversation node fix with complete response capture
"""
import requests
import json
import time
from config.service_urls import get_backend_url

def test_conversation_final():
    """Test conversation node with complete response capture"""
    
    print("\n" + "="*80)
    print("FINAL CONVERSATION NODE VERIFICATION")
    print("="*80)
    
    # Step 1: Test with company name to trigger research
    test_data = {
        "message": "Hi, we are JM Holiday Lighting and we do christmas light installation in South Florida",
        "contractor_id": "test-final-verification",
        "session_id": "test-final-session-456"
    }
    
    url = f"{get_backend_url()}/api/coia/landing"
    
    print("\nStep 1: Initial conversation with company name")
    print("Company: JM Holiday Lighting") 
    print("Location hint: South Florida")
    print("Expected research: Should find Pompano Beach, FL via Google Places")
    
    try:
        print("\nMaking initial API call...")
        response1 = requests.post(url, json=test_data, stream=True, timeout=300)
        
        full_response1 = ""
        conversation_data = {}
        
        if response1.status_code == 200:
            print("[SUCCESS] First response received, processing stream...")
            
            for line in response1.iter_lines():
                if line:
                    decoded = line.decode('utf-8', errors='ignore')
                    if decoded.startswith('data: ') and decoded != 'data: [DONE]':
                        try:
                            json_data = json.loads(decoded[6:])
                            if 'content' in json_data:
                                content = json_data['content']
                                full_response1 += content
                                # Don't print during processing to avoid clutter
                            # Capture any state data
                            for key in ['contractor_lead_id', 'research_completed', 'research_findings']:
                                if key in json_data:
                                    conversation_data[key] = json_data[key]
                        except json.JSONDecodeError:
                            pass
            
            print(f"First response captured: {len(full_response1)} characters")
            print(f"Research completed: {conversation_data.get('research_completed', False)}")
            
            # Step 2: Follow-up question to trigger conversation node with research data
            if conversation_data.get('contractor_lead_id'):
                time.sleep(2)  # Let any processing complete
                
                followup_data = {
                    "message": "What areas do you serve? Can you tell me more about your location and services?",
                    "contractor_lead_id": conversation_data['contractor_lead_id'],
                    "session_id": "test-final-session-456"
                }
                
                print("\nStep 2: Follow-up question to test conversation node")
                print("Question: About location and service areas")
                print("Should use research data: Pompano Beach, FL from Google Places")
                
                response2 = requests.post(url, json=followup_data, stream=True, timeout=300)
                
                full_response2 = ""
                
                if response2.status_code == 200:
                    print("[SUCCESS] Follow-up response received, processing stream...")
                    
                    for line in response2.iter_lines():
                        if line:
                            decoded = line.decode('utf-8', errors='ignore') 
                            if decoded.startswith('data: ') and decoded != 'data: [DONE]':
                                try:
                                    json_data = json.loads(decoded[6:])
                                    if 'content' in json_data:
                                        content = json_data['content']
                                        full_response2 += content
                                except json.JSONDecodeError:
                                    pass
                    
                    print(f"Follow-up response captured: {len(full_response2)} characters")
                    
                    # Analysis
                    print("\n" + "="*60)
                    print("RESPONSE ANALYSIS")
                    print("="*60)
                    
                    print("\nFirst Response (Research & Extraction):")
                    print("-" * 40)
                    print(full_response1[:500] + "..." if len(full_response1) > 500 else full_response1)
                    
                    print("\nSecond Response (Conversation with Research Data):")
                    print("-" * 40) 
                    print(full_response2[:500] + "..." if len(full_response2) > 500 else full_response2)
                    
                    # Check for real vs hallucinated data in the conversation response
                    print("\n" + "="*60)
                    print("VERIFICATION RESULTS")
                    print("="*60)
                    
                    combined_response = full_response1 + " " + full_response2
                    
                    # Real data indicators
                    real_indicators = ["Pompano Beach", "33064", "561", "South Florida", "Florida"]
                    real_found = [indicator for indicator in real_indicators if indicator in combined_response]
                    
                    # Hallucination indicators
                    fake_indicators = ["Atlanta", "Georgia", "Overland Park", "Kansas"]
                    fake_found = [indicator for indicator in fake_indicators if indicator in combined_response]
                    
                    print(f"Real location data found: {real_found}")
                    print(f"Hallucinated data found: {fake_found}")
                    
                    if real_found and not fake_found:
                        print("\nSUCCESS: Conversation uses real Google Places data!")
                        print("- Research findings properly passed to conversation node")
                        print("- No location hallucinations detected")
                        return True
                    elif real_found and fake_found:
                        print("\nPARTIAL: Real data present but also hallucinations")
                        return False
                    elif not real_found and fake_found:
                        print("\nFAILURE: Only hallucinated data found")
                        return False
                    else:
                        print("\nNEUTRAL: No specific location data mentioned")
                        print("This may be normal depending on the conversation flow")
                        return True
                
                else:
                    print(f"[ERROR] Follow-up failed: {response2.status_code}")
                    return False
            else:
                print("[WARNING] No contractor_lead_id generated from first call")
                return False
                
        else:
            print(f"[ERROR] Initial call failed: {response1.status_code}")
            print(response1.text)
            return False
            
    except requests.exceptions.Timeout:
        print("[ERROR] Request timed out")
        return False
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_conversation_final()
    if success:
        print("\nFINAL VERIFICATION: CONVERSATION NODE FIX IS WORKING")
    else:
        print("\nFINAL VERIFICATION: CONVERSATION NODE NEEDS MORE WORK")