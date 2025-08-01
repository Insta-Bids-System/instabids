import subprocess
import sys

# Start the server with output visible
process = subprocess.Popen([sys.executable, "main.py"], 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.STDOUT,
                         text=True,
                         bufsize=1)

# Print first 20 lines of output
for i in range(20):
    line = process.stdout.readline()
    if line:
        print(line.strip())
        if "Application startup complete" in line:
            break

print("\nServer started. Running test...")

# Now run the test
import time
time.sleep(2)  # Give server time to fully start

import requests
import json

url = "http://localhost:8008/api/iris/chat"
payload = {
    "message": "Generate a kitchen vision",
    "homeowner_id": "550e8400-e29b-41d4-a716-446655440001",
    "board_id": "26cf972b-83e4-484c-98b6-a5d1a4affee3"
}

try:
    response = requests.post(url, json=payload, timeout=35)
    print(f"\nTest Status Code: {response.status_code}")
    if response.ok:
        result = response.json()
        if "image_generated" in result:
            print(f"Image was generated: {result['image_generated']}")
            print(f"Image URL: {result.get('image_url', 'Not found')}")
        else:
            print("No image generation data in response")
except Exception as e:
    print(f"Test Error: {e}")

# Keep server running to see any error output
print("\nWaiting for any error output...")
for i in range(10):
    line = process.stdout.readline()
    if line:
        print(line.strip())