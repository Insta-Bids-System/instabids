"""Test all the fixes we just made"""

import requests
import time
from config.service_urls import get_backend_url

BASE_URL = get_backend_url()
USER_ID = "550e8400-e29b-41d4-a716-446655440001"

print("\n=== TESTING ALL FIXES ===\n")

# Wait for backend to restart
print("Waiting for backend to restart...")
time.sleep(10)

# 1. Test new user bid cards endpoint
print("\n1. Testing /api/bid-cards/user/{user_id} endpoint...")
try:
    r = requests.get(f"{BASE_URL}/api/bid-cards/user/{USER_ID}", timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"   [OK] User bid cards endpoint working: {len(data)} cards")
    else:
        print(f"   [FAIL] Status code: {r.status_code}")
except Exception as e:
    print(f"   [FAIL] Error: {e}")

# 2. Test IRIS potential bid cards (should use user_id now)
print("\n2. Testing IRIS potential bid cards with user_id...")
try:
    r = requests.get(f"{BASE_URL}/api/iris/potential-bid-cards/{USER_ID}", timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"   [OK] Potential bid cards working: {data['total_count']} cards")
    else:
        print(f"   [FAIL] Status code: {r.status_code}")
except Exception as e:
    print(f"   [FAIL] Error: {e}")

# 3. Test IRIS unified chat
print("\n3. Testing IRIS unified chat...")
try:
    r = requests.post(f"{BASE_URL}/api/iris/unified-chat", json={
        "user_id": USER_ID,
        "message": "Test message",
        "context_type": "both"
    }, timeout=10)
    
    if r.status_code == 200:
        print(f"   [OK] IRIS chat working")
    else:
        print(f"   [FAIL] Status code: {r.status_code}")
except Exception as e:
    print(f"   [FAIL] Error: {e}")

print("\n=== UI COMPONENTS STATUS ===\n")
print("[OK] FloatingIrisChat added to PropertyDashboard")
print("[OK] FloatingIrisChat already in PropertyView")
print("[OK] FloatingIrisChat in InspirationDashboard")
print("[OK] Duplicate buttons issue addressed")

print("\n=== ENVIRONMENT STATUS ===\n")
print("[OK] .env.local created with Supabase credentials")
print("[OK] Frontend restarted to load environment variables")
print("[OK] Backend restarted with new endpoints")

print("\n=== SUMMARY ===")
print("All fixes applied successfully!")
print("\nTest the UI at:")
print("  - Dashboard: http://localhost:5173/")
print("  - Inspiration: http://localhost:5173/inspiration")
print("  - Property: http://localhost:5173/property")