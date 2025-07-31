"""
Kill existing server and start new one
"""
import os
import subprocess
import time
import psutil

def kill_process_on_port(port):
    """Kill process using specific port"""
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            for conn in proc.connections('inet'):
                if conn.laddr.port == port:
                    print(f"Killing process {proc.info['name']} (PID: {proc.info['pid']}) on port {port}")
                    proc.kill()
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False

print("Stopping existing server on port 8000...")
if kill_process_on_port(8000):
    print("Server stopped")
    time.sleep(2)
else:
    print("No server running on port 8000")

print("\nStarting new server with JAA support...")
os.chdir(r"C:\Users\Not John Or Justin\Documents\instabids\ai-agents")

# Start server in new window
subprocess.Popen(['cmd', '/c', 'start', 'cmd', '/k', 'python', 'main.py'])

print("Server starting in new window...")
print("Wait a few seconds, then run: python test_end_to_end_api.py")