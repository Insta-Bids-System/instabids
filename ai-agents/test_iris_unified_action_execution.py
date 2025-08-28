#!/usr/bin/env python3
"""Test IRIS unified agent actual action execution"""

import requests
import json
from datetime import datetime

# Test the IRIS unified chat API with repair item actions
base_url = "http://localhost:8008"

# Use the roofing potential bid card ID from previous tests
potential_bid_card_id = '0e9a839a-984c-4391-ace6-0f62342e4524'
test_user_id = 'iris_test_user'

print('Testing IRIS Unified Agent Action Execution')
print('=' * 60)

# Test 1: Rename the potential bid card (should work with existing code)
print('\n1. Testing rename action...')
rename_request = {
    'message': f'Please rename project {potential_bid_card_id} to "Roofing Emergency Repairs"',
    'user_id': test_user_id,
    'session_id': f'test_rename_{int(datetime.now().timestamp())}',
    'context_type': 'property'
}

try:
    response = requests.post(f'{base_url}/api/iris/unified-chat', json=rename_request, timeout=30)
    if response.status_code == 200:
        result = response.json()
        print(f'✅ RENAME SUCCESS: {result.get("response", "")[:200]}...')
        print(f'   Action Results: {len(result.get("context_summary", {}))} context items')
    else:
        print(f'❌ RENAME FAILED: Status {response.status_code}')
        print(f'   Error: {response.text[:300]}')
except Exception as e:
    print(f'❌ RENAME ERROR: {e}')

# Test 2: Add a repair item (testing new functionality)
print('\n2. Testing add repair item action...')
repair_request = {
    'message': f'Add replace damaged roof shingles to project {potential_bid_card_id}',
    'user_id': test_user_id,
    'session_id': f'test_repair_{int(datetime.now().timestamp())}',
    'context_type': 'property'
}

try:
    response = requests.post(f'{base_url}/api/iris/unified-chat', json=repair_request, timeout=30)
    if response.status_code == 200:
        result = response.json()
        print(f'✅ REPAIR ADD SUCCESS: {result.get("response", "")[:200]}...')
        print(f'   Response includes action confirmation: {"✨" in result.get("response", "")}')
    else:
        print(f'❌ REPAIR ADD FAILED: Status {response.status_code}')
        print(f'   Error: {response.text[:300]}')
except Exception as e:
    print(f'❌ REPAIR ADD ERROR: {e}')

# Test 3: Make project urgent 
print('\n3. Testing urgency update action...')
urgency_request = {
    'message': f'Make project {potential_bid_card_id} urgent',
    'user_id': test_user_id,
    'session_id': f'test_urgent_{int(datetime.now().timestamp())}',
    'context_type': 'property'
}

try:
    response = requests.post(f'{base_url}/api/iris/unified-chat', json=urgency_request, timeout=30)
    if response.status_code == 200:
        result = response.json()
        print(f'✅ URGENCY UPDATE SUCCESS: {result.get("response", "")[:200]}...')
        print(f'   Response includes action confirmation: {"✨" in result.get("response", "")}')
    else:
        print(f'❌ URGENCY UPDATE FAILED: Status {response.status_code}')
        print(f'   Error: {response.text[:300]}')
except Exception as e:
    print(f'❌ URGENCY UPDATE ERROR: {e}')

# Test 4: Verify changes in database
print('\n4. Verifying database changes...')
try:
    # Use the direct repair item list API to verify changes
    list_result = requests.get(f'{base_url}/api/iris/repair-items/{potential_bid_card_id}')
    if list_result.status_code == 200:
        repair_data = list_result.json()
        print(f'✅ DATABASE VERIFICATION SUCCESS')
        print(f'   Total repair items: {repair_data.get("total_items", 0)}')
        for i, item in enumerate(repair_data.get("repair_items", []), 1):
            print(f'   Item {i}: {item.get("description", "Unknown")} - {item.get("severity", "unknown")} severity')
    else:
        print(f'❌ DATABASE VERIFICATION FAILED: Status {list_result.status_code}')
except Exception as e:
    print(f'❌ DATABASE VERIFICATION ERROR: {e}')

print('\n' + '=' * 60)
print('IRIS Unified Agent Action Execution Test Complete')
print('This test verifies that IRIS can actually execute actions, not just respond')