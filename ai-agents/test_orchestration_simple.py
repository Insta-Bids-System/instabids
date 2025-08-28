#!/usr/bin/env python3
"""
Orchestration System Testing Suite
Tests the campaign orchestration components
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory for imports
sys.path.append(os.path.dirname(__file__))

def test_orchestration_imports():
    """Test if orchestration components can be imported"""
    print("\n[TEST] Testing Orchestration Component Imports...")
    
    try:
        from agents.orchestration.enhanced_campaign_orchestrator import EnhancedCampaignOrchestrator
        print("  [PASS] EnhancedCampaignOrchestrator imported")
        
        from agents.orchestration.campaign_orchestrator import OutreachCampaignOrchestrator
        print("  [PASS] OutreachCampaignOrchestrator imported")
        
        from agents.orchestration.timing_probability_engine import ContractorOutreachCalculator
        print("  [PASS] ContractorOutreachCalculator imported")
        
        from agents.orchestration.check_in_manager import CampaignCheckInManager
        print("  [PASS] CampaignCheckInManager imported")
        
        from agents.orchestration.contractor_interest_classifier import ContractorInterestClassifier
        print("  [PASS] ContractorInterestClassifier imported")
        
        return True
    except Exception as e:
        print(f"  [FAIL] Import error: {e}")
        return False

def test_timing_engine():
    """Test the timing probability engine"""
    print("\n[TEST] Testing Timing Probability Engine...")
    
    try:
        from agents.orchestration.timing_probability_engine import ContractorOutreachCalculator
        
        calculator = ContractorOutreachCalculator()
        print("  [PASS] Calculator initialized")
        
        # Test strategy calculation
        strategy = calculator.calculate_outreach_strategy(
            bids_needed=4,
            timeline_hours=24,
            project_type="Lawn Care"
        )
        
        print(f"  Test Strategy Results:")
        print(f"    Total to contact: {strategy.total_to_contact}")
        print(f"    Expected responses: {strategy.expected_total_responses:.1f}")
        print(f"    Confidence: {strategy.confidence_score}%")
        
        if strategy.total_to_contact > 0:
            print("  [PASS] Strategy calculation working")
            return True
        else:
            print("  [FAIL] Strategy returned zero contacts")
            return False
            
    except Exception as e:
        print(f"  [FAIL] Timing engine error: {e}")
        return False

def test_orchestrator_initialization():
    """Test orchestrator initialization"""
    print("\n[TEST] Testing Orchestrator Initialization...")
    
    try:
        from agents.orchestration.enhanced_campaign_orchestrator import EnhancedCampaignOrchestrator
        
        orchestrator = EnhancedCampaignOrchestrator()
        print("  [PASS] Enhanced orchestrator initialized")
        
        # Check if it has required components
        if hasattr(orchestrator, 'timing_calculator'):
            print("  [PASS] Has timing calculator")
        else:
            print("  [WARN] Missing timing calculator")
            
        if hasattr(orchestrator, 'base_orchestrator'):
            print("  [PASS] Has base orchestrator")
        else:
            print("  [WARN] Missing base orchestrator")
            
        return True
        
    except Exception as e:
        print(f"  [FAIL] Orchestrator initialization error: {e}")
        return False

def test_check_in_manager():
    """Test check-in manager functionality"""
    print("\n[TEST] Testing Check-in Manager...")
    
    try:
        from agents.orchestration.check_in_manager import CampaignCheckInManager
        
        manager = CampaignCheckInManager()
        print("  [PASS] Check-in manager initialized")
        
        # Test check-in calculation
        check_ins = manager._calculate_check_in_times(
            start_time=datetime.now(),
            timeline_hours=24
        )
        
        print(f"  Check-in times calculated: {len(check_ins)} intervals")
        for i, check_in in enumerate(check_ins):
            print(f"    Check-in {i+1}: {check_in}")
        
        if len(check_ins) >= 3:
            print("  [PASS] Check-in scheduling working")
            return True
        else:
            print("  [WARN] Too few check-ins scheduled")
            return False
            
    except Exception as e:
        print(f"  [FAIL] Check-in manager error: {e}")
        return False

def test_contractor_classifiers():
    """Test contractor classification agents"""
    print("\n[TEST] Testing Contractor Classifiers...")
    
    results = []
    
    # Test Interest Classifier
    try:
        from agents.orchestration.contractor_interest_classifier import ContractorInterestClassifier
        
        classifier = ContractorInterestClassifier()
        print("  [PASS] Interest classifier initialized")
        results.append(True)
        
    except Exception as e:
        print(f"  [FAIL] Interest classifier error: {e}")
        results.append(False)
    
    # Test Qualification Agent
    try:
        from agents.orchestration.contractor_qualification_agent import ContractorQualificationAgent
        
        qualifier = ContractorQualificationAgent()
        print("  [PASS] Qualification agent initialized")
        results.append(True)
        
    except Exception as e:
        print(f"  [FAIL] Qualification agent error: {e}")
        results.append(False)
    
    return all(results)

def test_error_handling():
    """Test error handling system"""
    print("\n[TEST] Testing Error Handling...")
    
    try:
        from agents.orchestration.error_handler import error_handler, ErrorSeverity, ErrorCategory
        
        # Test error handling
        test_error = ValueError("Test error for orchestration")
        
        result = error_handler.handle_error(
            test_error,
            {"context": "test", "component": "orchestration"},
            ErrorSeverity.LOW,
            ErrorCategory.VALIDATION
        )
        
        if result.get("success") is False and "error_id" in result:
            print("  [PASS] Error handling working")
            print(f"    Error ID: {result['error_id']}")
            print(f"    Recovery: {result.get('recovery_strategy', {}).get('action', 'none')}")
            return True
        else:
            print("  [FAIL] Error handling not working properly")
            return False
            
    except Exception as e:
        print(f"  [FAIL] Error handling test failed: {e}")
        return False

def main():
    """Run orchestration test suite"""
    print("=" * 60)
    print("Orchestration System Test Suite")
    print("=" * 60)
    
    results = []
    
    # Test 1: Component imports
    results.append(("Component Imports", test_orchestration_imports()))
    
    # Test 2: Timing engine
    results.append(("Timing Engine", test_timing_engine()))
    
    # Test 3: Orchestrator initialization
    results.append(("Orchestrator Init", test_orchestrator_initialization()))
    
    # Test 4: Check-in manager
    results.append(("Check-in Manager", test_check_in_manager()))
    
    # Test 5: Contractor classifiers
    results.append(("Contractor Classifiers", test_contractor_classifiers()))
    
    # Test 6: Error handling
    results.append(("Error Handling", test_error_handling()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{test_name:.<40} {status}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n[SUCCESS] ALL ORCHESTRATION TESTS PASSED!")
    elif total_passed >= total_tests * 0.7:
        print("\n[WARNING] Orchestration mostly functional but needs attention")
    else:
        print("\n[ERROR] Orchestration has critical issues")

if __name__ == "__main__":
    main()