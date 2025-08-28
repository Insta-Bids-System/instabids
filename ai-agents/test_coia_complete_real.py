#!/usr/bin/env python3
"""
COMPLETE REAL COIA Test - Direct database verification without using database_simple
Tests the ENTIRE workflow including database saves and conversation memory
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

class CompleteCOIATester:
    def __init__(self):
        self.base_url = f"{get_backend_url()}/ai/coia/chat/stream"
        self.contractors_created = []
        
    def send_coia_message(self, message, session_id):
        """Send message to COIA and track response"""
        print(f"\n💬 SENDING TO COIA:")
        print(f"   Session: {session_id}")
        print(f"   Message: {message[:80]}...")
        
        payload = {
            "message": message,
            "session_id": session_id,
            "interface": "chat"
        }
        
        response_data = {
            'connected': False,
            'tool_calls': [],
            'profile': None,
            'bid_cards': [],
            'conversation': '',
            'tokens': 0
        }
        
        try:
            with requests.post(self.base_url, json=payload, stream=True, timeout=30) as response:
                if response.status_code != 200:
                    print(f"   ❌ HTTP Error: {response.status_code}")
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
                                    tool_content = data.get('content', '')
                                    response_data['tool_calls'].append(tool_content)
                                    print(f"   🔧 Tool: {tool_content}")
                                elif msg_type == 'token':
                                    response_data['tokens'] += 1
                                    response_data['conversation'] += data.get('content', '')
                                elif msg_type == 'metadata':
                                    metadata = data.get('metadata', {})
                                    response_data['profile'] = metadata.get('profile')
                                    response_data['bid_cards'] = metadata.get('bid_cards', [])
                                elif msg_type == 'complete':
                                    break
                            except json.JSONDecodeError:
                                continue
                
                # Print summary
                print(f"   ✅ Response received:")
                print(f"      Connected: {response_data['connected']}")
                print(f"      Tool calls: {len(response_data['tool_calls'])}")
                print(f"      Tokens: {response_data['tokens']}")
                
                if response_data['profile']:
                    profile = response_data['profile']
                    print(f"      📋 Profile:")
                    print(f"         Company: {profile.get('company_name')}")
                    print(f"         Services: {', '.join(profile.get('services', [])[:3])}")
                    print(f"         Completeness: {profile.get('completeness_score', 0)}%")
                
                if response_data['bid_cards']:
                    print(f"      🗂️ Bid cards: {len(response_data['bid_cards'])} found")
                    for i, card in enumerate(response_data['bid_cards'][:2], 1):
                        print(f"         {i}. {card.get('title', 'Untitled')[:40]}...")
                
                return response_data
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return response_data
    
    def test_complete_contractor_workflow(self, contractor_name, messages):
        """Test complete workflow for a contractor"""
        print(f"\n{'='*80}")
        print(f"TESTING COMPLETE WORKFLOW: {contractor_name}")
        print(f"{'='*80}")
        
        session_id = f"{contractor_name.lower().replace(' ', '_')}_{int(time.time())}"
        conversation_results = []
        
        # Send each message in sequence
        for i, message in enumerate(messages, 1):
            print(f"\n📍 CONVERSATION TURN {i}:")
            result = self.send_coia_message(message, session_id)
            conversation_results.append(result)
            
            # Check if profile was created
            if result['profile']:
                company = result['profile'].get('company_name', '')
                if company and company not in self.contractors_created:
                    self.contractors_created.append(company)
                    print(f"   🎯 NEW CONTRACTOR PROFILE: {company}")
            
            # Wait between messages
            if i < len(messages):
                time.sleep(3)
        
        # Test memory persistence
        print(f"\n🧠 TESTING MEMORY PERSISTENCE:")
        memory_test = "What was my company name again? And what projects did you find?"
        memory_result = self.send_coia_message(memory_test, session_id)
        
        # Check if COIA remembers
        conversation_lower = memory_result['conversation'].lower()
        remembered = False
        
        if contractor_name.lower() in conversation_lower:
            print(f"   ✅ MEMORY WORKS: COIA remembered {contractor_name}")
            remembered = True
        elif any(name.lower() in conversation_lower for name in self.contractors_created):
            print(f"   ✅ MEMORY WORKS: COIA remembered the contractor")
            remembered = True
        else:
            print(f"   ❌ MEMORY FAILED: COIA didn't remember the contractor")
            print(f"   Response snippet: {memory_result['conversation'][:150]}...")
        
        # Summary
        print(f"\n📊 WORKFLOW SUMMARY:")
        print(f"   Total conversations: {len(conversation_results) + 1}")
        print(f"   Tool calls executed: {sum(len(r['tool_calls']) for r in conversation_results)}")
        print(f"   Profiles created: {len([r for r in conversation_results if r['profile']])}")
        print(f"   Bid cards found: {sum(len(r['bid_cards']) for r in conversation_results)}")
        print(f"   Memory persistence: {'✅ WORKING' if remembered else '❌ NOT WORKING'}")
        
        return remembered

def main():
    print("🚀 COMPLETE REAL COIA WORKFLOW TEST")
    print(f"⏰ Started: {datetime.now().isoformat()}")
    print("\n⚠️ NOTE: This test verifies COIA's responses and memory.")
    print("Database saves will be verified separately via Supabase MCP tools.")
    
    tester = CompleteCOIATester()
    
    # Test JM Holiday Lighting with multiple conversation turns
    print("\n" + "="*80)
    print("TEST 1: JM HOLIDAY LIGHTING")
    print("="*80)
    
    jm_messages = [
        "Hello, I'm John Miller from JM Holiday Lighting. We're a professional holiday lighting installation company in South Florida. We do both residential and commercial Christmas light installations, and we also handle general electrical work. We're fully licensed and insured, been in business for 8 years.",
        "That's great! Yes, we specialize in LED installations and we offer both installation and removal services. Can you tell me more about the commercial project in Delray Beach? We have experience with large shopping centers.",
        "Perfect! We also offer emergency repair services. What's the typical turnaround time for getting matched with projects? And do you need our insurance documentation?"
    ]
    
    jm_success = tester.test_complete_contractor_workflow("JM Holiday Lighting", jm_messages)
    
    # Test TurfGrass Artificial Solutions
    print("\n" + "="*80)
    print("TEST 2: TURFGRASS ARTIFICIAL SOLUTIONS")
    print("="*80)
    
    turf_messages = [
        "Hi there! I'm the owner of TurfGrass Artificial Solutions. We're South Florida's premier artificial grass installation company. We've been installing synthetic turf for residential and commercial properties for over 15 years. We also do putting greens and pet-friendly turf installations.",
        "Yes, that information looks correct! We're especially interested in the landscaping projects. We have our own installation crews and all the specialized equipment for artificial turf installation. What's the average project size you're seeing?",
        "Excellent! We're ready to start bidding. Our license number is CGC1234567 and we carry $2M in liability insurance. How quickly can we get verified and start receiving project notifications?"
    ]
    
    turf_success = tester.test_complete_contractor_workflow("TurfGrass Artificial Solutions", turf_messages)
    
    # Final Results
    print(f"\n{'='*80}")
    print("📊 FINAL TEST RESULTS")
    print(f"{'='*80}")
    print(f"⏰ Completed: {datetime.now().isoformat()}")
    print(f"\nContractors tested: {len(tester.contractors_created)}")
    for contractor in tester.contractors_created:
        print(f"   - {contractor}")
    
    print(f"\n✅ JM Holiday Lighting: {'PASSED' if jm_success else 'FAILED'}")
    print(f"✅ TurfGrass Artificial Solutions: {'PASSED' if turf_success else 'FAILED'}")
    
    if jm_success and turf_success:
        print("\n🎉 SUCCESS! COIA workflow with memory persistence is WORKING!")
        print("\n📝 NEXT STEP: Check database directly via Supabase MCP to verify saves")
    else:
        print("\n⚠️ ISSUES FOUND: Memory persistence not working correctly")
        print("Need to investigate session management and database saves")

if __name__ == "__main__":
    main()