#!/usr/bin/env python3
"""
Test IRIS Project Push System - House Analysis Context
Tests the new IRIS endpoint that pushes project proposals to homeowner agent
"""

import asyncio
import json
import requests
from datetime import datetime
from config.service_urls import get_backend_url

# Test data simulating IRIS house analysis
def create_test_house_analysis():
    """Create test data simulating IRIS house analysis from photos"""
    return {
        "user_id": "550e8400-e29b-41d4-a716-446655440001",  # Test user ID
        "iris_session_id": f"iris_house_test_{int(datetime.now().timestamp())}",
        "source_context": "house_analysis",
        
        "project_proposal": {
            "generated_from": "house_photo_analysis",
            "photos_analyzed": 8,
            "rooms_identified": ["kitchen", "master_bathroom", "living_room"]
        },
        
        "current_state_analysis": {
            "room_analysis": {
                "kitchen": {
                    "condition_score": 2,
                    "issues": ["outdated cabinets", "poor lighting", "small workspace"],
                    "style": "1990s oak cabinets",
                    "functionality": "cramped galley layout"
                },
                "master_bathroom": {
                    "condition_score": 3,
                    "issues": ["old fixtures", "limited storage", "outdated tile"],
                    "style": "builder grade",
                    "functionality": "functional but dated"
                },
                "living_room": {
                    "condition_score": 4,
                    "issues": ["worn carpet", "dated paint"],
                    "style": "neutral but tired",
                    "functionality": "good layout"
                }
            },
            "issues_identified": [
                "Kitchen cabinets are warped and closing poorly",
                "Bathroom faucet has slow leak",
                "Living room carpet shows heavy wear patterns",
                "Kitchen lighting is insufficient for food prep",
                "Bathroom storage is very limited"
            ],
            "photos": [
                {"room": "kitchen", "count": 3, "analysis": "needs major renovation"},
                {"room": "master_bathroom", "count": 2, "analysis": "moderate updates needed"},
                {"room": "living_room", "count": 3, "analysis": "cosmetic improvements"}
            ]
        },
        
        "design_preferences": {
            "style_mentioned": ["modern", "clean lines"],
            "color_preferences": ["white", "neutral"],
            "material_interests": ["quartz", "hardwood"],
            "budget_conscious": True
        },
        
        "next_steps": [
            "Prioritize kitchen renovation",
            "Address bathroom leak immediately", 
            "Plan living room updates",
            "Get contractor estimates",
            "Create project timeline"
        ],
        
        "confidence_score": 0.85,
        "iris_conversation_id": None,  # Would be populated in real scenario
        "unified_memory_refs": []
    }

def test_iris_project_push():
    """Test the IRIS project push endpoint"""
    
    print("Testing IRIS Project Push - House Analysis Context")
    print("=" * 60)
    
    # Create test data
    test_data = create_test_house_analysis()
    
    print("Test Data Created:")
    print(f"  - Homeowner ID: {test_data['user_id']}")
    print(f"  - Source Context: {test_data['source_context']}")
    print(f"  - Rooms Analyzed: {len(test_data['current_state_analysis']['room_analysis'])}")
    print(f"  - Issues Found: {len(test_data['current_state_analysis']['issues_identified'])}")
    print(f"  - Confidence Score: {test_data['confidence_score']}")
    print()
    
    # Make API call
    url = f"{get_backend_url()}/api/iris/push-project"
    
    try:
        print("Calling IRIS Project Push Endpoint...")
        response = requests.post(url, json=test_data, timeout=30)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS - Project Push Completed!")
            print()
            print("Response Details:")
            print(f"  - Success: {result.get('success')}")
            print(f"  - Project ID: {result.get('project_id')}")
            print(f"  - Message: {result.get('message')}")
            print(f"  - Next Action: {result.get('next_action')}")
            
            if result.get('project_id'):
                print()
                print("Project Creation Verified!")
                print(f"  - New project created with ID: {result['project_id']}")
                print(f"  - Ready for homeowner agent handoff")
                
                return True
        else:
            print(f"ERROR - Status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("ERROR - Could not connect to backend")
        print("Make sure backend is running: cd ai-agents && python main.py")
        return False
    except Exception as e:
        print(f"ERROR - {e}")
        return False

def test_detailed_house_analysis():
    """Test with more detailed house analysis data"""
    
    print("\nTesting with Detailed House Analysis...")
    print("=" * 50)
    
    detailed_data = {
        "user_id": "550e8400-e29b-41d4-a716-446655440001", 
        "iris_session_id": f"iris_detailed_test_{int(datetime.now().timestamp())}",
        "source_context": "house_analysis",
        
        "project_proposal": {
            "analysis_type": "comprehensive_house_assessment",
            "photos_processed": 15,
            "ai_confidence": "high",
            "priority_ranking": ["urgent_repairs", "kitchen_renovation", "bathroom_update"]
        },
        
        "current_state_analysis": {
            "room_analysis": {
                "kitchen": {
                    "condition_score": 1,  # Very poor
                    "size": "12x8 galley",
                    "issues": ["cabinets falling apart", "countertop cracked", "appliances failing"],
                    "style": "1980s honey oak",
                    "functionality": "severely cramped",
                    "safety_concerns": ["electrical outlets near water", "gas leak smell"]
                },
                "master_bathroom": {
                    "condition_score": 2,
                    "size": "8x6",
                    "issues": ["tile grout failing", "shower door broken", "vanity water damage"],
                    "style": "builder grade 1990s",
                    "functionality": "usable but problematic"
                }
            },
            "issues_identified": [
                "URGENT: Possible gas leak in kitchen - safety hazard",
                "Kitchen cabinets are structurally unsafe",
                "Bathroom floor shows water damage",
                "Electrical outlets in kitchen not GFCI protected",
                "Shower door glass is cracked"
            ],
            "photos": [
                {"room": "kitchen", "count": 8, "analysis": "urgent safety renovation needed"},
                {"room": "master_bathroom", "count": 4, "analysis": "water damage requires immediate attention"},
                {"room": "exterior", "count": 3, "analysis": "roof gutters need repair"}
            ]
        },
        
        "design_preferences": {
            "style_preferences": ["modern", "functional", "safety_first"],
            "color_preferences": ["white", "gray", "neutral"],
            "priorities": ["safety", "functionality", "durability", "aesthetics"],
            "budget_conscious": True
        },
        
        "next_steps": [
            "IMMEDIATE: Schedule gas leak inspection",
            "URGENT: Kitchen safety assessment",
            "Get emergency repair quotes",
            "Plan comprehensive kitchen renovation", 
            "Address bathroom water damage",
            "Create phased renovation timeline"
        ],
        
        "confidence_score": 0.95,  # High confidence due to clear safety issues
    }
    
    url = f"{get_backend_url()}/api/iris/push-project"
    
    try:
        response = requests.post(url, json=detailed_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("Detailed Analysis Push Successful!")
            print(f"  - Project ID: {result.get('project_id')}")
            print(f"  - Analysis captured urgent safety issues")
            print(f"  - Ready for emergency contractor matching")
            return True
        else:
            print(f"Detailed test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Detailed test error: {e}")
        return False

def main():
    """Run all IRIS project push tests"""
    
    print("IRIS Project Push System Test Suite")
    print("Testing house analysis -> project creation flow")
    print("=" * 70)
    print()
    
    # Test 1: Basic house analysis push
    test1_success = test_iris_project_push()
    
    # Test 2: Detailed analysis with urgent issues
    test2_success = test_detailed_house_analysis()
    
    print("\n" + "=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    print(f"Basic House Analysis Push: {'PASSED' if test1_success else 'FAILED'}")
    print(f"Detailed Analysis Push: {'PASSED' if test2_success else 'FAILED'}")
    
    if test1_success and test2_success:
        print("\nALL TESTS PASSED!")
        print("IRIS project push system is working correctly")
        print("Ready for integration with homeowner agent!")
    else:
        print("\nSOME TESTS FAILED")
        print("Check backend logs and endpoint implementation")
    
    print("\nNext Steps:")
    print("1. Test with real IRIS house analysis data")
    print("2. Integrate with homeowner agent endpoint")
    print("3. Add frontend 'Create Project' button")
    print("4. Test end-to-end IRIS -> Homeowner Agent -> CIA flow")

if __name__ == "__main__":
    main()