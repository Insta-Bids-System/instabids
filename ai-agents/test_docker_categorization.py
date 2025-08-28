"""
Test categorization integration via Docker API endpoint
"""

import requests
import json
import uuid

def test_cia_stream_endpoint():
    """Test the /api/cia/stream endpoint with categorization scenarios"""
    
    base_url = "http://localhost:8008"
    endpoint = f"{base_url}/api/cia/stream"
    
    # Test data
    user_id = str(uuid.uuid4())
    
    scenarios = [
        {
            "name": "Artificial Turf",
            "message": "I need artificial turf installed in my backyard",
            "expected": "Should categorize as Installation, turf_installation"
        },
        {
            "name": "Christmas Lights", 
            "message": "Looking for someone to install christmas lights",
            "expected": "Should categorize as Installation, holiday_lighting_installation"
        },
        {
            "name": "Solar Panel",
            "message": "Solar panel installation with battery backup",
            "expected": "Should categorize as Installation, solar_panel_installation"
        }
    ]
    
    print("Testing CIA Categorization via Docker Backend")
    print("=" * 60)
    
    for i, scenario in enumerate(scenarios):
        conversation_id = f"test_{i}_{uuid.uuid4()}"
        
        print(f"\nTEST {i+1}: {scenario['name']}")
        print(f"Message: '{scenario['message']}'")
        
        # Prepare request data
        request_data = {
            "messages": [{"content": scenario['message'], "images": []}],
            "conversation_id": conversation_id,
            "user_id": user_id
        }
        
        try:
            # Make API call to Docker backend
            response = requests.post(
                endpoint,
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                # Try to read SSE stream response
                response_text = response.text
                print(f"Response length: {len(response_text)} chars")
                print(f"Response preview: {response_text[:200]}...")
                
                # Look for categorization indicators
                if any(word in response_text.lower() for word in ["installation", "turf", "lighting", "solar"]):
                    print("[SUCCESS] CATEGORIZATION EVIDENCE FOUND")
                else:
                    print("[FAILED] NO CATEGORIZATION EVIDENCE")
                    
            else:
                print(f"[ERROR] {response.status_code}")
                print(f"Response: {response.text[:300]}")
                
        except Exception as e:
            print(f"[EXCEPTION] {str(e)}")
            
        print("-" * 40)

if __name__ == "__main__":
    test_cia_stream_endpoint()