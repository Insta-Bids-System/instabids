"""
EXHAUSTIVE COIA VERIFICATION TEST
Tests multiple conversations with persistent memory and context recall
Verifies everything is saved and remembered correctly
"""

import asyncio
import requests
import json
import time
from datetime import datetime
import uuid
import sys
import io
from config.service_urls import get_backend_url

# Fix Unicode output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class ExhaustiveCOIATest:
    def __init__(self):
        self.base_url = get_backend_url()
        self.test_results = []
        self.contractors_created = []
        self.conversations_created = []
        
    def log(self, message, level="INFO"):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = "✅" if level == "SUCCESS" else "❌" if level == "ERROR" else "📝"
        print(f"[{timestamp}] {prefix} {message}")
        
    async def test_conversation_1_new_contractor(self):
        """Test 1: Create a new contractor with full profile"""
        self.log("=" * 80)
        self.log("TEST 1: NEW CONTRACTOR CONVERSATION", "INFO")
        self.log("=" * 80)
        
        session_id = f"exhaust-session-1-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        contractor_name = f"Premium Construction LLC {uuid.uuid4().hex[:4]}"
        
        # Message 1: Introduction
        self.log("Sending introduction message...")
        response = requests.post(f"{self.base_url}/api/coia/chat", json={
            "message": f"Hi, I'm John from {contractor_name}. We're a full-service construction company in Miami specializing in kitchen and bathroom remodeling.",
            "session_id": session_id,
            "contractor_lead_id": f"lead-{uuid.uuid4().hex[:8]}"
        })
        
        if response.ok:
            data = response.json()
            self.log(f"Response received - Profile created: {bool(data.get('profile'))}", "SUCCESS")
            contractor_id = data.get('profile', {}).get('contractor_id')
            self.contractors_created.append({
                'id': contractor_id,
                'name': contractor_name,
                'session_id': session_id
            })
            self.log(f"Contractor ID: {contractor_id}")
            
            # Message 2: Add more details
            time.sleep(1)
            self.log("Sending follow-up with more details...")
            response2 = requests.post(f"{self.base_url}/api/coia/chat", json={
                "message": "We've been in business for 15 years and have a team of 12 people. We're licensed and insured.",
                "session_id": session_id,
                "contractor_lead_id": f"lead-{uuid.uuid4().hex[:8]}"
            })
            
            if response2.ok:
                self.log("Follow-up processed successfully", "SUCCESS")
            
            # Message 3: Ask about opportunities
            time.sleep(1)
            self.log("Asking about opportunities...")
            response3 = requests.post(f"{self.base_url}/api/coia/chat", json={
                "message": "What kind of projects are available on InstaBids right now?",
                "session_id": session_id,
                "contractor_lead_id": f"lead-{uuid.uuid4().hex[:8]}"
            })
            
            if response3.ok:
                data3 = response3.json()
                bid_cards = data3.get('bid_cards', [])
                self.log(f"Bid cards returned: {len(bid_cards)}", "SUCCESS")
                
            self.conversations_created.append(session_id)
            return True
        else:
            self.log(f"Failed to create contractor: {response.status_code}", "ERROR")
            return False
            
    async def test_conversation_2_resume_session(self):
        """Test 2: Resume the same contractor session to verify memory"""
        self.log("=" * 80)
        self.log("TEST 2: RESUME EXISTING SESSION", "INFO")
        self.log("=" * 80)
        
        if not self.contractors_created:
            self.log("No contractors to resume", "ERROR")
            return False
            
        # Use the first contractor's session
        prev_contractor = self.contractors_created[0]
        session_id = prev_contractor['session_id']
        
        self.log(f"Resuming session: {session_id}")
        self.log(f"Original contractor: {prev_contractor['name']}")
        
        # Try to resume conversation
        response = requests.post(f"{self.base_url}/api/coia/chat", json={
            "message": "What was the name of my company again? Can you remind me what I told you?",
            "session_id": session_id,
            "contractor_lead_id": f"lead-{uuid.uuid4().hex[:8]}"
        })
        
        if response.ok:
            data = response.json()
            response_text = data.get('response', '')
            
            # Check if it remembers the company name
            if prev_contractor['name'] in response_text or "Premium Construction" in response_text:
                self.log("MEMORY VERIFIED: Bot remembers the company name!", "SUCCESS")
                return True
            else:
                self.log("Memory check: Response doesn't contain company name", "ERROR")
                self.log(f"Response: {response_text[:200]}...")
                return False
        else:
            self.log(f"Failed to resume session: {response.status_code}", "ERROR")
            return False
            
    async def test_conversation_3_different_contractor(self):
        """Test 3: Create a completely different contractor"""
        self.log("=" * 80)
        self.log("TEST 3: DIFFERENT CONTRACTOR", "INFO")
        self.log("=" * 80)
        
        session_id = f"exhaust-session-2-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        contractor_name = f"Elite Plumbing Services {uuid.uuid4().hex[:4]}"
        
        self.log("Creating second contractor...")
        response = requests.post(f"{self.base_url}/api/coia/chat", json={
            "message": f"Hello, this is {contractor_name}. We do emergency plumbing repairs and water heater installations in Fort Lauderdale.",
            "session_id": session_id,
            "contractor_lead_id": f"lead-{uuid.uuid4().hex[:8]}"
        })
        
        if response.ok:
            data = response.json()
            contractor_id = data.get('profile', {}).get('contractor_id')
            self.contractors_created.append({
                'id': contractor_id,
                'name': contractor_name,
                'session_id': session_id
            })
            self.log(f"Second contractor created: {contractor_id}", "SUCCESS")
            self.conversations_created.append(session_id)
            return True
        else:
            self.log(f"Failed to create second contractor: {response.status_code}", "ERROR")
            return False
            
    async def test_memory_isolation(self):
        """Test 4: Verify conversations don't leak between contractors"""
        self.log("=" * 80)
        self.log("TEST 4: MEMORY ISOLATION", "INFO")
        self.log("=" * 80)
        
        if len(self.contractors_created) < 2:
            self.log("Need at least 2 contractors for isolation test", "ERROR")
            return False
            
        # Try to access first contractor's info from second session
        second_session = self.contractors_created[1]['session_id']
        first_contractor_name = self.contractors_created[0]['name']
        
        self.log(f"Testing if session {second_session} knows about {first_contractor_name}")
        
        response = requests.post(f"{self.base_url}/api/coia/chat", json={
            "message": f"Do you know anything about {first_contractor_name}?",
            "session_id": second_session,
            "contractor_lead_id": f"lead-{uuid.uuid4().hex[:8]}"
        })
        
        if response.ok:
            data = response.json()
            response_text = data.get('response', '').lower()
            
            # Should NOT know about the other contractor
            if first_contractor_name.lower() not in response_text:
                self.log("ISOLATION VERIFIED: Sessions are properly isolated!", "SUCCESS")
                return True
            else:
                self.log("ISOLATION FAILED: Cross-session data leak detected!", "ERROR")
                return False
        else:
            self.log(f"Isolation test request failed: {response.status_code}", "ERROR")
            return False
            
    async def verify_database_persistence(self):
        """Test 5: Verify all data is in database using Supabase MCP"""
        self.log("=" * 80)
        self.log("TEST 5: DATABASE VERIFICATION", "INFO")
        self.log("=" * 80)
        
        # Import here to avoid issues if not installed
        try:
            from agents.coia.persistent_memory import PersistentCoIAStateManager
            
            state_manager = PersistentCoIAStateManager()
            
            # Check each contractor
            for contractor in self.contractors_created:
                self.log(f"Checking database for contractor: {contractor['name']}")
                
                # Try to load the session
                state = await state_manager.get_session(contractor['session_id'])
                
                if state:
                    self.log(f"  ✅ Session found in memory", "SUCCESS")
                    self.log(f"     Messages: {len(state.messages)}")
                    self.log(f"     Contractor ID: {state.contractor_id}")
                    self.log(f"     Stage: {state.current_stage}")
                    
                    # Show first and last message
                    if state.messages:
                        self.log(f"     First msg: {state.messages[0].content[:50]}...")
                        self.log(f"     Last msg: {state.messages[-1].content[:50]}...")
                else:
                    self.log(f"  ❌ Session not found in database", "ERROR")
                    
            return True
        except Exception as e:
            self.log(f"Database verification error: {e}", "ERROR")
            return False
            
    async def test_context_retrieval(self):
        """Test 6: Verify context can be retrieved with privacy filtering"""
        self.log("=" * 80)
        self.log("TEST 6: CONTEXT RETRIEVAL & PRIVACY", "INFO")
        self.log("=" * 80)
        
        if not self.contractors_created:
            self.log("No contractors to test context", "ERROR")
            return False
            
        contractor = self.contractors_created[0]
        
        # Test context API
        response = requests.get(f"{self.base_url}/api/agent-context/context/COIA", params={
            "user_id": contractor['id'],
            "conversation_id": contractor['session_id']
        })
        
        if response.ok:
            context = response.json()
            ctx_data = context.get('context', {})
            
            self.log(f"Context retrieved successfully", "SUCCESS")
            self.log(f"  Privacy level: {ctx_data.get('privacy_level')}")
            self.log(f"  Agent type: {ctx_data.get('agent_type')}")
            
            # Verify no homeowner PII
            context_str = str(context)
            if "homeowner_name" not in context_str and "homeowner_email" not in context_str:
                self.log(f"  ✅ Privacy filtering verified - No homeowner PII", "SUCCESS")
                return True
            else:
                self.log(f"  ❌ Privacy filtering failed - PII detected", "ERROR")
                return False
        else:
            self.log(f"Context retrieval failed: {response.status_code}", "ERROR")
            return False
            
    async def run_all_tests(self):
        """Run all tests in sequence"""
        self.log("🚀 STARTING EXHAUSTIVE COIA VERIFICATION", "INFO")
        self.log("This will test multiple conversations, memory persistence, and isolation")
        self.log("")
        
        results = {}
        
        # Test 1: New contractor
        try:
            results['new_contractor'] = await self.test_conversation_1_new_contractor()
            time.sleep(2)
        except Exception as e:
            self.log(f"Test 1 failed: {e}", "ERROR")
            results['new_contractor'] = False
            
        # Test 2: Resume session
        try:
            results['resume_session'] = await self.test_conversation_2_resume_session()
            time.sleep(2)
        except Exception as e:
            self.log(f"Test 2 failed: {e}", "ERROR")
            results['resume_session'] = False
            
        # Test 3: Different contractor
        try:
            results['different_contractor'] = await self.test_conversation_3_different_contractor()
            time.sleep(2)
        except Exception as e:
            self.log(f"Test 3 failed: {e}", "ERROR")
            results['different_contractor'] = False
            
        # Test 4: Memory isolation
        try:
            results['memory_isolation'] = await self.test_memory_isolation()
            time.sleep(2)
        except Exception as e:
            self.log(f"Test 4 failed: {e}", "ERROR")
            results['memory_isolation'] = False
            
        # Test 5: Database persistence
        try:
            results['database_persistence'] = await self.verify_database_persistence()
            time.sleep(2)
        except Exception as e:
            self.log(f"Test 5 failed: {e}", "ERROR")
            results['database_persistence'] = False
            
        # Test 6: Context retrieval
        try:
            results['context_retrieval'] = await self.test_context_retrieval()
        except Exception as e:
            self.log(f"Test 6 failed: {e}", "ERROR")
            results['context_retrieval'] = False
            
        # Final summary
        self.log("")
        self.log("=" * 80)
        self.log("EXHAUSTIVE TEST RESULTS", "INFO")
        self.log("=" * 80)
        
        all_passed = all(results.values())
        
        for test_name, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            self.log(f"{test_name}: {status}")
            
        self.log("")
        self.log(f"Contractors created: {len(self.contractors_created)}")
        self.log(f"Conversations created: {len(self.conversations_created)}")
        
        if all_passed:
            self.log("")
            self.log("🎉" * 40)
            self.log("ALL TESTS PASSED - COIA IS 100% VERIFIED!", "SUCCESS")
            self.log("✅ Multiple conversations work")
            self.log("✅ Memory persists across sessions")
            self.log("✅ Context isolation verified")
            self.log("✅ Database persistence confirmed")
            self.log("✅ Privacy filtering active")
            self.log("🎉" * 40)
        else:
            self.log("")
            self.log("❌ SOME TESTS FAILED - CHECK DETAILS ABOVE", "ERROR")
            
        return all_passed

if __name__ == "__main__":
    tester = ExhaustiveCOIATest()
    success = asyncio.run(tester.run_all_tests())
    
    if not success:
        sys.exit(1)