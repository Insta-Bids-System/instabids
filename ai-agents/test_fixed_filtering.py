"""
Complete test of intelligent messaging filtering
This will verify the actual workflow works end-to-end
"""

import asyncio
import uuid
from datetime import datetime
from agents.intelligent_messaging_agent import intelligent_messaging_agent, MessageType

async def test_complete_filtering():
    """Test the complete intelligent messaging workflow"""
    
    print("=" * 70)
    print("TESTING COMPLETE BID SUBMISSION FILTERING WORKFLOW")
    print("=" * 70)
    
    # Create test message with contact info
    test_message = """I can complete your project for $5000.
Please call me at 555-123-4567 or email contractor@email.com
I have 10 years experience and can start immediately."""
    
    print("\n1. ORIGINAL MESSAGE:")
    print("-" * 40)
    print(test_message)
    
    # Create proper state with all required fields
    initial_state = {
        'original_content': test_message,
        'sender_type': 'contractor',
        'sender_id': str(uuid.uuid4()),  # Use valid UUID
        'bid_card_id': str(uuid.uuid4()),  # Use valid UUID
        'conversation_id': str(uuid.uuid4()),  # Use valid UUID
        'message_type': MessageType.TEXT,
        'attachments': [],
        'has_attachments': False,
        'threats_detected': [],
        'agent_comments': {},
        'timestamp': datetime.now().isoformat()
    }
    
    config = {
        'configurable': {
            'thread_id': f'test-{uuid.uuid4()}',
            'checkpoint_ns': ''
        }
    }
    
    print("\n2. PROCESSING WITH INTELLIGENT AGENT...")
    print("-" * 40)
    
    try:
        # Run the workflow
        result = await intelligent_messaging_agent.ainvoke(initial_state, config)
        
        # Check what fields are actually returned
        print("\n3. RETURNED FIELDS:")
        print("-" * 40)
        for key in result.keys():
            if 'content' in key.lower() or 'message' in key.lower():
                print(f"  {key}: {result.get(key, 'N/A')[:100] if result.get(key) else 'None'}")
        
        # Check for filtered content (the actual field used)
        filtered = result.get('filtered_content', '')
        detected_violations = result.get('detected_violations', [])
        threats = result.get('threats_detected', [])
        agent_action = result.get('agent_decision', 'UNKNOWN')
        
        print("\n4. FILTERING RESULTS:")
        print("-" * 40)
        print(f"Filtered Content: {filtered}")
        print(f"Detected Violations: {detected_violations}")
        print(f"Threats Detected: {threats}")
        print(f"Agent Decision: {agent_action}")
        
        # Verify filtering worked
        print("\n5. VERIFICATION:")
        print("-" * 40)
        
        if not filtered:
            print("❌ FAILED: No filtered content returned")
            return False
        elif '555-123-4567' in filtered or 'contractor@email.com' in filtered:
            print("❌ FAILED: Contact information NOT filtered")
            return False
        else:
            print("✅ SUCCESS: Contact information properly filtered")
            print(f"✅ Original length: {len(test_message)} chars")
            print(f"✅ Filtered length: {len(filtered)} chars")
            return True
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    success = await test_complete_filtering()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ WORKFLOW TEST PASSED - System filters contact info correctly")
    else:
        print("❌ WORKFLOW TEST FAILED - System NOT working properly")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())