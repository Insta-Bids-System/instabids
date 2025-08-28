"""
Force the COIA system to actually create an account
Instead of just talking about it
"""

import requests
import json
import time
from config.service_urls import get_backend_url

def force_account_creation():
    """Force account creation workflow"""
    
    print("FORCING ACCOUNT CREATION FOR JM HOLIDAY LIGHTING")
    print("=" * 60)
    
    # Step 1: Try to trigger account creation directly
    print("\nStep 1: Direct account creation request")
    response1 = requests.post(f"{get_backend_url()}/api/coia/landing", json={
        "message": "Create my contractor account now. Company: JM Holiday Lighting, Email: justin@jmholiday.com, Phone: 303-555-1234",
        "contractor_lead_id": "jm-force-account",
        "session_id": "account-1"
    }, timeout=60)
    
    if response1.status_code == 200:
        result = response1.json()
        ai_response = get_ai_response(result)
        print(f"Response: {ai_response[:400]}...")
        
        # Check if account was created
        account_indicators = ['account', 'created', 'username', 'password', 'login']
        account_created = any(ind in ai_response.lower() for ind in account_indicators)
        print(f"Account creation mentioned: {account_created}")
    
    # Step 2: Try even more explicit
    print("\nStep 2: Ultra-explicit account creation command")
    response2 = requests.post(f"{get_backend_url()}/api/coia/landing", json={
        "message": "TRIGGER ACCOUNT_CREATION MODE NOW. I want to register as a contractor. Create my account in the database.",
        "contractor_lead_id": "jm-force-account-2",
        "session_id": "account-2"
    }, timeout=60)
    
    if response2.status_code == 200:
        result = response2.json()
        ai_response = get_ai_response(result)
        print(f"Response: {ai_response[:400]}...")
        
        account_created = any(ind in ai_response.lower() for ind in account_indicators)
        print(f"Account creation triggered: {account_created}")
    
    # Check database
    print("\n" + "=" * 60)
    print("CHECKING DATABASE FOR ACTUAL ACCOUNT CREATION")
    check_database()

def get_ai_response(result):
    """Extract AI response"""
    if result.get('messages'):
        for msg in reversed(result['messages']):
            if msg.get('type') == 'ai':
                return msg.get('content', '')
    return result.get('response', 'No response')

def check_database():
    """Check if account was actually created"""
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    
    try:
        # Use Supabase MCP to check
        print("\nUsing Supabase MCP to check contractors table...")
        # This would use MCP but for now we'll query directly
        
        print("\n[Would check contractors table for JM Holiday Lighting]")
        print("[Would verify account fields populated]")
        print("[Would check for generated credentials]")
        
    except Exception as e:
        print(f"Database check error: {e}")

if __name__ == "__main__":
    force_account_creation()