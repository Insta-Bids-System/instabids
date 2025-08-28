"""
Test COIA landing page with real Google Places data for JM Holiday Lighting
"""
import asyncio
import requests
import json
import time
from config.service_urls import get_backend_url

async def test_coia_landing_with_real_data():
    """Test the COIA landing page endpoint with JM Holiday Lighting"""
    
    print("\n" + "="*80)
    print("TESTING COIA LANDING PAGE WITH REAL GOOGLE PLACES DATA")
    print("="*80)
    
    # Test with JM Holiday Lighting
    test_data = {
        "message": "We are JM Holiday Lighting and we do christmas light installation",
        "contractor_id": "test-contractor-id",
        "session_id": "test-session-id"
    }
    
    url = f"{get_backend_url()}/api/coia/landing"
    
    print(f"\nCalling COIA landing page endpoint...")
    print(f"URL: {url}")
    print(f"Request data: {json.dumps(test_data, indent=2)}")
    
    try:
        # Make the request with SSE streaming
        response = requests.post(
            url,
            json=test_data,
            stream=True,
            timeout=60
        )
        
        print(f"\nResponse status: {response.status_code}")
        
        if response.status_code == 200:
            print("\nStreaming response:")
            print("-" * 40)
            
            full_response = ""
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data: '):
                        data_content = decoded_line[6:]
                        if data_content and data_content != '[DONE]':
                            try:
                                # Parse the JSON data
                                json_data = json.loads(data_content)
                                if 'content' in json_data:
                                    content = json_data['content']
                                    print(content, end='', flush=True)
                                    full_response += content
                                elif 'research_data' in json_data:
                                    print(f"\n\nResearch Data Received:")
                                    research = json_data['research_data']
                                    print(json.dumps(research, indent=2))
                                elif 'contractor_profile' in json_data:
                                    print(f"\n\nContractor Profile Created:")
                                    profile = json_data['contractor_profile']
                                    print(json.dumps(profile, indent=2))
                            except json.JSONDecodeError:
                                pass
            
            print("\n" + "-" * 40)
            print(f"\nSUCCESS: Received complete response")
            
            # Check if we got real data (not hallucinated)
            if "Pompano Beach" in full_response or "561" in full_response:
                print("\nVERIFIED: Using REAL Google Places data (Pompano Beach, FL location found!)")
            elif "Atlanta" in full_response:
                print("\nWARNING: Still hallucinating Atlanta location - Google API not working")
            else:
                print("\nCould not verify if using real or hallucinated data")
                
        else:
            print(f"\nERROR: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("\nRequest timed out after 60 seconds")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting COIA landing page test with real Google Places data...")
    asyncio.run(test_coia_landing_with_real_data())