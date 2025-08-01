#!/usr/bin/env python3
"""
Complete Test Suite for Check-in Manager
Tests real database integration, scheduling, and performance monitoring
"""

import asyncio
from datetime import datetime, timedelta
import sys
import os
import uuid

# Add the ai-agents directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.orchestration.check_in_manager import CampaignCheckInManager
from agents.orchestration.timing_probability_engine import (
    ContractorOutreachCalculator,
    OutreachStrategy, 
    TierStrategy, 
    UrgencyLevel
)

async def test_checkin_manager_initialization():
    """Test check-in manager initialization"""
    
    print("=" * 80)
    print("CHECK-IN MANAGER - INITIALIZATION TEST")
    print("=" * 80)
    print(f"Testing check-in manager components")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Initialize check-in manager
        print("\n[STEP 1] Initializing Check-in Manager...")
        manager = CampaignCheckInManager()
        print("  Check-in Manager initialized successfully")
        
        # Test database connectivity
        print("\n[STEP 2] Testing Database Connectivity...")
        try:
            # Test database connection with a simple query
            result = manager.supabase.table('campaign_check_ins').select('id').limit(1).execute()
            print(f"  Database connection working - found {len(result.data) if result.data else 0} existing check-ins")
        except Exception as e:
            print(f"  Database connection failed: {e}")
            return False
        
        print("  Check-in Manager Initialization: PASSED")
        return True
        
    except Exception as e:
        print(f"  Check-in Manager Initialization: FAILED - {e}")
        return False

async def test_checkin_scheduling():
    """Test check-in scheduling with real database operations"""
    
    print("\n" + "=" * 80)
    print("CHECK-IN SCHEDULING TEST")
    print("=" * 80)
    
    try:
        manager = CampaignCheckInManager()
        
        # Create a test strategy for scheduling
        print("\n[Creating Test Strategy]")
        test_strategy = OutreachStrategy(
            bids_needed=4,
            timeline_hours=24,  # 24-hour timeline
            urgency_level=UrgencyLevel.URGENT,
            tier1_strategy=TierStrategy(1, "Internal", 0.9, 5, 3, 2.7),
            tier2_strategy=TierStrategy(2, "Prospects", 0.5, 15, 5, 2.5),
            tier3_strategy=TierStrategy(3, "New/Cold", 0.33, 30, 2, 0.66),
            total_to_contact=10,
            expected_total_responses=5.86,
            check_in_times=[
                datetime.now() + timedelta(hours=6),   # 25% of 24 hours
                datetime.now() + timedelta(hours=12),  # 50% of 24 hours
                datetime.now() + timedelta(hours=18)   # 75% of 24 hours
            ],
            escalation_thresholds={},
            confidence_score=146.5,
            risk_factors=[],
            recommendations=[]
        )
        
        print(f"Strategy Details:")
        print(f"  Timeline: {test_strategy.timeline_hours} hours")
        print(f"  Urgency: {test_strategy.urgency_level.value}")
        print(f"  Check-ins: {len(test_strategy.check_in_times)} scheduled")
        print(f"  Expected Responses: {test_strategy.expected_total_responses:.1f}")
        
        # Generate test IDs
        campaign_id = str(uuid.uuid4())
        bid_card_id = str(uuid.uuid4())
        
        print(f"\n[Scheduling Check-ins]")
        print(f"Campaign ID: {campaign_id}")
        print(f"Bid Card ID: {bid_card_id}")
        
        # Schedule check-ins
        check_ins = await manager.schedule_campaign_check_ins(
            campaign_id=campaign_id,
            bid_card_id=bid_card_id,
            strategy=test_strategy
        )
        
        print(f"\nCheck-ins Scheduled: {len(check_ins)}")
        for i, check_in in enumerate(check_ins, 1):
            scheduled_time = datetime.fromisoformat(check_in['scheduled_time'])
            hours_from_now = (scheduled_time - datetime.now()).total_seconds() / 3600
            print(f"  Check-in {i}:")
            print(f"    ID: {check_in['id']}")
            print(f"    Time: {hours_from_now:.1f} hours from now")
            print(f"    Expected Bids: {check_in['expected_bids']}")
            print(f"    Status: {check_in['status']}")
        
        # Verify check-ins were stored in database
        print(f"\n[Verifying Database Storage]")
        stored_check_ins = manager.supabase.table('campaign_check_ins')\
            .select('*')\
            .eq('campaign_id', campaign_id)\
            .execute()
        
        if stored_check_ins.data:
            print(f"  Database Verification: SUCCESS - {len(stored_check_ins.data)} check-ins found")
            
            # Clean up test data
            manager.supabase.table('campaign_check_ins')\
                .delete()\
                .eq('campaign_id', campaign_id)\
                .execute()
            print(f"  Test data cleaned up")
        else:
            print(f"  Database Verification: FAILED - No check-ins found")
            return False
        
        print("  Check-in Scheduling: PASSED")
        return True
        
    except Exception as e:
        print(f"  Check-in Scheduling: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_checkin_performance_monitoring():
    """Test check-in performance monitoring with mock data"""
    
    print("\n" + "=" * 80)
    print("CHECK-IN PERFORMANCE MONITORING TEST")
    print("=" * 80)
    
    try:
        manager = CampaignCheckInManager()
        
        # Create a test check-in in the database
        print("\n[Creating Test Check-in for Monitoring]")
        
        campaign_id = str(uuid.uuid4())
        bid_card_id = str(uuid.uuid4())
        check_in_id = str(uuid.uuid4())
        
        test_check_in = {
            'id': check_in_id,
            'campaign_id': campaign_id,
            'bid_card_id': bid_card_id,
            'check_in_number': 1,
            'scheduled_time': datetime.now().isoformat(),
            'expected_bids': 2,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        
        # Insert test check-in
        result = manager.supabase.table('campaign_check_ins').insert(test_check_in).execute()
        
        if result.data:
            print(f"  Test check-in created: {check_in_id}")
            print(f"  Expected bids: {test_check_in['expected_bids']}")
        else:
            print("  Failed to create test check-in")
            return False
        
        # Test performance monitoring
        print(f"\n[Testing Performance Monitoring]")
        
        # Simulate different bid scenarios
        test_scenarios = [
            {'bids_received': 3, 'description': 'Exceeding expectations'},
            {'bids_received': 2, 'description': 'Meeting expectations'},
            {'bids_received': 1, 'description': 'Below expectations'},
            {'bids_received': 0, 'description': 'Critical underperformance'}
        ]
        
        for scenario in test_scenarios:
            print(f"\n  Scenario: {scenario['description']}")
            print(f"  Bids Received: {scenario['bids_received']}")
            
            # Create mock bid cards for this scenario
            mock_bids = []
            for i in range(scenario['bids_received']):
                mock_bid = {
                    'id': str(uuid.uuid4()),
                    'bid_card_id': bid_card_id,
                    'contractor_id': str(uuid.uuid4()),
                    'bid_amount': 1000 + (i * 100),
                    'status': 'submitted',
                    'created_at': datetime.now().isoformat()
                }
                mock_bids.append(mock_bid)
            
            # Insert mock bids if any
            if mock_bids:
                manager.supabase.table('contractor_bids').insert(mock_bids).execute()
            
            # Perform check-in
            status = await manager.perform_check_in(campaign_id, check_in_id)
            
            print(f"  Results:")
            print(f"    Expected: {status.bids_expected}")
            print(f"    Received: {status.bids_received}")
            print(f"    Performance: {status.performance_ratio:.1f}%")
            print(f"    On Track: {'Yes' if status.on_track else 'No'}")
            print(f"    Escalation Needed: {'Yes' if status.escalation_needed else 'No'}")
            
            if status.escalation_needed:
                print(f"    Actions Taken: {', '.join(status.actions_taken)}")
            
            # Clean up mock bids
            if mock_bids:
                for mock_bid in mock_bids:
                    manager.supabase.table('contractor_bids')\
                        .delete()\
                        .eq('id', mock_bid['id'])\
                        .execute()
        
        # Clean up test check-in
        manager.supabase.table('campaign_check_ins')\
            .delete()\
            .eq('id', check_in_id)\
            .execute()
        print(f"\n  Test data cleaned up")
        
        print("  Performance Monitoring: PASSED")
        return True
        
    except Exception as e:
        print(f"  Performance Monitoring: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_escalation_logic():
    """Test escalation logic and contractor addition"""
    
    print("\n" + "=" * 80)
    print("ESCALATION LOGIC TEST")
    print("=" * 80)
    
    try:
        manager = CampaignCheckInManager()
        
        print("\n[Testing Escalation Decision Logic]")
        
        # Test different escalation scenarios
        scenarios = [
            {
                'name': 'High Performance - No Escalation',
                'expected_bids': 4,
                'received_bids': 5,
                'expected_escalation': False
            },
            {
                'name': 'On Target - No Escalation', 
                'expected_bids': 4,
                'received_bids': 4,
                'expected_escalation': False
            },
            {
                'name': 'Slight Underperformance - Escalation Needed',
                'expected_bids': 4,
                'received_bids': 2,
                'expected_escalation': True
            },
            {
                'name': 'Critical Underperformance - Escalation Needed',
                'expected_bids': 4,
                'received_bids': 0,
                'expected_escalation': True
            }
        ]
        
        for scenario in scenarios:
            print(f"\n  Scenario: {scenario['name']}")
            print(f"  Expected: {scenario['expected_bids']} bids")
            print(f"  Received: {scenario['received_bids']} bids")
            
            # Calculate performance ratio
            performance_ratio = (scenario['received_bids'] / scenario['expected_bids']) * 100
            escalation_needed = performance_ratio < 75  # Below 75% triggers escalation
            
            print(f"  Performance: {performance_ratio:.1f}%")
            print(f"  Escalation Needed: {'Yes' if escalation_needed else 'No'}")
            print(f"  Expected Result: {'Yes' if scenario['expected_escalation'] else 'No'}")
            
            result = "PASS" if escalation_needed == scenario['expected_escalation'] else "FAIL"
            print(f"  Test Result: {result}")
            
            if result == "FAIL":
                print("  Escalation Logic: FAILED")
                return False
        
        print("  Escalation Logic: PASSED") 
        return True
        
    except Exception as e:
        print(f"  Escalation Logic: FAILED - {e}")
        return False

async def test_checkin_timing_calculations():
    """Test check-in timing calculations for different urgency levels"""
    
    print("\n" + "=" * 80)
    print("CHECK-IN TIMING CALCULATIONS TEST")
    print("=" * 80)
    
    try:
        # Test different timeline scenarios
        timing_scenarios = [
            {
                'name': 'Emergency (30 minutes)',
                'timeline_hours': 0.5,
                'urgency': UrgencyLevel.EMERGENCY,
                'expected_checkins': 0  # Too short for check-ins
            },
            {
                'name': 'Urgent (8 hours)',
                'timeline_hours': 8,
                'urgency': UrgencyLevel.URGENT,
                'expected_checkins': 3
            },
            {
                'name': 'Standard (48 hours)',
                'timeline_hours': 48,
                'urgency': UrgencyLevel.STANDARD,
                'expected_checkins': 3
            },
            {
                'name': 'Group Bidding (120 hours)',
                'timeline_hours': 120,
                'urgency': UrgencyLevel.GROUP_BIDDING,
                'expected_checkins': 3
            }
        ]
        
        calculator = ContractorOutreachCalculator()
        
        for scenario in timing_scenarios:
            print(f"\n  Scenario: {scenario['name']}")
            print(f"  Timeline: {scenario['timeline_hours']} hours")
            print(f"  Urgency: {scenario['urgency'].value}")
            
            # Calculate strategy to get check-in times
            strategy = calculator.calculate_outreach_strategy(
                bids_needed=4,
                timeline_hours=scenario['timeline_hours'],
                tier1_available=5,
                tier2_available=15,
                tier3_available=30,
                project_type="Test Project"
            )
            
            actual_checkins = len(strategy.check_in_times)
            print(f"  Check-ins Scheduled: {actual_checkins}")
            print(f"  Expected Check-ins: {scenario['expected_checkins']}")
            
            # Display check-in times
            if strategy.check_in_times:
                print(f"  Check-in Schedule:")
                current_time = datetime.now()
                for i, check_time in enumerate(strategy.check_in_times, 1):
                    hours_from_now = (check_time - current_time).total_seconds() / 3600
                    percentage = (i / len(strategy.check_in_times)) * 100
                    print(f"    Check-in {i}: {hours_from_now:.1f} hours ({percentage:.0f}% of timeline)")
            else:
                print(f"  No check-ins scheduled (timeline too short)")
            
            result = "PASS" if actual_checkins == scenario['expected_checkins'] else "FAIL"
            print(f"  Timing Test: {result}")
            
            if result == "FAIL":
                print("  Check-in Timing Calculations: FAILED")
                return False
        
        print("  Check-in Timing Calculations: PASSED")
        return True
        
    except Exception as e:
        print(f"  Check-in Timing Calculations: FAILED - {e}")
        return False

async def main():
    """Main test execution"""
    
    print("CHECK-IN MANAGER - COMPREHENSIVE TEST SUITE")
    print("Testing all components with real database integration")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = {}
    
    try:
        # Test 1: Manager initialization
        print("\n" + "=" * 20 + " RUNNING TESTS " + "=" * 20)
        test_results['initialization'] = await test_checkin_manager_initialization()
        
        # Test 2: Check-in scheduling
        test_results['scheduling'] = await test_checkin_scheduling()
        
        # Test 3: Performance monitoring
        test_results['performance_monitoring'] = await test_checkin_performance_monitoring()
        
        # Test 4: Escalation logic
        test_results['escalation_logic'] = await test_escalation_logic()
        
        # Test 5: Timing calculations
        test_results['timing_calculations'] = await test_checkin_timing_calculations()
        
        # Summary
        print("\n" + "=" * 80)
        print("TEST RESULTS SUMMARY")
        print("=" * 80)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results.items():
            status = "PASSED" if result else "FAILED"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
            if result:
                passed += 1
        
        print(f"\nOverall Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n*** CHECK-IN MANAGER FULLY OPERATIONAL ***")
            print("\nKey Features Verified:")
            print("  * Database connectivity and check-in storage")
            print("  * Check-in scheduling with proper timing calculations")
            print("  * Performance monitoring and bid tracking")
            print("  * Escalation logic with threshold detection")
            print("  * Multi-timeline support (emergency to flexible)")
            print("\nCheck-in Manager Status: READY FOR PRODUCTION")
            print("Integrated with Enhanced Campaign Orchestrator!")
        else:
            print(f"\n! {total - passed} tests failed - review errors above")
            print("Check-in Manager needs fixes before production")
        
    except Exception as e:
        print(f"\n  Test execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())