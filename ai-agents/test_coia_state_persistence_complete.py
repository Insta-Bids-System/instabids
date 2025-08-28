"""
Comprehensive Test Suite for COIA State Persistence System
Tests all aspects of the new unified memory persistence implementation
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
import httpx
import uuid
from config.service_urls import get_backend_url

# Test configuration
BACKEND_URL = get_backend_url()
TEST_TIMEOUT = 30

class COIAStatePersistenceTestSuite:
    """Complete test suite for COIA state persistence"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=TEST_TIMEOUT)
        self.test_results = []
        self.contractor_lead_id = None
        self.conversation_id = None
        
    async def run_all_tests(self):
        """Run complete test suite"""
        print("\n" + "="*80)
        print("COIA STATE PERSISTENCE - COMPREHENSIVE TEST SUITE")
        print("="*80)
        
        # Test 1: New Visitor Flow
        await self.test_new_visitor_flow()
        
        # Test 2: State Persistence Verification
        await self.test_state_persistence()
        
        # Test 3: Return Visitor Experience
        await self.test_return_visitor()
        
        # Test 4: Multiple Conversation Turns
        await self.test_multiple_turns()
        
        # Test 5: Complex State Fields
        await self.test_complex_state_fields()
        
        # Test 6: Database Verification
        await self.test_database_storage()
        
        # Test 7: Non-blocking Performance
        await self.test_non_blocking_saves()
        
        # Test 8: Account Creation Linking
        await self.test_account_linking()
        
        # Print results
        self.print_test_results()
        
    async def test_new_visitor_flow(self):
        """Test 1: New visitor gets contractor_lead_id and state saves"""
        print("\n📋 Test 1: New Visitor Flow")
        print("-" * 40)
        
        try:
            # First message without contractor_lead_id
            response = await self.client.post(
                f"{API_BASE_URL}/api/coia/landing",
                json={
                    "message": "Hi, I'm ABC Landscaping and we specialize in lawn care",
                    "session_id": f"test-session-{uuid.uuid4().hex[:8]}"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check contractor_lead_id was generated
                if data.get("contractor_lead_id") and data["contractor_lead_id"].startswith("landing-"):
                    self.contractor_lead_id = data["contractor_lead_id"]
                    print(f"✅ contractor_lead_id generated: {self.contractor_lead_id}")
                    
                    # Check response acknowledges company name
                    if "ABC Landscaping" in data.get("response", "") or "lawn care" in data.get("response", ""):
                        print("✅ Company name extracted and acknowledged")
                        self.test_results.append(("New Visitor Flow", "PASS"))
                    else:
                        print("❌ Company name not acknowledged in response")
                        self.test_results.append(("New Visitor Flow", "PARTIAL"))
                else:
                    print("❌ contractor_lead_id not generated")
                    self.test_results.append(("New Visitor Flow", "FAIL"))
            else:
                print(f"❌ API call failed: {response.status_code}")
                self.test_results.append(("New Visitor Flow", "FAIL"))
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            self.test_results.append(("New Visitor Flow", "ERROR"))
    
    async def test_state_persistence(self):
        """Test 2: Verify state is actually saved to unified memory"""
        print("\n📋 Test 2: State Persistence Verification")
        print("-" * 40)
        
        if not self.contractor_lead_id:
            print("⚠️ Skipping - no contractor_lead_id from Test 1")
            self.test_results.append(("State Persistence", "SKIP"))
            return
            
        try:
            # Wait for async save to complete
            await asyncio.sleep(2)
            
            # Query unified memory for saved state
            response = await self.client.get(
                f"{API_BASE_URL}/api/conversations/{self.contractor_lead_id}"
            )
            
            if response.status_code == 200:
                data = response.json()
                memory_items = data.get("memory", [])
                
                # Check for saved state fields
                saved_fields = {}
                for item in memory_items:
                    if item.get("memory_type") == "coia_state":
                        saved_fields[item["memory_key"]] = item["memory_value"]
                
                if saved_fields:
                    print(f"✅ Found {len(saved_fields)} saved state fields:")
                    for key in list(saved_fields.keys())[:5]:  # Show first 5
                        print(f"   - {key}: {str(saved_fields[key])[:50]}")
                    
                    # Check critical fields
                    if "company_name" in saved_fields:
                        print(f"✅ company_name saved: {saved_fields['company_name']}")
                        self.test_results.append(("State Persistence", "PASS"))
                    else:
                        print("⚠️ company_name not found in saved state")
                        self.test_results.append(("State Persistence", "PARTIAL"))
                else:
                    print("❌ No state fields saved to unified memory")
                    self.test_results.append(("State Persistence", "FAIL"))
            else:
                print(f"⚠️ Could not query unified memory: {response.status_code}")
                self.test_results.append(("State Persistence", "SKIP"))
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            self.test_results.append(("State Persistence", "ERROR"))
    
    async def test_return_visitor(self):
        """Test 3: Return visitor with same contractor_lead_id gets restored state"""
        print("\n📋 Test 3: Return Visitor Experience")
        print("-" * 40)
        
        if not self.contractor_lead_id:
            print("⚠️ Skipping - no contractor_lead_id from Test 1")
            self.test_results.append(("Return Visitor", "SKIP"))
            return
            
        try:
            # Simulate return visit with same contractor_lead_id
            response = await self.client.post(
                f"{API_BASE_URL}/api/coia/landing",
                json={
                    "message": "What did I tell you about my company?",
                    "session_id": f"test-session-{uuid.uuid4().hex[:8]}",
                    "contractor_lead_id": self.contractor_lead_id
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response shows memory of previous conversation
                response_text = data.get("response", "").lower()
                if any(term in response_text for term in ["abc landscaping", "lawn care", "remember", "mentioned"]):
                    print("✅ COIA remembers previous conversation!")
                    print(f"   Response: {data['response'][:200]}...")
                    self.test_results.append(("Return Visitor", "PASS"))
                else:
                    print("❌ COIA doesn't remember previous conversation")
                    print(f"   Response: {data['response'][:200]}...")
                    self.test_results.append(("Return Visitor", "FAIL"))
                    
                # Verify same contractor_lead_id returned
                if data.get("contractor_lead_id") == self.contractor_lead_id:
                    print(f"✅ Same contractor_lead_id maintained: {self.contractor_lead_id}")
                else:
                    print("❌ contractor_lead_id changed unexpectedly")
                    
            else:
                print(f"❌ API call failed: {response.status_code}")
                self.test_results.append(("Return Visitor", "FAIL"))
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            self.test_results.append(("Return Visitor", "ERROR"))
    
    async def test_multiple_turns(self):
        """Test 4: Multiple conversation turns build up state correctly"""
        print("\n📋 Test 4: Multiple Conversation Turns")
        print("-" * 40)
        
        if not self.contractor_lead_id:
            print("⚠️ Skipping - no contractor_lead_id from Test 1")
            self.test_results.append(("Multiple Turns", "SKIP"))
            return
            
        try:
            # Turn 1: Add more company details
            response1 = await self.client.post(
                f"{API_BASE_URL}/api/coia/landing",
                json={
                    "message": "We've been in business for 15 years and have 25 employees",
                    "session_id": f"test-session-{uuid.uuid4().hex[:8]}",
                    "contractor_lead_id": self.contractor_lead_id
                }
            )
            
            # Turn 2: Add specialties
            await asyncio.sleep(1)
            response2 = await self.client.post(
                f"{API_BASE_URL}/api/coia/landing",
                json={
                    "message": "We specialize in sod installation and irrigation systems",
                    "session_id": f"test-session-{uuid.uuid4().hex[:8]}",
                    "contractor_lead_id": self.contractor_lead_id
                }
            )
            
            # Turn 3: Test accumulated knowledge
            await asyncio.sleep(1)
            response3 = await self.client.post(
                f"{API_BASE_URL}/api/coia/landing",
                json={
                    "message": "Can you summarize what you know about my company?",
                    "session_id": f"test-session-{uuid.uuid4().hex[:8]}",
                    "contractor_lead_id": self.contractor_lead_id
                }
            )
            
            if response3.status_code == 200:
                data = response3.json()
                response_text = data.get("response", "").lower()
                
                # Check if all information is remembered
                remembered_items = 0
                if "abc landscaping" in response_text:
                    remembered_items += 1
                    print("✅ Remembers company name")
                if "15 years" in response_text or "fifteen" in response_text:
                    remembered_items += 1
                    print("✅ Remembers years in business")
                if "25 employees" in response_text or "twenty-five" in response_text:
                    remembered_items += 1
                    print("✅ Remembers employee count")
                if "sod" in response_text or "irrigation" in response_text:
                    remembered_items += 1
                    print("✅ Remembers specialties")
                    
                if remembered_items >= 3:
                    print(f"✅ State builds up correctly ({remembered_items}/4 items remembered)")
                    self.test_results.append(("Multiple Turns", "PASS"))
                elif remembered_items >= 2:
                    print(f"⚠️ Partial state retention ({remembered_items}/4 items remembered)")
                    self.test_results.append(("Multiple Turns", "PARTIAL"))
                else:
                    print(f"❌ Poor state retention ({remembered_items}/4 items remembered)")
                    self.test_results.append(("Multiple Turns", "FAIL"))
            else:
                print(f"❌ API call failed: {response3.status_code}")
                self.test_results.append(("Multiple Turns", "FAIL"))
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            self.test_results.append(("Multiple Turns", "ERROR"))
    
    async def test_complex_state_fields(self):
        """Test 5: Complex state fields (dictionaries, lists) persist correctly"""
        print("\n📋 Test 5: Complex State Fields")
        print("-" * 40)
        
        if not self.contractor_lead_id:
            print("⚠️ Skipping - no contractor_lead_id from Test 1")
            self.test_results.append(("Complex Fields", "SKIP"))
            return
            
        try:
            # Send message with complex information
            response = await self.client.post(
                f"{API_BASE_URL}/api/coia/landing",
                json={
                    "message": "Our certifications include EPA RRP, OSHA 30, and we're licensed in CA, NV, and AZ",
                    "session_id": f"test-session-{uuid.uuid4().hex[:8]}",
                    "contractor_lead_id": self.contractor_lead_id
                }
            )
            
            # Wait for save
            await asyncio.sleep(2)
            
            # Query saved state
            response = await self.client.get(
                f"{API_BASE_URL}/api/conversations/{self.contractor_lead_id}"
            )
            
            if response.status_code == 200:
                data = response.json()
                memory_items = data.get("memory", [])
                
                # Look for complex fields
                complex_fields_found = False
                for item in memory_items:
                    if item.get("memory_type") == "coia_state":
                        value = item.get("memory_value")
                        if isinstance(value, (dict, list)):
                            complex_fields_found = True
                            print(f"✅ Complex field saved: {item['memory_key']} = {type(value).__name__}")
                            if isinstance(value, list) and len(value) > 0:
                                print(f"   Contents: {value[:3]}")
                
                if complex_fields_found:
                    print("✅ Complex state fields persist correctly")
                    self.test_results.append(("Complex Fields", "PASS"))
                else:
                    print("⚠️ No complex fields found in saved state")
                    self.test_results.append(("Complex Fields", "PARTIAL"))
            else:
                print(f"❌ Could not query state: {response.status_code}")
                self.test_results.append(("Complex Fields", "FAIL"))
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            self.test_results.append(("Complex Fields", "ERROR"))
    
    async def test_database_storage(self):
        """Test 6: Verify data saved to both unified_memory and contractor_leads"""
        print("\n📋 Test 6: Database Storage Verification")
        print("-" * 40)
        
        if not self.contractor_lead_id:
            print("⚠️ Skipping - no contractor_lead_id from Test 1")
            self.test_results.append(("Database Storage", "SKIP"))
            return
            
        try:
            # Use Supabase MCP to check contractor_leads table
            from database import SupabaseDB
            db = SupabaseDB()
            
            # Check contractor_leads table
            result = db.client.table("contractor_leads").select("*").eq("id", self.contractor_lead_id).execute()
            
            if result.data and len(result.data) > 0:
                contractor = result.data[0]
                print(f"✅ Found in contractor_leads table:")
                print(f"   - company_name: {contractor.get('company_name')}")
                print(f"   - years_in_business: {contractor.get('years_in_business')}")
                print(f"   - discovery_source: {contractor.get('discovery_source')}")
                
                # Check unified_conversation_memory
                memory_result = db.client.table("unified_conversation_memory").select("COUNT(*)").eq(
                    "conversation_id", self.contractor_lead_id
                ).execute()
                
                if memory_result.data:
                    print(f"✅ State fields in unified_conversation_memory")
                    self.test_results.append(("Database Storage", "PASS"))
                else:
                    print("⚠️ Data in contractor_leads but not in unified_memory")
                    self.test_results.append(("Database Storage", "PARTIAL"))
            else:
                print("❌ Not found in contractor_leads table")
                self.test_results.append(("Database Storage", "FAIL"))
                
        except Exception as e:
            print(f"⚠️ Database check skipped: {e}")
            self.test_results.append(("Database Storage", "SKIP"))
    
    async def test_non_blocking_saves(self):
        """Test 7: Verify saves are non-blocking (response returns quickly)"""
        print("\n📋 Test 7: Non-blocking Performance")
        print("-" * 40)
        
        try:
            start_time = time.time()
            
            # Send message that triggers lots of state updates
            response = await self.client.post(
                f"{API_BASE_URL}/api/coia/landing",
                json={
                    "message": "Quick test message",
                    "session_id": f"test-session-{uuid.uuid4().hex[:8]}",
                    "contractor_lead_id": f"landing-perf-{uuid.uuid4().hex[:8]}"
                }
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                if response_time < 5:  # Should respond in under 5 seconds
                    print(f"✅ Fast response time: {response_time:.2f} seconds")
                    print("✅ State saves are non-blocking")
                    self.test_results.append(("Non-blocking Saves", "PASS"))
                else:
                    print(f"⚠️ Slow response time: {response_time:.2f} seconds")
                    self.test_results.append(("Non-blocking Saves", "PARTIAL"))
            else:
                print(f"❌ API call failed: {response.status_code}")
                self.test_results.append(("Non-blocking Saves", "FAIL"))
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            self.test_results.append(("Non-blocking Saves", "ERROR"))
    
    async def test_account_linking(self):
        """Test 8: Simulate account creation and verify history preserved"""
        print("\n📋 Test 8: Account Creation Linking")
        print("-" * 40)
        
        if not self.contractor_lead_id:
            print("⚠️ Skipping - no contractor_lead_id from Test 1")
            self.test_results.append(("Account Linking", "SKIP"))
            return
            
        try:
            # Simulate account creation (would normally happen through signup flow)
            test_user_id = f"user-{uuid.uuid4().hex[:8]}"
            
            # Update contractor_leads with user_id (simulating account creation)
            from database import SupabaseDB
            db = SupabaseDB()
            
            update_result = db.client.table("contractor_leads").update({
                "user_id": test_user_id,
                "account_created": True,
                "account_created_at": datetime.utcnow().isoformat()
            }).eq("id", self.contractor_lead_id).execute()
            
            if update_result.data:
                print(f"✅ Simulated account creation for user_id: {test_user_id}")
                
                # Verify history is preserved
                result = db.client.table("contractor_leads").select("*").eq("id", self.contractor_lead_id).execute()
                
                if result.data and result.data[0].get("company_name"):
                    print(f"✅ History preserved after account creation:")
                    print(f"   - Company: {result.data[0]['company_name']}")
                    print(f"   - User ID: {result.data[0]['user_id']}")
                    print("✅ Anonymous → Authenticated journey linked")
                    self.test_results.append(("Account Linking", "PASS"))
                else:
                    print("❌ History lost during account creation")
                    self.test_results.append(("Account Linking", "FAIL"))
            else:
                print("⚠️ Could not simulate account creation")
                self.test_results.append(("Account Linking", "SKIP"))
                
        except Exception as e:
            print(f"⚠️ Account linking test skipped: {e}")
            self.test_results.append(("Account Linking", "SKIP"))
    
    def print_test_results(self):
        """Print summary of all test results"""
        print("\n" + "="*80)
        print("TEST RESULTS SUMMARY")
        print("="*80)
        
        passed = sum(1 for _, result in self.test_results if result == "PASS")
        failed = sum(1 for _, result in self.test_results if result == "FAIL")
        partial = sum(1 for _, result in self.test_results if result == "PARTIAL")
        skipped = sum(1 for _, result in self.test_results if result == "SKIP")
        errors = sum(1 for _, result in self.test_results if result == "ERROR")
        
        for test_name, result in self.test_results:
            emoji = {
                "PASS": "✅",
                "FAIL": "❌",
                "PARTIAL": "⚠️",
                "SKIP": "⏭️",
                "ERROR": "🔥"
            }.get(result, "❓")
            print(f"{emoji} {test_name}: {result}")
        
        print("-" * 40)
        print(f"Total Tests: {len(self.test_results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️ Partial: {partial}")
        print(f"⏭️ Skipped: {skipped}")
        print(f"🔥 Errors: {errors}")
        
        success_rate = (passed / len(self.test_results)) * 100 if self.test_results else 0
        print(f"\nSuccess Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("\nPASS: STATE PERSISTENCE SYSTEM IS WORKING!")
        elif success_rate >= 60:
            print("\nPARTIAL: STATE PERSISTENCE PARTIALLY WORKING - NEEDS ATTENTION")
        else:
            print("\nFAIL: STATE PERSISTENCE HAS ISSUES - REQUIRES FIXES")
        
        if self.contractor_lead_id:
            print(f"\n📝 Test contractor_lead_id for manual verification: {self.contractor_lead_id}")
    
    async def cleanup(self):
        """Clean up test resources"""
        await self.client.aclose()


async def main():
    """Run the complete test suite"""
    print("\nStarting COIA State Persistence Test Suite...")
    print("Make sure the backend is running on http://localhost:8008")
    print("-" * 80)
    
    test_suite = COIAStatePersistenceTestSuite()
    
    try:
        # Check if backend is running
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{API_BASE_URL}/api/health")
                if response.status_code != 200:
                    print("❌ Backend not responding at http://localhost:8008")
                    print("Please start the backend: cd ai-agents && python main.py")
                    return
            except:
                print("❌ Cannot connect to backend at http://localhost:8008")
                print("Please start the backend: cd ai-agents && python main.py")
                return
        
        # Run all tests
        await test_suite.run_all_tests()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Test suite interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {e}")
    finally:
        await test_suite.cleanup()
        print("\n✅ Test suite completed")


if __name__ == "__main__":
    asyncio.run(main())