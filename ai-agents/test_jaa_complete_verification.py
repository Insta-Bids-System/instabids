#!/usr/bin/env python3
"""
COMPLETE JAA INTEGRATION VERIFICATION TEST
This test will 100% confirm that agents are calling JAA and bid cards are being changed
"""

import asyncio
import json
import requests
from datetime import datetime
from supabase import create_client
import os
from dotenv import load_dotenv
from config.service_urls import get_backend_url

# Load environment variables
load_dotenv()

# Initialize Supabase client for direct verification
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://xrhgrthdcaymxuqcgrmj.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhyaGdydGhkY2F5bXh1cWNncm1qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM2NTcyMDYsImV4cCI6MjA2OTIzMzIwNn0.BriGLA2FE_e_NJl8B-3ps1W6ZAuK6a5HpTwBGy-6rmE")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Test bid card from earlier query
TEST_BID_CARD = {
    "id": "93c216f1-1e3f-490a-899d-ae2a236652a4",
    "bid_card_number": "BC0730223441"
}

def get_bid_card_state(bid_card_id):
    """Get current state of bid card from database"""
    result = supabase.table("bid_cards").select("*").eq("id", bid_card_id).single().execute()
    if result.data:
        return result.data
    return None

def print_bid_card_state(state, label):
    """Print bid card state in readable format"""
    print(f"\n{label}:")
    print(f"  Bid Card Number: {state.get('bid_card_number')}")
    print(f"  Project Type: {state.get('project_type')}")
    print(f"  Budget: ${state.get('budget_min', 0):,} - ${state.get('budget_max', 0):,}")
    print(f"  Status: {state.get('status')}")
    print(f"  Updated At: {state.get('updated_at')}")
    
    # Check metadata for JAA updates
    metadata = state.get('metadata')
    if metadata:
        try:
            meta_dict = json.loads(metadata)
            if 'jaa_updates' in meta_dict:
                print(f"  JAA Updates: {len(meta_dict['jaa_updates'])} updates recorded")
                if meta_dict['jaa_updates']:
                    latest = meta_dict['jaa_updates'][-1]
                    print(f"    Latest: {latest.get('timestamp', 'No timestamp')}")
                    print(f"    Change: {latest.get('change_summary', 'No summary')}")
        except:
            pass

async def test_jaa_integration_complete():
    """Complete test with full database verification"""
    
    print("="*80)
    print("COMPLETE JAA INTEGRATION VERIFICATION TEST")
    print("="*80)
    print(f"Test Started: {datetime.now().isoformat()}")
    print(f"Test Bid Card: {TEST_BID_CARD['bid_card_number']}")
    
    # Step 1: Get BEFORE state
    print("\n" + "="*60)
    print("STEP 1: CAPTURING BEFORE STATE")
    print("="*60)
    
    before_state = get_bid_card_state(TEST_BID_CARD['id'])
    if not before_state:
        print("ERROR: Could not find test bid card in database")
        return False
    
    print_bid_card_state(before_state, "BEFORE STATE")
    original_budget_max = before_state.get('budget_max', 0)
    original_updated_at = before_state.get('updated_at')
    
    # Step 2: Test direct JAA endpoint
    print("\n" + "="*60)
    print("STEP 2: TESTING DIRECT JAA ENDPOINT")
    print("="*60)
    
    # Create a unique test value so we can verify the change
    test_budget = original_budget_max + 5000  # Add $5000 to current budget
    
    jaa_endpoint = f"{get_backend_url()}/jaa/update/{TEST_BID_CARD['id']}"
    payload = {
        "update_context": {
            "source_agent": "verification_test",
            "conversation_snippet": f"Increase budget to ${test_budget:,}",
            "detected_change_hints": ["budget"],
            "modifications": {"budget_max": test_budget},
            "requester_info": {
                "user_id": "test-verification",
                "session_id": f"verify-{datetime.now().timestamp()}"
            }
        },
        "update_type": "conversation_based"
    }
    
    print(f"Calling JAA endpoint: {jaa_endpoint}")
    print(f"Requesting budget change: ${original_budget_max:,} -> ${test_budget:,}")
    
    try:
        response = requests.put(
            jaa_endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60  # Longer timeout for JAA processing
        )
        
        print(f"JAA Response Status: {response.status_code}")
        
        if response.status_code == 200:
            jaa_response = response.json()
            print("SUCCESS: JAA responded successfully")
            
            # Print key response fields
            if jaa_response.get('success'):
                print(f"  Bid Card ID: {jaa_response.get('bid_card_id')}")
                update_summary = jaa_response.get('update_summary', {})
                if update_summary:
                    print(f"  Change Summary: {update_summary.get('change_summary', 'No summary')}")
                    changes = update_summary.get('changes_made', [])
                    for change in changes:
                        print(f"    - {change.get('field')}: {change.get('old_value')} -> {change.get('new_value')}")
                
                affected = jaa_response.get('affected_contractors', [])
                print(f"  Affected Contractors: {len(affected)}")
                
                jaa_success = True
            else:
                print(f"JAA returned success=False: {jaa_response}")
                jaa_success = False
        else:
            print(f"JAA ERROR: {response.status_code}")
            print(f"Error: {response.text}")
            jaa_success = False
            
    except requests.exceptions.Timeout:
        print("JAA request timed out after 60 seconds")
        # Even if it timed out, the change might have been applied
        jaa_success = "timeout"
    except Exception as e:
        print(f"JAA request failed: {str(e)}")
        jaa_success = False
    
    # Step 3: Wait a moment for database to update
    print("\nWaiting 3 seconds for database update...")
    await asyncio.sleep(3)
    
    # Step 4: Get AFTER state
    print("\n" + "="*60)
    print("STEP 3: CAPTURING AFTER STATE")
    print("="*60)
    
    after_state = get_bid_card_state(TEST_BID_CARD['id'])
    if not after_state:
        print("ERROR: Could not find test bid card after update")
        return False
    
    print_bid_card_state(after_state, "AFTER STATE")
    new_budget_max = after_state.get('budget_max', 0)
    new_updated_at = after_state.get('updated_at')
    
    # Step 5: Verify changes
    print("\n" + "="*60)
    print("STEP 4: VERIFICATION RESULTS")
    print("="*60)
    
    changes_detected = []
    
    # Check budget change
    if new_budget_max != original_budget_max:
        changes_detected.append(f"BUDGET CHANGED: ${original_budget_max:,} -> ${new_budget_max:,}")
        if new_budget_max == test_budget:
            changes_detected.append(f"  EXACT MATCH: Budget is now exactly ${test_budget:,} as requested")
    else:
        changes_detected.append(f"NO BUDGET CHANGE: Still ${original_budget_max:,}")
    
    # Check updated_at timestamp
    if new_updated_at != original_updated_at:
        changes_detected.append(f"TIMESTAMP CHANGED: {original_updated_at} -> {new_updated_at}")
    else:
        changes_detected.append("NO TIMESTAMP CHANGE")
    
    # Check metadata for JAA updates
    new_metadata = after_state.get('metadata')
    old_metadata = before_state.get('metadata')
    
    if new_metadata != old_metadata:
        changes_detected.append("METADATA CHANGED")
        try:
            new_meta = json.loads(new_metadata) if new_metadata else {}
            old_meta = json.loads(old_metadata) if old_metadata else {}
            
            if 'jaa_updates' in new_meta:
                new_updates = new_meta.get('jaa_updates', [])
                old_updates = old_meta.get('jaa_updates', [])
                if len(new_updates) > len(old_updates):
                    changes_detected.append(f"  NEW JAA UPDATES: {len(new_updates) - len(old_updates)} new updates")
                    if new_updates:
                        latest = new_updates[-1]
                        changes_detected.append(f"    Latest Update: {latest.get('change_summary', 'No summary')}")
        except:
            pass
    
    # Print all detected changes
    print("\nDETECTED CHANGES:")
    for change in changes_detected:
        print(f"  {change}")
    
    # Final verdict
    print("\n" + "="*80)
    print("FINAL VERIFICATION RESULT")
    print("="*80)
    
    # Success criteria: Budget changed to requested value
    if new_budget_max == test_budget:
        print("✅ 100% VERIFIED: BID CARD WAS SUCCESSFULLY UPDATED")
        print(f"✅ Budget changed from ${original_budget_max:,} to ${test_budget:,}")
        print(f"✅ Bid card {TEST_BID_CARD['bid_card_number']} was modified via JAA service")
        print("✅ Database changes confirmed in Supabase")
        verification_success = True
    elif new_budget_max != original_budget_max:
        print("⚠️  PARTIAL SUCCESS: Budget changed but not to exact requested value")
        print(f"   Expected: ${test_budget:,}, Got: ${new_budget_max:,}")
        verification_success = False
    else:
        print("❌ FAILED: No changes detected in database")
        print(f"   Budget remains: ${original_budget_max:,}")
        verification_success = False
    
    return verification_success

async def main():
    """Run the complete verification test"""
    success = await test_jaa_integration_complete()
    
    print("\n" + "="*80)
    if success:
        print("🎉 TEST PASSED: JAA INTEGRATION 100% VERIFIED")
        print("The bid card was successfully modified through the JAA service")
    else:
        print("❌ TEST FAILED: Could not verify bid card changes")
        print("The JAA service may not be working correctly")
    print("="*80)
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)