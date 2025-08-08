#!/usr/bin/env python3
"""
Debug Google Maps API to see what's happening
"""
import os

import requests
from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv("GOOGLE_MAPS_API_KEY")
print(f"API Key: {api_key[:20]}...{api_key[-5:]}")

# Test 1: Simple search
print("\nTEST 1: Simple contractor search")
url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
params = {
    "query": "contractors Florida",
    "key": api_key
}

response = requests.get(url, params=params)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Results: {len(data.get('results', []))}")
    print(f"Status: {data.get('status', 'N/A')}")
    if data.get("results"):
        first = data["results"][0]
        print(f"First result: {first.get('name', 'Unknown')} - {first.get('formatted_address', 'No address')}")
else:
    print(f"Error: {response.text}")

# Test 2: Check quota/billing
print("\nTEST 2: API Status Check")
test_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
test_params = {
    "input": "test",
    "inputtype": "textquery",
    "key": api_key,
    "fields": "name"
}

test_response = requests.get(test_url, params=test_params)
print(f"Test Status: {test_response.status_code}")
if test_response.status_code == 200:
    test_data = test_response.json()
    print(f"Test Response Status: {test_data.get('status', 'N/A')}")
    print(f"Test Response: {test_data}")
else:
    print(f"Test Error: {test_response.text}")
