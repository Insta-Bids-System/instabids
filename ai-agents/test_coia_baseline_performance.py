#!/usr/bin/env python3
"""
COIA Baseline Performance Testing Script
Tests all three unified_coia_api.py endpoints to validate baseline performance
Used to verify improvements after implementing async background tasks
"""

import asyncio
import json
import time
import requests
from typing import Dict, Any
import logging
from config.service_urls import get_backend_url

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = get_backend_url()

class COIAPerformanceTester:
    """Test all COIA endpoints and measure performance"""
    
    def __init__(self):
        self.results = {}
        
    def test_endpoint(self, endpoint: str, payload: Dict[str, Any], timeout: int = 65) -> Dict[str, Any]:
        """Test a single endpoint and measure performance"""
        start_time = time.time()
        
        try:
            logger.info(f"Testing {endpoint} with timeout {timeout}s...")
            
            response = requests.post(
                f"{BASE_URL}{endpoint}",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=timeout
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                result = {
                    "status": "SUCCESS",
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "response_size": len(response.text),
                    "content": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                }
                logger.info(f"✅ {endpoint} SUCCESS: {response_time:.2f}s")
            else:
                result = {
                    "status": "HTTP_ERROR", 
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "error": response.text
                }
                logger.error(f"❌ {endpoint} HTTP_ERROR: {response.status_code}")
                
        except requests.exceptions.Timeout:
            end_time = time.time()
            response_time = end_time - start_time
            result = {
                "status": "TIMEOUT",
                "response_time": response_time,
                "error": f"Request timed out after {timeout} seconds"
            }
            logger.error(f"⏰ {endpoint} TIMEOUT: {response_time:.2f}s")
            
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            result = {
                "status": "ERROR",
                "response_time": response_time,
                "error": str(e)
            }
            logger.error(f"💥 {endpoint} ERROR: {str(e)}")
            
        return result
    
    def test_chat_interface(self) -> Dict[str, Any]:
        """Test the chat interface endpoint (should work in 5-6 seconds)"""
        payload = {
            "message": "Hello, I own TurfGrass Artificial Solutions in South Florida",
            "session_id": "perf-test-chat-001",
            "interface": "chat"
        }
        
        return self.test_endpoint("/api/coia/chat", payload, timeout=15)
    
    def test_landing_interface(self) -> Dict[str, Any]:
        """Test the landing page interface endpoint (known to timeout)"""
        payload = {
            "message": "I own a landscaping business in Florida",
            "session_id": "perf-test-landing-001", 
            "interface": "landing_page"
        }
        
        return self.test_endpoint("/api/coia/landing", payload, timeout=65)
    
    def test_bid_card_interface(self) -> Dict[str, Any]:
        """Test the bid card link interface endpoint (known to timeout)"""
        payload = {
            "message": "I want to bid on this project",
            "session_id": "perf-test-bidcard-001",
            "interface": "bid_card_link",
            "bid_card_id": "test-bid-card",
            "contractor_lead_id": "test-contractor",
            "verification_token": "test-token"
        }
        
        return self.test_endpoint("/api/coia/bid-card-link", payload, timeout=65)
    
    def run_baseline_tests(self) -> Dict[str, Any]:
        """Run all baseline performance tests"""
        logger.info("🚀 Starting COIA Baseline Performance Testing...")
        
        # Test 1: Chat Interface (should work)
        logger.info("\n📱 Testing Chat Interface...")
        self.results["chat_interface"] = self.test_chat_interface()
        
        # Test 2: Landing Page Interface (known timeout)
        logger.info("\n🏠 Testing Landing Page Interface...")
        self.results["landing_interface"] = self.test_landing_interface()
        
        # Test 3: Bid Card Link Interface (known timeout)
        logger.info("\n🎯 Testing Bid Card Link Interface...")
        self.results["bid_card_interface"] = self.test_bid_card_interface()
        
        # Generate summary
        self.results["summary"] = self.generate_summary()
        
        return self.results
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate performance summary"""
        working_endpoints = []
        timeout_endpoints = []
        error_endpoints = []
        
        for endpoint, result in self.results.items():
            if endpoint == "summary":
                continue
                
            if result["status"] == "SUCCESS":
                working_endpoints.append({
                    "endpoint": endpoint,
                    "response_time": result["response_time"]
                })
            elif result["status"] == "TIMEOUT":
                timeout_endpoints.append({
                    "endpoint": endpoint,
                    "response_time": result["response_time"]
                })
            else:
                error_endpoints.append({
                    "endpoint": endpoint,
                    "status": result["status"],
                    "error": result.get("error", "Unknown error")
                })
        
        return {
            "total_endpoints_tested": len(self.results) - 1,  # -1 for summary itself
            "working_endpoints": working_endpoints,
            "timeout_endpoints": timeout_endpoints,
            "error_endpoints": error_endpoints,
            "performance_baseline_established": True,
            "ready_for_optimization": len(timeout_endpoints) > 0
        }
    
    def print_results(self):
        """Print formatted test results"""
        print("\n" + "="*80)
        print("🔬 COIA BASELINE PERFORMANCE TEST RESULTS")
        print("="*80)
        
        # Working endpoints
        working = self.results["summary"]["working_endpoints"]
        if working:
            print(f"\n✅ WORKING ENDPOINTS ({len(working)}):")
            for endpoint in working:
                print(f"   • {endpoint['endpoint']}: {endpoint['response_time']:.2f}s")
        
        # Timeout endpoints
        timeouts = self.results["summary"]["timeout_endpoints"]
        if timeouts:
            print(f"\n⏰ TIMEOUT ENDPOINTS ({len(timeouts)}):")
            for endpoint in timeouts:
                print(f"   • {endpoint['endpoint']}: {endpoint['response_time']:.2f}s (TIMEOUT)")
        
        # Error endpoints
        errors = self.results["summary"]["error_endpoints"]
        if errors:
            print(f"\n❌ ERROR ENDPOINTS ({len(errors)}):")
            for endpoint in errors:
                print(f"   • {endpoint['endpoint']}: {endpoint['status']} - {endpoint['error']}")
        
        # Summary
        summary = self.results["summary"]
        print(f"\n📊 SUMMARY:")
        print(f"   • Total Endpoints: {summary['total_endpoints_tested']}")
        print(f"   • Working: {len(working)}")
        print(f"   • Timeouts: {len(timeouts)}")
        print(f"   • Errors: {len(errors)}")
        print(f"   • Ready for Optimization: {summary['ready_for_optimization']}")
        
        # Recommendations
        print(f"\n🎯 RECOMMENDATIONS:")
        if timeouts:
            print("   • Implement async background tasks for timeout endpoints")
            print("   • Convert research_node from blocking to non-blocking execution")
            print("   • Use direct tool calls instead of async context managers")
        if working:
            print("   • Preserve working endpoint patterns during optimization")
        
        print("\n" + "="*80)

def main():
    """Main test execution"""
    tester = COIAPerformanceTester()
    
    # Run baseline tests
    results = tester.run_baseline_tests()
    
    # Print results
    tester.print_results()
    
    # Save results to file
    timestamp = int(time.time())
    results_file = f"coia_baseline_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    # Return success/failure based on whether optimization is needed
    return 0 if results["summary"]["ready_for_optimization"] else 1

if __name__ == "__main__":
    exit(main())