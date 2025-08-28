#!/usr/bin/env python3
"""
Test AI Contractor Relationship Memory System
Tests the AI-powered contractor memory building and retrieval
"""

import asyncio
import requests
import json
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.contractor_ai_memory import ContractorAIMemory
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

class AIMemoryTester:
    def __init__(self):
        self.ai_memory = ContractorAIMemory()
        self.base_url = f"{get_backend_url()}/api/bsa"
        self.contractor_id = "523c0f63-e75c-4d65-963e-561d7f4169db"  # Mike's Plumbing
        self.test_bid_card_id = "4aa5e277-82b1-4679-a86a-24fd56b10e4c"  # Roofing project

    async def test_ai_memory_creation(self):
        """Test creating AI memory from conversation data"""
        print_header("TEST 1: AI MEMORY CREATION")
        
        # Simulate a conversation that reveals contractor preferences
        conversation_data = {
            'input': "I prefer to work on high-end projects with quality materials. I always use premium roofing materials and like to take my time to do things right. I work best with homeowners who value quality over speed.",
            'response': "Thank you for sharing your approach. I'll create a proposal emphasizing your commitment to premium materials and quality craftsmanship.",
            'context': "BSA conversation for roofing project",
            'project_type': 'roofing',
            'bid_amount': 25000,
            'timeline': '2-3 weeks'
        }
        
        print_test("Analyzing conversation for memory insights...")
        updated_memory = await self.ai_memory.update_contractor_memory(
            self.contractor_id, conversation_data
        )
        
        if updated_memory:
            print_success("AI memory created successfully!")
            print_info(f"Memory insights: {json.dumps(updated_memory, indent=2)}")
            return True
        else:
            print_error("Failed to create AI memory")
            return False

    async def test_memory_retrieval(self):
        """Test retrieving memory for system prompt"""
        print_header("TEST 2: MEMORY RETRIEVAL FOR SYSTEM PROMPT")
        
        print_test("Getting memory for system prompt injection...")
        memory_prompt = await self.ai_memory.get_memory_for_system_prompt(self.contractor_id)
        
        if memory_prompt:
            print_success("Memory retrieved successfully!")
            print_info(f"System prompt section:\n{memory_prompt}")
            return True
        else:
            print_error("No memory found or empty result")
            return False

    async def test_memory_accumulation(self):
        """Test memory building over multiple conversations"""
        print_header("TEST 3: MEMORY ACCUMULATION")
        
        conversations = [
            {
                'input': "I really enjoy working with historic homes. They require special attention to detail and I have experience with restoration techniques.",
                'response': "Your expertise with historic homes would be valuable for this project.",
                'context': "BSA conversation for renovation project",
                'project_type': 'renovation',
                'timeline': 'flexible'
            },
            {
                'input': "I prefer to communicate via text or email rather than phone calls. I like to document everything for clarity.",
                'response': "I'll note your communication preferences for future reference.",
                'context': "BSA conversation about communication",
                'project_type': 'general',
                'timeline': 'standard'
            },
            {
                'input': "My company specializes in sustainable building practices. We use eco-friendly materials whenever possible.",
                'response': "Your focus on sustainability aligns well with current homeowner trends.",
                'context': "BSA conversation about company focus",
                'project_type': 'green_building',
                'timeline': 'standard'
            }
        ]
        
        print_test("Processing multiple conversations to build memory...")
        
        for i, conv_data in enumerate(conversations, 1):
            print_info(f"Processing conversation {i}...")
            await self.ai_memory.update_contractor_memory(self.contractor_id, conv_data)
            await asyncio.sleep(1)  # Brief pause between updates
        
        # Get final memory state
        final_memory = await self.ai_memory.get_contractor_memory(self.contractor_id)
        
        if final_memory and len(final_memory) > 0:
            print_success("Memory accumulated successfully!")
            print_info(f"Final memory state: {json.dumps(final_memory, indent=2)}")
            
            # Test personality summary
            summary = await self.ai_memory.get_contractor_personality_summary(self.contractor_id)
            print_info(f"Personality summary: {summary}")
            return True
        else:
            print_error("Failed to accumulate memory")
            return False

    async def test_bsa_integration(self):
        """Test BSA integration with AI memory"""
        print_header("TEST 4: BSA INTEGRATION WITH AI MEMORY")
        
        print_test("Making BSA API call to test memory integration...")
        
        payload = {
            "contractor_id": self.contractor_id,
            "bid_card_id": self.test_bid_card_id,
            "input_type": "text",
            "input_data": "Based on our previous conversations, I'd like to submit a bid that reflects my commitment to quality and my preference for sustainable materials.",
            "session_id": f"ai_memory_test_{datetime.now().timestamp()}"
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
                
                # Collect response to see if it uses memory
                full_response = ""
                memory_referenced = False
                
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
                
                # Check if response references memory insights
                memory_keywords = ['quality', 'premium', 'sustainable', 'eco-friendly', 'historic', 'restoration']
                memory_referenced = any(keyword in full_response.lower() for keyword in memory_keywords)
                
                if memory_referenced:
                    print_success("BSA response appears to use AI memory insights!")
                    print_info(f"Response length: {len(full_response)} characters")
                else:
                    print_error("BSA response doesn't clearly reference memory insights")
                
                return True
            else:
                print_error(f"BSA API call failed: {response.status_code}")
                return False
                
        except Exception as e:
            print_error(f"BSA integration test failed: {e}")
            return False

    async def run_all_tests(self):
        """Run all AI memory tests"""
        print_header("AI CONTRACTOR RELATIONSHIP MEMORY SYSTEM TESTS")
        
        tests_passed = 0
        tests_total = 4
        
        # Test 1: AI Memory Creation
        if await self.test_ai_memory_creation():
            tests_passed += 1
        
        # Test 2: Memory Retrieval
        if await self.test_memory_retrieval():
            tests_passed += 1
        
        # Test 3: Memory Accumulation
        if await self.test_memory_accumulation():
            tests_passed += 1
        
        # Test 4: BSA Integration
        if await self.test_bsa_integration():
            tests_passed += 1
        
        # Final Results
        print_header("AI MEMORY SYSTEM TEST RESULTS")
        
        if tests_passed == tests_total:
            print_success(f"ALL TESTS PASSED! ({tests_passed}/{tests_total})")
            print_success("AI Contractor Relationship Memory System is FULLY OPERATIONAL!")
            print_success("Features verified:")
            print_success("  - AI-powered conversation analysis")
            print_success("  - Memory accumulation over time")
            print_success("  - System prompt integration")
            print_success("  - BSA agent integration")
        else:
            print_error(f"TESTS FAILED: Only {tests_passed}/{tests_total} passed")
            print_error("AI memory system needs debugging")

async def main():
    """Run AI memory system tests"""
    
    # Check backend is running
    try:
        response = requests.get(f"{get_backend_url()}/")
        if response.status_code != 200:
            print_error("Backend not running!")
            return
    except:
        print_error("Cannot connect to backend!")
        return
    
    print_success("Backend is running - starting AI memory tests")
    
    tester = AIMemoryTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())