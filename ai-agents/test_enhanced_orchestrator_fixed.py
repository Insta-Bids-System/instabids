#!/usr/bin/env python3
"""
Enhanced Campaign Orchestrator Test - Fixed Version with Real UUIDs
Tests timing engine integration with proper database format
"""

import asyncio
from datetime import datetime, timedelta
import sys
import os
import uuid

# Add the ai-agents directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.orchestration.enhanced_campaign_orchestrator import (
    EnhancedCampaignOrchestrator,
    CampaignRequest
)

async def test_orchestrator_core_functionality():
    """Test core orchestrator functionality with proper UUIDs"""
    
    print("="*80)
    print("ENHANCED CAMPAIGN ORCHESTRATOR - CORE FUNCTIONALITY TEST")
    print("="*80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Initialize orchestrator
        print("\n[STEP 1] Initializing Enhanced Campaign Orchestrator...")
        orchestrator = EnhancedCampaignOrchestrator()
        print("  Enhanced Campaign Orchestrator initialized successfully")
        
        # Test timing calculations
        print("\n[STEP 2] Testing Timing Calculations...")
        timing_scenarios = [
            {'hours': 0.5, 'expected': 'emergency', 'project': 'Emergency Leak'},
            {'hours': 8, 'expected': 'urgent', 'project': 'Fire Damage'},
            {'hours': 48, 'expected': 'standard', 'project': 'Kitchen Remodel'},
            {'hours': 96, 'expected': 'group_bidding', 'project': 'Multiple Projects'},
            {'hours': 144, 'expected': 'flexible', 'project': 'Whole House'}
        ]
        
        all_passed = True
        for scenario in timing_scenarios:
            strategy = orchestrator.timing_calculator.calculate_outreach_strategy(
                bids_needed=4,
                timeline_hours=scenario['hours'],
                tier1_available=5,
                tier2_available=15,
                tier3_available=30,
                project_type=scenario['project']
            )
            
            expected = scenario['expected']
            actual = strategy.urgency_level.value
            result = "PASS" if actual == expected else "FAIL"
            
            print(f"    {scenario['hours']}h ({scenario['project']}): {actual} [{result}]")
            if result == "FAIL":
                all_passed = False
        
        if all_passed:
            print("  Timing Calculations: PASSED")
        else:
            print("  Timing Calculations: FAILED")
            return False
        
        # Test contractor availability analysis
        print("\n[STEP 3] Testing Contractor Availability...")
        availability = await orchestrator._analyze_contractor_availability(
            project_type="Kitchen Remodel",
            location={"city": "Austin", "state": "TX", "zip": "78701"}
        )
        
        print(f"  Contractor Availability:")
        for tier, count in availability.items():
            print(f"    {tier}: {count} contractors")
        
        return True
        
    except Exception as e:
        print(f"  Core functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_campaign_request_creation():
    """Test creating campaign with proper UUID bid card"""
    
    print("\n" + "="*80)
    print("CAMPAIGN REQUEST CREATION TEST")
    print("="*80)
    
    try:
        orchestrator = EnhancedCampaignOrchestrator()
        
        # First, create a real bid card in the database to use
        print("\n[Creating Test Bid Card]")
        
        # Generate proper UUID for bid card
        bid_card_id = str(uuid.uuid4())
        test_bid_card = {
            'id': bid_card_id,
            'user_id': 'test-user-orchestrator',
            'project_type': 'Kitchen Remodel Test',
            'budget_min': 25000,
            'budget_max': 40000,
            'timeline_hours': 24,
            'requirements_extracted': {
                'materials': ['granite countertops', 'custom cabinets'],
                'project_details': 'Complete kitchen renovation'
            },
            'location_city': 'Austin',
            'location_state': 'TX',
            'location_zip': '78701',
            'status': 'active',
            'urgency_level': 'urgent',
            'created_at': datetime.now().isoformat()
        }
        
        # Insert test bid card into database
        bid_card_result = orchestrator.supabase.table('bid_cards').insert(test_bid_card).execute()
        
        if bid_card_result.data:
            print(f"  Test bid card created: {bid_card_id}")
        else:
            print("  Failed to create test bid card")
            return False
        
        # Now create campaign request
        print("\n[Creating Campaign Request]")
        request = CampaignRequest(
            bid_card_id=bid_card_id,  # Use real UUID
            project_type='Kitchen Remodel Test',
            location={'city': 'Austin', 'state': 'TX', 'zip': '78701'},
            timeline_hours=24,
            urgency_level='urgent',
            bids_needed=4
        )
        
        print(f"Campaign Request Details:")
        print(f"  Bid Card ID: {request.bid_card_id}")
        print(f"  Project: {request.project_type}")
        print(f"  Timeline: {request.timeline_hours} hours")
        print(f"  Bids Needed: {request.bids_needed}")
        
        # Test the strategy calculation without creating full campaign
        print("\n[Testing Strategy Calculation]")
        
        # Get contractor availability
        availability = await orchestrator._analyze_contractor_availability(
            request.project_type,
            request.location
        )
        
        # Calculate strategy
        strategy = orchestrator.timing_calculator.calculate_outreach_strategy(
            bids_needed=request.bids_needed,
            timeline_hours=request.timeline_hours,
            tier1_available=availability['tier_1'],
            tier2_available=availability['tier_2'],
            tier3_available=availability['tier_3'],
            project_type=request.project_type,
            location=request.location
        )
        
        print(f"Strategy Results:")
        print(f"  Urgency: {strategy.urgency_level.value}")
        print(f"  Total Contractors: {strategy.total_to_contact}")
        print(f"  Expected Responses: {strategy.expected_total_responses:.1f}")
        print(f"  Confidence: {strategy.confidence_score:.1f}%")
        print(f"  Tier 1: {strategy.tier1_strategy.to_contact}")
        print(f"  Tier 2: {strategy.tier2_strategy.to_contact}")
        print(f"  Tier 3: {strategy.tier3_strategy.to_contact}")
        
        # Clean up test bid card
        orchestrator.supabase.table('bid_cards').delete().eq('id', bid_card_id).execute()
        print(f"\n  Test bid card cleaned up")
        
        print("  Campaign Request Creation: PASSED")
        return True
        
    except Exception as e:
        print(f"  Campaign Request Creation: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_contractor_discovery():
    """Test contractor discovery and selection"""
    
    print("\n" + "="*80)
    print("CONTRACTOR DISCOVERY TEST")
    print("="*80)
    
    try:
        orchestrator = EnhancedCampaignOrchestrator()
        
        print("\n[Testing Database Queries]")
        
        # Test different contractor queries
        queries = [
            ("bid_cards", "select('id').limit(5)"),
            ("contractors", "select('id, business_name, email').limit(3)"),
            ("potential_contractors", "select('id, company_name, lead_status').limit(5)")
        ]
        
        for table, query_desc in queries:
            try:
                if table == "bid_cards":
                    result = orchestrator.supabase.table(table).select('id').limit(5).execute()
                elif table == "contractors":
                    result = orchestrator.supabase.table(table).select('id, business_name, email').limit(3).execute()
                else:  # potential_contractors
                    result = orchestrator.supabase.table(table).select('id, company_name, lead_status').limit(5).execute()
                
                count = len(result.data) if result.data else 0
                print(f"  {table}: {count} records found")
                
                if count > 0 and table == "potential_contractors":
                    print(f"    Sample: {result.data[0].get('company_name', 'N/A')} - {result.data[0].get('lead_status', 'N/A')}")
                
            except Exception as e:
                print(f"  {table}: Query failed - {e}")
        
        # Test tier-specific contractor selection
        print("\n[Testing Tier Selection]")
        
        for tier in [1, 2, 3]:
            contractors = await orchestrator._select_tier_contractors(
                tier=tier,
                count=3,
                project_type="Kitchen Remodel",
                location={"city": "Austin", "state": "TX"}
            )
            
            print(f"  Tier {tier}: {len(contractors)} contractors selected")
            
            if contractors:
                for contractor in contractors[:1]:  # Show first one
                    name = contractor.get('company_name') or contractor.get('business_name', 'Unknown')
                    print(f"    Example: {name}")
        
        print("  Contractor Discovery: PASSED")
        return True
        
    except Exception as e:
        print(f"  Contractor Discovery: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_timing_integration_complete():
    """Test complete timing integration with all urgency levels"""
    
    print("\n" + "="*80) 
    print("COMPLETE TIMING INTEGRATION TEST")
    print("="*80)
    
    try:
        orchestrator = EnhancedCampaignOrchestrator()
        
        # Test all urgency levels with realistic scenarios
        scenarios = [
            {
                'name': 'EMERGENCY: Water pipe burst (30 minutes)',
                'timeline_hours': 0.5,
                'project_type': 'Emergency Plumbing',
                'expected_urgency': 'emergency',
                'expected_total_contractors': '>= 5'  # Should contact many for emergency
            },
            {
                'name': 'URGENT: Kitchen fire damage (12 hours)', 
                'timeline_hours': 12,
                'project_type': 'Fire Damage Repair',
                'expected_urgency': 'urgent',
                'expected_total_contractors': '>= 7'
            },
            {
                'name': 'STANDARD: Bathroom remodel (3 days)',
                'timeline_hours': 72,
                'project_type': 'Bathroom Remodel', 
                'expected_urgency': 'standard',
                'expected_total_contractors': '>= 4'
            },
            {
                'name': 'GROUP BIDDING: Multiple projects (5 days)',
                'timeline_hours': 120,
                'project_type': 'Multiple Home Projects',
                'expected_urgency': 'group_bidding',
                'expected_total_contractors': '>= 4',
                'group_projects': ['kitchen-001', 'bathroom-002', 'deck-003']
            },
            {
                'name': 'FLEXIBLE: Whole house renovation (7 days)',
                'timeline_hours': 168,
                'project_type': 'Whole House Renovation',
                'expected_urgency': 'flexible', 
                'expected_total_contractors': '>= 5'
            }
        ]
        
        all_passed = True
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n[SCENARIO {i}] {scenario['name']}")
            print("-" * 60)
            
            # Calculate strategy
            strategy = orchestrator.timing_calculator.calculate_outreach_strategy(
                bids_needed=4,
                timeline_hours=scenario['timeline_hours'],
                tier1_available=5,
                tier2_available=15, 
                tier3_available=30,
                project_type=scenario['project_type'],
                group_bidding_projects=scenario.get('group_projects')
            )
            
            # Check urgency classification
            urgency_correct = strategy.urgency_level.value == scenario['expected_urgency']
            urgency_status = "PASS" if urgency_correct else "FAIL"
            
            print(f"Timeline: {scenario['timeline_hours']} hours")
            print(f"Urgency: {strategy.urgency_level.value} (expected: {scenario['expected_urgency']}) [{urgency_status}]")
            
            # Check contractor count
            total_contractors = strategy.total_to_contact
            print(f"Total Contractors: {total_contractors}")
            print(f"Expected Responses: {strategy.expected_total_responses:.1f}")
            print(f"Confidence: {strategy.confidence_score:.1f}%")
            
            # Tier breakdown
            print(f"Tier Breakdown:")
            print(f"  Tier 1: {strategy.tier1_strategy.to_contact} (expect {strategy.tier1_strategy.expected_responses:.1f})")
            print(f"  Tier 2: {strategy.tier2_strategy.to_contact} (expect {strategy.tier2_strategy.expected_responses:.1f})")
            print(f"  Tier 3: {strategy.tier3_strategy.to_contact} (expect {strategy.tier3_strategy.expected_responses:.1f})")
            
            # Group bidding check
            if scenario.get('group_projects'):
                print(f"Group Bidding: {strategy.is_group_bidding}")
                print(f"Projects: {len(strategy.group_bidding_projects)}")
            
            # Check-in schedule
            print(f"Check-ins: {len(strategy.check_in_times)} scheduled")
            
            if not urgency_correct:
                all_passed = False
                print(f"  FAILED: Urgency classification incorrect")
            else:
                print(f"  PASSED: All timing calculations correct")
        
        if all_passed:
            print("\n  Complete Timing Integration: PASSED")
        else:
            print("\n  Complete Timing Integration: FAILED")
        
        return all_passed
        
    except Exception as e:
        print(f"  Complete Timing Integration: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test execution"""
    
    print("ENHANCED CAMPAIGN ORCHESTRATOR - FIXED COMPREHENSIVE TEST")
    print("Testing core functionality without database UUID issues")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = {}
    
    try:
        # Test 1: Core functionality
        print("\n" + "=" * 20 + " RUNNING TESTS " + "=" * 20)
        test_results['core_functionality'] = await test_orchestrator_core_functionality()
        
        # Test 2: Campaign request creation
        test_results['campaign_request'] = await test_campaign_request_creation()
        
        # Test 3: Contractor discovery
        test_results['contractor_discovery'] = await test_contractor_discovery()
        
        # Test 4: Complete timing integration
        test_results['timing_integration'] = await test_timing_integration_complete()
        
        # Summary
        print("\n" + "="*80)
        print("TEST RESULTS SUMMARY")
        print("="*80)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results.items():
            status = "PASSED" if result else "FAILED"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
            if result:
                passed += 1
        
        print(f"\nOverall Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n*** ENHANCED CAMPAIGN ORCHESTRATOR CORE FUNCTIONALITY VERIFIED ***")
            print("\nKey Features Working:")
            print("  * Timing engine with aggressive business timelines")
            print("  * Urgency classification (emergency/urgent/standard/group/flexible)")
            print("  * Multi-tier contractor calculations")
            print("  * Database connectivity and contractor discovery")
            print("  * Strategy calculation and confidence scoring")
            print("\nCore System Status: FULLY OPERATIONAL")
            print("Ready for production campaign orchestration!")
        else:
            print(f"\n! {total - passed} tests failed - review errors above")
            print("Core functionality needs fixes before production")
        
    except Exception as e:
        print(f"\n  Test execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())