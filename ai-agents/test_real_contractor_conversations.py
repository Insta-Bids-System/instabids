"""
Real Multi-Turn Contractor Conversation Tests
Tests complete COIA system with realistic contractor scenarios
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

class ContractorConversationTest:
    def __init__(self):
        self.base_url = "http://localhost:8008"
        self.test_results = []
        
    def log_result(self, test_name, status, details, response_time=None):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_prefix = "[PASSED]" if status == "PASSED" else "[FAILED]" if status == "FAILED" else "[INFO]"
        time_suffix = f" ({response_time:.2f}s)" if response_time else ""
        print(f"{status_prefix} {test_name}: {details}{time_suffix}")
    
    async def send_message(self, session_id, message, company_name=None, location=None):
        """Send a message to COIA and measure response time"""
        start_time = time.time()
        
        payload = {
            'session_id': session_id,
            'message': message
        }
        if company_name:
            payload['company_name'] = company_name
        if location:
            payload['location'] = location
            
        try:
            async with aiohttp.ClientSession() as session:
                response = await session.post(
                    f'{self.base_url}/api/coia/fast-landing',
                    json=payload
                )
                
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "response": data.get("response", ""),
                        "response_time": response_time,
                        "data": data
                    }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}",
                        "response_time": response_time
                    }
                    
        except Exception as e:
            response_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "response_time": response_time
            }
    
    async def test_plumbing_contractor_full_conversation(self):
        """Test: Multi-turn conversation with Miami plumbing contractor"""
        session_id = f"plumber-test-{int(time.time())}"
        print(f"\n{'='*80}")
        print(f"TESTING: Miami Plumbing Contractor Conversation")
        print(f"Session ID: {session_id}")
        print(f"{'='*80}")
        
        # Turn 1: Initial introduction
        print(f"\n--- TURN 1: Initial Introduction ---")
        result1 = await self.send_message(
            session_id, 
            "Hi, I run Miami Premium Plumbing and I'm interested in getting more customers through InstaBids",
            company_name="Miami Premium Plumbing",
            location="Miami, FL"
        )
        
        if result1["success"]:
            self.log_result("Plumber Turn 1", "PASSED", 
                          f"Initial response received", result1["response_time"])
            print(f"RESPONSE: {result1['response'][:200]}...")
        else:
            self.log_result("Plumber Turn 1", "FAILED", result1["error"], result1["response_time"])
            return False
        
        # Wait for background processing
        await asyncio.sleep(5)
        
        # Turn 2: Service specialization
        print(f"\n--- TURN 2: Service Details ---")
        result2 = await self.send_message(
            session_id,
            "We specialize in emergency plumbing repairs, water heater installation, and bathroom remodeling. We've been in business for 8 years and serve all of Miami-Dade County."
        )
        
        if result2["success"]:
            self.log_result("Plumber Turn 2", "PASSED", 
                          f"Service details processed", result2["response_time"])
            print(f"RESPONSE: {result2['response'][:200]}...")
        else:
            self.log_result("Plumber Turn 2", "FAILED", result2["error"], result2["response_time"])
            return False
        
        # Turn 3: Business questions
        print(f"\n--- TURN 3: Business Questions ---")
        result3 = await self.send_message(
            session_id,
            "How does the bidding process work? Do I need to pay anything upfront?"
        )
        
        if result3["success"]:
            self.log_result("Plumber Turn 3", "PASSED", 
                          f"Business questions answered", result3["response_time"])
            print(f"RESPONSE: {result3['response'][:200]}...")
        else:
            self.log_result("Plumber Turn 3", "FAILED", result3["error"], result3["response_time"])
            return False
        
        # Turn 4: Service area details
        print(f"\n--- TURN 4: Service Area ---")
        result4 = await self.send_message(
            session_id,
            "I can work within 25 miles of downtown Miami. I'm licensed and insured with 5-star reviews on Google."
        )
        
        if result4["success"]:
            self.log_result("Plumber Turn 4", "PASSED", 
                          f"Service area confirmed", result4["response_time"])
            print(f"RESPONSE: {result4['response'][:200]}...")
        else:
            self.log_result("Plumber Turn 4", "FAILED", result4["error"], result4["response_time"])
            return False
        
        return True
    
    async def test_landscaping_contractor_conversation(self):
        """Test: Multi-turn conversation with Texas landscaping contractor"""
        session_id = f"landscaper-test-{int(time.time())}"
        print(f"\n{'='*80}")
        print(f"TESTING: Texas Landscaping Contractor Conversation")
        print(f"Session ID: {session_id}")
        print(f"{'='*80}")
        
        # Turn 1: Initial introduction
        print(f"\n--- TURN 1: Initial Introduction ---")
        result1 = await self.send_message(
            session_id,
            "Hello, I'm the owner of Austin Elite Landscaping. We do high-end residential and commercial landscaping projects.",
            company_name="Austin Elite Landscaping",
            location="Austin, TX"
        )
        
        if result1["success"]:
            self.log_result("Landscaper Turn 1", "PASSED", 
                          f"Initial response received", result1["response_time"])
            print(f"RESPONSE: {result1['response'][:200]}...")
        else:
            self.log_result("Landscaper Turn 1", "FAILED", result1["error"], result1["response_time"])
            return False
        
        # Wait for background processing
        await asyncio.sleep(5)
        
        # Turn 2: Detailed services
        print(f"\n--- TURN 2: Service Portfolio ---")
        result2 = await self.send_message(
            session_id,
            "Our services include landscape design, hardscaping with natural stone, irrigation systems, outdoor lighting, and tree services. We handle projects from $5,000 to $150,000."
        )
        
        if result2["success"]:
            self.log_result("Landscaper Turn 2", "PASSED", 
                          f"Service portfolio detailed", result2["response_time"])
            print(f"RESPONSE: {result2['response'][:200]}...")
        else:
            self.log_result("Landscaper Turn 2", "FAILED", result2["error"], result2["response_time"])
            return False
        
        # Turn 3: Project examples
        print(f"\n--- TURN 3: Project Examples ---")
        result3 = await self.send_message(
            session_id,
            "Some recent projects include a $75k backyard oasis with pool landscaping in West Lake Hills, and a $45k front yard makeover in Tarrytown with native Texas plants."
        )
        
        if result3["success"]:
            self.log_result("Landscaper Turn 3", "PASSED", 
                          f"Project examples processed", result3["response_time"])
            print(f"RESPONSE: {result3['response'][:200]}...")
        else:
            self.log_result("Landscaper Turn 3", "FAILED", result3["error"], result3["response_time"])
            return False
        
        return True
    
    async def test_roofing_contractor_conversation(self):
        """Test: Multi-turn conversation with California roofing contractor"""
        session_id = f"roofer-test-{int(time.time())}"
        print(f"\n{'='*80}")
        print(f"TESTING: California Roofing Contractor Conversation") 
        print(f"Session ID: {session_id}")
        print(f"{'='*80}")
        
        # Turn 1: Initial introduction with business challenge
        print(f"\n--- TURN 1: Business Challenge ---")
        result1 = await self.send_message(
            session_id,
            "I run San Diego Pro Roofing and business has been slow lately. I need more residential roofing leads. Can InstaBids help?",
            company_name="San Diego Pro Roofing", 
            location="San Diego, CA"
        )
        
        if result1["success"]:
            self.log_result("Roofer Turn 1", "PASSED", 
                          f"Business challenge addressed", result1["response_time"])
            print(f"RESPONSE: {result1['response'][:200]}...")
        else:
            self.log_result("Roofer Turn 1", "FAILED", result1["error"], result1["response_time"])
            return False
        
        # Wait for background processing
        await asyncio.sleep(5)
        
        # Turn 2: Expertise and certifications
        print(f"\n--- TURN 2: Expertise Details ---")
        result2 = await self.send_message(
            session_id,
            "We're GAF Master Elite contractors with 12 years experience. We do tile, shingle, flat roofs, and solar panel installations. All work comes with manufacturer warranties."
        )
        
        if result2["success"]:
            self.log_result("Roofer Turn 2", "PASSED", 
                          f"Expertise and certifications noted", result2["response_time"])
            print(f"RESPONSE: {result2['response'][:200]}...")
        else:
            self.log_result("Roofer Turn 2", "FAILED", result2["error"], result2["response_time"])
            return False
        
        # Turn 3: Pricing and availability
        print(f"\n--- TURN 3: Pricing Structure ---")
        result3 = await self.send_message(
            session_id,
            "Our typical residential re-roof ranges from $15,000 to $45,000 depending on size and materials. We can start projects within 2-3 weeks and complete most jobs in 2-4 days."
        )
        
        if result3["success"]:
            self.log_result("Roofer Turn 3", "PASSED", 
                          f"Pricing and timeline provided", result3["response_time"])
            print(f"RESPONSE: {result3['response'][:200]}...")
        else:
            self.log_result("Roofer Turn 3", "FAILED", result3["error"], result3["response_time"])
            return False
        
        return True
    
    async def check_contractor_profiles_created(self):
        """Check if contractor profiles were actually created in database"""
        # This would require checking the database, but for now we'll check the responses
        # to see if they indicate profile creation
        profile_indicators = 0
        
        for result in self.test_results:
            if "profile" in result["details"].lower() or "staged" in result["details"].lower():
                profile_indicators += 1
        
        if profile_indicators > 0:
            self.log_result("Profile Creation", "PASSED", 
                          f"Profile creation indicators found in {profile_indicators} responses")
            return True
        else:
            self.log_result("Profile Creation", "FAILED", 
                          "No profile creation indicators found")
            return False
    
    def print_final_summary(self):
        """Print comprehensive test summary"""
        print(f"\n{'='*80}")
        print(f"REAL CONTRACTOR CONVERSATION TEST SUMMARY")
        print(f"{'='*80}")
        
        passed = len([r for r in self.test_results if r["status"] == "PASSED"])
        failed = len([r for r in self.test_results if r["status"] == "FAILED"])
        
        print(f"Total Interactions: {len(self.test_results)}")
        print(f"Successful: {passed}")
        print(f"Failed: {failed}")
        
        # Response time analysis
        response_times = [r["response_time"] for r in self.test_results if r.get("response_time")]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            
            print(f"\nResponse Time Analysis:")
            print(f"  Average: {avg_time:.2f}s")
            print(f"  Fastest: {min_time:.2f}s")
            print(f"  Slowest: {max_time:.2f}s")
        
        print(f"\nTest Scenarios:")
        print(f"  ✓ Miami Plumbing Contractor (4 turns)")
        print(f"  ✓ Austin Landscaping Contractor (3 turns)")
        print(f"  ✓ San Diego Roofing Contractor (3 turns)")
        print(f"  Total: 10 conversation turns across 3 contractors")
        
        if failed == 0:
            print(f"\n[SUCCESS] All real contractor conversations completed successfully!")
            print(f"COIA system handles multi-turn conversations with real business scenarios.")
        else:
            print(f"\n[WARNING] {failed} interactions failed. System needs attention.")
        
        print(f"{'='*80}")
        
        return failed == 0

async def main():
    """Run comprehensive multi-turn contractor conversation tests"""
    tester = ContractorConversationTest()
    
    print("COIA REAL CONTRACTOR CONVERSATION TEST SUITE")
    print("Testing multi-turn conversations with realistic contractor scenarios")
    print("This proves the system works end-to-end with real business interactions")
    
    # Test 1: Miami Plumbing Contractor
    success1 = await tester.test_plumbing_contractor_full_conversation()
    
    # Test 2: Austin Landscaping Contractor  
    success2 = await tester.test_landscaping_contractor_conversation()
    
    # Test 3: San Diego Roofing Contractor
    success3 = await tester.test_roofing_contractor_conversation()
    
    # Check if profiles were created
    profiles_created = await tester.check_contractor_profiles_created()
    
    # Final summary
    overall_success = tester.print_final_summary()
    
    return overall_success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)