"""
Test messaging API with real bid card
"""

import uuid

import requests


# Use real bid card ID from database
bid_card_id = "2cb6e43a-2c92-4e30-93f2-e44629f8975f"

print("Testing messaging API with real bid card...")
print(f"Bid Card ID: {bid_card_id}")

message_data = {
    "bid_card_id": bid_card_id,
    "content": "Hi, my phone is 555-1234 and email is test@email.com",
    "sender_type": "homeowner",
    "sender_id": str(uuid.uuid4())
}

response = requests.post(
    "http://localhost:8008/api/messages/send",
    json=message_data,
    params={"user_type": "homeowner", "user_id": message_data["sender_id"]}
)

print(f"\nAPI Response Status: {response.status_code}")
result = response.json()

if result.get("success"):
    print("SUCCESS! Message sent")
    print(f"- Filtered content: {result.get('filtered_content', 'N/A')}")
    print(f"- Was filtered: {result.get('content_filtered', False)}")
    print(f"- Filter reasons: {result.get('filter_reasons', [])}")
    print(f"- Message ID: {result.get('message_id', 'N/A')}")
else:
    print(f"FAILED: {result.get('error', 'Unknown error')}")
