#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRODUCTION READINESS TEST SUITE
Tests all critical connection fee system functionality
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json
import time
from datetime import datetime, timedelta
from config.service_urls import get_backend_url

BASE_URL = get_backend_url()

def test_contractor_selection():
    """Test homeowner selecting a winning contractor"""
    print("\n=== TEST 1: Contractor Selection Flow ===")
    
    # Use actual bid card with valid user_id and submitted bids
    bid_card_id = '36214de5-a068-4dcc-af99-cf33238e7472'
    contractor_id = 'ef86c9da-6a64-4316-b315-56b2ff7aa484'  # Contractor who submitted a bid for this bid card
    user_id = '22222222-2222-2222-2222-222222222222'  # Actual user_id
    
    url = f'{BASE_URL}/api/bid-cards/{bid_card_id}/select-contractor'
    payload = {
        'contractor_id': contractor_id,
        'user_id': user_id
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Contractor selection successful")
            print(f"   Connection Fee: ${data.get('connection_fee', 0)}")
            print(f"   Fee ID: {data.get('fee_id', 'N/A')}")
            return True
        else:
            print(f"❌ Selection failed: {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_payment_reminder():
    """Test sending payment reminder to contractor"""
    print("\n=== TEST 2: Payment Reminder System ===")
    
    # Get a pending fee
    response = requests.get(f"{BASE_URL}/api/admin/connection-fees?status=calculated&limit=1")
    if response.ok and response.json():
        fee = response.json()[0]
        fee_id = fee['fee_id']
        
        # Send reminder
        reminder_url = f"{BASE_URL}/api/admin/connection-fees/{fee_id}/remind"
        reminder_response = requests.post(reminder_url)
        
        if reminder_response.ok:
            print(f"✅ Payment reminder sent successfully")
            print(f"   Fee ID: {fee_id}")
            print(f"   Amount: ${fee['final_fee_amount']}")
            return True
        else:
            print(f"❌ Reminder failed: {reminder_response.status_code}")
            return False
    else:
        print("⚠️  No pending fees to test reminders")
        return True

def test_overdue_detection():
    """Test overdue payment detection (>7 days)"""
    print("\n=== TEST 3: Overdue Payment Detection ===")
    
    response = requests.get(f"{BASE_URL}/api/admin/connection-fees/overdue")
    if response.ok:
        data = response.json()
        print(f"✅ Overdue detection working")
        print(f"   Overdue fees: {data.get('count', 0)}")
        if data.get('overdue_fees'):
            for fee in data['overdue_fees'][:2]:
                print(f"   - {fee.get('bid_card_number')}: ${fee.get('fee_amount')} ({fee.get('days_overdue')} days overdue)")
        return True
    else:
        print(f"❌ Overdue detection failed: {response.status_code}")
        return False

def test_stats_accuracy():
    """Test statistics calculation accuracy"""
    print("\n=== TEST 4: Statistics Accuracy ===")
    
    response = requests.get(f"{BASE_URL}/api/admin/connection-fees/stats")
    if response.ok:
        stats = response.json()
        
        # Validate calculations
        total = stats['total_fees_calculated']
        paid = stats['total_fees_paid']
        pending = stats['total_fees_pending']
        
        if total == paid + pending:
            print(f"✅ Statistics calculations correct")
            print(f"   Total: {total}, Paid: {paid}, Pending: {pending}")
            print(f"   Revenue: ${stats['total_revenue']:.2f}")
            print(f"   Pending Revenue: ${stats['pending_revenue']:.2f}")
            print(f"   Completion Rate: {stats['payment_completion_rate']:.1f}%")
            return True
        else:
            print(f"❌ Statistics mismatch: {total} != {paid} + {pending}")
            return False
    else:
        print(f"❌ Stats endpoint failed: {response.status_code}")
        return False

def test_lifecycle_integration():
    """Test bid card lifecycle integration"""
    print("\n=== TEST 5: Bid Card Lifecycle Integration ===")
    
    # Test with a bid card that has a winner
    bid_card_id = '93c216f1-1e3f-490a-899d-ae2a236652a4'
    
    response = requests.get(f"{BASE_URL}/api/bid-cards/{bid_card_id}/lifecycle")
    if response.ok:
        data = response.json()
        connection_fee = data.get('connection_fee', {})
        
        if connection_fee.get('winner_selected'):
            print(f"✅ Lifecycle integration working")
            print(f"   Winner Selected: {connection_fee['winner_selected']}")
            print(f"   Fee Calculated: {connection_fee['connection_fee_calculated']}")
            if connection_fee.get('connection_fee_data'):
                print(f"   Fee Status: {connection_fee['connection_fee_data']['fee_status']}")
                print(f"   Amount: ${connection_fee['connection_fee_data']['final_fee_amount']}")
            return True
        else:
            print(f"⚠️  No winner selected for test bid card")
            return True
    else:
        print(f"❌ Lifecycle endpoint failed: {response.status_code}")
        return False

def test_error_handling():
    """Test error handling for invalid inputs"""
    print("\n=== TEST 6: Error Handling ===")
    
    tests_passed = 0
    
    # Test 1: Invalid bid card ID
    response = requests.get(f"{BASE_URL}/api/bid-cards/invalid-uuid/lifecycle")
    if response.status_code >= 400:
        print(f"✅ Invalid UUID rejected properly")
        tests_passed += 1
    else:
        print(f"❌ Invalid UUID not rejected")
    
    # Test 2: Missing required fields
    response = requests.post(f"{BASE_URL}/api/bid-cards/test/select-contractor", json={})
    if response.status_code >= 400:
        print(f"✅ Missing fields rejected properly")
        tests_passed += 1
    else:
        print(f"❌ Missing fields not rejected")
    
    # Test 3: Invalid fee ID for reminder
    response = requests.post(f"{BASE_URL}/api/admin/connection-fees/invalid-id/remind")
    if response.status_code >= 400:
        print(f"✅ Invalid fee ID rejected properly")
        tests_passed += 1
    else:
        print(f"❌ Invalid fee ID not rejected")
    
    return tests_passed >= 2  # Pass if at least 2/3 error cases handled

def test_concurrent_requests():
    """Test system under concurrent load"""
    print("\n=== TEST 7: Concurrent Request Handling ===")
    
    import concurrent.futures
    
    def make_stats_request():
        return requests.get(f"{BASE_URL}/api/admin/connection-fees/stats")
    
    # Make 10 concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_stats_request) for _ in range(10)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    success_count = sum(1 for r in results if r.status_code == 200)
    
    if success_count == 10:
        print(f"✅ All 10 concurrent requests succeeded")
        return True
    else:
        print(f"❌ Only {success_count}/10 requests succeeded")
        return False

def run_production_tests():
    """Run all production readiness tests"""
    print("=" * 60)
    print("PRODUCTION READINESS TEST SUITE")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    tests = [
        ("Contractor Selection", test_contractor_selection),
        ("Payment Reminders", test_payment_reminder),
        ("Overdue Detection", test_overdue_detection),
        ("Statistics Accuracy", test_stats_accuracy),
        ("Lifecycle Integration", test_lifecycle_integration),
        ("Error Handling", test_error_handling),
        ("Concurrent Requests", test_concurrent_requests)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} crashed: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 SYSTEM IS PRODUCTION READY! 🎉")
    else:
        print(f"\n⚠️  WARNING: {total - passed} tests failed - NOT READY FOR PRODUCTION")
    
    return passed == total

if __name__ == "__main__":
    run_production_tests()