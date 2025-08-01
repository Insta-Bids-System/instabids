import subprocess
import time
import requests
import threading

# Start server and capture output
print("Starting server with logging...")
process = subprocess.Popen(
    ["python", "main.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

# Function to read server output
def read_output():
    while True:
        line = process.stdout.readline()
        if line:
            print(f"[SERVER] {line.strip()}")
        if process.poll() is not None:
            break

# Start output reader thread
output_thread = threading.Thread(target=read_output)
output_thread.daemon = True
output_thread.start()

# Wait for server to start
print("Waiting for server to start...")
time.sleep(5)

# Test Iris
print("\n" + "="*50)
print("Testing Iris image generation...")
print("="*50)

url = "http://localhost:8008/api/iris/chat"
payload = {
    "message": "Generate a kitchen vision",
    "homeowner_id": "550e8400-e29b-41d4-a716-446655440001",
    "board_id": "26cf972b-83e4-484c-98b6-a5d1a4affee3"
}

try:
    response = requests.post(url, json=payload, timeout=40)
    print(f"\n[TEST] Status Code: {response.status_code}")
    
    if response.ok:
        result = response.json()
        print(f"[TEST] Image generated: {result.get('image_generated', False)}")
        print(f"[TEST] Image URL: {result.get('image_url', 'None')}")
        
except Exception as e:
    print(f"[TEST] Error: {e}")

# Keep running to see any additional logs
print("\n[TEST] Waiting for any additional server output...")
time.sleep(3)

# Kill the server
process.terminate()
print("\n[TEST] Server terminated")