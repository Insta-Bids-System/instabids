"""
Simple test to trigger bid card search
"""

import requests
import json
import uuid
from config.service_urls import get_backend_url

BACKEND_URL = get_backend_url()

contractor_lead_id = f"landing-{str(uuid.uuid4())[:8]}"

# Setup contractor
setup = {
    "message": "Hi, I'm a contractor in Miami specializing in holiday lighting",
    "session_id": contractor_lead_id,
    "contractor_lead_id": contractor_lead_id
}

print("Setting up contractor...")
r1 = requests.post(f"{BACKEND_URL}/api/coia/landing", json=setup)
print(f"Setup mode: {r1.json().get('current_mode')}")

# Try exact trigger phrase
search = {
    "message": "find projects",  # Exact trigger phrase from mode detector
    "session_id": contractor_lead_id,
    "contractor_lead_id": contractor_lead_id
}

print("\nSearching with 'find projects'...")
r2 = requests.post(f"{BACKEND_URL}/api/coia/landing", json=search)
result = r2.json()

print(f"Mode: {result.get('current_mode')}")
print(f"bidCards present: {'bidCards' in result}")

if 'bidCards' in result:
    cards = result['bidCards']
    if cards:
        print(f"Found {len(cards)} bid cards!")
    else:
        print("bidCards field exists but is None/empty")