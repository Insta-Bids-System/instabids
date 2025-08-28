"""
End-to-end test of bid submission contact filtering
Tests the complete flow from submission to filtered storage
"""

import asyncio
import json
from agents.intelligent_messaging_agent import intelligent_messaging_agent

async def test_contact_filtering():
    """Test that contact information gets filtered from contractor messages"""
    
    # Test message with contact info that should be filtered
    message_with_contact = """
    I can do this project for $5000. 
    Call me at 555-123-4567 or email me at contractor@email.com
    I'm available to start next week.
    """
    
    config = {
        'configurable': {
            'thread_id': 'test-thread-123',
            'checkpoint_ns': ''
        }
    }
    
    initial_state = {
        'original_content': message_with_contact,
        'sender_type': 'contractor',
        'sender_id': 'test-contractor-id',
        'bid_card_id': 'test-bid-card-id',
        'conversation_id': 'test-convo-id'
    }
    
    print('=' * 60)
    print('TESTING BID SUBMISSION CONTACT FILTERING')
    print('=' * 60)
    print('\nOriginal Message:')
    print(message_with_contact)
    print('\nProcessing with intelligent agent...\n')
    
    try:
        result = await intelligent_messaging_agent.ainvoke(initial_state, config)
        
        print('RESULTS:')
        print('-' * 40)
        print(f"Filtered Content: {result.get('processed_content', 'ERROR - No content')}")
        print(f"Detected Violations: {result.get('detected_violations', [])}")
        print(f"Agent Action: {result.get('agent_action', 'ERROR - No action')}")
        print(f"Agent Comments: {result.get('agent_comments', {})}")
        print(f"Message Saved: {result.get('message_saved', False)}")
        
        # Check if filtering worked
        if 'processed_content' in result:
            if '555-123-4567' not in result['processed_content'] and 'contractor@email.com' not in result['processed_content']:
                print('\n✅ SUCCESS: Contact information was filtered!')
            else:
                print('\n❌ FAILURE: Contact information was NOT filtered!')
        else:
            print('\n❌ ERROR: No processed content returned!')
            
    except Exception as e:
        print(f'\n❌ ERROR: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_contact_filtering())