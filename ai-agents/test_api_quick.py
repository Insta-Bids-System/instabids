import requests

# Test the API endpoint directly
url = "http://localhost:8008/api/intelligent-messages/test-security"
params = {"test_content": "Please call me at 555-1234"}

response = requests.post(url, params=params)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Test with legitimate message
params2 = {"test_content": "I can do kitchen remodel for $15000"}
response2 = requests.post(url, params=params2)
print(f"\nLegitimate message test:")
print(f"Status: {response2.status_code}")
print(f"Response: {response2.json()['analysis_result']['agent_decision']}")