#!/usr/bin/env python3
"""
Test Memory Extraction Only - Simple Test
Tests just the design preference extraction logic without API calls
"""

import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_memory_extraction():
    """Test design preference extraction logic"""
    print("TEST: Memory Extraction Logic")
    
    try:
        # Import the extraction function
        from api.iris_chat_unified import extract_design_preferences
        
        # Test cases with different design elements
        test_cases = [
            {
                "name": "Modern Farmhouse Kitchen",
                "message": "I love modern farmhouse style with white cabinets and dark hardware",
                "response": "Great choice! Modern farmhouse combines clean lines with rustic charm. White cabinets with dark hardware create beautiful contrast.",
                "context": {"conversation": {"metadata": {"room_type": "kitchen"}}},
                "expected": ["preferred_styles", "color_preferences", "focus_room"]
            },
            {
                "name": "Traditional Living Room",
                "message": "I prefer traditional style with warm colors and wood furniture",
                "response": "Traditional style offers timeless elegance. Warm colors create a cozy atmosphere, and wood furniture adds natural beauty.",
                "context": {"conversation": {"metadata": {"room_type": "living_room"}}},
                "expected": ["preferred_styles", "color_preferences", "material_preferences", "focus_room"]
            },
            {
                "name": "Budget-Conscious Bathroom",
                "message": "I want a modern bathroom but need to stay within budget",
                "response": "Modern bathrooms can be affordable with smart choices. Consider subway tile and simple fixtures to keep costs down.",
                "context": {"conversation": {"metadata": {"room_type": "bathroom"}}},
                "expected": ["preferred_styles", "budget_conscious", "focus_room"]
            }
        ]
        
        all_passed = True
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n  Test Case {i}: {test_case['name']}")
            
            preferences = extract_design_preferences(
                test_case["message"], 
                test_case["response"], 
                test_case["context"]
            )
            
            print(f"    Extracted preferences:")
            for key, value in preferences.items():
                print(f"      {key}: {value}")
            
            # Check if expected elements were found
            found_expected = [elem for elem in test_case["expected"] if elem in preferences]
            
            if len(found_expected) >= len(test_case["expected"]) * 0.7:  # At least 70% of expected elements
                print(f"    PASS: Found {len(found_expected)}/{len(test_case['expected'])} expected elements")
            else:
                print(f"    FAIL: Only found {len(found_expected)}/{len(test_case['expected'])} expected elements")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"FAIL: Test failed with exception: {e}")
        return False

def test_unified_memory_format():
    """Test that extracted preferences match unified memory format"""
    print("\nTEST: Unified Memory Format")
    
    try:
        from api.iris_chat_unified import extract_design_preferences
        
        test_message = "I love scandinavian style with light wood, neutral colors, and minimalist design"
        test_response = "Scandinavian design emphasizes simplicity and functionality. Light wood and neutral tones create a calm atmosphere."
        test_context = {"conversation": {"metadata": {"room_type": "bedroom"}}}
        
        preferences = extract_design_preferences(test_message, test_response, test_context)
        
        # Check format requirements for unified memory system
        format_checks = []
        
        # Should return a dictionary
        format_checks.append(("Dictionary type", isinstance(preferences, dict)))
        
        # Should have string keys
        string_keys = all(isinstance(k, str) for k in preferences.keys())
        format_checks.append(("String keys", string_keys))
        
        # Values should be JSON-serializable (lists, strings, bools)
        json_serializable = all(
            isinstance(v, (str, int, bool, list)) for v in preferences.values()
        )
        format_checks.append(("JSON serializable values", json_serializable))
        
        # Should extract meaningful content
        has_content = len(preferences) > 0
        format_checks.append(("Has extracted content", has_content))
        
        print("  Format validation:")
        all_passed = True
        for check_name, passed in format_checks:
            status = "PASS" if passed else "FAIL"
            print(f"    {status}: {check_name}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print(f"  Sample unified memory format:")
            print(f"    memory_type: design_preferences")
            print(f"    memory_key: iris_style_preferences") 
            print(f"    memory_value: {preferences}")
        
        return all_passed
        
    except Exception as e:
        print(f"FAIL: Test failed with exception: {e}")
        return False

def main():
    """Run memory extraction tests"""
    print("IRIS MEMORY EXTRACTION TEST")
    print("Testing design preference extraction for unified memory system")
    
    results = []
    
    # Test 1: Memory extraction logic
    result1 = test_memory_extraction()
    results.append(("Memory Extraction Logic", result1))
    
    # Test 2: Unified memory format
    result2 = test_unified_memory_format()
    results.append(("Unified Memory Format", result2))
    
    # Print results
    print("\n" + "="*50)
    print("TEST RESULTS")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nSUMMARY: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\nSUCCESS: Memory extraction working correctly!")
        print("Ready for unified memory system integration.")
    else:
        print("\nNOTICE: Some tests failed. Check details above.")

if __name__ == "__main__":
    main()