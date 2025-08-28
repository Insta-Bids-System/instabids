"""
REAL test of bid submission contact filtering
No fake claims - actual verification
"""

import asyncio
from agents.intelligent_messaging_agent import intelligent_messaging_agent, MessageType

async def test_contact_filtering():
    """Test that contact information ACTUALLY gets filtered"""
    
    # Test message with contact info that MUST be filtered
    message_with_contact = """I can do this project for $5000. 
Call me at 555-123-4567 or email me at contractor@email.com
I'm available to start next week."""
    
    config = {
        'configurable': {
            'thread_id': 'test-thread-123',
            'checkpoint_ns': ''
        }
    }
    
    # Include ALL required fields
    initial_state = {
        'original_content': message_with_contact,
        'sender_type': 'contractor',
        'sender_id': 'test-contractor-id',
        'bid_card_id': 'test-bid-card-id',
        'conversation_id': 'test-convo-id',
        'message_type': MessageType.TEXT,  # Add missing field
        'attachments': [],
        'has_attachments': False
    }
    
    print('TESTING BID SUBMISSION CONTACT FILTERING')
    print('=' * 60)
    print('\nOriginal Message:')
    print(message_with_contact)
    print('\nProcessing with intelligent agent...\n')
    
    try:
        result = await intelligent_messaging_agent.ainvoke(initial_state, config)
        
        print('RESULTS:')
        print('-' * 40)
        
        processed = result.get('processed_content', 'NO CONTENT RETURNED')
        violations = result.get('detected_violations', [])
        action = result.get('agent_action', 'NO ACTION')
        
        print(f"Filtered Content: {processed}")
        print(f"Detected Violations: {violations}")
        print(f"Agent Action: {action}")
        
        # ACTUAL VERIFICATION
        if '555-123-4567' in processed or 'contractor@email.com' in processed:
            print('\n[FAILURE] Contact information was NOT filtered!')
            return False
        elif processed == 'NO CONTENT RETURNED':
            print('\n[FAILURE] No processed content returned!')
            return False
        else:
            print('\n[SUCCESS] Contact information was filtered!')
            return True
            
    except Exception as e:
        print(f'\n[ERROR] Test failed with exception:')
        print(str(e))
        import traceback
        traceback.print_exc()
        return False

async def main():
    success = await test_contact_filtering()
    if success:
        print('\n' + '=' * 60)
        print('TEST PASSED - System is working')
    else:
        print('\n' + '=' * 60)
        print('TEST FAILED - System is NOT working')

if __name__ == '__main__':
    asyncio.run(main())