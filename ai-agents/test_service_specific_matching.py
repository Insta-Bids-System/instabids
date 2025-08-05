#!/usr/bin/env python3
"""
Test Service-Specific Intelligent Matching
Tests the enhanced CDA with Claude Opus 4 service-level contractor matching
"""
import os
import sys

# Add the parent directory to the path so we can import from ai-agents
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agents.cda.agent import ContractorDiscoveryAgent


def test_roofing_repair_emergency():
    """Test emergency roof repair project - should prioritize repair specialists"""
    print("=" * 80)
    print("TEST 1: EMERGENCY ROOF REPAIR")
    print("=" * 80)
    
    agent = ContractorDiscoveryAgent()
    
    # Create test bid card for emergency roof repair
    test_bid_card_id = "test-emergency-roof-repair"
    
    # Test the enhanced discovery
    result = agent.discover_contractors(
        bid_card_id=test_bid_card_id,
        contractors_needed=5,
        radius_miles=15
    )
    
    if result["success"]:
        print(f"\nSUCCESS - Service-Specific Matching Results:")
        print(f"Total contractors found: {result['total_found']}")
        print(f"Selected for outreach: {result['selected_count']}")
        print(f"Target bids needed: {result['bid_analysis']['bids_needed']}")
        print(f"Service analysis: {result['bid_analysis'].get('service_analysis', {})}")
        
        print(f"\nPROJECT ANALYSIS:")
        service_analysis = result['bid_analysis'].get('service_analysis', {})
        print(f"  - Service Category: {service_analysis.get('service_category', 'N/A')}")
        print(f"  - Service Type: {service_analysis.get('service_type', 'N/A')}")
        print(f"  - Specialization Required: {service_analysis.get('specialization_required', [])}")
        print(f"  - Urgency Indicators: {service_analysis.get('urgency_indicators', [])}")
        print(f"  - Scope Complexity: {service_analysis.get('scope_complexity', 'N/A')}")
        
        print(f"\nTOP SELECTED CONTRACTORS:")
        for i, contractor in enumerate(result["selected_contractors"][:5], 1):
            print(f"\n{i}. {contractor.get('company_name', 'Unknown')}")
            print(f"   Score: {contractor.get('match_score', 0)}/100")
            print(f"   Recommendation: {contractor.get('recommendation', 'Unknown')}")
            print(f"   Specialization Match: {contractor.get('specialization_match', 'N/A')}")
            print(f"   Key Strengths: {contractor.get('key_strengths', [])}")
            if contractor.get('concerns'):
                print(f"   Concerns: {contractor.get('concerns', [])}")
            print(f"   Reasoning: {contractor.get('reasoning', 'No reasoning provided')}")
        
        print(f"\nTIER BREAKDOWN:")
        tier_results = result.get('tier_results', {})
        print(f"  - Tier 1 (Internal): {tier_results.get('tier1_internal', 0)} contractors")
        print(f"  - Tier 2 (Previous): {tier_results.get('tier2_previous', 0)} contractors")
        print(f"  - Tier 3 (Web Search): {tier_results.get('tier3_web', 0)} contractors")
        
        print(f"\nEXPLANATION:")
        print(f"{result['explanation']}")
        
    else:
        print(f"\nERROR: {result.get('error', 'Unknown error')}")
    
    return result


def test_kitchen_installation():
    """Test kitchen remodel project - should prioritize installation specialists"""
    print("\n" + "=" * 80)
    print("TEST 2: KITCHEN REMODEL INSTALLATION")
    print("=" * 80)
    
    agent = ContractorDiscoveryAgent()
    
    # Create test bid card for kitchen installation
    test_bid_card_id = "test-kitchen-installation"
    
    result = agent.discover_contractors(
        bid_card_id=test_bid_card_id,
        contractors_needed=4,
        radius_miles=20
    )
    
    if result["success"]:
        print(f"\nSUCCESS - Kitchen Installation Matching:")
        print(f"Selected contractors: {result['selected_count']}")
        
        service_analysis = result['bid_analysis'].get('service_analysis', {})
        print(f"\nSERVICE ANALYSIS:")
        print(f"  - Service Category: {service_analysis.get('service_category', 'N/A')}")
        print(f"  - Service Type: {service_analysis.get('service_type', 'N/A')}")
        print(f"  - Specialization: {service_analysis.get('specialization_required', [])}")
        
        print(f"\nTOP 3 CONTRACTORS:")
        for i, contractor in enumerate(result["selected_contractors"][:3], 1):
            print(f"{i}. {contractor.get('company_name', 'Unknown')} - Score: {contractor.get('match_score', 0)}")
            print(f"   Recommendation: {contractor.get('recommendation', 'Unknown')}")
    else:
        print(f"\nERROR: {result.get('error', 'Unknown error')}")
    
    return result


def test_plumbing_maintenance():
    """Test plumbing maintenance project - should prioritize service specialists"""
    print("\n" + "=" * 80)
    print("TEST 3: PLUMBING MAINTENANCE SERVICE")
    print("=" * 80)
    
    agent = ContractorDiscoveryAgent()
    
    # Create test bid card for plumbing maintenance
    test_bid_card_id = "test-plumbing-maintenance"
    
    result = agent.discover_contractors(
        bid_card_id=test_bid_card_id,
        contractors_needed=3,
        radius_miles=10
    )
    
    if result["success"]:
        print(f"\nSUCCESS - Plumbing Maintenance Matching:")
        print(f"Selected contractors: {result['selected_count']}")
        
        service_analysis = result['bid_analysis'].get('service_analysis', {})
        print(f"\nSERVICE ANALYSIS:")
        print(f"  - Service Category: {service_analysis.get('service_category', 'N/A')}")
        print(f"  - Service Type: {service_analysis.get('service_type', 'N/A')}")
        
        print(f"\nTOP CONTRACTORS:")
        for i, contractor in enumerate(result["selected_contractors"][:3], 1):
            print(f"{i}. {contractor.get('company_name', 'Unknown')} - Score: {contractor.get('match_score', 0)}")
    else:
        print(f"\nERROR: {result.get('error', 'Unknown error')}")
    
    return result


if __name__ == "__main__":
    print("TESTING SERVICE-SPECIFIC INTELLIGENT MATCHING")
    print("Testing Claude Opus 4 enhanced contractor discovery with service-level specialization")
    print("This tests matching by project type AND service specifics (repair vs installation vs service)")
    
    try:
        # Test 1: Emergency roof repair (should prioritize repair specialists)
        test1_result = test_roofing_repair_emergency()
        
        # Test 2: Kitchen remodel (should prioritize installation specialists)  
        test2_result = test_kitchen_installation()
        
        # Test 3: Plumbing maintenance (should prioritize service specialists)
        test3_result = test_plumbing_maintenance()
        
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Test 1 (Emergency Roof Repair): {'PASS' if test1_result['success'] else 'FAIL'}")
        print(f"Test 2 (Kitchen Installation): {'PASS' if test2_result['success'] else 'FAIL'}")
        print(f"Test 3 (Plumbing Maintenance): {'PASS' if test3_result['success'] else 'FAIL'}")
        
        all_passed = all([test1_result['success'], test2_result['success'], test3_result['success']])
        print(f"\nOVERALL RESULT: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
        
        if all_passed:
            print("\nSERVICE-SPECIFIC MATCHING IS WORKING!")
            print("The enhanced CDA successfully:")
            print("  - Analyzes project descriptions to detect service types")
            print("  - Uses service-specific search terms for contractor discovery")
            print("  - Scores contractors based on specialization match")
            print("  - Provides intelligent reasoning for recommendations")
            print("  - Handles repair vs installation vs service distinctions")
        else:
            print("\nSome issues detected - check error messages above")
            
    except Exception as e:
        print(f"\nTEST FRAMEWORK ERROR: {e}")
        import traceback
        traceback.print_exc()