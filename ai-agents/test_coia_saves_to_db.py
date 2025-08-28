#!/usr/bin/env python3
"""
QUICK TEST: Does COIA actually save contractors to database?
"""
import requests
import json
import time
import sys
from datetime import datetime
from config.service_urls import get_backend_url

# Fix Windows Unicode
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

def test_coia_saves():
    print("🚀 TESTING: Does COIA save contractors to database?")
    print(f"⏰ Time: {datetime.now().isoformat()}")
    
    # Step 1: Send message to COIA
    url = f"{get_backend_url()}/ai/coia/chat/stream"
    test_company = f"TestCompany_{int(time.time())}"
    
    payload = {
        "message": f"Hi, I own {test_company}, we do kitchen remodeling in Miami Florida. We've been in business for 10 years.",
        "session_id": f"test_session_{int(time.time())}",
        "interface": "chat"
    }
    
    print(f"\n1️⃣ SENDING TO COIA:")
    print(f"   Company: {test_company}")
    
    # Send request
    response = requests.post(url, json=payload, stream=True, timeout=30)
    
    if response.status_code != 200:
        print(f"   ❌ HTTP Error: {response.status_code}")
        return False
    
    # Read streaming response
    profile_found = False
    account_created = False
    
    for line in response.iter_lines():
        if line:
            line_text = line.decode('utf-8')
            if line_text.startswith('data: '):
                try:
                    data = json.loads(line_text[6:])
                    if data.get('type') == 'tool_call':
                        print(f"   🔧 {data.get('content', '')}")
                        if 'Creating contractor account' in data.get('content', ''):
                            account_created = True
                    elif data.get('type') == 'metadata':
                        if data.get('metadata', {}).get('profile'):
                            profile_found = True
                except:
                    pass
    
    print(f"\n2️⃣ COIA RESPONSE:")
    print(f"   Profile built: {'✅' if profile_found else '❌'}")
    print(f"   Account creation attempted: {'✅' if account_created else '❌'}")
    
    # Step 2: Check database directly
    print(f"\n3️⃣ CHECKING DATABASE:")
    
    # Check contractor_leads table
    check_url = f"{get_backend_url()}/api/supabase/query"
    query = f"SELECT * FROM contractor_leads WHERE company_name LIKE '%{test_company}%'"
    
    db_response = requests.post(check_url, json={"query": query})
    
    if db_response.status_code == 200:
        results = db_response.json()
        if results and len(results) > 0:
            print(f"   ✅ FOUND IN DATABASE: contractor_leads")
            print(f"   ID: {results[0].get('id')}")
            print(f"   Company: {results[0].get('company_name')}")
            return True
        else:
            print(f"   ❌ NOT FOUND in contractor_leads")
    else:
        print(f"   ⚠️ Can't check database directly, trying alternative...")
        
        # Try using Supabase MCP if available
        try:
            from database_simple import db
            result = db.client.table('contractor_leads').select('*').ilike('company_name', f'%{test_company}%').execute()
            if result.data:
                print(f"   ✅ FOUND IN DATABASE: contractor_leads")
                print(f"   ID: {result.data[0].get('id')}")
                print(f"   Company: {result.data[0].get('company_name')}")
                return True
            else:
                print(f"   ❌ NOT FOUND in contractor_leads")
        except Exception as e:
            print(f"   ❌ Database check failed: {e}")
    
    return False

if __name__ == "__main__":
    success = test_coia_saves()
    
    print(f"\n{'='*50}")
    if success:
        print("✅ SUCCESS: COIA is saving contractors to database!")
    else:
        print("❌ FAILED: COIA is NOT saving to database")
        print("Need to check the database save logic in tools.py")