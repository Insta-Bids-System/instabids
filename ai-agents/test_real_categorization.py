"""
Test REAL categorization tool execution after fixes
This will verify the actual categorization tool is called
"""

import requests
import json
import uuid
import time

def test_categorization_tool_execution():
    """Test that the categorization tool actually executes"""
    
    base_url = "http://localhost:8008"
    endpoint = f"{base_url}/api/cia/stream"
    
    # Test with artificial turf - should trigger categorization tool
    user_id = str(uuid.uuid4())
    conversation_id = f"categorization_fix_test_{uuid.uuid4()}"
    
    request_data = {
        "messages": [{"content": "I need artificial turf installed in my backyard", "images": []}],
        "conversation_id": conversation_id,
        "user_id": user_id
    }
    
    print("TESTING CATEGORIZATION TOOL EXECUTION")
    print("=" * 50)
    print("Request:", request_data)
    print()
    
    try:
        start_time = time.time()
        response = requests.post(
            endpoint,
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        duration = time.time() - start_time
        
        print(f"Status: {response.status_code}")
        print(f"Duration: {duration:.2f}s")
        print(f"Response length: {len(response.text)} chars")
        
        if response.status_code == 200:
            response_text = response.text
            
            # Look for evidence of actual categorization tool execution
            categorization_indicators = [
                "Tagged as",  # The specific output format from categorization tool
                "confidence",  # Confidence scores
                "categorize_project",  # Tool name
                "turf_installation",  # Expected normalized type
                "Installation"  # Expected category
            ]
            
            found_indicators = []
            for indicator in categorization_indicators:
                if indicator.lower() in response_text.lower():
                    found_indicators.append(indicator)
            
            print(f"Found categorization indicators: {found_indicators}")
            
            # Look for the specific Tagged output that indicates tool execution
            if "tagged as" in response_text.lower():
                print("\n[SUCCESS] CATEGORIZATION TOOL EXECUTED!")
                print("Found 'Tagged as' output indicating real tool execution")
                
                # Extract the tagged line
                lines = response_text.split('\n')
                for line in lines:
                    if 'tagged as' in line.lower():
                        print(f"Tool output: {line.strip()}")
                        break
                        
            elif found_indicators:
                print(f"\n[PARTIAL] Some categorization evidence found: {found_indicators}")
                print("But no 'Tagged as' output - tool may not be fully working")
                
            else:
                print("\n[FAILED] No categorization tool evidence found")
                print("CIA agent may still not be calling the categorization tool")
            
            print(f"\nResponse preview:")
            print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
            
        else:
            print(f"Error: {response.status_code}")
            print(response.text[:300])
            
    except Exception as e:
        print(f"Exception: {e}")

def monitor_backend_logs():
    """Check backend logs for categorization tool calls"""
    print("\nCHECKING BACKEND LOGS...")
    print("=" * 30)
    
    import subprocess
    try:
        result = subprocess.run([
            "docker", "logs", "instabids-instabids-backend-1", "--tail", "20"
        ], capture_output=True, text=True, timeout=10)
        
        logs = result.stdout
        
        # Look for categorization-related log entries
        categorization_logs = []
        for line in logs.split('\n'):
            if any(keyword in line.lower() for keyword in ['categorization', 'tool', 'tagged']):
                categorization_logs.append(line.strip())
        
        if categorization_logs:
            print("Found categorization-related logs:")
            for log in categorization_logs[-5:]:  # Last 5 entries
                print(f"  {log}")
        else:
            print("No categorization-related logs found")
            
    except Exception as e:
        print(f"Could not check logs: {e}")

if __name__ == "__main__":
    test_categorization_tool_execution()
    monitor_backend_logs()