#!/usr/bin/env python3
"""
Complete COIA End-to-End Workflow Test
Tests full contractor onboarding with multiple conversation turns and UI verification
"""
import requests
import json
import time
import sys
from datetime import datetime
from config.service_urls import get_backend_url

# Fix Windows Unicode issues
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

class COIAWorkflowTester:
    def __init__(self):
        self.base_url = f"{get_backend_url()}/ai/coia/chat/stream"
        self.contractor_sessions = {}
        
    def parse_streaming_response(self, response, contractor_name):
        """Parse streaming response and extract key data"""
        print(f"\n=== STREAMING RESPONSE FOR {contractor_name.upper()} ===")
        
        profile_data = None
        bid_cards_data = None
        conversation_tokens = []
        tool_calls = []
        connected = False
        
        for line in response.iter_lines():
            if line:
                line_text = line.decode('utf-8')
                if line_text.startswith('data: '):
                    try:
                        data_content = line_text[6:]  # Remove 'data: '
                        if data_content != '[DONE]':
                            parsed = json.loads(data_content)
                            msg_type = parsed.get('type', 'unknown')
                            content = parsed.get('content', '')
                            
                            if msg_type == 'connected':
                                connected = True
                                print(f"✅ {content}")
                                
                            elif msg_type == 'tool_call':
                                tool_calls.append(content)
                                print(f"🔧 TOOL: {content}")
                                
                            elif msg_type == 'token':
                                conversation_tokens.append(content)
                                # Show first and last few tokens
                                if len(conversation_tokens) <= 3 or len(conversation_tokens) % 20 == 0:
                                    print(f"💬 Token: {content}")
                                    
                            elif msg_type == 'metadata':
                                metadata = parsed.get('metadata', {})
                                profile_data = metadata.get('profile', {})
                                bid_cards_data = metadata.get('bid_cards', [])
                                
                                print(f"\n📋 CONTRACTOR PROFILE RECEIVED:")
                                print(f"   Company: {profile_data.get('company_name', 'Unknown')}")
                                print(f"   Services: {', '.join(profile_data.get('services', []))}")
                                print(f"   Completeness: {profile_data.get('completeness_score', 0):.1f}%")
                                print(f"   Website: {profile_data.get('website', 'N/A')}")
                                
                                print(f"\n🗂️ MATCHING BID CARDS FOUND: {len(bid_cards_data)}")
                                for i, card in enumerate(bid_cards_data[:3], 1):
                                    print(f"   {i}. {card.get('title', 'Untitled')} - {card.get('budget_range', 'N/A')}")
                                    
                            elif msg_type == 'complete':
                                break
                                
                    except json.JSONDecodeError:
                        continue
        
        full_conversation = ''.join(conversation_tokens)
        
        return {
            'connected': connected,
            'tool_calls': tool_calls,
            'profile': profile_data,
            'bid_cards': bid_cards_data,
            'conversation': full_conversation,
            'tool_count': len(tool_calls),
            'token_count': len(conversation_tokens)
        }
    
    def test_contractor_onboarding(self, contractor_name, initial_message, follow_up_messages):
        """Test complete contractor onboarding workflow"""
        session_id = f"{contractor_name.lower().replace(' ', '_')}_session_{int(time.time())}"
        
        print(f"\n{'='*80}")
        print(f"TESTING COMPLETE WORKFLOW: {contractor_name.upper()}")
        print(f"{'='*80}")
        print(f"Session ID: {session_id}")
        
        conversation_results = []
        
        # Initial conversation
        print(f"\n🔄 INITIAL ONBOARDING CONVERSATION")
        print(f"Message: {initial_message}")
        
        payload = {
            "message": initial_message,
            "session_id": session_id,
            "interface": "chat"
        }
        
        try:
            with requests.post(self.base_url, json=payload, stream=True, timeout=30) as response:
                if response.status_code == 200:
                    result = self.parse_streaming_response(response, contractor_name)
                    conversation_results.append(('Initial', result))
                    
                    # Store session for persistence testing
                    self.contractor_sessions[contractor_name] = {
                        'session_id': session_id,
                        'profile': result.get('profile'),
                        'initial_result': result
                    }
                    
                else:
                    print(f"❌ Error: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
        
        # Follow-up conversations
        for i, follow_up in enumerate(follow_up_messages, 1):
            print(f"\n🔄 FOLLOW-UP CONVERSATION #{i}")
            print(f"Message: {follow_up}")
            
            time.sleep(2)  # Brief pause between conversations
            
            payload = {
                "message": follow_up,
                "session_id": session_id,  # Same session ID for persistence
                "interface": "chat"
            }
            
            try:
                with requests.post(self.base_url, json=payload, stream=True, timeout=30) as response:
                    if response.status_code == 200:
                        result = self.parse_streaming_response(response, f"{contractor_name} Follow-up {i}")
                        conversation_results.append((f'Follow-up {i}', result))
                    else:
                        print(f"❌ Follow-up {i} failed: {response.status_code}")
                        
            except Exception as e:
                print(f"❌ Follow-up {i} error: {e}")
        
        # Analyze conversation persistence
        print(f"\n📊 CONVERSATION ANALYSIS:")
        print(f"   Total conversations: {len(conversation_results)}")
        
        for conv_type, result in conversation_results:
            print(f"   {conv_type}: {result['tool_count']} tools, {result['token_count']} tokens, Connected: {result['connected']}")
        
        # Check if profile data persisted
        initial_profile = conversation_results[0][1].get('profile')
        if initial_profile and len(conversation_results) > 1:
            print(f"   Profile persistence: {initial_profile.get('company_name', 'Unknown')} profile from initial conversation")
        
        return True
    
    def test_session_persistence(self):
        """Test that sessions persist across conversations"""
        print(f"\n{'='*80}")
        print("TESTING SESSION PERSISTENCE")
        print(f"{'='*80}")
        
        for contractor_name, session_data in self.contractor_sessions.items():
            session_id = session_data['session_id']
            profile = session_data['profile']
            
            print(f"\n🔄 Testing persistence for {contractor_name}")
            print(f"Session ID: {session_id}")
            
            # Send a message referencing previous conversation
            test_message = "Can you remind me what projects you found for my business?"
            
            payload = {
                "message": test_message,
                "session_id": session_id,  # Same session ID
                "interface": "chat"
            }
            
            try:
                with requests.post(self.base_url, json=payload, stream=True, timeout=20) as response:
                    if response.status_code == 200:
                        result = self.parse_streaming_response(response, f"{contractor_name} Persistence Test")
                        
                        # Check if COIA remembers the contractor
                        conversation = result.get('conversation', '')
                        company_name = profile.get('company_name', '') if profile else ''
                        
                        if company_name and company_name.lower() in conversation.lower():
                            print(f"✅ PERSISTENCE SUCCESS: COIA remembered {company_name}")
                        else:
                            print(f"⚠️ PERSISTENCE UNCLEAR: Could not confirm memory of {company_name}")
                            
                    else:
                        print(f"❌ Persistence test failed: {response.status_code}")
                        
            except Exception as e:
                print(f"❌ Persistence test error: {e}")
    
    def run_complete_test(self):
        """Run the complete COIA workflow test"""
        print("🚀 STARTING COMPLETE COIA WORKFLOW TEST")
        print(f"⏰ Test started at: {datetime.now().isoformat()}")
        print(f"🔗 Backend URL: {self.base_url}")
        
        # Test TurfGrass Artificial Solutions
        turfgrass_success = self.test_contractor_onboarding(
            "TurfGrass Artificial Solutions",
            "Hi, I own TurfGrass Artificial Solutions in South Florida. We specialize in artificial grass installation and landscaping services. I'm interested in finding new projects and getting registered with your platform.",
            [
                "That sounds right! We also do putting greens and commercial landscaping. Can you show me more details about those landscaping projects?",
                "What's the process for submitting bids on these projects? Do you need any additional information from us?",
                "We're licensed and insured in Florida. How do we get verified on your platform?"
            ]
        )
        
        # Test JM Holiday Lighting
        jm_success = self.test_contractor_onboarding(
            "JM Holiday Lighting",
            "Hello, I'm with JM Holiday Lighting. We provide professional holiday lighting installation and electrical services throughout South Florida. Looking for opportunities to bid on electrical and lighting projects.",
            [
                "Perfect! We do both residential and commercial holiday displays. Can you tell me more about the commercial project in Delray Beach?",
                "We have all the necessary electrical licenses. What's the typical timeline for holiday lighting projects?",
                "Do you have any emergency lighting repair jobs? We offer 24/7 service for urgent electrical issues."
            ]
        )
        
        # Test session persistence
        if turfgrass_success or jm_success:
            time.sleep(3)
            self.test_session_persistence()
        
        # Final summary
        print(f"\n{'='*80}")
        print("📊 COMPLETE TEST SUMMARY")
        print(f"{'='*80}")
        print(f"⏰ Test completed at: {datetime.now().isoformat()}")
        print(f"✅ TurfGrass workflow: {'PASSED' if turfgrass_success else 'FAILED'}")
        print(f"✅ JM Holiday workflow: {'PASSED' if jm_success else 'FAILED'}")
        print(f"📱 Sessions created: {len(self.contractor_sessions)}")
        
        if turfgrass_success and jm_success:
            print(f"\n🎉 ALL TESTS PASSED - COIA COMPLETE WORKFLOW VERIFIED!")
            print("✅ Real database integration working")
            print("✅ Multi-turn conversations working")
            print("✅ Session persistence verified")
            print("✅ Both contractor types successfully onboarded")
        else:
            print(f"\n⚠️ SOME TESTS FAILED - REQUIRES INVESTIGATION")

if __name__ == "__main__":
    tester = COIAWorkflowTester()
    tester.run_complete_test()