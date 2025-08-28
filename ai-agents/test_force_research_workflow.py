"""
Test that FORCES the research workflow to execute
We'll directly call the research endpoint if it exists
"""

import requests
import json
import time
from config.service_urls import get_backend_url

def test_force_research():
    """Force the COIA system to research JM Holiday Lighting"""
    
    print("FORCING COIA RESEARCH WORKFLOW")
    print("=" * 60)
    
    # Try different approaches to trigger research
    
    # Approach 1: Direct research trigger
    print("\nAPPROACH 1: Explicit research request")
    response1 = requests.post(f"{get_backend_url()}/api/coia/landing", json={
        "message": "Please research JM Holiday Lighting company in Denver Colorado. Use Google Places API to find their phone, address, website, ratings and reviews.",
        "contractor_lead_id": "jm-force-research-1",
        "session_id": "research-1"
    }, timeout=60)
    
    if response1.status_code == 200:
        result = response1.json()
        ai_response = get_ai_response(result)
        print(f"Response: {ai_response[:300]}...")
        
        # Check for research indicators
        research_indicators = ['phone', 'address', 'website', 'rating', 'google', 'found']
        research_triggered = any(ind in ai_response.lower() for ind in research_indicators)
        print(f"Research triggered: {research_triggered}")
    
    time.sleep(2)
    
    # Approach 2: Company introduction that should trigger research
    print("\nAPPROACH 2: Company introduction")
    response2 = requests.post(f"{get_backend_url()}/api/coia/landing", json={
        "message": "I own JM Holiday Lighting. We're a holiday lighting installation company in Denver. Can you look up our business information?",
        "contractor_lead_id": "jm-force-research-2", 
        "session_id": "research-2"
    }, timeout=60)
    
    if response2.status_code == 200:
        result = response2.json()
        ai_response = get_ai_response(result)
        print(f"Response: {ai_response[:300]}...")
        
        research_triggered = any(ind in ai_response.lower() for ind in research_indicators)
        print(f"Research triggered: {research_triggered}")
    
    # Approach 3: Check if there's a direct research endpoint
    print("\nAPPROACH 3: Checking for research endpoint")
    try:
        response3 = requests.post(f"{get_backend_url()}/api/coia/research", json={
            "company_name": "JM Holiday Lighting",
            "location": "Denver, Colorado"
        }, timeout=30)
        
        if response3.status_code == 200:
            print("Research endpoint exists!")
            print(json.dumps(response3.json(), indent=2)[:500])
        else:
            print(f"Research endpoint returned: {response3.status_code}")
    except:
        print("No direct research endpoint found")
    
    # Check database for any updates
    print("\nChecking database for research results...")
    check_database_for_research()

def get_ai_response(result):
    """Extract AI response from result"""
    if result.get('messages'):
        for msg in reversed(result['messages']):
            if msg.get('type') == 'ai':
                return msg.get('content', '')
    return result.get('response', 'No response')

def check_database_for_research():
    """Check if any research data was saved"""
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from database_simple import db
    
    # Check contractor_leads for enriched data
    leads = db.client.table("contractor_leads").select("*").ilike("company_name", "%JM Holiday%").execute()
    
    if leads.data:
        for lead in leads.data:
            print(f"\nFound in contractor_leads:")
            print(f"  Company: {lead['company_name']}")
            print(f"  Phone: {lead.get('phone', 'Not found')}")
            print(f"  Website: {lead.get('website', 'Not found')}")
            print(f"  Address: {lead.get('address', 'Not found')}")
            print(f"  Enrichment Data: {lead.get('enrichment_data', 'None')}")
    else:
        print("No JM Holiday Lighting found in contractor_leads")

if __name__ == "__main__":
    test_force_research()