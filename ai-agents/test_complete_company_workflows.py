"""
Complete Company Workflows Test
Tests both JM Holiday Lighting and TurfGrass Artificial Solutions
"""

import asyncio
import requests
import time
import json
from config.service_urls import get_backend_url

class CompanyWorkflowTest:
    def __init__(self, company_info):
        self.company_info = company_info
        self.session_id = f"{company_info['name'].lower().replace(' ', '-')}-test"
        self.account_data = None
        
    async def test_complete_workflow(self):
        """Test the complete contractor onboarding workflow"""
        print(f"\n{'='*80}")
        print(f"[CHRISTMAS TREE] TESTING {self.company_info['name'].upper()} WORKFLOW [CHRISTMAS TREE]")
        print(f"{'='*80}")
        
        results = {}
        
        # Step 1: Introduction
        results['intro'] = await self.test_introduction()
        
        # Step 2: Business details
        if results['intro']:
            results['details'] = await self.test_business_details()
        
        # Step 3: Account creation request
        if results.get('details'):
            results['account_request'] = await self.test_account_creation_request()
        
        # Step 4: Verify account creation
        if results.get('account_request'):
            results['account_verify'] = await self.test_account_verification()
        
        # Step 5: Second conversation test
        if results.get('account_verify'):
            results['second_conversation'] = await self.test_second_conversation()
        
        await self.print_results(results)
        return results
    
    async def test_introduction(self):
        """Test initial company introduction"""
        print(f"\n[STEP 1] Company Introduction")
        
        payload = {
            "message": self.company_info['intro_message'],
            "session_id": self.session_id
        }
        
        try:
            print(f"[{self.company_info['name']}] Sending introduction...")
            response = requests.post(
                f"{get_backend_url()}/api/coia/landing",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"[SUCCESS] Introduction accepted")
                print(f"[RESPONSE] {data.get('response', 'No response')[:100]}...")
                return True
            else:
                print(f"[ERROR] Introduction failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Introduction error: {e}")
            return False
    
    async def test_business_details(self):
        """Test providing business details"""
        print(f"\n[STEP 2] Business Details")
        
        payload = {
            "message": self.company_info['details_message'],
            "session_id": self.session_id
        }
        
        try:
            response = requests.post(
                f"{get_backend_url()}/api/coia/chat",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"[SUCCESS] Business details collected")
                print(f"[RESPONSE] {data.get('response', 'No response')[:100]}...")
                return True
            else:
                print(f"[ERROR] Business details failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Business details error: {e}")
            return False
    
    async def test_account_creation_request(self):
        """Test requesting account creation"""
        print(f"\n[STEP 3] Account Creation Request")
        
        payload = {
            "message": "Perfect! I'd like to create my InstaBids contractor account now so I can start bidding on projects. Please set up my account with all the information I provided.",
            "session_id": self.session_id
        }
        
        try:
            response = requests.post(
                f"{get_backend_url()}/api/coia/chat",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"[SUCCESS] Account creation request processed")
                print(f"[RESPONSE] {data.get('response', 'No response')[:100]}...")
                
                # Look for account data in response
                if 'account_data' in data:
                    self.account_data = data['account_data']
                    print(f"[ACCOUNT] Username: {self.account_data.get('username')}")
                    print(f"[ACCOUNT] Password: {self.account_data.get('password')}")
                
                return True
            else:
                print(f"[ERROR] Account creation request failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Account creation request error: {e}")
            return False
    
    async def test_account_verification(self):
        """Test verifying the account was created in database"""
        print(f"\n[STEP 4] Account Verification")
        
        try:
            # Check database directly
            import sys
            sys.path.append(".")
            from database_simple import db
            
            result = db.client.table("contractors").select("*").eq(
                "company_name", self.company_info['name']
            ).execute()
            
            if result.data:
                contractor = result.data[0]
                print(f"[SUCCESS] Account found in database")
                print(f"[DATABASE] ID: {contractor.get('id')}")
                print(f"[DATABASE] Company: {contractor.get('company_name')}")
                print(f"[DATABASE] Email: {contractor.get('email')}")
                print(f"[DATABASE] Phone: {contractor.get('phone')}")
                return True
            else:
                print(f"[ERROR] Account not found in database")
                return False
                
        except Exception as e:
            print(f"[ERROR] Account verification error: {e}")
            return False
    
    async def test_second_conversation(self):
        """Test a second conversation with existing profile"""
        print(f"\n[STEP 5] Second Conversation Test")
        
        # Use a new session ID to test profile persistence
        new_session = f"{self.session_id}-session2"
        
        payload = {
            "message": f"Hello! This is {self.company_info['owner']} from {self.company_info['name']} again. I created an account earlier and wanted to check for new opportunities.",
            "session_id": new_session
        }
        
        try:
            response = requests.post(
                f"{get_backend_url()}/api/coia/chat",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"[SUCCESS] Second conversation successful")
                print(f"[RESPONSE] {data.get('response', 'No response')[:100]}...")
                return True
            else:
                print(f"[ERROR] Second conversation failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Second conversation error: {e}")
            return False
    
    async def print_results(self, results):
        """Print final test results"""
        print(f"\n{'='*80}")
        print(f"[RESULTS] {self.company_info['name'].upper()} WORKFLOW TEST RESULTS")
        print(f"{'='*80}")
        
        all_passed = all(results.values())
        
        print(f"\n[TEST RESULTS]:")
        print(f"  [1] Company Introduction: {'PASS' if results.get('intro') else 'FAIL'}")
        print(f"  [2] Business Details: {'PASS' if results.get('details') else 'FAIL'}")
        print(f"  [3] Account Creation Request: {'PASS' if results.get('account_request') else 'FAIL'}")
        print(f"  [4] Account Verification: {'PASS' if results.get('account_verify') else 'FAIL'}")
        print(f"  [5] Second Conversation: {'PASS' if results.get('second_conversation') else 'FAIL'}")
        
        if all_passed:
            print(f"\n[SUCCESS] {self.company_info['name']} workflow FULLY FUNCTIONAL!")
        else:
            failed_steps = [step for step, passed in results.items() if not passed]
            print(f"\n[ISSUES] Failed steps: {failed_steps}")

async def main():
    """Test both company workflows"""
    
    # Company information
    companies = [
        {
            'name': 'JM Holiday Lighting',
            'owner': 'Justin Mancuso',
            'intro_message': "Hi there! I'm Justin Mancuso and I own JM Holiday Lighting here in South Florida. We specialize in holiday and Christmas lighting installations for homes and businesses. I heard about InstaBids and I'm interested in finding more customers.",
            'details_message': "Sure! I've been running JM Holiday Lighting for about 8 years now. We're based in Fort Lauderdale, Florida 33301. My business phone is (954) 555-0123 and email is justin@jmholidaylighting.com. We do both residential and commercial holiday lighting installations, takedowns, and storage. We're licensed and insured."
        },
        {
            'name': 'TurfGrass Artificial Solutions',
            'owner': 'the owner',
            'intro_message': "Hello! I own TurfGrass Artificial Solutions and we specialize in artificial turf installation for residential and commercial properties. We've been in business for several years and are looking to expand our customer base through InstaBids.",
            'details_message': "Absolutely! TurfGrass Artificial Solutions has been serving South Florida for over 5 years. We're based in Miami, Florida 33101. You can reach us at (305) 555-0456 and our email is info@turfgrassartificialsolutions.com. We handle complete artificial turf installations, landscape design, and maintenance. We're fully licensed and insured."
        }
    ]
    
    print("\n[CHRISTMAS TREE] STARTING COMPLETE COMPANY WORKFLOW TESTS [CHRISTMAS TREE]")
    print("Testing both JM Holiday Lighting and TurfGrass Artificial Solutions")
    
    # Clean up any existing contractors first
    try:
        from database_simple import db
        db.client.table("contractors").delete().in_(
            "company_name", ["JM Holiday Lighting", "TurfGrass Artificial Solutions"]
        ).execute()
        print("\n[CLEANUP] Removed any existing contractor records")
    except Exception as e:
        print(f"\n[WARNING] Cleanup error: {e}")
    
    # Test both companies
    results = {}
    for company in companies:
        test = CompanyWorkflowTest(company)
        results[company['name']] = await test.test_complete_workflow()
        
        # Add a small delay between tests
        await asyncio.sleep(2)
    
    # Final summary
    print(f"\n{'='*80}")
    print(f"[FINAL] COMPLETE WORKFLOW TEST SUMMARY")
    print(f"{'='*80}")
    
    for company_name, company_results in results.items():
        all_passed = all(company_results.values())
        status = "FULLY FUNCTIONAL" if all_passed else "HAS ISSUES"
        print(f"\n{company_name}: {status}")
        
        if all_passed:
            print(f"  [CHRISTMAS TREE] Complete contractor onboarding working!")
        else:
            failed_steps = [step for step, passed in company_results.items() if not passed]
            print(f"  [ERROR] Failed: {failed_steps}")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())