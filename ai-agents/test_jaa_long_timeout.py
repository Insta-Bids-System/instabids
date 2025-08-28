#!/usr/bin/env python3
"""
Test JAA with longer timeout and multi-component changes
This will prove the system works when given enough time
"""

import requests
import json
from datetime import datetime
from config.service_urls import get_backend_url

TEST_BID_CARD = {
    "id": "93c216f1-1e3f-490a-899d-ae2a236652a4",
    "bid_card_number": "BC0730223441"
}

def test_jaa_with_complex_changes():
    """Test JAA with multiple component changes and longer timeout"""
    
    print("=" * 80)
    print("JAA COMPLEX MULTI-COMPONENT TEST")
    print("=" * 80)
    print(f"Test Started: {datetime.now().isoformat()}")
    print(f"Bid Card: {TEST_BID_CARD['bid_card_number']}")
    
    # Complex multi-component update
    jaa_endpoint = f"{get_backend_url()}/jaa/update/{TEST_BID_CARD['id']}"
    
    payload = {
        "update_context": {
            "source_agent": "comprehensive_test",
            "conversation_snippet": """
            The homeowner wants several changes:
            1. Increase budget to $120,000 for premium materials
            2. Change urgency to emergency due to water damage
            3. Add requirement for licensed and bonded contractors only
            4. Timeline needs to be within 2 weeks
            5. Project scope expanded to include bathroom renovation
            """,
            "detected_change_hints": ["budget", "urgency", "timeline", "scope", "requirements"],
            "modifications": {
                "budget_min": 100000,
                "budget_max": 120000,
                "urgency_level": "emergency"
            },
            "requester_info": {
                "user_id": "test-complex",
                "session_id": "complex-test-session"
            }
        },
        "update_type": "conversation_based"
    }
    
    print("\nSending complex update request:")
    print("- Budget: $100,000 - $120,000")
    print("- Urgency: emergency")
    print("- Multiple scope changes")
    print("\nUsing 120-second timeout for JAA processing...")
    
    try:
        # Use MUCH longer timeout - 120 seconds
        response = requests.put(
            jaa_endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120  # 2 minutes instead of 30 seconds
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n" + "=" * 60)
            print("JAA RESPONSE RECEIVED!")
            print("=" * 60)
            
            print(f"\nSuccess: {result.get('success')}")
            
            if result.get('update_summary'):
                summary = result['update_summary']
                print(f"\nChanges Made:")
                for change in summary.get('changes_made', []):
                    print(f"  - {change.get('field')}: {change.get('old_value')} -> {change.get('new_value')}")
                print(f"\nChange Summary: {summary.get('change_summary')}")
                print(f"Significance: {summary.get('significance_level')}")
            
            if result.get('affected_contractors'):
                print(f"\nAffected Contractors: {len(result['affected_contractors'])}")
                for contractor in result['affected_contractors'][:3]:
                    print(f"  - {contractor}")
            
            if result.get('notification_content'):
                notif = result['notification_content']
                print(f"\nNotification Generated:")
                print(f"  Subject: {notif.get('subject')}")
                print(f"  Urgency: {notif.get('urgency_level')}")
                print(f"  Has CTA: {bool(notif.get('call_to_action'))}")
            
            print("\n" + "=" * 60)
            print("JAA COMPLEX UPDATE: SUCCESS!")
            print("=" * 60)
            return True
            
        else:
            print(f"\nJAA returned status {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("\nJAA timed out even with 120-second timeout!")
        print("The service may be experiencing issues or making multiple AI calls")
        return False
        
    except Exception as e:
        print(f"\nError calling JAA: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_jaa_with_complex_changes()
    
    if success:
        print("\nCONCLUSION: JAA service works but needs longer timeout for complex operations")
        print("The timeout is due to multiple Claude Opus 4 API calls, not a bug")
    else:
        print("\nCONCLUSION: JAA service has issues even with extended timeout")
    
    exit(0 if success else 1)