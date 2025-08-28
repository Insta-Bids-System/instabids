#!/usr/bin/env python3
"""
Test the connection fees API directly
"""

import requests
import json
from config.service_urls import get_backend_url

def test_connection_fees_api():
    print("Testing connection fees API...")
    
    try:
        # Test the admin connection fees endpoint
        url = f"{get_backend_url()}/api/admin/connection-fees"
        response = requests.get(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Found {len(data)} connection fees:")
            for fee in data[:3]:  # Show first 3
                print(f"  - {fee.get('contractor_company', 'Unknown')}: ${fee.get('final_fee_amount', 0)} ({fee.get('fee_status', 'unknown')})")
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"Error: {e}")

    # Test the stats endpoint
    try:
        print("\nTesting stats endpoint...")
        url = f"{get_backend_url()}/api/admin/connection-fees/stats"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            stats = response.json()
            print("Stats:")
            print(f"  - Total fees calculated: {stats.get('total_fees_calculated', 0)}")
            print(f"  - Total fees paid: {stats.get('total_fees_paid', 0)}")
            print(f"  - Total revenue: ${stats.get('total_revenue', 0)}")
            print(f"  - Pending revenue: ${stats.get('pending_revenue', 0)}")
        else:
            print(f"Stats error: {response.text}")
            
    except Exception as e:
        print(f"Stats request failed: {e}")

if __name__ == "__main__":
    test_connection_fees_api()