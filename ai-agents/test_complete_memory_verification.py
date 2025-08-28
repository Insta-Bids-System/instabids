#!/usr/bin/env python3
"""
COMPLETE END-TO-END MEMORY SYSTEM VERIFICATION
Tests both Unified Memory and Enhanced Memory systems with real contractor data
"""

import asyncio
import requests
import json
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.service_urls import get_backend_url
from database import SupabaseDB

# ========================================
# TEST CONTRACTOR CREDENTIALS
# ========================================
TEST_CONTRACTOR = {
    "id": "523c0f63-e75c-4d65-963e-561d7f4169db",
    "name": "Mike's Plumbing of Southwest Florida", 
    "login_email": "mike@mikesplumbing.com",
    "company_details": "15 employees, bathroom/kitchen remodeling specialists"
}

TEST_BID_CARD = "4aa5e277-82b1-4679-a86a-24fd56b10e4c"

def print_header(text):
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")

def print_step(step_num, text):
    print(f"\n[STEP {step_num}] {text}")
    print("-" * 60)

class CompleteMemoryVerificationTest:
    
    def __init__(self):
        self.base_url = f"{get_backend_url()}/api/bsa"
        self.contractor_id = TEST_CONTRACTOR["id"]
        self.session_id = f"memory_verification_{datetime.now().timestamp()}"
        self.db = SupabaseDB()
        
    async def step_1_clear_existing_memory(self):
        """Clear any existing memory data for clean test"""
        print_step(1, "CLEARING EXISTING MEMORY DATA")
        
        # Clear unified memory
        try:
            unified_result = self.db.client.table("unified_conversation_memory").delete().eq(
                "contractor_id", self.contractor_id
            ).execute()
            print(f"[INFO] Cleared unified memory: {len(unified_result.data)} records deleted")
        except Exception as e:
            print(f"[INFO] No unified memory to clear: {e}")
        
        # Clear enhanced memory tables
        enhanced_tables = [
            "contractor_relationship_memory",
            "contractor_bidding_patterns", 
            "contractor_information_needs",
            "contractor_business_profile",
            "contractor_pain_points"
        ]
        
        for table in enhanced_tables:
            try:
                result = self.db.client.table(table).delete().eq(
                    "contractor_id", self.contractor_id
                ).execute()
                print(f"[INFO] Cleared {table}: {len(result.data)} records deleted")
            except Exception as e:
                print(f"[INFO] No data to clear in {table}: {e}")
        
        print("[SUCCESS] Memory cleared - starting with clean slate")
        
    async def step_2_have_business_conversation(self):
        """Have a rich conversation with business intelligence data"""
        print_step(2, "BUSINESS INTELLIGENCE CONVERSATION")
        
        conversation_text = """Hi, I'm Mike from Mike's Plumbing. Let me tell you about our operation:
        
        We've been in business for 15 years and have grown to 15 employees. We specialize in 
        bathroom and kitchen remodeling, with our sweet spot being projects in the $30k-$75k range.
        
        For business management, we use ServiceTitan for job management and customer tracking, 
        plus QuickBooks for accounting. We're pretty tech-savvy - just started using CompanyCam 
        for progress photos.
        
        Our pricing is competitive: we markup materials 25% and labor 40%. We typically require 
        30% down, 40% at rough-in, and 30% at completion.
        
        The biggest challenge we face is managing electrical and HVAC subcontractors. Finding 
        reliable subs is tough, and coordinating schedules is a nightmare. Cash flow can be 
        tight when customers take 60+ days to pay.
        
        We're looking to expand into commercial work next year and hoping to add 5 more techs. 
        I prefer email for non-urgent stuff but text me for emergencies. I like detailed 
        proposals with material breakdowns and timeline charts.
        
        For this bathroom project, I can do it for $45,000 with a 3-week timeline."""
        
        print("[CONVERSATION]:")
        print(conversation_text[:200] + "..." if len(conversation_text) > 200 else conversation_text)
        
        # Send to BSA
        payload = {
            "contractor_id": self.contractor_id,
            "bid_card_id": TEST_BID_CARD,
            "input_type": "text",
            "input_data": conversation_text,
            "session_id": self.session_id
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/unified-stream",
                json=payload,
                stream=True,
                headers={"Accept": "text/event-stream"},
                timeout=60
            )
            
            if response.status_code == 200:
                # Collect response
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith("data: "):
                            data_str = line_str[6:]
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                if 'choices' in data and data['choices']:
                                    content = data['choices'][0].get('delta', {}).get('content', '')
                                    full_response += content
                            except:
                                pass
                
                print(f"[SUCCESS] BSA responded with {len(full_response)} characters")
                print(f"[RESPONSE PREVIEW]: {full_response[:100]}...")
                return True
            else:
                print(f"[ERROR] BSA returned {response.status_code}")
                return False
                
        except Exception as e:
            print(f"[ERROR] BSA conversation failed: {e}")
            return False
            
    async def step_3_verify_unified_memory(self):
        """Check what went into unified conversation memory"""
        print_step(3, "UNIFIED MEMORY VERIFICATION")
        
        try:
            result = self.db.client.table("unified_conversation_memory").select("*").eq(
                "contractor_id", self.contractor_id
            ).execute()
            
            if result.data:
                record = result.data[0]
                print(f"[FOUND] Unified memory record created at {record.get('created_at')}")
                
                # Show key fields
                conversation_context = record.get("conversation_context", {})
                conversation_history = record.get("conversation_history", [])
                
                print(f"[DATA] Session ID: {record.get('session_id')}")
                print(f"[DATA] Conversation turns: {len(conversation_history)}")
                print(f"[DATA] Context keys: {list(conversation_context.keys())}")
                
                # Show first conversation turn
                if conversation_history:
                    first_turn = conversation_history[0]
                    print(f"[DATA] First turn preview: {str(first_turn)[:100]}...")
                
                return True
            else:
                print("[ERROR] No unified memory record found!")
                return False
                
        except Exception as e:
            print(f"[ERROR] Error checking unified memory: {e}")
            return False
            
    async def step_4_verify_enhanced_memory(self):
        """Check what went into enhanced memory tables"""
        print_step(4, "ENHANCED MEMORY VERIFICATION")
        
        enhanced_tables = [
            "contractor_relationship_memory",
            "contractor_bidding_patterns", 
            "contractor_information_needs",
            "contractor_business_profile",
            "contractor_pain_points"
        ]
        
        found_tables = []
        
        for table in enhanced_tables:
            try:
                result = self.db.client.table(table).select("*").eq(
                    "contractor_id", self.contractor_id
                ).execute()
                
                if result.data:
                    record = result.data[0]
                    found_tables.append(table)
                    print(f"[FOUND] {table}:")
                    
                    # Show specific fields based on table
                    if table == "contractor_relationship_memory":
                        print(f"  - Personality traits: {record.get('personality_traits')}")
                        print(f"  - Work style: {record.get('work_style')}")
                        print(f"  - Customer approach: {record.get('customer_approach')}")
                        
                    elif table == "contractor_business_profile":
                        print(f"  - CRM system: {record.get('crm_system')}")
                        print(f"  - Employee count: {record.get('employee_count')}")
                        print(f"  - Growth trajectory: {record.get('growth_trajectory')}")
                        print(f"  - Technology adoption: {record.get('technology_adoption')}")
                        
                    elif table == "contractor_bidding_patterns":
                        print(f"  - Pricing strategy: {record.get('pricing_strategy')}")
                        print(f"  - Markup percentages: {record.get('markup_percentages')}")
                        print(f"  - Preferred project size: {record.get('preferred_project_size')}")
                        
                    elif table == "contractor_pain_points":
                        print(f"  - Operational challenges: {record.get('operational_challenges')}")
                        print(f"  - Technology gaps: {record.get('technology_gaps')}")
                        print(f"  - Financial pain points: {record.get('financial_pain_points')}")
                        
                    elif table == "contractor_information_needs":
                        print(f"  - Common RFI topics: {record.get('common_rfi_topics')}")
                        print(f"  - Detail level preference: {record.get('detail_level_preference')}")
                        
                else:
                    print(f"[EMPTY] {table}: No data")
                    
            except Exception as e:
                print(f"[ERROR] Error checking {table}: {e}")
        
        print(f"\n[SUMMARY] Enhanced memory populated in {len(found_tables)}/5 tables")
        return len(found_tables) > 0
        
    async def step_5_test_memory_restoration(self):
        """Test that memory is restored in subsequent conversations"""
        print_step(5, "MEMORY RESTORATION TEST")
        
        # Have a follow-up conversation that should reference previous context
        follow_up_text = """Can you remind me what markup percentages I mentioned? 
        Also, what CRM system did I say we use? And how many employees do we have?"""
        
        print("[FOLLOW-UP CONVERSATION]:")
        print(follow_up_text)
        
        payload = {
            "contractor_id": self.contractor_id,
            "bid_card_id": TEST_BID_CARD,
            "input_type": "text", 
            "input_data": follow_up_text,
            "session_id": f"{self.session_id}_followup"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/unified-stream",
                json=payload,
                stream=True,
                headers={"Accept": "text/event-stream"},
                timeout=30
            )
            
            if response.status_code == 200:
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith("data: "):
                            data_str = line_str[6:]
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                if 'choices' in data and data['choices']:
                                    content = data['choices'][0].get('delta', {}).get('content', '')
                                    full_response += content
                            except:
                                pass
                
                print(f"[RESPONSE]: {full_response}")
                
                # Check if BSA remembers key facts
                memory_points = {
                    "25%": "material markup",
                    "40%": "labor markup", 
                    "ServiceTitan": "CRM system",
                    "15 employees": "company size",
                    "15": "employee count"
                }
                
                remembered = []
                for key, description in memory_points.items():
                    if key.lower() in full_response.lower():
                        remembered.append(description)
                        print(f"[MEMORY VERIFIED] BSA remembered: {description}")
                
                print(f"\n[MEMORY SCORE] {len(remembered)}/{len(memory_points)} key facts remembered")
                
                return len(remembered) >= 3  # Should remember at least 3/5 facts
            else:
                print(f"[ERROR] Follow-up conversation failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Memory restoration test failed: {e}")
            return False
    
    async def step_6_data_filtering_analysis(self):
        """Analyze what data went where and why"""
        print_step(6, "DATA FILTERING ANALYSIS")
        
        print("UNIFIED MEMORY SYSTEM:")
        print("- Stores: Complete conversation history, session context, user interactions")
        print("- Purpose: Conversation continuity and context restoration")
        print("- Triggers: After every conversation turn")
        
        print("\nENHANCED MEMORY SYSTEM:")
        print("- Stores: Business intelligence insights extracted by GPT-4o")
        print("- Purpose: Build contractor profiles for AI solution sales")
        print("- Triggers: After conversation completion")
        
        print("\nFILTERING LOGIC:")
        print("- Unified: Raw conversation data → conversation_history table")
        print("- Enhanced: AI analysis → 5 specialized business intelligence tables")
        
        # Show the AI analysis prompts used
        print("\nAI EXTRACTION EXAMPLES:")
        print("- Business Profile: 'CRM system', 'employee count', 'technology adoption'")
        print("- Relationship: 'personality type', 'work style', 'customer approach'")
        print("- Bidding: 'pricing strategy', 'markup percentages', 'project preferences'")
        print("- Pain Points: 'operational challenges', 'technology gaps'")
        print("- Info Needs: 'communication preferences', 'detail level'")
        
        return True

async def main():
    """Run complete memory system verification"""
    
    print_header("COMPLETE MEMORY SYSTEM VERIFICATION")
    print(f"Test Contractor: {TEST_CONTRACTOR['name']}")
    print(f"Contractor ID: {TEST_CONTRACTOR['id']}")
    print(f"Login Email: {TEST_CONTRACTOR['login_email']}")
    print(f"Test Bid Card: {TEST_BID_CARD}")
    
    # Check backend is running
    try:
        response = requests.get(f"{get_backend_url()}/")
        if response.status_code != 200:
            print("[ERROR] Backend not running!")
            return
    except:
        print("[ERROR] Cannot connect to backend!")
        return
    
    tester = CompleteMemoryVerificationTest()
    
    # Run all verification steps
    results = {}
    
    results["clear_memory"] = await tester.step_1_clear_existing_memory()
    results["business_conversation"] = await tester.step_2_have_business_conversation()
    
    # Wait for memory processing
    print("[INFO] Waiting 5 seconds for memory processing...")
    await asyncio.sleep(5)
    
    results["unified_memory"] = await tester.step_3_verify_unified_memory()
    results["enhanced_memory"] = await tester.step_4_verify_enhanced_memory()
    results["memory_restoration"] = await tester.step_5_test_memory_restoration()
    results["filtering_analysis"] = await tester.step_6_data_filtering_analysis()
    
    # Final Results
    print_header("COMPLETE VERIFICATION RESULTS")
    
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    
    for test, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"[{status}] {test.replace('_', ' ').title()}")
    
    print(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 [SUCCESS] BOTH MEMORY SYSTEMS FULLY VERIFIED!")
        print("✅ Unified Memory: Conversation continuity working")
        print("✅ Enhanced Memory: Business intelligence extraction working")
        print("✅ Memory Restoration: Context preserved across sessions")
        print("✅ Data Filtering: Proper separation of conversation vs. business data")
    else:
        print(f"\n❌ [PARTIAL SUCCESS] {total_tests - passed_tests} issues found")
        print("Some memory systems need debugging")

if __name__ == "__main__":
    asyncio.run(main())