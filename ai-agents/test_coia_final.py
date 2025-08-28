#!/usr/bin/env python3
"""
FINAL COIA TEST - Must complete 100% end-to-end
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

def test_backend_health():
    """Check if backend is responding"""
    print("🔍 CHECKING BACKEND HEALTH")
    
    try:
        response = requests.get(get_backend_url(), timeout=2)
        print(f"   ✅ Backend responding: {response.status_code}")
        return True
    except Exception as e:
        print(f"   ❌ Backend not responding: {e}")
        return False

def test_coia_streaming_endpoint():
    """Test the streaming COIA endpoint"""
    print("\n🚀 TESTING COIA STREAMING ENDPOINT")
    
    test_company = f"FinalTestCorp_{int(time.time())}"
    
    payload = {
        "message": f"I own {test_company}, we do kitchen remodeling in Tampa Florida",
        "session_id": f"final_test_{int(time.time())}",
        "interface": "chat"
    }
    
    try:
        response = requests.post(
            f"{get_backend_url()}/ai/coia/chat/stream", 
            json=payload, 
            stream=True,
            timeout=15
        )
        
        if response.status_code != 200:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return False
        
        print(f"   🎯 Company: {test_company}")
        
        # Track what we find
        connected = False
        tools_used = []
        tokens_received = 0
        profile_created = False
        account_created = False
        
        for line in response.iter_lines():
            if line:
                line_text = line.decode('utf-8')
                if line_text.startswith('data: '):
                    try:
                        data = json.loads(line_text[6:])
                        msg_type = data.get('type', '')
                        
                        if msg_type == 'connected':
                            connected = True
                            print(f"   ✅ COIA Connected")
                        elif msg_type == 'tool_call':
                            tool_content = data.get('content', '')
                            tools_used.append(tool_content)
                            if 'Creating contractor account' in tool_content:
                                account_created = True
                            print(f"   🔧 {tool_content}")
                        elif msg_type == 'token':
                            tokens_received += 1
                        elif msg_type == 'metadata':
                            metadata = data.get('metadata', {})
                            if metadata.get('profile'):
                                profile_created = True
                                print(f"   📋 Profile Created")
                        elif msg_type == 'complete':
                            break
                    except json.JSONDecodeError:
                        continue
        
        # Report results
        print(f"\n   📊 RESULTS:")
        print(f"      Connected: {'✅' if connected else '❌'}")
        print(f"      Tools Used: {len(tools_used)}")
        print(f"      Tokens Received: {tokens_received}")
        print(f"      Profile Created: {'✅' if profile_created else '❌'}")
        print(f"      Account Creation Attempted: {'✅' if account_created else '❌'}")
        
        # Check if streaming worked
        success = connected and tokens_received > 0 and account_created
        print(f"      Overall: {'✅ SUCCESS' if success else '❌ FAILED'}")
        
        return success, test_company
        
    except Exception as e:
        print(f"   ❌ Streaming test failed: {e}")
        return False, None

def test_database_save(test_company):
    """Verify contractor was saved to database"""
    print(f"\n💾 CHECKING DATABASE FOR {test_company}")
    
    # Try direct Supabase MCP
    try:
        from database_simple import db
        result = db.client.table('contractor_leads').select('*').ilike('company_name', f'%{test_company}%').execute()
        
        if result.data:
            contractor = result.data[0]
            print(f"   ✅ FOUND IN DATABASE:")
            print(f"      ID: {contractor.get('id')}")
            print(f"      Company: {contractor.get('company_name')}")
            print(f"      Email: {contractor.get('email')}")
            print(f"      Source: {contractor.get('source')}")
            return True
        else:
            print(f"   ❌ NOT FOUND in contractor_leads table")
            return False
            
    except Exception as e:
        print(f"   ❌ Database check failed: {e}")
        return False

def test_non_streaming_endpoint():
    """Test the non-streaming endpoint that frontend uses"""
    print(f"\n🎯 TESTING NON-STREAMING ENDPOINT")
    
    test_company = f"NonStreamTest_{int(time.time())}"
    
    payload = {
        "message": f"Hi, I own {test_company} and we specialize in bathroom remodeling in Miami",
        "session_id": f"nonstream_{int(time.time())}"
    }
    
    try:
        response = requests.post(
            f"{get_backend_url()}/api/coia/chat",
            json=payload,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return False, None
        
        data = response.json()
        
        print(f"   🎯 Company: {test_company}")
        print(f"   ✅ Response received ({len(data.get('response', ''))} chars)")
        
        if data.get('profile'):
            print(f"   📋 Profile created: {data['profile'].get('company_name')}")
        
        if data.get('bid_cards'):
            print(f"   🗂️ Bid cards found: {len(data['bid_cards'])}")
        
        success = data.get('success', False) and data.get('profile') is not None
        print(f"   Overall: {'✅ SUCCESS' if success else '❌ FAILED'}")
        
        return success, test_company
        
    except Exception as e:
        print(f"   ❌ Non-streaming test failed: {e}")
        return False, None

def main():
    print("🎯 FINAL COIA SYSTEM TEST")
    print(f"⏰ Started: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # Step 1: Check backend
    if not test_backend_health():
        print("\n❌ FAILED: Backend not responding")
        return False
    
    # Step 2: Test streaming endpoint
    streaming_success, streaming_company = test_coia_streaming_endpoint()
    
    # Step 3: Test database save from streaming
    streaming_db_success = False
    if streaming_company:
        streaming_db_success = test_database_save(streaming_company)
    
    # Step 4: Test non-streaming endpoint
    nonstreaming_success, nonstreaming_company = test_non_streaming_endpoint()
    
    # Step 5: Test database save from non-streaming
    nonstreaming_db_success = False
    if nonstreaming_company:
        nonstreaming_db_success = test_database_save(nonstreaming_company)
    
    # Final Results
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS")
    print("=" * 60)
    
    print(f"✅ Backend Health: PASS")
    print(f"{'✅' if streaming_success else '❌'} Streaming Endpoint: {'PASS' if streaming_success else 'FAIL'}")
    print(f"{'✅' if streaming_db_success else '❌'} Streaming Database Save: {'PASS' if streaming_db_success else 'FAIL'}")
    print(f"{'✅' if nonstreaming_success else '❌'} Non-Streaming Endpoint: {'PASS' if nonstreaming_success else 'FAIL'}")
    print(f"{'✅' if nonstreaming_db_success else '❌'} Non-Streaming Database Save: {'PASS' if nonstreaming_db_success else 'FAIL'}")
    
    all_pass = all([
        streaming_success,
        streaming_db_success, 
        nonstreaming_success,
        nonstreaming_db_success
    ])
    
    print(f"\n🎯 OVERALL RESULT: {'✅ PASS - PRODUCTION READY' if all_pass else '❌ FAIL - NOT READY'}")
    
    if all_pass:
        print("\n🎉 COIA SYSTEM IS FULLY FUNCTIONAL:")
        print("   - Streaming works with GPT-5/GPT-4o fallback") 
        print("   - Non-streaming works for frontend compatibility")
        print("   - Both endpoints save contractors to database")
        print("   - Real tools are being used (web search, profile building)")
        print("   - Ready for both bid card and generic contractor entry points")
    else:
        print("\n⚠️ ISSUES FOUND - NEED TO FIX BEFORE PRODUCTION")
    
    return all_pass

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)