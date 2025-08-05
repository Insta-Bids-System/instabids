import json

import requests


# Test what the API actually returns
message_data = {
    "bid_card_id": "test-bid-123",
    "content": "Hi, my phone is 555-1234 and email is test@email.com",
    "sender_type": "homeowner",
    "sender_id": "test-homeowner-123"
}

response = requests.post(
    "http://localhost:8008/api/messages/send",
    json=message_data,
    params={"user_type": "homeowner", "user_id": "test-homeowner-123"}
)

print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
