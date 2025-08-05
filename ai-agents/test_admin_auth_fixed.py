#!/usr/bin/env python3
"""
Test Fixed Admin Authentication
Tests the corrected authentication flow
"""

import json
import sys

import requests


def test_admin_authentication():
    """Test fixed admin authentication"""
    print("Testing fixed admin authentication...")
    try:
        login_data = {
            "email": "admin@instabids.com",
            "password": "admin123",
            "remember_me": False
        }

        response = requests.post("http://localhost:8008/api/admin/login", json=login_data, timeout=10)

        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")

        if response.status_code == 200:
            data = response.json()
            print(f"Response data: {json.dumps(data, indent=2)}")

            if data.get("success"):
                session = data.get("session", {})
                admin_user = data.get("admin_user", {})

                print("[PASS] Admin authentication successful!")
                print(f"[INFO] Session ID: {session.get('session_id', 'N/A')[:20]}...")
                print(f"[INFO] Admin email: {admin_user.get('email', 'N/A')}")
                print(f"[INFO] Permissions: {len(admin_user.get('permissions', []))} permissions")

                return True
            else:
                print(f"[FAIL] Login failed: {data.get('error')}")
                return False
        else:
            print(f"[FAIL] HTTP error: {response.status_code}")
            if response.text:
                print(f"Response text: {response.text}")
            return False

    except Exception as e:
        print(f"[ERROR] Authentication test failed: {e}")
        return False

def test_backend_health():
    """Test backend server health"""
    print("Testing backend server health...")
    try:
        response = requests.get("http://localhost:8008/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"[PASS] Backend server online: {data.get('status')}")
            return True
        else:
            print(f"[FAIL] Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] Backend test failed: {e}")
        return False

def main():
    """Run authentication tests"""
    print("=== FIXED ADMIN AUTHENTICATION TEST ===")

    results = {
        "backend_health": test_backend_health(),
        "admin_auth": test_admin_authentication()
    }

    # Summary
    print("\n=== TEST RESULTS ===")
    passed = sum(1 for result in results.values() if result)
    total = len(results)

    print(f"Overall: {passed}/{total} tests passed")

    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")

    if passed == total:
        print("\n*** AUTHENTICATION FIXED! ***")
        print("Admin system is now operational!")
        return True
    else:
        print(f"\n*** {total - passed} TESTS FAILED ***")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Test execution failed: {e}")
        sys.exit(1)
