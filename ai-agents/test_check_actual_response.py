"""
Check the actual API response structure
"""

import requests
import json
import uuid
from config.service_urls import get_backend_url

BACKEND_URL = get_backend_url()

contractor_lead_id = f"landing-{str(uuid.uuid4())[:8]}"

# Setup
stage1 = {
    "message": "Hi, I'm from TurfGrass in Miami. We do landscaping.",
    "session_id": contractor_lead_id,
    "contractor_lead_id": contractor_lead_id
}
requests.post(f"{BACKEND_URL}/api/coia/landing", json=stage1)

# Request bid cards
stage2 = {
    "message": "Show me projects to bid on",
    "session_id": contractor_lead_id,
    "contractor_lead_id": contractor_lead_id
}

response = requests.post(f"{BACKEND_URL}/api/coia/landing", json=stage2)
result = response.json()

print("API RESPONSE KEYS:")
for key in result.keys():
    value = result[key]
    if key in ['bidCards', 'bid_cards']:
        print(f"  {key}: {type(value)} - Length: {len(value) if value else 0}")
    else:
        print(f"  {key}: {type(value)}")

# Check specifically for bid card fields
print("\nBID CARD FIELDS CHECK:")
print(f"  'bid_cards' exists: {'bid_cards' in result}")
print(f"  'bidCards' exists: {'bidCards' in result}")
print(f"  'bid_cards_attached' exists: {'bid_cards_attached' in result}")

if 'bidCards' in result and result['bidCards']:
    print(f"\n[SUCCESS] Found {len(result['bidCards'])} bid cards in 'bidCards' field")
    print("First card structure:")
    for k, v in result['bidCards'][0].items():
        print(f"    {k}: {v}")