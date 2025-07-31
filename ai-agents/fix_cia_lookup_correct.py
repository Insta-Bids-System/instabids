"""
CORRECT CIA BID CARD LOOKUP
Find the actual way bid cards are linked to users
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_simple import db

def trace_bid_card_ownership():
    """Trace how bid cards connect to users"""
    print("\n[ANALYSIS] How are bid cards linked to users?")
    print("-"*50)
    
    # Get a recent bid card
    bid_card = db.client.table('bid_cards').select('*').order('created_at', desc=True).limit(1).execute()
    
    if not bid_card.data:
        print("No bid cards found")
        return
    
    bc = bid_card.data[0]
    print(f"Bid card: {bc['bid_card_number']}")
    print(f"Thread ID: {bc['cia_thread_id']}")
    
    # Find the conversation
    conv = db.client.table('agent_conversations').select('*').eq('thread_id', bc['cia_thread_id']).execute()
    
    if conv.data:
        print(f"\nFound conversation:")
        print(f"  - user_id: {conv.data[0]['user_id']}")
        print(f"  - agent_type: {conv.data[0]['agent_type']}")
        
        # So the link is: bid_card -> cia_thread_id -> agent_conversations -> user_id
        print(f"\n[DISCOVERY] Link chain: bid_card.cia_thread_id -> agent_conversations.thread_id -> user_id")
        
        return conv.data[0]['user_id']
    else:
        print("No conversation found for this bid card")
        return None

def create_correct_lookup():
    """Create the correct lookup method"""
    print("\n[SOLUTION] Correct CIA lookup method")
    print("-"*50)
    
    code = '''
async def _find_user_bid_cards(self, user_id: str) -> List[Dict[str, Any]]:
    """Find all bid cards for a user through conversations"""
    try:
        # Step 1: Get all user's conversations
        conversations = db.client.table('agent_conversations').select('thread_id').eq('user_id', user_id).execute()
        
        if not conversations.data:
            print(f"[CIA] No conversations found for user {user_id}")
            return []
        
        # Step 2: Get thread_ids
        thread_ids = [c['thread_id'] for c in conversations.data]
        
        # Step 3: Find bid cards with these thread_ids
        bid_cards = db.client.table('bid_cards').select('*').in_('cia_thread_id', thread_ids).order('created_at', desc=True).execute()
        
        if bid_cards.data:
            print(f"[CIA] Found {len(bid_cards.data)} bid cards for user")
            return bid_cards.data
        else:
            print(f"[CIA] No bid cards found for user's {len(thread_ids)} conversations")
            return []
            
    except Exception as e:
        print(f"[CIA] Error finding bid cards: {e}")
        return []

async def _find_latest_bid_card(self, user_id: str, project_type: Optional[str] = None) -> Optional[str]:
    """Find the most recent bid card for a user"""
    bid_cards = await self._find_user_bid_cards(user_id)
    
    if not bid_cards:
        return None
    
    # Filter by project type if specified
    if project_type:
        filtered = [bc for bc in bid_cards if project_type.lower() in bc.get('project_type', '').lower()]
        if filtered:
            return filtered[0]['bid_card_number']
    
    # Return most recent
    return bid_cards[0]['bid_card_number']
'''
    
    print(code)
    return code

def test_real_lookup():
    """Test the lookup with real data"""
    print("\n[TEST] Testing with real data")
    print("-"*50)
    
    # Trace a real user
    user_id = trace_bid_card_ownership()
    
    if user_id:
        print(f"\n[TEST] Looking up bid cards for user: {user_id}")
        
        # Test our method
        conversations = db.client.table('agent_conversations').select('thread_id').eq('user_id', user_id).execute()
        
        if conversations.data:
            thread_ids = [c['thread_id'] for c in conversations.data]
            print(f"Found {len(thread_ids)} conversations")
            
            bid_cards = db.client.table('bid_cards').select('*').in_('cia_thread_id', thread_ids).execute()
            
            if bid_cards.data:
                print(f"Found {len(bid_cards.data)} bid cards:")
                for bc in bid_cards.data:
                    print(f"  - {bc['bid_card_number']} ({bc['project_type']})")
            else:
                print("No bid cards found")

def main():
    print("\n" + "="*70)
    print("CORRECT CIA BID CARD LOOKUP SOLUTION")
    print("="*70)
    
    # Create correct lookup
    create_correct_lookup()
    
    # Test it
    test_real_lookup()
    
    print("\n" + "="*70)
    print("THE ANSWER TO YOUR QUESTION")
    print("="*70)
    
    print("\n1. YES - We're using the single homeowner agent (CIA) approach")
    print("2. CIA has FULL AUTONOMY to search the database")
    print("3. The lookup chain is: user_id -> conversations -> bid_cards")
    print("4. CIA will find bid cards and call JAA to modify them")
    print("5. This keeps everything in one agent as you wanted")
    
    print("\nNext step: Add these methods to CIA and test the complete flow")

if __name__ == "__main__":
    main()