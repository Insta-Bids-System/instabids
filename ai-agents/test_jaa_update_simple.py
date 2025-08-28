#!/usr/bin/env python3
"""
JAA Update System Testing - Simple Version
Tests the new bid card update functionality with contractor notifications
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta

# Add the ai-agents directory to the Python path
sys.path.append(os.path.dirname(__file__))

from agents.jaa.agent import JobAssessmentAgent
from database_simple import SupabaseDB

class JAUpdateTestSuite:
    """Test suite for JAA update functionality"""
    
    def __init__(self):
        """Initialize test suite"""
        print("[JAA UPDATE TESTS] Initializing test suite...")
        self.jaa = JobAssessmentAgent()
        self.db = SupabaseDB()
        self.test_results = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "failures": []
        }
        
    async def run_all_tests(self):
        """Run complete test suite"""
        print("\n" + "="*80)
        print("JAA UPDATE SYSTEM - COMPLETE TEST SUITE")
        print("="*80)
        
        # Test sequence
        test_methods = [
            ("Test 1: Update Analysis", self.test_update_analysis),
            ("Test 2: Contractor Discovery", self.test_contractor_discovery), 
            ("Test 3: Notification Generation", self.test_notification_generation),
            ("Test 4: Complete Update Flow", self.test_complete_update_flow),
            ("Test 5: API Integration", self.test_api_integration),
            ("Test 6: Error Handling", self.test_error_handling)
        ]
        
        for test_name, test_method in test_methods:
            try:
                print(f"\n[TEST] {test_name}")
                print("-" * 60)
                await test_method()
                self.test_results["tests_passed"] += 1
                print(f"[PASS] {test_name} PASSED")
            except Exception as e:
                self.test_results["tests_failed"] += 1
                self.test_results["failures"].append(f"{test_name}: {str(e)}")
                print(f"[FAIL] {test_name} FAILED: {e}")
            finally:
                self.test_results["tests_run"] += 1
        
        # Final results
        self.print_test_summary()
    
    async def test_update_analysis(self):
        """Test Claude Opus 4 update analysis"""
        print("Testing bid card update analysis with Claude Opus 4...")
        
        # Mock current bid card
        current_bid_card = {
            "id": "test-bid-card-123",
            "project_type": "kitchen_renovation",
            "budget_min": 15000,
            "budget_max": 25000,
            "urgency_level": "week",
            "location_city": "Austin",
            "location_state": "TX",
            "requirements": ["granite countertops", "stainless appliances"]
        }
        
        # Mock update request
        update_request = {
            "update_context": {
                "source_agent": "homeowner_agent", 
                "conversation_snippet": "Actually, I think we can increase the budget to $35,000 and I need this done ASAP - emergency timeline!",
                "detected_change_hints": ["budget_increase", "urgency_change"]
            }
        }
        
        # Test the analysis
        analysis = await self.jaa._analyze_bid_card_update(current_bid_card, update_request)
        
        # Verify analysis results
        assert "changes_made" in analysis, "Missing changes_made in analysis"
        assert "updated_bid_card_data" in analysis, "Missing updated_bid_card_data"
        assert "change_summary" in analysis, "Missing change_summary"
        assert "significance_level" in analysis, "Missing significance_level"
        
        print(f"Analysis completed successfully")
        print(f"Change summary: {analysis.get('change_summary', 'N/A')}")
        print(f"Significance level: {analysis.get('significance_level', 'N/A')}")
    
    async def test_contractor_discovery(self):
        """Test contractor discovery for notifications"""
        print("Testing contractor discovery functionality...")
        
        # Get a real bid card from database for testing
        bid_cards = self.jaa.supabase.table("bid_cards").select("*").limit(1).execute()
        
        if not bid_cards.data:
            print("WARNING: No bid cards found, using mock test...")
            affected_contractors = []
        else:
            # Use real bid card
            bid_card = bid_cards.data[0]
            bid_card_id = bid_card["id"]
            print(f"Testing with real bid card: {bid_card_id}")
            
            # Test contractor discovery
            affected_contractors = await self.jaa._find_affected_contractors(bid_card_id)
        
        print(f"Found {len(affected_contractors)} affected contractors")
        
        if affected_contractors:
            contractor = affected_contractors[0]
            
            # Verify contractor data structure
            required_fields = ["contractor_id", "contractor_type", "company_name", 
                             "engagement_status", "requires_notification"]
            
            for field in required_fields:
                assert field in contractor, f"Missing field {field} in contractor data"
            
            print(f"Contractor structure verified: {contractor['company_name']}")
            print(f"Engagement status: {contractor['engagement_status']}")
        
        return affected_contractors
    
    async def test_notification_generation(self):
        """Test notification content generation"""
        print("Testing AI-powered notification content generation...")
        
        # Mock data for notification generation
        current_bid_card = {
            "project_type": "bathroom_renovation",
            "budget_min": 8000,
            "budget_max": 12000,
            "urgency_level": "week"
        }
        
        updated_data = {
            "budget_min": 10000,
            "budget_max": 18000,
            "urgency_level": "urgent"
        }
        
        changes_made = [
            {
                "field": "budget_range",
                "old_value": "$8,000-$12,000",
                "new_value": "$10,000-$18,000",
                "change_type": "increased",
                "change_significance": "major"
            }
        ]
        
        update_request = {
            "update_context": {
                "conversation_snippet": "We decided to increase the budget and need this done urgently"
            }
        }
        
        # Generate notification content
        notification_content = await self.jaa._generate_update_notification_content(
            current_bid_card, updated_data, changes_made, update_request
        )
        
        # Verify notification structure
        required_fields = ["subject", "message_template", "urgency_level", 
                         "call_to_action", "sender", "footer"]
        
        for field in required_fields:
            assert field in notification_content, f"Missing field {field} in notification"
        
        print(f"Subject: {notification_content['subject']}")
        print(f"Urgency level: {notification_content['urgency_level']}")
        print(f"Call to action: {notification_content['call_to_action']}")
        print("Notification content generated successfully")
        
        return notification_content
    
    async def test_complete_update_flow(self):
        """Test complete update flow end-to-end"""
        print("Testing complete bid card update workflow...")
        
        # Get a real bid card for testing
        bid_cards = self.jaa.supabase.table("bid_cards").select("*").limit(1).execute()
        
        if not bid_cards.data:
            print("WARNING: No bid cards found for complete flow test")
            return
            
        bid_card = bid_cards.data[0]
        bid_card_id = bid_card["id"]
        original_budget_max = bid_card.get("budget_max", 15000)
        
        print(f"Testing complete flow with bid card: {bid_card_id}")
        print(f"Original budget max: ${original_budget_max}")
        
        # Create update request
        update_request = {
            "update_context": {
                "source_agent": "test_suite",
                "conversation_snippet": "I need to increase the budget and make this more urgent",
                "detected_change_hints": ["budget_increase", "urgency_change"]
            }
        }
        
        # Run complete update process
        result = await self.jaa.update_existing_bid_card(bid_card_id, update_request)
        
        # Verify result structure
        assert result["success"] == True, f"Update failed: {result.get('error')}"
        assert "update_summary" in result, "Missing update_summary"
        assert "affected_contractors" in result, "Missing affected_contractors" 
        assert "notification_content" in result, "Missing notification_content"
        assert "next_actions" in result, "Missing next_actions"
        
        update_summary = result["update_summary"]
        assert "changes_made" in update_summary, "Missing changes_made in summary"
        assert "change_summary" in update_summary, "Missing change_summary"
        
        print(f"Update successful: {len(result['affected_contractors'])} contractors affected")
        print(f"Changes made: {len(update_summary['changes_made'])} modifications")
        print(f"Next actions: {', '.join(result['next_actions'])}")
        
        print("Complete update workflow successful")
        return result
    
    async def test_api_integration(self):
        """Test API endpoint integration"""
        print("Testing JAA API endpoint integration...")
        
        # Test imports to ensure API integration works
        try:
            from routers.jaa_routes import router, jaa_agent, update_bid_card_with_jaa
            print("API router imports successful")
            
            # Verify endpoint exists
            routes = [route.path for route in router.routes]
            assert "/update/{bid_card_id}" in routes, "Update endpoint not found in router"
            print("Update endpoint found in router")
            
        except ImportError as e:
            raise AssertionError(f"API integration failed: {e}")
        
        print("API integration verified")
    
    async def test_error_handling(self):
        """Test error handling in update system"""
        print("Testing error handling...")
        
        # Test with non-existent bid card
        result = await self.jaa.update_existing_bid_card("non-existent-id", {
            "update_context": {"source_agent": "test"}
        })
        
        assert result["success"] == False, "Should fail with non-existent bid card"
        assert "not found" in result["error"].lower(), "Should have 'not found' error message"
        print("Non-existent bid card error handling works")
        
        print("Error handling tests passed")
    
    def print_test_summary(self):
        """Print final test results"""
        print("\n" + "="*80)
        print("JAA UPDATE SYSTEM - TEST RESULTS SUMMARY")
        print("="*80)
        
        results = self.test_results
        print(f"Total Tests Run: {results['tests_run']}")
        print(f"Tests Passed: {results['tests_passed']}")
        print(f"Tests Failed: {results['tests_failed']}")
        
        if results["tests_failed"] > 0:
            print(f"\nFAILURES:")
            for failure in results["failures"]:
                print(f"  - {failure}")
        
        success_rate = (results["tests_passed"] / results["tests_run"]) * 100 if results["tests_run"] > 0 else 0
        print(f"\nSuccess Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("JAA UPDATE SYSTEM IS PRODUCTION READY!")
        elif success_rate >= 70:
            print("JAA UPDATE SYSTEM NEEDS MINOR FIXES")
        else:
            print("JAA UPDATE SYSTEM NEEDS MAJOR WORK")

async def main():
    """Main test execution"""
    test_suite = JAUpdateTestSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())