#!/usr/bin/env python3
"""
Test the exact Iris endpoint directly to see what's failing
"""

import requests
import json

def test_iris_endpoint():
    """Test the failing endpoint"""
    
    print("Testing /api/iris/chat endpoint directly...")
    
    payload = {
        "message": "Can you make me a vision image now?",
        "homeowner_id": "550e8400-e29b-41d4-a716-446655440001", 
        "board_id": "26cf972b-83e4-484c-98b6-a5d1a4affee3"
    }
    
    try:
        response = requests.post(
            "http://localhost:8008/api/iris/chat",
            json=payload,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {response.headers}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success! Response: {result.get('response', 'No response')}")
        else:
            print(f"Failed with status {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_iris_endpoint()