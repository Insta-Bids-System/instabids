#!/usr/bin/env python3
"""
Test the fast mode detector directly
"""
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from agents.coia.fast_mode_detector import fast_detect_mode

def test_mode_detection():
    """Test fast mode detection with various messages"""
    
    test_messages = [
        "show me available projects",
        "Show me available projects", 
        "available projects",
        "I need projects to bid on",
        "find projects",
        "opportunities",
        "what can i bid",
        "Hello, I'm a contractor",
        "research my company"
    ]
    
    print("Testing fast mode detection...")
    
    for message in test_messages:
        mode = fast_detect_mode(message)
        print(f"Message: '{message}' -> Mode: '{mode}'")
    
    # Test the exact message from our API test
    api_message = "show me available projects"
    api_mode = fast_detect_mode(api_message)
    print(f"\nAPI test message: '{api_message}' -> Mode: '{api_mode}'")
    
    if api_mode == "bid_card_search":
        print("SUCCESS: Fast mode detector should trigger bid_card_search")
        return True
    else:
        print("ISSUE: Fast mode detector is not triggering bid_card_search")
        return False

if __name__ == "__main__":
    success = test_mode_detection()
    sys.exit(0 if success else 1)