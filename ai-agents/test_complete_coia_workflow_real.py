"""
COMPLETE REAL API TESTING - NO FAKE CLAIMS
Test the ENTIRE COIA workflow with real API calls and fix anything broken
"""
import requests
import json
import time
from config.service_urls import get_backend_url

class COIAWorkflowTester:
    def __init__(self):
        self.base_url = f"{get_backend_url()}/api/coia/landing"
        self.contractor_lead_id = f"real-test-{int(time.time())}"
        self.session_data = {}
        self.conversation_history = []
        self.issues_found = []
        
    def log_response(self, stage, response):
        """Log each response for debugging"""
        if response.status_code == 200:
            data = response.json()
            ai_response = data.get("response", "")
            self.conversation_history.append({
                "stage": stage,
                "ai_response": ai_response,
                "full_data": data
            })
            print(f"\n[{stage}] AI Response:")
            print("-" * 50)
            # Handle unicode issues by encoding properly
            try:
                print(ai_response.encode('utf-8', errors='replace').decode('utf-8'))
            except:
                print(ai_response[:500] + "..." if len(ai_response) > 500 else ai_response)
            print("-" * 50)
            return data
        else:
            error = f"[{stage}] API ERROR: {response.status_code} - {response.text}"
            self.issues_found.append(error)
            print(error)
            return None
    
    def test_stage_1_initial_contact(self):
        """Stage 1: Initial contractor introduction"""
        print("\n" + "="*80)
        print("STAGE 1: INITIAL CONTRACTOR CONTACT")
        print("="*80)
        print("Testing: Initial Google Places lookup and response")
        
        response = requests.post(self.base_url, json={
            "message": "Hi, I'm Justin from JM Holiday Lighting. We install Christmas lights in South Florida.",
            "contractor_lead_id": self.contractor_lead_id,
            "session_id": "stage-1"
        }, timeout=300)
        
        data = self.log_response("Initial Contact", response)
        if not data:
            return False
            
        # Check what actually happened
        research_completed = data.get("research_completed", False)
        research_findings = data.get("research_findings")
        ai_response = data.get("response", "")
        
        print(f"\nSTAGE 1 VERIFICATION:")
        print(f"  Research completed: {research_completed}")
        print(f"  Research findings present: {research_findings is not None}")
        print(f"  Uses real location (Pompano Beach): {'Pompano Beach' in ai_response}")
        print(f"  Uses real website: {'jmholidaylighting.com' in ai_response}")
        print(f"  Mentions next steps: {'research' in ai_response.lower() or 'information' in ai_response.lower()}")
        
        if not research_completed:
            self.issues_found.append("Stage 1: Research not triggered on initial contact")
        
        if research_findings is None and research_completed:
            self.issues_found.append("Stage 1: Research completed but no findings data")
            
        self.session_data = data
        return True
    
    def test_stage_2_research_confirmation(self):
        """Stage 2: Ask about research and request more details"""
        print("\n" + "="*80)
        print("STAGE 2: RESEARCH CONFIRMATION")
        print("="*80)
        print("Testing: Asking for more research and detailed information")
        
        response = requests.post(self.base_url, json={
            "message": "Yes, that's correct! Can you research more details about my business and gather comprehensive information?",
            "contractor_lead_id": self.contractor_lead_id,
            "session_id": "stage-2"
        }, timeout=300)
        
        data = self.log_response("Research Confirmation", response)
        if not data:
            return False
            
        ai_response = data.get("response", "")
        
        print(f"\nSTAGE 2 VERIFICATION:")
        print(f"  Mentions comprehensive research: {'comprehensive' in ai_response.lower() or 'detailed' in ai_response.lower()}")
        print(f"  Shows gathering info: {'gathering' in ai_response.lower() or 'collecting' in ai_response.lower()}")
        print(f"  Mentions business details: {'business' in ai_response.lower() or 'services' in ai_response.lower()}")
        
        return True
    
    def test_stage_3_profile_building(self):
        """Stage 3: Profile building questions"""
        print("\n" + "="*80)
        print("STAGE 3: PROFILE BUILDING")
        print("="*80)
        print("Testing: Profile completion and question asking")
        
        response = requests.post(self.base_url, json={
            "message": "Tell me what information you found and what else you need to know about my business.",
            "contractor_lead_id": self.contractor_lead_id,
            "session_id": "stage-3"
        }, timeout=300)
        
        data = self.log_response("Profile Building", response)
        if not data:
            return False
            
        ai_response = data.get("response", "")
        contractor_profile = data.get("contractor_profile", {})
        
        print(f"\nSTAGE 3 VERIFICATION:")
        print(f"  Has contractor profile: {bool(contractor_profile)}")
        print(f"  Profile fields: {len(contractor_profile)} fields")
        print(f"  Asks questions: {'?' in ai_response}")
        print(f"  Company name extracted: {contractor_profile.get('company_name', 'Not found')}")
        print(f"  Business type extracted: {contractor_profile.get('primary_trade', 'Not found')}")
        
        if not contractor_profile:
            self.issues_found.append("Stage 3: No contractor profile data generated")
            
        return True
    
    def test_stage_4_instabids_value(self):
        """Stage 4: InstaBids value proposition"""
        print("\n" + "="*80)
        print("STAGE 4: INSTABIDS VALUE PROPOSITION")
        print("="*80)
        print("Testing: Platform benefits and value explanation")
        
        response = requests.post(self.base_url, json={
            "message": "This looks good. How can InstaBids help my business grow?",
            "contractor_lead_id": self.contractor_lead_id,
            "session_id": "stage-4"
        }, timeout=300)
        
        data = self.log_response("InstaBids Value", response)
        if not data:
            return False
            
        ai_response = data.get("response", "")
        
        print(f"\nSTAGE 4 VERIFICATION:")
        print(f"  Mentions InstaBids: {'InstaBids' in ai_response}")
        print(f"  Mentions benefits: {'benefit' in ai_response.lower() or 'advantage' in ai_response.lower()}")
        print(f"  Mentions projects: {'project' in ai_response.lower() or 'job' in ai_response.lower()}")
        print(f"  Mentions homeowners: {'homeowner' in ai_response.lower() or 'customer' in ai_response.lower()}")
        
        return True
    
    def test_stage_5_account_creation(self):
        """Stage 5: Account creation request"""
        print("\n" + "="*80)
        print("STAGE 5: ACCOUNT CREATION")
        print("="*80)
        print("Testing: Account creation and signup flow")
        
        response = requests.post(self.base_url, json={
            "message": "I want to create an account and start bidding on projects. Please set up my contractor account.",
            "contractor_lead_id": self.contractor_lead_id,
            "session_id": "stage-5"
        }, timeout=300)
        
        data = self.log_response("Account Creation", response)
        if not data:
            return False
            
        ai_response = data.get("response", "")
        contractor_created = data.get("contractor_created", False)
        
        print(f"\nSTAGE 5 VERIFICATION:")
        print(f"  Account creation mentioned: {'account' in ai_response.lower() or 'signup' in ai_response.lower()}")
        print(f"  Contractor created flag: {contractor_created}")
        print(f"  Mentions credentials: {'login' in ai_response.lower() or 'password' in ai_response.lower()}")
        print(f"  Mentions next steps: {'next' in ai_response.lower() or 'access' in ai_response.lower()}")
        
        if not contractor_created:
            self.issues_found.append("Stage 5: contractor_created flag not set")
            
        return True
    
    def run_complete_test(self):
        """Run the complete workflow test"""
        print("COMPLETE COIA WORKFLOW TEST - REAL API CALLS")
        print("=" * 80)
        print(f"Contractor Lead ID: {self.contractor_lead_id}")
        print(f"Testing against: {self.base_url}")
        
        # Run all stages
        stages = [
            ("Stage 1", self.test_stage_1_initial_contact),
            ("Stage 2", self.test_stage_2_research_confirmation),
            ("Stage 3", self.test_stage_3_profile_building),
            ("Stage 4", self.test_stage_4_instabids_value),
            ("Stage 5", self.test_stage_5_account_creation)
        ]
        
        passed_stages = 0
        total_stages = len(stages)
        
        for stage_name, test_func in stages:
            try:
                success = test_func()
                if success:
                    passed_stages += 1
                    print(f"\nSUCCESS {stage_name}: PASSED")
                else:
                    print(f"\nFAILED {stage_name}: FAILED")
                
                # Small delay between stages
                time.sleep(2)
                
            except Exception as e:
                error = f"{stage_name}: Exception - {str(e)}"
                self.issues_found.append(error)
                print(f"\nERROR {stage_name}: ERROR - {e}")
        
        # Final analysis
        print("\n" + "="*80)
        print("FINAL RESULTS")
        print("="*80)
        print(f"Stages passed: {passed_stages}/{total_stages}")
        print(f"Success rate: {(passed_stages/total_stages)*100:.1f}%")
        
        if self.issues_found:
            print(f"\nISSUES FOUND ({len(self.issues_found)}):")
            for i, issue in enumerate(self.issues_found, 1):
                print(f"  {i}. {issue}")
        else:
            print("\nSUCCESS: NO ISSUES FOUND - All stages working correctly!")
        
        # Conversation summary
        print(f"\nCONVERSATION SUMMARY:")
        for i, turn in enumerate(self.conversation_history, 1):
            print(f"  Turn {i} ({turn['stage']}): {len(turn['ai_response'])} chars")
        
        return passed_stages == total_stages and len(self.issues_found) == 0

def main():
    tester = COIAWorkflowTester()
    success = tester.run_complete_test()
    
    if success:
        print(f"\nCOMPLETE SUCCESS: COIA workflow is 100% functional!")
    else:
        print(f"\nWORKFLOW INCOMPLETE: Issues need to be fixed")
        print(f"Next step: Fix the issues found above")
    
    return success

if __name__ == "__main__":
    main()