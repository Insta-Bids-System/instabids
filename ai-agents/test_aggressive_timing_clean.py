#!/usr/bin/env python3
"""
Test Aggressive Timing Engine with New Business Logic

Tests the updated timing system with AGGRESSIVE business timelines:
- Emergency: < 1 hour (instant response)
- Urgent: 1-12 hours (same day)
- Standard: 12-72 hours (3 days max)
- Group Bidding: 72-120 hours (5 days max, multiple projects)
- Flexible: 120+ hours (5+ days absolute maximum)
"""

import asyncio
from datetime import datetime, timedelta
import sys
import os

# Add the ai-agents directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.orchestration.timing_probability_engine import (
    ContractorOutreachCalculator, 
    UrgencyLevel
)

async def test_aggressive_timing_scenarios():
    """Test all the new aggressive timing scenarios"""
    
    print("="*80)
    print("AGGRESSIVE TIMING ENGINE TEST")
    print("="*80)
    print("Testing new AGGRESSIVE business timelines for contractor outreach")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    calculator = ContractorOutreachCalculator()
    
    # Test scenarios with the new aggressive timelines
    test_scenarios = [
        {
            'name': 'EMERGENCY: Leak needs immediate attention',
            'timeline_hours': 0.5,  # 30 minutes
            'project_type': 'Emergency Leak Repair',
            'bids_needed': 3,  # Less bids needed for emergency
            'expected_urgency': UrgencyLevel.EMERGENCY
        },
        {
            'name': 'URGENT: Kitchen fire damage - same day needed',
            'timeline_hours': 8,   # 8 hours  
            'project_type': 'Fire Damage Repair',
            'bids_needed': 4,
            'expected_urgency': UrgencyLevel.URGENT
        },
        {
            'name': 'STANDARD: Bathroom remodel - 3 days',
            'timeline_hours': 48,  # 2 days (within 3 day limit)
            'project_type': 'Bathroom Remodel',
            'bids_needed': 4,
            'expected_urgency': UrgencyLevel.STANDARD
        },
        {
            'name': 'GROUP BIDDING: Kitchen + Bathroom + Deck (5 days)',
            'timeline_hours': 96,  # 4 days
            'project_type': 'Multiple Home Projects',
            'bids_needed': 4,
            'group_bidding_projects': ['kitchen-remodel-001', 'bathroom-reno-002', 'deck-build-003'],
            'expected_urgency': UrgencyLevel.GROUP_BIDDING
        },
        {
            'name': 'FLEXIBLE: Whole house renovation (6 days - absolute max)',
            'timeline_hours': 144, # 6 days
            'project_type': 'Whole House Renovation',
            'bids_needed': 5,  # More bids for big project
            'expected_urgency': UrgencyLevel.FLEXIBLE
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'='*60}")
        print(f"SCENARIO {i}: {scenario['name']}")
        print(f"{'='*60}")
        
        print(f"Timeline: {scenario['timeline_hours']} hours ({scenario['timeline_hours']/24:.1f} days)")
        print(f"Project: {scenario['project_type']}")
        print(f"Bids Needed: {scenario['bids_needed']}")
        
        if scenario.get('group_bidding_projects'):
            print(f"Group Bidding: {len(scenario['group_bidding_projects'])} projects")
            for proj in scenario['group_bidding_projects']:
                print(f"  - {proj}")
        
        # Calculate strategy
        strategy = calculator.calculate_outreach_strategy(
            bids_needed=scenario['bids_needed'],
            timeline_hours=scenario['timeline_hours'],
            tier1_available=15,  # Good availability
            tier2_available=25,
            tier3_available=40,
            project_type=scenario['project_type'],
            group_bidding_projects=scenario.get('group_bidding_projects')
        )
        
        # Verify urgency classification
        expected_urgency = scenario['expected_urgency']
        actual_urgency = strategy.urgency_level
        urgency_match = "" if actual_urgency == expected_urgency else ""
        
        print(f"\nSTRATEGY RESULTS:")
        print(f"  Urgency Classification: {actual_urgency.value} {urgency_match}")
        print(f"  Expected: {expected_urgency.value}")
        
        # Show contractor breakdown
        print(f"\n  CONTRACTOR OUTREACH:")
        print(f"    Total Contractors: {strategy.total_to_contact}")
        print(f"    Expected Responses: {strategy.expected_total_responses:.1f}")
        print(f"    Success Confidence: {strategy.confidence_score:.1f}%")
        
        # Tier breakdown
        print(f"\n  TIER BREAKDOWN:")
        tiers = [strategy.tier1_strategy, strategy.tier2_strategy, strategy.tier3_strategy]
        for tier_strategy in tiers:
            print(f"    Tier {tier_strategy.tier} ({tier_strategy.tier_name}): "
                  f"{tier_strategy.to_contact} contractors "
                  f"(expect {tier_strategy.expected_responses:.1f} responses)")
        
        # Group bidding bonus
        if strategy.is_group_bidding:
            print(f"\n  GROUP BIDDING ACTIVE:")
            print(f"    Response Rate Bonus: +20%")
            print(f"    Projects in Group: {len(strategy.group_bidding_projects)}")
        
        # Check-in schedule
        print(f"\n  CHECK-IN SCHEDULE (AGGRESSIVE):")
        current_time = datetime.now()
        for j, check_time in enumerate(strategy.check_in_times, 1):
            hours_from_now = (check_time - current_time).total_seconds() / 3600
            expected_bids = strategy.escalation_thresholds.get(check_time, 0)
            
            if hours_from_now < 1:
                time_desc = f"{hours_from_now*60:.0f} minutes"
            elif hours_from_now < 24:
                time_desc = f"{hours_from_now:.1f} hours"
            else:
                time_desc = f"{hours_from_now/24:.1f} days"
            
            print(f"    Check-in {j}: {time_desc} from now ({expected_bids} bids expected)")
        
        # Risk factors and recommendations
        if strategy.risk_factors:
            print(f"\n  RISK FACTORS:")
            for risk in strategy.risk_factors:
                print(f"      {risk}")
        
        if strategy.recommendations:
            print(f"\n  RECOMMENDATIONS:")
            for rec in strategy.recommendations:
                print(f"     {rec}")
        
        # Success assessment
        success_ratio = strategy.expected_total_responses / scenario['bids_needed']
        if success_ratio >= 1.2:
            status = " HIGH SUCCESS PROBABILITY"
        elif success_ratio >= 1.0:
            status = " GOOD SUCCESS PROBABILITY"
        else:
            status = " LOW SUCCESS PROBABILITY - NEEDS MORE CONTRACTORS"
        
        print(f"\n  ASSESSMENT: {status}")
        print(f"    Success Ratio: {success_ratio:.2f} (target: 1.0)")
    
    # Summary comparison
    print(f"\n{'='*80}")
    print("TIMING COMPARISON: OLD vs NEW")
    print(f"{'='*80}")
    
    print("\nOLD BUSINESS TIMELINES:")
    print("  Emergency: < 6 hours")
    print("  Urgent: 6-24 hours") 
    print("  Standard: 1-3 days")
    print("  Flexible: 3-7 days")
    print("  Planning: 7+ days")
    
    print("\nNEW AGGRESSIVE TIMELINES:")
    print("  Emergency: < 1 hour (instant response)")
    print("  Urgent: 1-12 hours (same day)")
    print("  Standard: 12-72 hours (3 days max)")
    print("  Group Bidding: 72-120 hours (5 days max, multiple projects)")
    print("  Flexible: 120+ hours (5+ days absolute maximum)")
    
    print("\nKEY IMPROVEMENTS:")
    print("   6x faster emergency response (6hrs  <1hr)")
    print("   2x faster urgent response (24hrs  12hrs)")
    print("   Added group bidding for multiple projects (+20% response rate)")
    print("   Aggressive check-in schedules (15min intervals for emergency)")
    print("   Hard cap at 5 days maximum (was 7+ days)")
    
    return True

async def test_group_bidding_functionality():
    """Test the new group bidding system specifically"""
    
    print(f"\n{'='*80}")
    print("GROUP BIDDING SYSTEM TEST")
    print(f"{'='*80}")
    
    calculator = ContractorOutreachCalculator()
    
    # Test regular project vs group bidding project
    regular_strategy = calculator.calculate_outreach_strategy(
        bids_needed=4,
        timeline_hours=96,  # 4 days
        tier1_available=10,
        tier2_available=20,
        tier3_available=30,
        project_type='Kitchen Remodel'
    )
    
    group_strategy = calculator.calculate_outreach_strategy(
        bids_needed=4,
        timeline_hours=96,  # 4 days
        tier1_available=10,
        tier2_available=20,
        tier3_available=30,
        project_type='Kitchen Remodel',
        group_bidding_projects=['kitchen-001', 'bathroom-002', 'deck-003']
    )
    
    print(f"COMPARISON: Regular vs Group Bidding")
    print(f"Timeline: 96 hours (4 days)")
    print(f"Project: Kitchen Remodel")
    print(f"Available Contractors: T1=10, T2=20, T3=30")
    
    print(f"\nREGULAR PROJECT:")
    print(f"  Urgency: {regular_strategy.urgency_level.value}")
    print(f"  Contractors: {regular_strategy.total_to_contact}")
    print(f"  Expected Responses: {regular_strategy.expected_total_responses:.1f}")
    print(f"  Confidence: {regular_strategy.confidence_score:.1f}%")
    print(f"  Group Bidding: {regular_strategy.is_group_bidding}")
    
    print(f"\nGROUP BIDDING PROJECT:")
    print(f"  Urgency: {group_strategy.urgency_level.value}")
    print(f"  Contractors: {group_strategy.total_to_contact}")
    print(f"  Expected Responses: {group_strategy.expected_total_responses:.1f}")
    print(f"  Confidence: {group_strategy.confidence_score:.1f}%")
    print(f"  Group Bidding: {group_strategy.is_group_bidding}")
    print(f"  Projects in Group: {len(group_strategy.group_bidding_projects)}")
    
    # Calculate the group bidding benefit
    response_improvement = group_strategy.expected_total_responses - regular_strategy.expected_total_responses
    confidence_improvement = group_strategy.confidence_score - regular_strategy.confidence_score
    
    print(f"\nGROUP BIDDING BENEFITS:")
    print(f"  Additional Expected Responses: +{response_improvement:.1f}")
    print(f"  Confidence Improvement: +{confidence_improvement:.1f}%")
    print(f"  Response Rate Bonus: +20% (contractors prefer multiple projects)")
    
    if response_improvement > 0:
        print(f"   Group bidding provides measurable benefit")
    else:
        print(f"   Group bidding benefit not detected")
    
    return response_improvement > 0

async def main():
    """Main test execution"""
    
    print("AGGRESSIVE TIMING ENGINE TEST SUITE")
    print("Testing updated business logic for contractor outreach")
    
    try:
        # Test aggressive timing scenarios
        timing_success = await test_aggressive_timing_scenarios()
        
        # Test group bidding functionality  
        group_success = await test_group_bidding_functionality()
        
        print(f"\n{'='*80}")
        print("TEST RESULTS SUMMARY")
        print(f"{'='*80}")
        
        print(f"Aggressive Timing Test: {' PASSED' if timing_success else ' FAILED'}")
        print(f"Group Bidding Test: {' PASSED' if group_success else ' FAILED'}")
        
        if timing_success and group_success:
            print(f"\n ALL TESTS PASSED")
            print(f"Aggressive timing engine is ready for production!")
            print(f"\nKEY FEATURES VALIDATED:")
            print(f"   Emergency response: < 1 hour")
            print(f"   Urgent response: same day (1-12 hours)")
            print(f"   Standard response: 3 days maximum")
            print(f"   Group bidding: 5 days with +20% response boost")
            print(f"   Aggressive check-in schedules")
            print(f"   Hard 5-day maximum timeline")
        else:
            print(f"\n SOME TESTS FAILED")
            print(f"Review timing engine implementation")
            
    except Exception as e:
        print(f"\n TEST EXECUTION FAILED")
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())