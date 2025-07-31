#!/usr/bin/env python3
"""
Debug budget extraction issue
"""
import re

def test_budget_extraction():
    """Test various budget extraction scenarios"""
    
    test_cases = [
        # (message, expected_min, expected_max)
        ("My budget is around $500-800 for the initial cleanup", 500, 800),
        ("I can spend $500 to $800", 500, 800),
        ("Budget: 500-800 dollars", 500, 800),
        ("I'm in Melbourne, Florida 32904. Budget is $500-800", 500, 800),
        ("32904 is my zip. Budget is between $500 and $800", 500, 800),
    ]
    
    for message, expected_min, expected_max in test_cases:
        print(f"\nTesting: {message}")
        
        # This is the CIA budget extraction logic
        message_lower = message.lower()
        collected = {}
        
        if not collected.get("budget_min") and ('budget' in message_lower or 'spend' in message_lower or '$' in message):
            # Look for budget ranges like "500-800" or "$500 to $800"
            range_pattern = r'\$?(\d{1,3}(?:,\d{3})*)\s*(?:-|to)\s*\$?(\d{1,3}(?:,\d{3})*)'
            range_match = re.search(range_pattern, message)
            
            if range_match:
                # Found a range
                collected["budget_min"] = int(range_match.group(1).replace(',', ''))
                collected["budget_max"] = int(range_match.group(2).replace(',', ''))
                print(f"  Extracted: ${collected['budget_min']}-${collected['budget_max']}")
            else:
                # Look for single amounts with dollar signs or in budget context
                dollar_amounts = re.findall(r'\$(\d{1,3}(?:,\d{3})*)', message)
                if dollar_amounts:
                    if len(dollar_amounts) >= 2:
                        nums = [int(a.replace(',', '')) for a in dollar_amounts]
                        collected["budget_min"] = min(nums)
                        collected["budget_max"] = max(nums)
                    else:
                        amount = int(dollar_amounts[0].replace(',', ''))
                        collected["budget_min"] = int(amount * 0.8)
                        collected["budget_max"] = int(amount * 1.2)
                    print(f"  Extracted from dollars: ${collected['budget_min']}-${collected['budget_max']}")
                else:
                    print("  No budget found")
        
        # Check if correct
        if collected.get("budget_min") == expected_min and collected.get("budget_max") == expected_max:
            print("  [OK] CORRECT")
        else:
            print(f"  [FAIL] WRONG - Expected ${expected_min}-${expected_max}")
    
    # Test the problematic case
    print("\n" + "="*60)
    print("PROBLEMATIC CASE - Multiple messages")
    print("="*60)
    
    messages = [
        "Hi, I need help with my lawn. It's completely overgrown and needs professional care.",
        "I'm in Melbourne, Florida 32904. The lawn is about half an acre.",
        "I need it done ASAP, within the next week if possible. The grass is knee-high!",
        "My budget is around $500-800 for the initial cleanup, then regular maintenance."
    ]
    
    collected = {}
    
    for i, message in enumerate(messages, 1):
        print(f"\n[{i}] Processing: {message}")
        message_lower = message.lower()
        
        # Budget extraction
        if not collected.get("budget_min") and ('budget' in message_lower or 'spend' in message_lower or '$' in message):
            # Look for budget ranges like "500-800" or "$500 to $800"
            range_pattern = r'\$?(\d{1,3}(?:,\d{3})*)\s*(?:-|to)\s*\$?(\d{1,3}(?:,\d{3})*)'
            range_match = re.search(range_pattern, message)
            
            if range_match:
                # Found a range
                collected["budget_min"] = int(range_match.group(1).replace(',', ''))
                collected["budget_max"] = int(range_match.group(2).replace(',', ''))
                print(f"    Extracted budget range: ${collected['budget_min']}-${collected['budget_max']}")
            else:
                # Look for single amounts with dollar signs or in budget context
                dollar_amounts = re.findall(r'\$(\d{1,3}(?:,\d{3})*)', message)
                if dollar_amounts:
                    if len(dollar_amounts) >= 2:
                        nums = [int(a.replace(',', '')) for a in dollar_amounts]
                        collected["budget_min"] = min(nums)
                        collected["budget_max"] = max(nums)
                    else:
                        amount = int(dollar_amounts[0].replace(',', ''))
                        collected["budget_min"] = int(amount * 0.8)
                        collected["budget_max"] = int(amount * 1.2)
                    print(f"    Extracted from dollars: ${collected['budget_min']}-${collected['budget_max']}")
    
    print(f"\nFinal collected budget: ${collected.get('budget_min', 'None')}-${collected.get('budget_max', 'None')}")

if __name__ == "__main__":
    test_budget_extraction()