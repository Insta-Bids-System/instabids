"""
Final test for categorization tool integration
This test calls the API endpoint directly to check if categorization is working
"""

import requests
import json
import time

def test_categorization():
    """Test categorization through the working API"""
    
    print("=" * 60)
    print("TESTING CIA CATEGORIZATION TOOL INTEGRATION")
    print("=" * 60)
    
    # Test scenarios that should trigger categorization
    test_messages = [
        "I need artificial turf installed in my backyard",
        "Christmas lights installation for the holidays",
        "I want to install a new pool and hot tub",
        "Need some work done on my house",
        "Solar panel installation on my roof"
    ]
    
    base_url = "http://localhost:8008/api/cia/stream"
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n[TEST {i}] Message: '{message}'")
        print("-" * 40)
        
        payload = {
            "messages": [{"role": "user", "content": message}],
            "user_id": f"test-user-{i}",
            "conversation_id": f"test-conv-{i}"
        }
        
        try:
            # Send request
            response = requests.post(base_url, json=payload, stream=True)
            
            if response.status_code == 200:
                # Collect streamed response
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            data_str = line_str[6:]  # Remove 'data: ' prefix
                            if data_str != '[DONE]':
                                try:
                                    data = json.loads(data_str)
                                    if 'choices' in data and data['choices']:
                                        content = data['choices'][0].get('delta', {}).get('content', '')
                                        full_response += content
                                except json.JSONDecodeError:
                                    pass
                
                # Check for categorization evidence
                categorization_indicators = [
                    "Tagged as", "confidence", "Installation", "Repair",
                    "turf_installation", "christmas_lights", "pool_installation",
                    "solar_installation", "categorize_project"
                ]
                
                response_lower = full_response.lower()
                found_indicators = []
                
                for indicator in categorization_indicators:
                    if indicator.lower() in response_lower:
                        found_indicators.append(indicator)
                
                if found_indicators:
                    print(f"[OK] CATEGORIZATION EVIDENCE FOUND: {found_indicators}")
                    
                    # Look for specific Tagged output
                    if "tagged as" in response_lower:
                        print("[SUCCESS] 'Tagged as' output found - categorization tool executed!")
                        # Extract the tagged line
                        lines = full_response.split('\n')
                        for line in lines:
                            if 'tagged' in line.lower():
                                print(f"   Tool output: {line.strip()}")
                    else:
                        print("[PARTIAL] Found keywords but no 'Tagged as' output")
                else:
                    print("[FAILED] No categorization evidence found")
                
                # Show first 200 chars of response
                print(f"Response preview: {full_response[:200]}...")
                
            else:
                print(f"[ERROR] HTTP {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"[EXCEPTION] {str(e)}")
        
        time.sleep(1)  # Small delay between tests
    
    print("\n" + "=" * 60)
    print("CATEGORIZATION TEST COMPLETE")
    print("=" * 60)
    
    print("\n[ANALYSIS]")
    print("If no 'Tagged as' outputs were found, the categorization tool is NOT being called.")
    print("The CIA agent should be calling the categorize_project tool for clear project types.")

if __name__ == "__main__":
    test_categorization()