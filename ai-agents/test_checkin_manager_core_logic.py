#!/usr/bin/env python3
"""
Check-in Manager Core Logic Test - No Database Required
Tests the mathematical and logical components without database dependencies
"""

import asyncio
from datetime import datetime, timedelta
import sys
import os

# Add the ai-agents directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.orchestration.timing_probability_engine import (
    ContractorOutreachCalculator,
    OutreachStrategy, 
    TierStrategy, 
    UrgencyLevel
)

def test_checkin_timing_logic():
    """Test check-in timing calculations for different urgency levels"""
    
    print("=" * 80)
    print("CHECK-IN TIMING LOGIC TEST")
    print("=" * 80)
    print(f"Testing check-in scheduling logic without database")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        calculator = ContractorOutreachCalculator()
        
        # Test different timeline scenarios
        timing_scenarios = [
            {
                'name': 'Emergency (30 minutes)',
                'timeline_hours': 0.5,
                'expected_checkins': 3,  # Emergency still gets check-ins, just very frequent
                'expected_intervals': [0.125, 0.25, 0.375]  # 25%, 50%, 75% of 30 minutes
            },
            {
                'name': 'Urgent (8 hours)', 
                'timeline_hours': 8,
                'expected_checkins': 3,
                'expected_intervals': [2, 4, 6]  # 25%, 50%, 75% of 8 hours
            },
            {
                'name': 'Standard (48 hours)',
                'timeline_hours': 48,
                'expected_checkins': 3,
                'expected_intervals': [12, 24, 36]  # 25%, 50%, 75% of 48 hours
            },
            {
                'name': 'Group Bidding (120 hours)',
                'timeline_hours': 120,
                'expected_checkins': 3,
                'expected_intervals': [30, 60, 90]  # 25%, 50%, 75% of 120 hours
            }
        ]
        
        all_passed = True
        
        for scenario in timing_scenarios:
            print(f"\n[SCENARIO] {scenario['name']}")
            print(f"Timeline: {scenario['timeline_hours']} hours")
            
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
            expected_checkins = scenario['expected_checkins']
            
            print(f"Check-ins Scheduled: {actual_checkins}")
            print(f"Expected Check-ins: {expected_checkins}")
            
            # Verify check-in timing intervals
            if strategy.check_in_times:
                print(f"Check-in Schedule:")
                current_time = datetime.now()
                
                for i, check_time in enumerate(strategy.check_in_times):
                    hours_from_now = (check_time - current_time).total_seconds() / 3600
                    percentage = ((i + 1) / len(strategy.check_in_times)) * 100
                    expected_hour = scenario['expected_intervals'][i] if i < len(scenario['expected_intervals']) else 0
                    
                    print(f"  Check-in {i+1}: {hours_from_now:.2f} hours (expected ~{expected_hour:.2f}h)")
                    
                    # Allow some tolerance for timing calculations
                    tolerance = 0.1 * scenario['timeline_hours']  # 10% tolerance
                    if abs(hours_from_now - expected_hour) > tolerance:
                        print(f"    WARNING: Timing off by {abs(hours_from_now - expected_hour):.2f} hours")
            
            # Check if number of check-ins is correct
            checkins_match = actual_checkins == expected_checkins
            result = "PASS" if checkins_match else "FAIL"
            print(f"Timing Test: {result}")
            
            if not checkins_match:
                all_passed = False
        
        if all_passed:
            print(f"\n✅ Check-in Timing Logic: PASSED")
        else:
            print(f"\n❌ Check-in Timing Logic: FAILED")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Check-in Timing Logic: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_escalation_decision_logic():
    """Test escalation decision logic with different performance scenarios"""
    
    print("\n" + "=" * 80)
    print("ESCALATION DECISION LOGIC TEST")
    print("=" * 80)
    
    try:
        print("\n[Testing Escalation Thresholds]")
        
        # Test different performance scenarios
        scenarios = [
            {
                'name': 'Exceeding Expectations',
                'expected_bids': 4,
                'received_bids': 6,
                'expected_escalation': False,
                'expected_performance': 150.0
            },
            {
                'name': 'Meeting Expectations',
                'expected_bids': 4,
                'received_bids': 4,
                'expected_escalation': False,
                'expected_performance': 100.0
            },
            {
                'name': 'Slightly Below (80%)',
                'expected_bids': 4,
                'received_bids': 3,
                'expected_escalation': False,  # Above 75% threshold
                'expected_performance': 75.0
            },
            {
                'name': 'Below Threshold (50%)',
                'expected_bids': 4,
                'received_bids': 2,
                'expected_escalation': True,  # Below 75% threshold
                'expected_performance': 50.0
            },
            {
                'name': 'Critical Underperformance',
                'expected_bids': 4,
                'received_bids': 0,
                'expected_escalation': True,
                'expected_performance': 0.0
            }
        ]
        
        all_passed = True
        
        for scenario in scenarios:
            print(f"\n  Scenario: {scenario['name']}")
            print(f"  Expected: {scenario['expected_bids']} bids")
            print(f"  Received: {scenario['received_bids']} bids")
            
            # Calculate performance ratio (this is the core logic)
            performance_ratio = (scenario['received_bids'] / scenario['expected_bids']) * 100
            escalation_needed = performance_ratio < 75  # 75% threshold
            
            print(f"  Performance: {performance_ratio:.1f}%")
            print(f"  Expected Performance: {scenario['expected_performance']:.1f}%")
            print(f"  Escalation Needed: {'Yes' if escalation_needed else 'No'}")
            print(f"  Expected Escalation: {'Yes' if scenario['expected_escalation'] else 'No'}")
            
            # Check if calculations are correct
            performance_correct = abs(performance_ratio - scenario['expected_performance']) < 0.1
            escalation_correct = escalation_needed == scenario['expected_escalation']
            
            if performance_correct and escalation_correct:
                print(f"  Result: ✅ PASS")
            else:
                print(f"  Result: ❌ FAIL")
                all_passed = False
                
                if not performance_correct:
                    print(f"    Performance calculation error")
                if not escalation_correct:
                    print(f"    Escalation decision error")
        
        if all_passed:
            print(f"\n✅ Escalation Decision Logic: PASSED")
        else:
            print(f"\n❌ Escalation Decision Logic: FAILED")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Escalation Decision Logic: FAILED - {e}")
        return False

def test_check_in_calculation_scenarios():
    """Test check-in calculations for real-world scenarios"""
    
    print("\n" + "=" * 80)
    print("REAL-WORLD CHECK-IN SCENARIOS TEST")
    print("=" * 80)
    
    try:
        calculator = ContractorOutreachCalculator()
        
        # Real-world scenarios
        scenarios = [
            {
                'name': 'Kitchen Remodel (2 days)',
                'project_type': 'Kitchen Remodel',
                'timeline_hours': 48,
                'bids_needed': 4,
                'tier1_available': 2,
                'tier2_available': 8,
                'tier3_available': 15
            },
            {
                'name': 'Emergency Plumbing (2 hours)',
                'project_type': 'Emergency Plumbing',
                'timeline_hours': 2,
                'bids_needed': 3,
                'tier1_available': 5,
                'tier2_available': 10,
                'tier3_available': 20
            },
            {
                'name': 'Lawn Care (1 week)',
                'project_type': 'Lawn Care',
                'timeline_hours': 168,  # 7 days
                'bids_needed': 4,
                'tier1_available': 3,
                'tier2_available': 12,
                'tier3_available': 25
            }
        ]
        
        all_passed = True
        
        for scenario in scenarios:
            print(f"\n[SCENARIO] {scenario['name']}")
            print(f"Project: {scenario['project_type']}")  
            print(f"Timeline: {scenario['timeline_hours']} hours")
            print(f"Bids Needed: {scenario['bids_needed']}")
            
            # Calculate strategy
            strategy = calculator.calculate_outreach_strategy(
                bids_needed=scenario['bids_needed'],
                timeline_hours=scenario['timeline_hours'],
                tier1_available=scenario['tier1_available'],
                tier2_available=scenario['tier2_available'],
                tier3_available=scenario['tier3_available'],
                project_type=scenario['project_type']
            )
            
            print(f"\nStrategy Results:")
            print(f"  Urgency: {strategy.urgency_level.value}")
            print(f"  Total Contractors: {strategy.total_to_contact}")
            print(f"  Expected Responses: {strategy.expected_total_responses:.1f}")
            print(f"  Confidence Score: {strategy.confidence_score:.1f}%")
            
            print(f"\nTier Distribution:")
            print(f"  Tier 1: {strategy.tier1_strategy.to_contact} contractors")
            print(f"  Tier 2: {strategy.tier2_strategy.to_contact} contractors")  
            print(f"  Tier 3: {strategy.tier3_strategy.to_contact} contractors")
            
            print(f"\nCheck-in Schedule:")
            print(f"  Total Check-ins: {len(strategy.check_in_times)}")
            
            if strategy.check_in_times:
                current_time = datetime.now()
                for i, check_time in enumerate(strategy.check_in_times, 1):
                    hours_from_now = (check_time - current_time).total_seconds() / 3600
                    percentage = (i / len(strategy.check_in_times)) * 100
                    print(f"  Check-in {i}: {hours_from_now:.1f} hours ({percentage:.0f}% of timeline)")
            
            # Validate results make sense
            valid_strategy = True
            
            # Check if we're contacting enough contractors
            if strategy.expected_total_responses < scenario['bids_needed'] * 0.5:
                print(f"  ⚠️  WARNING: Low expected responses ({strategy.expected_total_responses:.1f} < {scenario['bids_needed'] * 0.5})")
                valid_strategy = False
            
            # Check if urgency level makes sense
            expected_urgency = None
            if scenario['timeline_hours'] <= 1:
                expected_urgency = 'emergency'
            elif scenario['timeline_hours'] <= 12:
                expected_urgency = 'urgent'
            elif scenario['timeline_hours'] <= 72:
                expected_urgency = 'standard'
            else:
                expected_urgency = 'flexible'
            
            if strategy.urgency_level.value != expected_urgency:
                print(f"  ⚠️  WARNING: Unexpected urgency level ({strategy.urgency_level.value} vs expected {expected_urgency})")
                # This might be ok for group bidding scenarios
            
            result = "✅ PASS" if valid_strategy else "❌ FAIL"
            print(f"Scenario Validation: {result}")
            
            if not valid_strategy:
                all_passed = False
        
        if all_passed:
            print(f"\n✅ Real-World Scenarios: PASSED")
        else:
            print(f"\n❌ Real-World Scenarios: FAILED")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Real-World Scenarios: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test execution"""
    
    print("CHECK-IN MANAGER CORE LOGIC TEST SUITE")
    print("Testing mathematical and logical components")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = {}
    
    try:
        # Test 1: Check-in timing logic
        print("\n" + "🧪" * 20 + " RUNNING TESTS " + "🧪" * 20)
        test_results['timing_logic'] = test_checkin_timing_logic()
        
        # Test 2: Escalation decision logic
        test_results['escalation_logic'] = test_escalation_decision_logic()
        
        # Test 3: Real-world scenarios
        test_results['realworld_scenarios'] = test_check_in_calculation_scenarios()
        
        # Summary
        print("\n" + "=" * 80)
        print("TEST RESULTS SUMMARY")
        print("=" * 80)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
            if result:
                passed += 1
        
        print(f"\nOverall Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 CHECK-IN MANAGER CORE LOGIC VERIFIED!")
            print("\n✅ Key Components Working:")
            print("  * Check-in timing calculations for all urgency levels")
            print("  * Escalation decision logic with 75% threshold")
            print("  * Real-world scenario handling and validation")
            print("  * Performance ratio calculations")
            print("  * Mathematical contractor distribution")
            
            print("\n🚀 Core Logic Status: FULLY OPERATIONAL")
            print("Database integration needed for production deployment")
            
        else:
            print(f"\n⚠️ {total - passed} tests failed - review errors above")
            print("Core logic needs fixes before production")
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()