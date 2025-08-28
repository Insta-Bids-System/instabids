#!/usr/bin/env python3
"""
Quick test to verify all admin dashboard tabs are working
"""
import requests
from config.service_urls import get_backend_url

BASE_URL = get_backend_url()

def test_endpoints():
    endpoints = [
        ("Dashboard", f"{BASE_URL}/api/admin/dashboard"),
        ("Bid Cards Enhanced", f"{BASE_URL}/api/admin/bid-cards-enhanced"),
        ("Campaigns", f"{BASE_URL}/api/campaign-management/campaigns"),
        ("Campaign Stats", f"{BASE_URL}/api/campaign-management/dashboard-stats"),
        ("Agent Status", f"{BASE_URL}/api/agents/status"),
        ("Contractors", f"{BASE_URL}/api/contractor-management/contractors"),
    ]
    
    print("ADMIN DASHBOARD TAB ENDPOINTS TEST")
    print("=" * 50)
    
    all_working = True
    for name, url in endpoints:
        try:
            response = requests.get(url, timeout=5)
            status = "✅ OK" if response.status_code == 200 else f"❌ {response.status_code}"
            print(f"{name:<20}: {status}")
            if response.status_code != 200:
                all_working = False
        except Exception as e:
            print(f"{name:<20}: ❌ ERROR - {e}")
            all_working = False
    
    print("=" * 50)
    print("RESULT:", "✅ ALL TABS SHOULD WORK!" if all_working else "❌ SOME TABS MAY FAIL")
    return all_working

if __name__ == "__main__":
    test_endpoints()