import subprocess
import time
import os

# Change to the correct directory
os.chdir(r"C:\Users\Not John Or Justin\Documents\instabids\ai-agents")

# Start the server
print("Starting server...")
process = subprocess.Popen(["python", "main.py"])

# Give it time to start
time.sleep(5)

print(f"Server started with PID: {process.pid}")
print("Server should be running on http://localhost:8008")