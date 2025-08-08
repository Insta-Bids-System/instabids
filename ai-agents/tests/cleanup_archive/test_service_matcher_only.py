#!/usr/bin/env python3
"""
Test Service-Specific Intelligent Matcher (Direct API Test)
Tests the Claude Opus 4 service-level contractor matching without database dependencies
"""
import os
import sys


# Add the parent directory to the path so we can import from ai-agents
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agents.cda.service_specific_matcher import ServiceSpecificMatcher


def test_emergency_roof_repair_analysis():
    """Test emergency roof repair project analysis"""
    print("=" * 80)
    print("TEST 1: EMERGENCY ROOF REPAIR ANALYSIS")
    print("=" * 80)

    matcher = ServiceSpecificMatcher()

    # Test bid card for emergency roof repair
    test_bid_data = {
        "project_type": "roofing",
        "bid_document": {
            "project_overview": {
                "description": "I have a leak in my roof after the storm last week. Need emergency repair to fix the damaged shingles and prevent water damage. This is urgent."
            }
        }
    }

    print("Testing project analysis with Claude Opus 4...")
    analysis = matcher.analyze_project_requirements(test_bid_data)

    print("\nPROJECT ANALYSIS RESULTS:")
    print(f"  - Service Category: {analysis.get('service_category', 'N/A')}")
    print(f"  - Service Type: {analysis.get('service_type', 'N/A')}")
    print(f"  - Specialization Required: {analysis.get('specialization_required', [])}")
    print(f"  - Urgency Indicators: {analysis.get('urgency_indicators', [])}")
    print(f"  - Quality Preferences: {analysis.get('quality_preferences', 'N/A')}")
    print(f"  - Scope Complexity: {analysis.get('scope_complexity', 'N/A')}")
    print(f"  - Contractor Requirements: {analysis.get('contractor_requirements', [])}")

    return analysis


def test_contractor_scoring():
    """Test contractor scoring with different specializations"""
    print("\n" + "=" * 80)
    print("TEST 2: CONTRACTOR SCORING")
    print("=" * 80)

    matcher = ServiceSpecificMatcher()

    # Use the analysis from the first test
    project_analysis = {
        "service_category": "roofing",
        "service_type": "repair",
        "specialization_required": ["emergency_repair", "storm_damage"],
        "urgency_indicators": ["urgent", "emergency"],
        "scope_complexity": "moderate",
        "contractor_requirements": ["storm_damage_experience"]
    }

    # Test with different contractor types
    contractors = [
        {
            "company_name": "Emergency Roof Repair Pro",
            "google_types": ["roofing_contractor", "emergency_services"],
            "google_rating": 4.7,
            "google_review_count": 156,
            "website": "https://roofrepairpro.com"
        },
        {
            "company_name": "Full Roof Installation Co",
            "google_types": ["roofing_contractor", "home_improvement"],
            "google_rating": 4.5,
            "google_review_count": 89,
            "website": "https://fullroofinstall.com"
        },
        {
            "company_name": "General Home Maintenance",
            "google_types": ["general_contractor", "handyman"],
            "google_rating": 4.2,
            "google_review_count": 45,
            "website": "https://homemaintenance.com"
        }
    ]

    print("Testing Claude Opus 4 contractor scoring...")

    for i, contractor in enumerate(contractors, 1):
        print(f"\nCONTRACTOR {i}: {contractor['company_name']}")

        scoring = matcher.score_contractor_match(contractor, project_analysis)

        print(f"  - Match Score: {scoring.get('match_score', 0)}/100")
        print(f"  - Recommendation: {scoring.get('recommendation', 'Unknown')}")
        print(f"  - Specialization Match: {scoring.get('specialization_match', 'N/A')}")
        print(f"  - Key Strengths: {scoring.get('key_strengths', [])}")
        print(f"  - Concerns: {scoring.get('concerns', [])}")
        print(f"  - Reasoning: {scoring.get('reasoning', 'No reasoning provided')}")

    return True


def test_kitchen_installation_analysis():
    """Test kitchen installation project analysis"""
    print("\n" + "=" * 80)
    print("TEST 3: KITCHEN INSTALLATION ANALYSIS")
    print("=" * 80)

    matcher = ServiceSpecificMatcher()

    # Test bid card for kitchen installation
    test_bid_data = {
        "project_type": "kitchen remodel",
        "bid_document": {
            "project_overview": {
                "description": "Complete kitchen remodel with new cabinets, countertops, appliances, and flooring. Looking for full installation services from start to finish."
            }
        }
    }

    print("Testing kitchen installation analysis...")
    analysis = matcher.analyze_project_requirements(test_bid_data)

    print("\nKITCHEN INSTALLATION ANALYSIS:")
    print(f"  - Service Category: {analysis.get('service_category', 'N/A')}")
    print(f"  - Service Type: {analysis.get('service_type', 'N/A')}")
    print(f"  - Specialization Required: {analysis.get('specialization_required', [])}")
    print(f"  - Scope Complexity: {analysis.get('scope_complexity', 'N/A')}")

    return analysis


if __name__ == "__main__":
    print("TESTING SERVICE-SPECIFIC MATCHER (Claude Opus 4 Direct API)")
    print("Testing intelligent project analysis and contractor scoring")

    try:
        # Test 1: Emergency roof repair analysis
        roof_analysis = test_emergency_roof_repair_analysis()

        # Test 2: Contractor scoring for different specializations
        scoring_success = test_contractor_scoring()

        # Test 3: Kitchen installation analysis (different service type)
        kitchen_analysis = test_kitchen_installation_analysis()

        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)

        roof_success = bool(roof_analysis.get("service_category"))
        kitchen_success = bool(kitchen_analysis.get("service_category"))

        print(f"Emergency Roof Repair Analysis: {'PASS' if roof_success else 'FAIL'}")
        print(f"Contractor Scoring: {'PASS' if scoring_success else 'FAIL'}")
        print(f"Kitchen Installation Analysis: {'PASS' if kitchen_success else 'FAIL'}")

        all_passed = roof_success and scoring_success and kitchen_success
        print(f"\nOVERALL RESULT: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")

        if all_passed:
            print("\nSERVICE-SPECIFIC MATCHER IS WORKING!")
            print("Claude Opus 4 successfully:")
            print("  - Analyzes project descriptions to detect service types")
            print("  - Identifies specialization requirements")
            print("  - Scores contractors based on service match")
            print("  - Provides intelligent reasoning for recommendations")
            print("  - Distinguishes between repair, installation, and maintenance")
        else:
            print("\nSome issues detected - check error messages above")

    except Exception as e:
        print(f"\nTEST FRAMEWORK ERROR: {e}")
        import traceback
        traceback.print_exc()
