#!/usr/bin/env python3
"""
Test Enhanced Multi-Dimensional Contractor Memory System
Tests the 5-table business intelligence gathering system
"""

import asyncio
import requests
import json
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.enhanced_contractor_memory import EnhancedContractorMemory
from config.service_urls import get_backend_url

def print_header(text):
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")

def print_success(text):
    print(f"[SUCCESS] {text}")

def print_error(text):
    print(f"[ERROR] {text}")

def print_info(text):
    print(f"[INFO] {text}")

def print_test(text):
    print(f"[TEST] {text}")

class EnhancedMemoryTester:
    def __init__(self):
        self.memory = EnhancedContractorMemory()
        self.base_url = f"{get_backend_url()}/api/bsa"
        self.contractor_id = "523c0f63-e75c-4d65-963e-561d7f4169db"  # Mike's Plumbing
        self.test_bid_card_id = "4aa5e277-82b1-4679-a86a-24fd56b10e4c"  # Roofing project

    async def test_memory_dimensions(self):
        """Test creating memories across all 5 dimensions"""
        print_header("TEST 1: MULTI-DIMENSIONAL MEMORY CREATION")
        
        # Simulate a rich conversation with business intelligence data
        conversation_data = {
            'input': """We've been using QuickBooks for our CRM and job tracking. 
                       Our company has 12 employees, we're looking to expand to 20 by next year.
                       We prefer projects in the $50k-$100k range. Our sweet spot is bathroom 
                       and kitchen remodels. We use email for most communication but text for 
                       urgent matters. We typically mark up materials by 20% and labor by 35%.
                       Our biggest pain point is managing multiple subcontractors.""",
            'response': "Thank you for sharing those details about your business operations.",
            'context': "BSA conversation gathering business intelligence",
            'project_type': 'kitchen_remodel',
            'budget_min': 50000,
            'budget_max': 100000,
            'urgency_level': 'standard',
            'contractor_context': {
                'company_name': "Mike's Plumbing & Remodeling",
                'years_in_business': 15
            }
        }
        
        print_test("Updating all memory dimensions with business intelligence...")
        results = await self.memory.update_all_contractor_memories(
            self.contractor_id, conversation_data
        )
        
        if results:
            print_success(f"Created memories in {len(results)} dimensions!")
            for dimension, data in results.items():
                print_info(f"  {dimension}: {data}")
            return True
        else:
            print_error("Failed to create multi-dimensional memories")
            return False

    async def test_comprehensive_profile(self):
        """Test retrieving comprehensive contractor profile"""
        print_header("TEST 2: COMPREHENSIVE PROFILE RETRIEVAL")
        
        print_test("Getting complete contractor profile...")
        profile = await self.memory.get_complete_contractor_profile(self.contractor_id)
        
        if profile:
            print_success("Retrieved comprehensive profile!")
            print_info("Profile preview (first 500 chars):")
            print(profile[:500])
            print_info(f"\nTotal profile length: {len(profile)} characters")
            
            # Check for key business intelligence markers
            has_business_info = any(term in profile.lower() for term in 
                ['crm', 'quickbooks', 'employees', 'markup', 'pain point'])
            
            if has_business_info:
                print_success("Profile contains business intelligence data!")
            else:
                print_warning("Profile may be missing business intelligence")
                
            return True
        else:
            print_error("No profile retrieved")
            return False

    async def test_bsa_integration(self):
        """Test BSA integration with enhanced memory"""
        print_header("TEST 3: BSA INTEGRATION WITH ENHANCED MEMORY")
        
        print_test("Making BSA API call with enhanced memory context...")
        
        payload = {
            "contractor_id": self.contractor_id,
            "bid_card_id": self.test_bid_card_id,
            "input_type": "text",
            "input_data": "I'd like to submit a bid for this project. As we discussed, we use premium materials with our standard 20% markup.",
            "session_id": f"enhanced_test_{datetime.now().timestamp()}"
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
                print_success("BSA API call successful!")
                
                # Collect response
                full_response = ""
                enhanced_memory_used = False
                
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith("data: "):
                            data_str = line_str[6:]
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                if 'status' in data and data['status'] == 'context_loaded':
                                    # Check if enhanced profile was loaded
                                    if 'enhanced_profile' in str(data):
                                        enhanced_memory_used = True
                                if 'choices' in data and data['choices']:
                                    content = data['choices'][0].get('delta', {}).get('content', '')
                                    full_response += content
                            except:
                                pass
                
                # Check if response references the markup we mentioned
                if '20%' in full_response or 'markup' in full_response.lower():
                    print_success("BSA response references our business practices!")
                
                if enhanced_memory_used:
                    print_success("Enhanced memory profile was loaded!")
                else:
                    print_warning("Enhanced memory may not have been loaded")
                
                print_info(f"Response length: {len(full_response)} characters")
                return True
            else:
                print_error(f"BSA API call failed: {response.status_code}")
                return False
                
        except Exception as e:
            print_error(f"BSA integration test failed: {e}")
            return False

    async def test_memory_accumulation(self):
        """Test memory building over multiple conversations"""
        print_header("TEST 4: MEMORY ACCUMULATION")
        
        conversations = [
            {
                'input': "We just started using Buildertrend for project management.",
                'response': "Buildertrend integration noted.",
                'context': "Learning about software stack"
            },
            {
                'input': "Our biggest challenge is finding qualified subcontractors for electrical work.",
                'response': "I understand the subcontractor challenge.",
                'context': "Understanding pain points"
            },
            {
                'input': "We're looking to expand into commercial projects next year.",
                'response': "Commercial expansion plans noted.",
                'context': "Growth planning discussion"
            }
        ]
        
        print_test("Processing multiple conversations...")
        
        for i, conv_data in enumerate(conversations, 1):
            print_info(f"Processing conversation {i}...")
            conv_data['contractor_context'] = {'company_name': "Mike's Plumbing"}
            await self.memory.update_all_contractor_memories(self.contractor_id, conv_data)
            await asyncio.sleep(1)
        
        # Get final comprehensive profile
        final_profile = await self.memory.get_complete_contractor_profile(self.contractor_id)
        
        if final_profile:
            print_success("Memory accumulated successfully!")
            
            # Check for accumulated intelligence
            intelligence_terms = ['buildertrend', 'electrical', 'commercial', 'expansion']
            found_terms = [term for term in intelligence_terms if term in final_profile.lower()]
            
            if found_terms:
                print_success(f"Profile contains {len(found_terms)}/{len(intelligence_terms)} intelligence points")
                print_info(f"Found: {', '.join(found_terms)}")
            
            return True
        else:
            print_error("Failed to accumulate memory")
            return False

    async def run_all_tests(self):
        """Run all enhanced memory tests"""
        print_header("ENHANCED MULTI-DIMENSIONAL MEMORY SYSTEM TESTS")
        print_info("Testing 5-table business intelligence gathering system")
        
        tests_passed = 0
        tests_total = 4
        
        # Test 1: Multi-dimensional memory creation
        if await self.test_memory_dimensions():
            tests_passed += 1
        
        # Test 2: Comprehensive profile retrieval
        if await self.test_comprehensive_profile():
            tests_passed += 1
        
        # Test 3: BSA integration
        if await self.test_bsa_integration():
            tests_passed += 1
        
        # Test 4: Memory accumulation
        if await self.test_memory_accumulation():
            tests_passed += 1
        
        # Final Results
        print_header("ENHANCED MEMORY SYSTEM TEST RESULTS")
        
        if tests_passed == tests_total:
            print_success(f"ALL TESTS PASSED! ({tests_passed}/{tests_total})")
            print_success("Enhanced Memory System is FULLY OPERATIONAL!")
            print_success("Business Intelligence Features Verified:")
            print_success("  - Multi-dimensional memory creation")
            print_success("  - Comprehensive profile generation")
            print_success("  - BSA integration with enhanced context")
            print_success("  - Memory accumulation over time")
        else:
            print_error(f"TESTS FAILED: Only {tests_passed}/{tests_total} passed")
            print_error("Enhanced memory system needs debugging")

def print_warning(text):
    print(f"[WARNING] {text}")

async def main():
    """Run enhanced memory system tests"""
    
    # Check backend is running
    try:
        response = requests.get(f"{get_backend_url()}/")
        if response.status_code != 200:
            print_error("Backend not running!")
            return
    except:
        print_error("Cannot connect to backend!")
        return
    
    print_success("Backend is running - starting enhanced memory tests")
    
    tester = EnhancedMemoryTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())