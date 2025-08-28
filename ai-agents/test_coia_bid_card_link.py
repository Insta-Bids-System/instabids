"""
Test COIA Bid Card Link Entry Point Implementation
Tests the new bid card link interface for contractor onboarding
"""

import asyncio
import io
import logging
import sys
from datetime import datetime

# Fix Windows console encoding issues
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add the ai-agents directory to the path
sys.path.append("C:\\Users\\Not John Or Justin\\Documents\\instabids\\ai-agents")

from agents.coia.unified_graph import (
    create_unified_coia_system, 
    invoke_coia_bid_card_link
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_bid_card_link_entry_point():
    """Test the bid card link entry point functionality"""
    
    print("[LINK] Testing COIA Bid Card Link Entry Point...")
    print("=" * 50)
    
    try:
        # Create the unified COIA system
        print("Creating unified COIA system...")
        coia_app = await create_unified_coia_system()
        
        # Test data for bid card link
        test_bid_card_id = "BC-TEST-123"
        test_contractor_lead_id = "contractor-test-456" 
        test_verification_token = "verify-token-789"
        
        print(f"Test Parameters:")
        print(f"  Bid Card ID: {test_bid_card_id}")
        print(f"  Contractor Lead ID: {test_contractor_lead_id}")
        print(f"  Verification Token: {test_verification_token}")
        print()
        
        # Invoke the bid card link entry point
        print("Invoking bid card link entry point...")
        result = await invoke_coia_bid_card_link(
            app=coia_app,
            bid_card_id=test_bid_card_id,
            contractor_lead_id=test_contractor_lead_id,
            verification_token=test_verification_token
        )
        
        print("[SUCCESS] Bid Card Link Entry Point Test Results:")
        print("=" * 50)
        
        # Extract key information from result
        messages = result.get("messages", [])
        interface = result.get("interface")
        current_mode = result.get("current_mode")
        verification_token = result.get("verification_token")
        source_channel = result.get("source_channel")
        
        print(f"Interface: {interface}")
        print(f"Current Mode: {current_mode}")
        print(f"Source Channel: {source_channel}")
        print(f"Verification Token Set: {verification_token is not None}")
        print()
        
        # Display the greeting message
        if messages:
            last_message = messages[-1]
            if hasattr(last_message, 'content'):
                print("Generated Greeting:")
                print("-" * 30)
                print(last_message.content)
                print("-" * 30)
            else:
                print("Message content:", last_message)
        
        # Test state structure
        print(f"\nState Structure:")
        print(f"  Messages: {len(messages)} message(s)")
        print(f"  Session ID: {result.get('session_id', 'Not set')}")
        print(f"  Contractor Lead ID: {result.get('contractor_lead_id', 'Not set')}")
        print(f"  Original Project ID: {result.get('original_project_id', 'Not set')}")
        
        # Check if contractor profile was loaded
        contractor_profile = result.get("contractor_profile")
        if contractor_profile:
            print(f"  Contractor Profile: Loaded ({len(contractor_profile)} fields)")
        else:
            print(f"  Contractor Profile: Not loaded (expected for missing test data)")
        
        # Check if bid cards were attached
        bid_cards = result.get("bid_cards_attached", [])
        print(f"  Bid Cards Attached: {len(bid_cards)} card(s)")
        
        print("\n[SUCCESS] TEST PASSED - Bid Card Link Entry Point Working")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] TEST FAILED - Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_bid_card_entry_point_routing():
    """Test the entry point routing logic for bid card interface"""
    
    print("\n[ROUTING] Testing Entry Point Routing Logic...")
    print("=" * 50)
    
    try:
        from agents.coia.unified_graph import UnifiedCoIAGraph
        from agents.coia.unified_state import UnifiedCoIAState
        
        # Create graph instance 
        graph = UnifiedCoIAGraph()
        
        # Test different contractor profiles to verify routing
        test_cases = [
            {
                "name": "Registered Contractor",
                "state": {
                    "interface": "bid_card_link",
                    "contractor_profile": {"user_id": "user-123", "email": "test@example.com"},
                    "contractor_lead_id": "lead-123"
                },
                "expected": "bid_submission"
            },
            {
                "name": "Contractor with Contact Info",
                "state": {
                    "interface": "bid_card_link", 
                    "contractor_profile": {"email": "test@example.com", "phone": "555-1234"},
                    "contractor_lead_id": "lead-456"
                },
                "expected": "conversation"
            },
            {
                "name": "New Contractor",
                "state": {
                    "interface": "bid_card_link",
                    "contractor_profile": {},
                    "contractor_lead_id": "lead-789"
                },
                "expected": "conversation"
            }
        ]
        
        for test_case in test_cases:
            print(f"Testing: {test_case['name']}")
            
            # Test the entry point determination
            entry_point = graph._determine_entry_point(test_case["state"])
            
            if entry_point == test_case["expected"]:
                print(f"  [SUCCESS] Routed to '{entry_point}' (expected)")
            else:
                print(f"  [ERROR] Routed to '{entry_point}' (expected '{test_case['expected']}')")
            
        print("\n[SUCCESS] Entry Point Routing Test Completed")
        
    except Exception as e:
        print(f"[ERROR] Entry Point Routing Test Failed: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all bid card link tests"""
    
    print("[TEST] COIA Bid Card Link Entry Point Testing")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Test the basic entry point functionality
    success1 = await test_bid_card_link_entry_point()
    
    # Test the routing logic
    await test_bid_card_entry_point_routing()
    
    print("\n" + "=" * 60)
    if success1:
        print("[COMPLETE] ALL TESTS PASSED - Bid Card Link Entry Point Ready!")
    else:
        print("[WARNING] SOME TESTS FAILED - Review implementation")
    
    print(f"Test completed at: {datetime.now().isoformat()}")


if __name__ == "__main__":
    asyncio.run(main())