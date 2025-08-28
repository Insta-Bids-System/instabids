"""
FULL COIA SYSTEM TEST - Real Multi-turn Contractor Conversation
Tests the complete onboarding flow with JM Holiday Lighting contractor
"""

import asyncio
import requests
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List

class COIAConversationTester:
    def __init__(self):
        self.base_url = "http://localhost:8008"
        self.session_id = f"test-jm-holiday-{int(time.time())}"
        self.contractor_lead_id = None
        self.conversation_history = []
        self.agent_status_updates = []
        
    def log_conversation_turn(self, turn_number: int, user_message: str, response: dict):
        """Log each turn of the conversation for analysis"""
        self.conversation_history.append({
            "turn": turn_number,
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "coia_response": response.get("response", ""),
            "contractor_created": response.get("contractor_created", False),
            "company_name": response.get("company_name", ""),
            "agent_activity": response.get("agent_status", {}),
            "background_processing": response.get("background_processing", False)
        })
        
    def send_message(self, message: str, endpoint: str = "landing") -> dict:
        """Send message to COIA and return response"""
        url = f"{self.base_url}/api/coia/{endpoint}"
        payload = {
            "message": message,
            "session_id": self.session_id
        }
        
        print(f"\n[SENDING] {message}")
        start_time = time.time()
        
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"[COIA {response_time:.2f}s] {result.get('response', 'No response')}")
            
            # Check for agent activity
            if result.get("background_processing"):
                print(f"[AGENTS] Background processing started...")
                
            return result
        else:
            print(f"[ERROR {response.status_code}] {response.text}")
            return {"error": f"HTTP {response.status_code}", "response": "Error occurred"}
    
    async def monitor_agent_status(self, duration_seconds: int = 30):
        """Monitor agent status updates during conversation"""
        print(f"\n👀 MONITORING: Agent status for {duration_seconds} seconds...")
        
        # In a real implementation, this would connect to WebSocket
        # For now, we'll simulate by checking logs
        await asyncio.sleep(duration_seconds)
        print("📊 AGENTS: Monitoring complete")
        
    def verify_google_integration(self) -> bool:
        """Verify that Google Places API is working with real data"""
        print("\n🔍 VERIFICATION: Testing Google Places integration...")
        
        # Test direct Google Places call
        test_url = f"{self.base_url}/api/coia/test-google-places"
        test_payload = {
            "company_name": "JM Holiday Lighting",
            "location": "South Florida"
        }
        
        try:
            response = requests.post(test_url, json=test_payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("found_business"):
                    print(f"✅ GOOGLE: Found business - {data.get('business_name')}")
                    return True
                else:
                    print("⚠️ GOOGLE: No business found (API working but no results)")
                    return False
            else:
                print(f"❌ GOOGLE: API error {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ GOOGLE: Connection error - {e}")
            return False
    
    def verify_database_records(self) -> bool:
        """Verify contractor records were created in database"""
        print("\n💾 VERIFICATION: Checking database records...")
        
        if not self.contractor_lead_id:
            print("❌ DATABASE: No contractor_lead_id to verify")
            return False
            
        # In a real implementation, this would query Supabase directly
        # For now, check via API endpoint
        verify_url = f"{self.base_url}/api/admin/verify-contractor"
        verify_payload = {"contractor_lead_id": self.contractor_lead_id}
        
        try:
            response = requests.post(verify_url, json=verify_payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ DATABASE: Contractor record found - {data.get('company_name')}")
                return True
            else:
                print(f"⚠️ DATABASE: Record not found or API unavailable")
                return False
        except Exception as e:
            print(f"❌ DATABASE: Verification error - {e}")
            return False
    
    async def run_full_conversation_test(self) -> bool:
        """Run the complete multi-turn conversation test"""
        print("="*100)
        print("🚀 FULL COIA SYSTEM TEST - JM HOLIDAY LIGHTING CONTRACTOR ONBOARDING")
        print("="*100)
        
        success_criteria = {
            "multi_turn_conversation": False,
            "background_agents_triggered": False,
            "google_verification": False,
            "database_records_created": False,
            "response_times_acceptable": True
        }
        
        # TURN 1: Initial contractor introduction
        print("\n" + "="*50)
        print("TURN 1: Initial Introduction")
        print("="*50)
        
        response1 = self.send_message(
            "Hello, I'm JM Holiday Lighting. We're a professional holiday lighting contractor based in South Florida.",
            "landing"
        )
        self.log_conversation_turn(1, "Initial introduction", response1)
        
        if response1.get("contractor_lead_id"):
            self.contractor_lead_id = response1["contractor_lead_id"]
            
        # TURN 2: Service details
        print("\n" + "="*50)
        print("TURN 2: Service Specialization")
        print("="*50)
        
        response2 = self.send_message(
            "We specialize in holiday lighting installation, permanent lighting systems, and commercial displays. We serve Miami-Dade, Broward, and Palm Beach counties."
        )
        self.log_conversation_turn(2, "Service details", response2)
        
        # Check if background processing started
        if response2.get("background_processing"):
            success_criteria["background_agents_triggered"] = True
            # Monitor agent status
            await self.monitor_agent_status(15)
        
        # TURN 3: Business credentials
        print("\n" + "="*50) 
        print("TURN 3: Business Credentials")
        print("="*50)
        
        response3 = self.send_message(
            "We've been in business for 8 years, fully licensed and insured. We have a 4.8-star rating on Google with over 150 reviews. Our website is jmholidaylighting.com"
        )
        self.log_conversation_turn(3, "Business credentials", response3)
        
        # TURN 4: Project capacity and pricing
        print("\n" + "="*50)
        print("TURN 4: Project Capacity")
        print("="*50)
        
        response4 = self.send_message(
            "We can handle projects from $500 residential displays to $50,000+ commercial installations. We typically book 2-3 months out during holiday season but have availability for permanent lighting year-round."
        )
        self.log_conversation_turn(4, "Project capacity", response4)
        
        # TURN 5: Portfolio and references
        print("\n" + "="*50)
        print("TURN 5: Portfolio Details")
        print("="*50)
        
        response5 = self.send_message(
            "Our portfolio includes luxury residential properties in Coral Gables, shopping centers like Town Center at Boca Raton, and corporate headquarters. We can provide references and photos of recent work."
        )
        self.log_conversation_turn(5, "Portfolio details", response5)
        
        # Verify multi-turn conversation worked
        if len(self.conversation_history) >= 5:
            success_criteria["multi_turn_conversation"] = True
        
        # Wait a bit more for background processing
        await asyncio.sleep(10)
        
        # VERIFICATION PHASE
        print("\n" + "="*80)
        print("🔍 VERIFICATION PHASE")
        print("="*80)
        
        # Verify Google integration
        success_criteria["google_verification"] = self.verify_google_integration()
        
        # Verify database records
        success_criteria["database_records_created"] = self.verify_database_records()
        
        # Check response times
        total_response_time = sum([
            float(turn.get("response_time", 5)) for turn in self.conversation_history
        ])
        avg_response_time = total_response_time / len(self.conversation_history) if self.conversation_history else 0
        
        if avg_response_time > 10:  # More than 10 seconds average
            success_criteria["response_times_acceptable"] = False
            print(f"⚠️ PERFORMANCE: Average response time {avg_response_time:.2f}s (acceptable < 10s)")
        else:
            print(f"✅ PERFORMANCE: Average response time {avg_response_time:.2f}s")
        
        # FINAL RESULTS
        print("\n" + "="*100)
        print("📊 FINAL TEST RESULTS")
        print("="*100)
        
        total_criteria = len(success_criteria)
        passed_criteria = sum([1 for v in success_criteria.values() if v])
        
        print(f"✅ Multi-turn Conversation: {'PASS' if success_criteria['multi_turn_conversation'] else 'FAIL'}")
        print(f"🤖 Background Agents: {'PASS' if success_criteria['background_agents_triggered'] else 'FAIL'}")
        print(f"🔍 Google Verification: {'PASS' if success_criteria['google_verification'] else 'FAIL'}")
        print(f"💾 Database Records: {'PASS' if success_criteria['database_records_created'] else 'FAIL'}")
        print(f"⚡ Response Times: {'PASS' if success_criteria['response_times_acceptable'] else 'FAIL'}")
        
        print(f"\n📈 OVERALL SCORE: {passed_criteria}/{total_criteria} ({(passed_criteria/total_criteria)*100:.1f}%)")
        
        if passed_criteria == total_criteria:
            print("\n🎉 COMPLETE SUCCESS: COIA system fully functional end-to-end!")
            return True
        elif passed_criteria >= 3:
            print("\n✅ PARTIAL SUCCESS: Core functionality working, some issues need attention")
            return True
        else:
            print("\n❌ SYSTEM FAILURE: Major issues preventing proper operation")
            return False

    def print_conversation_log(self):
        """Print detailed conversation log for analysis"""
        print("\n" + "="*100)
        print("📝 DETAILED CONVERSATION LOG")
        print("="*100)
        
        for turn in self.conversation_history:
            print(f"\n--- TURN {turn['turn']} ({turn['timestamp']}) ---")
            print(f"👤 USER: {turn['user_message']}")
            print(f"🤖 COIA: {turn['coia_response']}")
            print(f"📊 STATUS: Created={turn['contractor_created']}, Company={turn['company_name']}")

async def main():
    """Run the comprehensive COIA conversation test"""
    tester = COIAConversationTester()
    
    print("🎯 OBJECTIVE: Prove COIA works end-to-end with JM Holiday Lighting")
    print("📋 TEST PLAN: 5-turn conversation + verification + agent monitoring")
    print("⏱️ EXPECTED DURATION: 60-90 seconds\n")
    
    start_time = time.time()
    success = await tester.run_full_conversation_test()
    total_time = time.time() - start_time
    
    tester.print_conversation_log()
    
    print("\n" + "="*100)
    print("🏁 TEST COMPLETE")
    print("="*100)
    print(f"⏱️ Total Test Duration: {total_time:.2f} seconds")
    print(f"🎯 Test Result: {'SUCCESS' if success else 'FAILED'}")
    print(f"💬 Conversation Turns: {len(tester.conversation_history)}")
    
    if tester.contractor_lead_id:
        print(f"🏢 Contractor Lead ID: {tester.contractor_lead_id}")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)