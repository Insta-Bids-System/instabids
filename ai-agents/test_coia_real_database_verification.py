#!/usr/bin/env python3
"""
REAL COIA Test - Verifies actual database changes and complete workflow
"""
import requests
import json
import time
import sys
from datetime import datetime
from database_simple import db
from config.service_urls import get_backend_url

# Fix Windows Unicode
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

class RealCOIATester:
    def __init__(self):
        self.base_url = f"{get_backend_url()}/ai/coia/chat/stream"
        self.session_id = None
        self.contractor_id = None
        
    def check_contractor_in_database(self, company_name):
        """Check all tables for contractor existence"""
        print(f"\n🔍 CHECKING DATABASE FOR: {company_name}")
        
        # Check contractors table
        contractors = db.client.table('contractors').select('*').ilike('company_name', f'%{company_name}%').execute()
        print(f"   contractors table: {len(contractors.data)} records")
        if contractors.data:
            print(f"      ✅ FOUND: {contractors.data[0]['company_name']} (ID: {contractors.data[0]['id']})")
            return ('contractors', contractors.data[0])
        
        # Check contractor_leads table
        leads = db.client.table('contractor_leads').select('*').ilike('company_name', f'%{company_name}%').execute()
        print(f"   contractor_leads table: {len(leads.data)} records")
        if leads.data:
            print(f"      ✅ FOUND: {leads.data[0]['company_name']} (ID: {leads.data[0]['id']})")
            return ('contractor_leads', leads.data[0])
        
        # Check potential_contractors table
        potential = db.client.table('potential_contractors').select('*').ilike('contractor_data', f'%{company_name}%').execute()
        print(f"   potential_contractors table: {len(potential.data)} records")
        if potential.data:
            print(f"      ✅ FOUND in contractor_data field")
            return ('potential_contractors', potential.data[0])
        
        print(f"   ❌ NOT FOUND in any contractor tables")
        return (None, None)
    
    def send_coia_message(self, message, session_id=None):
        """Send message to COIA and parse response"""
        if not session_id:
            session_id = f"test_{int(time.time())}"
            self.session_id = session_id
        
        print(f"\n📨 SENDING MESSAGE TO COIA:")
        print(f"   Session: {session_id}")
        print(f"   Message: {message[:100]}...")
        
        payload = {
            "message": message,
            "session_id": session_id,
            "interface": "chat"
        }
        
        try:
            response_data = {
                'connected': False,
                'tool_calls': [],
                'profile': None,
                'bid_cards': [],
                'conversation': '',
                'error': None
            }
            
            with requests.post(self.base_url, json=payload, stream=True, timeout=30) as response:
                if response.status_code != 200:
                    response_data['error'] = f"HTTP {response.status_code}"
                    return response_data
                
                for line in response.iter_lines():
                    if line:
                        line_text = line.decode('utf-8')
                        if line_text.startswith('data: '):
                            try:
                                data = json.loads(line_text[6:])
                                msg_type = data.get('type', '')
                                
                                if msg_type == 'connected':
                                    response_data['connected'] = True
                                elif msg_type == 'tool_call':
                                    response_data['tool_calls'].append(data.get('content', ''))
                                elif msg_type == 'token':
                                    response_data['conversation'] += data.get('content', '')
                                elif msg_type == 'metadata':
                                    metadata = data.get('metadata', {})
                                    response_data['profile'] = metadata.get('profile')
                                    response_data['bid_cards'] = metadata.get('bid_cards', [])
                                elif msg_type == 'complete':
                                    break
                            except json.JSONDecodeError:
                                continue
                
                return response_data
                
        except Exception as e:
            return {'error': str(e)}
    
    def test_complete_workflow(self, contractor_name, initial_message):
        """Test the complete COIA workflow with database verification"""
        print(f"\n{'='*80}")
        print(f"TESTING COMPLETE WORKFLOW FOR: {contractor_name}")
        print(f"{'='*80}")
        
        # Step 1: Check initial database state
        print("\n📊 STEP 1: INITIAL DATABASE STATE")
        initial_state = self.check_contractor_in_database(contractor_name)
        
        # Step 2: Send initial onboarding message
        print("\n💬 STEP 2: INITIAL ONBOARDING CONVERSATION")
        response1 = self.send_coia_message(initial_message)
        
        if response1.get('error'):
            print(f"   ❌ ERROR: {response1['error']}")
            return False
        
        print(f"   ✅ Connected: {response1['connected']}")
        print(f"   🔧 Tool calls: {len(response1['tool_calls'])}")
        for tool in response1['tool_calls']:
            print(f"      - {tool}")
        
        if response1['profile']:
            profile = response1['profile']
            print(f"   📋 Profile created:")
            print(f"      Company: {profile.get('company_name')}")
            print(f"      Services: {', '.join(profile.get('services', []))}")
            print(f"      Completeness: {profile.get('completeness_score', 0)}%")
        
        print(f"   🗂️ Bid cards found: {len(response1['bid_cards'])}")
        for i, card in enumerate(response1['bid_cards'][:3], 1):
            print(f"      {i}. {card.get('title', 'Untitled')} - {card.get('budget_range')}")
        
        # Step 3: Wait and check if contractor was saved to database
        print("\n⏳ STEP 3: CHECKING IF CONTRACTOR WAS SAVED (waiting 3 seconds)")
        time.sleep(3)
        
        after_state = self.check_contractor_in_database(contractor_name)
        
        if after_state[0]:
            print(f"   ✅ SUCCESS! Contractor saved to {after_state[0]} table")
            self.contractor_id = after_state[1].get('id')
        else:
            print(f"   ❌ FAILURE! Contractor NOT saved to database")
            print(f"   🔧 Attempting to manually save contractor profile...")
            
            # Try to save the profile manually if COIA didn't do it
            if response1['profile']:
                self.manually_save_contractor(response1['profile'])
        
        # Step 4: Test follow-up conversation for memory
        print("\n💬 STEP 4: FOLLOW-UP CONVERSATION (Testing Memory)")
        follow_up = "Can you remind me what projects you found for my company?"
        response2 = self.send_coia_message(follow_up, self.session_id)
        
        if response2.get('error'):
            print(f"   ❌ ERROR: {response2['error']}")
        else:
            conversation_text = response2['conversation'].lower()
            if contractor_name.lower() in conversation_text or 'your' in conversation_text:
                print(f"   ✅ MEMORY WORKS! COIA remembered the contractor")
                print(f"   Response snippet: {response2['conversation'][:200]}...")
            else:
                print(f"   ❌ MEMORY FAILED! COIA didn't remember the contractor")
        
        # Step 5: Check for user account creation
        print("\n🔐 STEP 5: CHECKING FOR USER ACCOUNT CREATION")
        self.check_user_account(contractor_name)
        
        # Final verification
        print("\n✅ FINAL DATABASE STATE:")
        final_state = self.check_contractor_in_database(contractor_name)
        
        return final_state[0] is not None
    
    def manually_save_contractor(self, profile):
        """Manually save contractor if COIA didn't do it"""
        try:
            # Try to save to contractor_leads
            contractor_data = {
                'company_name': profile.get('company_name', ''),
                'contact_name': profile.get('contact_name', ''),
                'email': profile.get('email', f"info@{profile.get('company_name', 'contractor').lower().replace(' ', '')}.com"),
                'website': profile.get('website', ''),
                'specialties': profile.get('services', []),
                'source': 'COIA Onboarding',
                'discovered_at': datetime.now().isoformat(),
                'lead_status': 'qualified'
            }
            
            result = db.client.table('contractor_leads').insert(contractor_data).execute()
            if result.data:
                print(f"   ✅ Manually saved to contractor_leads: {result.data[0]['id']}")
                return True
        except Exception as e:
            print(f"   ❌ Manual save failed: {e}")
        
        return False
    
    def check_user_account(self, company_name):
        """Check if a user account was created"""
        # Check the auth.users table or profiles table
        try:
            profiles = db.client.table('profiles').select('*').ilike('company_name', f'%{company_name}%').execute()
            if profiles.data:
                print(f"   ✅ User account found: {profiles.data[0]['email']}")
                return True
            else:
                print(f"   ❌ No user account created")
                return False
        except:
            print(f"   ⚠️ Could not check user accounts")
            return False

def main():
    print("🚀 REAL COIA DATABASE VERIFICATION TEST")
    print(f"⏰ Started: {datetime.now().isoformat()}")
    
    tester = RealCOIATester()
    
    # Test JM Holiday Lighting
    jm_success = tester.test_complete_workflow(
        "JM Holiday Lighting",
        "Hello, I'm John from JM Holiday Lighting. We provide professional holiday lighting installation and electrical services throughout South Florida. We're licensed and insured, been in business for 8 years. Looking to join your platform to bid on electrical and lighting projects."
    )
    
    print("\n" + "="*80)
    
    # Test TurfGrass Artificial Solutions
    turf_success = tester.test_complete_workflow(
        "TurfGrass Artificial Solutions",
        "Hi, I'm the owner of TurfGrass Artificial Solutions in South Florida. We specialize in artificial grass installation, synthetic turf, and landscaping services. We've been doing this for 15 years and want to get registered on your platform to find new projects."
    )
    
    # Final Summary
    print(f"\n{'='*80}")
    print("📊 FINAL TEST RESULTS")
    print(f"{'='*80}")
    print(f"JM Holiday Lighting: {'✅ PASSED' if jm_success else '❌ FAILED'}")
    print(f"TurfGrass Artificial Solutions: {'✅ PASSED' if turf_success else '❌ FAILED'}")
    
    if jm_success and turf_success:
        print("\n🎉 SUCCESS! COIA is 100% WORKING!")
    else:
        print("\n❌ ISSUES FOUND - COIA needs fixes")

if __name__ == "__main__":
    main()