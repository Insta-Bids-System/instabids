"""
Simple test to check if React messaging components use API
"""

import uuid

import requests


# First test the API directly
print("1. Testing API directly...")

message_data = {
    "bid_card_id": str(uuid.uuid4()),
    "content": "Hi, my phone is 555-1234 and email is test@email.com",
    "sender_type": "homeowner",
    "sender_id": str(uuid.uuid4())
}

response = requests.post(
    "http://localhost:8008/api/messages/send",
    json=message_data,
    params={"user_type": "homeowner", "user_id": message_data["sender_id"]}
)

print(f"API Status: {response.status_code}")
result = response.json()
print(f"Success: {result.get('success', False)}")

if result.get("success"):
    print(f"Filtered content: {result.get('filtered_content', 'N/A')}")
    print(f"Was filtered: {result.get('content_filtered', False)}")
else:
    print(f"Error: {result.get('error', 'Unknown')}")

print("\n2. Frontend is running on http://localhost:5173")
print("   To test React components:")
print("   - Open http://localhost:5173 in browser")
print("   - Navigate to messaging section")
print("   - Open browser DevTools (F12)")
print("   - Go to Network tab")
print("   - Send a message with phone/email")
print("   - Check if /api/messages endpoint is called")
print("   - Or if it goes directly to Supabase")
