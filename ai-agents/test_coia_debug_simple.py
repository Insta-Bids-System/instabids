#!/usr/bin/env python3
"""
Simple COIA Debug Test
Start test and immediately check what happens
"""

import requests
import json
import threading
import time
import subprocess

def test_coia_simple():
    """Simple test with immediate logging"""
    
    print("STARTING COIA DEBUG TEST")
    print("=" * 30)
    
    test_message = "ABC Lighting company"
    
    print(f"Testing: '{test_message}'")
    print("Starting request...")
    
    try:
        response = requests.post(
            "http://localhost:8008/api/coia/landing",
            json={
                "message": test_message,
                "session_id": "debug-simple-001",
                "contractor_lead_id": "landing-debug-001"
            },
            timeout=30  # 30 seconds max
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS: Got response")
            print(f"Company: {result.get('company_name', 'None')}")
            print(f"Research: {result.get('research_completed', False)}")
            print(f"Messages: {len(result.get('messages', []))}")
            return True
        else:
            print(f"FAILED: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.ReadTimeout:
        print("TIMEOUT: Request took longer than 30 seconds")
        return False
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    # Start test
    result = test_coia_simple()
    
    print(f"\nResult: {'SUCCESS' if result else 'FAILED'}")
    
    # Check recent logs
    print("\nChecking recent logs...")
    try:
        logs_result = subprocess.run(
            ["docker", "logs", "instabids-instabids-backend-1", "--tail", "20"],
            capture_output=True,
            text=True,
            timeout=10
        )
        print("Recent backend logs:")
        print(logs_result.stdout[-1000:])  # Last 1000 chars
    except Exception as e:
        print(f"Could not get logs: {e}")