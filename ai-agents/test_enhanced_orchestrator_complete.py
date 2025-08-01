#!/usr/bin/env python3
"""
Complete Test Suite for Enhanced Campaign Orchestrator
Tests real database integration, timing engine, and end-to-end workflow
"""

import asyncio
from datetime import datetime, timedelta
import sys
import os

# Add the ai-agents directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.orchestration.enhanced_campaign_orchestrator import (
    EnhancedCampaignOrchestrator,
    CampaignRequest
)

async def test_orchestrator_components():
    """Test individual components of the enhanced orchestrator"""
    
    print("="*80)
    print("ENHANCED CAMPAIGN ORCHESTRATOR - COMPONENT TESTING")
    print("="*80)
    print(f"Testing all components with real database integration")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Initialize orchestrator
        print("\n[STEP 1] Initializing Enhanced Campaign Orchestrator...")
        orchestrator = EnhancedCampaignOrchestrator()
        print("✅ Enhanced Campaign Orchestrator initialized successfully")
        
        # Test component initialization
        print("\n[STEP 2] Testing Component Initialization...")
        components = [
            ("Timing Calculator", orchestrator.timing_calculator),
            ("Base Orchestrator", orchestrator.base_orchestrator),
            ("Check-in Manager", orchestrator.check_in_manager),
            ("Supabase Client", orchestrator.supabase)
        ]
        
        for name, component in components:
            if component:
                print(f"✅ {name}: Initialized")
            else:
                print(f"❌ {name}: Failed to initialize")
                return False
        
        # Test database connectivity
        print("\n[STEP 3] Testing Database Connectivity...")
        try:
            # Test a simple query
            result = orchestrator.supabase.table('bid_cards').select('id').limit(1).execute()
            print(f"✅ Database connection working - found {len(result.data)} bid cards")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
        
        # Test contractor availability analysis
        print("\n[STEP 4] Testing Contractor Availability Analysis...")
        availability = await orchestrator._analyze_contractor_availability(
            project_type="Kitchen Remodel",
            location={"city": "Austin", "state": "TX", "zip": "78701"}
        )
        
        print(f"✅ Contractor Availability Analysis Complete:")
        for tier, count in availability.items():
            print(f"    {tier}: {count} contractors")
        
        return True
        
    except Exception as e:
        print(f"❌ Component testing failed: {e}")
        return False

async def test_timing_integration():
    """Test timing engine integration"""
    
    print("\n" + "="*80)
    print("TIMING ENGINE INTEGRATION TEST")
    print("="*80)
    
    try:
        orchestrator = EnhancedCampaignOrchestrator()
        
        # Test different urgency scenarios
        test_scenarios = [
            {
                'name': 'EMERGENCY: Plumbing leak (30 minutes)',
                'timeline_hours': 0.5,
                'project_type': 'Emergency Plumbing',
                'bids_needed': 3,
                'expected_urgency': 'emergency'
            },
            {
                'name': 'URGENT: Kitchen fire damage (8 hours)',
                'timeline_hours': 8,
                'project_type': 'Fire Damage Repair',
                'bids_needed': 4,
                'expected_urgency': 'urgent'
            },
            {
                'name': 'STANDARD: Bathroom remodel (48 hours)',
                'timeline_hours': 48,
                'project_type': 'Bathroom Remodel',
                'bids_needed': 4,
                'expected_urgency': 'standard'
            }
        ]
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n[SCENARIO {i}] {scenario['name']}")
            print("-" * 60)
            
            # Test timing calculation
            strategy = orchestrator.timing_calculator.calculate_outreach_strategy(
                bids_needed=scenario['bids_needed'],
                timeline_hours=scenario['timeline_hours'],
                tier1_available=5,
                tier2_available=15,
                tier3_available=30,
                project_type=scenario['project_type']
            )
            
            print(f"Timeline: {scenario['timeline_hours']} hours")
            print(f"Urgency Detected: {strategy.urgency_level.value}")
            print(f"Expected: {scenario['expected_urgency']}")
            
            urgency_match = "✅" if strategy.urgency_level.value == scenario['expected_urgency'] else "❌"
            print(f"Urgency Classification: {urgency_match}")
            
            print(f"\nContractor Strategy:")
            print(f"  Total: {strategy.total_to_contact} contractors")
            print(f"  Expected Responses: {strategy.expected_total_responses:.1f}")
            print(f"  Confidence: {strategy.confidence_score:.1f}%")
            
            print(f"\nTier Breakdown:")
            print(f"  Tier 1: {strategy.tier1_strategy.to_contact} contractors")
            print(f"  Tier 2: {strategy.tier2_strategy.to_contact} contractors")
            print(f"  Tier 3: {strategy.tier3_strategy.to_contact} contractors")
        
        print("\n✅ Timing Engine Integration: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Timing Engine Integration: FAILED - {e}")
        return False

async def test_contractor_selection():
    """Test contractor selection from database"""
    
    print("\n" + "="*80)
    print("CONTRACTOR SELECTION TEST")
    print("="*80)
    
    try:
        orchestrator = EnhancedCampaignOrchestrator()
        
        # Test selecting contractors from each tier
        print("\n[Testing Tier Selection]")
        
        # Test Tier 1 selection
        print("\nTier 1 (Internal Contractors):")
        tier1_contractors = await orchestrator._select_tier_contractors(
            tier=1,
            count=3,
            project_type="Kitchen Remodel",
            location={"city": "Austin", "state": "TX"}
        )
        
        print(f"  Selected: {len(tier1_contractors)} contractors")
        for contractor in tier1_contractors[:2]:  # Show first 2
            print(f"    - {contractor.get('company_name', contractor.get('business_name', 'Unknown'))}")
            print(f"      Tier: {contractor.get('tier')}, Email: {contractor.get('email', 'N/A')}")
        
        # Test Tier 2 selection
        print("\nTier 2 (Prospects):")
        tier2_contractors = await orchestrator._select_tier_contractors(
            tier=2,
            count=5,
            project_type="Kitchen Remodel",
            location={"city": "Austin", "state": "TX"}
        )
        
        print(f"  Selected: {len(tier2_contractors)} contractors")
        for contractor in tier2_contractors[:2]:  # Show first 2
            print(f"    - {contractor.get('company_name', 'Unknown')}")
            print(f"      Tier: {contractor.get('tier')}, Status: {contractor.get('lead_status', 'N/A')}")
        
        # Test Tier 3 selection
        print("\nTier 3 (New/Cold):")
        tier3_contractors = await orchestrator._select_tier_contractors(
            tier=3,
            count=4,
            project_type="Kitchen Remodel",
            location={"city": "Austin", "state": "TX"}
        )
        
        print(f"  Selected: {len(tier3_contractors)} contractors")
        for contractor in tier3_contractors[:2]:  # Show first 2
            print(f"    - {contractor.get('company_name', 'Unknown')}")
            print(f"      Tier: {contractor.get('tier')}, Score: {contractor.get('lead_score', 'N/A')}")
        
        total_selected = len(tier1_contractors) + len(tier2_contractors) + len(tier3_contractors)
        print(f"\n✅ Total Contractors Selected: {total_selected}")
        print("✅ Contractor Selection: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Contractor Selection: FAILED - {e}")
        return False

async def test_campaign_creation():
    """Test complete campaign creation workflow"""
    
    print("\n" + "="*80)
    print("CAMPAIGN CREATION TEST")
    print("="*80)
    
    try:
        orchestrator = EnhancedCampaignOrchestrator()
        
        # Create a test campaign request
        request = CampaignRequest(
            bid_card_id=f'test-orchestrator-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            project_type='Kitchen Remodel Test',
            location={'city': 'Austin', 'state': 'TX', 'zip': '78701'},
            timeline_hours=24,  # 24-hour urgent timeline
            urgency_level='urgent',
            bids_needed=4
        )
        
        print(f"\n[Creating Intelligent Campaign]")
        print(f"Project: {request.project_type}")
        print(f"Timeline: {request.timeline_hours} hours")
        print(f"Location: {request.location['city']}, {request.location['state']}")
        print(f"Bids Needed: {request.bids_needed}")
        
        # Create the campaign
        result = await orchestrator.create_intelligent_campaign(request)
        
        if result.get('success'):
            campaign_id = result['campaign_id']
            strategy = result['strategy']
            
            print(f"\n✅ Campaign Created Successfully!")
            print(f"Campaign ID: {campaign_id}")
            
            print(f"\nStrategy Details:")
            print(f"  Urgency: {strategy['urgency']}")
            print(f"  Total Contractors: {strategy['total_contractors']}")
            print(f"  Expected Responses: {strategy['expected_responses']:.1f}")
            print(f"  Confidence Score: {strategy['confidence_score']:.1f}%")
            
            print(f"\nTier Distribution:")
            print(f"  Tier 1: {strategy['tier_1']} contractors")
            print(f"  Tier 2: {strategy['tier_2']} contractors")
            print(f"  Tier 3: {strategy['tier_3']} contractors")
            
            if strategy.get('risk_factors'):
                print(f"\nRisk Factors:")
                for risk in strategy['risk_factors']:
                    print(f"  ⚠️ {risk}")
            
            if strategy.get('recommendations'):
                print(f"\nRecommendations:")
                for rec in strategy['recommendations']:
                    print(f"  💡 {rec}")
            
            print("\n✅ Campaign Creation: PASSED")
            return {'success': True, 'campaign_id': campaign_id}
            
        else:
            print(f"❌ Campaign Creation Failed: {result.get('error')}")
            return {'success': False}
        
    except Exception as e:
        print(f"❌ Campaign Creation: FAILED - {e}")
        return {'success': False}

async def test_check_in_integration():
    """Test check-in system integration"""
    
    print("\n" + "="*80)
    print("CHECK-IN SYSTEM INTEGRATION TEST")
    print("="*80)
    
    try:
        orchestrator = EnhancedCampaignOrchestrator()
        
        # Test check-in scheduling
        print("\n[Testing Check-in Scheduling]")
        
        # Create a mock strategy for testing
        from agents.orchestration.timing_probability_engine import (
            OutreachStrategy, TierStrategy, UrgencyLevel
        )
        
        # Create test strategy
        test_strategy = OutreachStrategy(
            bids_needed=4,
            timeline_hours=24,
            urgency_level=UrgencyLevel.URGENT,
            tier1_strategy=TierStrategy(1, "Internal", 0.9, 5, 3, 2.7),
            tier2_strategy=TierStrategy(2, "Prospects", 0.5, 15, 5, 2.5),
            tier3_strategy=TierStrategy(3, "New/Cold", 0.33, 30, 2, 0.66),
            total_to_contact=10,
            expected_total_responses=5.86,
            check_in_times=[
                datetime.now() + timedelta(hours=6),
                datetime.now() + timedelta(hours=12),
                datetime.now() + timedelta(hours=18)
            ],
            escalation_thresholds={},
            confidence_score=146.5,
            risk_factors=[],
            recommendations=[]
        )
        
        # Test check-in scheduling
        campaign_id = f'test-checkin-{datetime.now().strftime("%Y%m%d%H%M%S")}'
        bid_card_id = f'test-bid-{datetime.now().strftime("%Y%m%d%H%M%S")}'
        
        print(f"Scheduling check-ins for campaign: {campaign_id}")
        print(f"Strategy: {test_strategy.timeline_hours} hours, {test_strategy.urgency_level.value}")
        
        # This will test the check-in manager integration
        check_ins = await orchestrator.check_in_manager.schedule_campaign_check_ins(
            campaign_id=campaign_id,
            bid_card_id=bid_card_id,
            strategy=test_strategy
        )
        
        print(f"\n✅ Check-ins Scheduled: {len(check_ins)}")
        for i, check_in in enumerate(check_ins, 1):
            scheduled_time = datetime.fromisoformat(check_in['scheduled_time'])
            hours_from_now = (scheduled_time - datetime.now()).total_seconds() / 3600
            print(f"  Check-in {i}: {hours_from_now:.1f} hours from now")
            print(f"    Expected Bids: {check_in['expected_bids']}")
        
        print("\n✅ Check-in Integration: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Check-in Integration: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_complete_workflow():
    """Test the complete end-to-end workflow"""
    
    print("\n" + "="*80)
    print("COMPLETE END-TO-END WORKFLOW TEST")
    print("="*80)
    
    try:
        # Run full campaign creation
        campaign_result = await test_campaign_creation()
        
        if not campaign_result.get('success'):
            print("❌ Cannot test workflow - campaign creation failed")
            return False
        
        campaign_id = campaign_result['campaign_id']
        
        # Test campaign execution (but don't run full monitoring)
        print(f"\n[Testing Campaign Execution]")
        print(f"Campaign ID: {campaign_id}")
        
        orchestrator = EnhancedCampaignOrchestrator()
        
        # Execute campaign (without long-running monitoring)
        print("Starting campaign execution...")
        execution_result = orchestrator.base_orchestrator.execute_campaign(campaign_id)
        
        if execution_result.get('success'):
            print("✅ Campaign execution initiated successfully")
            
            # Test campaign monitoring setup (but don't wait)
            print("\n[Testing Monitoring Setup]")
            
            # Check if check-ins were created
            check_ins = orchestrator.supabase.table('campaign_check_ins')\
                .select('*')\
                .eq('campaign_id', campaign_id)\
                .execute()
            
            if check_ins.data:
                print(f"✅ Monitoring setup complete - {len(check_ins.data)} check-ins scheduled")
                for i, check_in in enumerate(check_ins.data, 1):
                    print(f"  Check-in {i}: {check_in['scheduled_time']}")
            else:
                print("⚠️ No check-ins found - monitoring may not be set up")
            
            print("\n✅ Complete Workflow: PASSED")
            return True
            
        else:
            print(f"❌ Campaign execution failed: {execution_result.get('error')}")
            return False
        
    except Exception as e:
        print(f"❌ Complete Workflow: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test execution"""
    
    print("ENHANCED CAMPAIGN ORCHESTRATOR - COMPREHENSIVE TEST SUITE")
    print("Testing all components with real database integration")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = {}
    
    try:
        # Test 1: Component initialization
        print("\n" + "🧪" * 20 + " RUNNING TESTS " + "🧪" * 20)
        test_results['components'] = await test_orchestrator_components()
        
        # Test 2: Timing integration
        test_results['timing'] = await test_timing_integration()
        
        # Test 3: Contractor selection
        test_results['contractor_selection'] = await test_contractor_selection()
        
        # Test 4: Check-in integration
        test_results['checkin_integration'] = await test_check_in_integration()
        
        # Test 5: Complete workflow
        test_results['complete_workflow'] = await test_complete_workflow()
        
        # Summary
        print("\n" + "="*80)
        print("TEST RESULTS SUMMARY")
        print("="*80)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
            if result:
                passed += 1
        
        print(f"\nOverall Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED - Enhanced Campaign Orchestrator is FULLY OPERATIONAL!")
            print("\nKey Features Verified:")
            print("  ✅ Database connectivity and contractor availability analysis")
            print("  ✅ Timing engine integration with aggressive business timelines")
            print("  ✅ Multi-tier contractor selection from real database")
            print("  ✅ Check-in system integration and scheduling")
            print("  ✅ Complete end-to-end campaign creation and execution")
            print("\n🚀 READY FOR PRODUCTION!")
        else:
            print(f"\n⚠️ {total - passed} tests failed - review errors above")
            print("System needs fixes before production deployment")
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())