"""
FIX CIA BID CARD LOOKUP
Make CIA properly find bid cards by homeowner_id
"""
import os
import sys
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_simple import db

def analyze_bid_card_schema():
    """First, let's see what columns bid_cards actually has"""
    print("\n[STEP 1] Analyzing bid_cards table schema")
    print("-"*50)
    
    # Get a sample bid card to see structure
    sample = db.client.table('bid_cards').select('*').limit(1).execute()
    
    if sample.data:
        print("Bid card columns:")
        for key in sample.data[0].keys():
            print(f"  - {key}: {type(sample.data[0][key]).__name__}")
    else:
        print("No bid cards found in database")
    
    return sample.data[0] if sample.data else None

def find_user_bid_cards(user_id):
    """Find the right way to query bid cards for a user"""
    print(f"\n[STEP 2] Finding bid cards for user")
    print("-"*50)
    
    # Method 1: Try direct user_id
    try:
        result = db.client.table('bid_cards').select('*').eq('user_id', user_id).execute()
        if result.data:
            print(f"Method 1 SUCCESS: Found {len(result.data)} bid cards by user_id")
            return result.data
    except Exception as e:
        print(f"Method 1 failed: {e}")
    
    # Method 2: Try through homeowner_id
    try:
        # First get homeowner_id
        homeowner = db.client.table('homeowners').select('id').eq('user_id', user_id).single().execute()
        if homeowner.data:
            homeowner_id = homeowner.data['id']
            result = db.client.table('bid_cards').select('*').eq('homeowner_id', homeowner_id).execute()
            if result.data:
                print(f"Method 2 SUCCESS: Found {len(result.data)} bid cards by homeowner_id")
                return result.data
    except Exception as e:
        print(f"Method 2 failed: {e}")
    
    # Method 3: Try through conversations
    try:
        # Get user's conversations
        convs = db.client.table('agent_conversations').select('thread_id').eq('user_id', user_id).execute()
        if convs.data:
            thread_ids = [c['thread_id'] for c in convs.data]
            # Look for bid cards with matching thread_ids
            result = db.client.table('bid_cards').select('*').in_('cia_thread_id', thread_ids).execute()
            if result.data:
                print(f"Method 3 SUCCESS: Found {len(result.data)} bid cards by cia_thread_id")
                return result.data
    except Exception as e:
        print(f"Method 3 failed: {e}")
    
    print("No bid cards found for user")
    return []

def create_cia_lookup_method():
    """Generate the correct lookup method for CIA"""
    print("\n[STEP 3] Creating CIA lookup method")
    print("-"*50)
    
    code = '''
async def _find_user_bid_cards(self, user_id: str) -> List[Dict[str, Any]]:
    """Find all bid cards for a user"""
    try:
        # Get homeowner_id first
        homeowner = db.client.table('homeowners').select('id').eq('user_id', user_id).single().execute()
        if not homeowner.data:
            return []
        
        homeowner_id = homeowner.data['id']
        
        # Get bid cards by homeowner_id
        result = db.client.table('bid_cards').select('*').eq('homeowner_id', homeowner_id).order('created_at', desc=True).execute()
        
        return result.data if result.data else []
    except Exception as e:
        print(f"[CIA] Error finding bid cards: {e}")
        return []

async def _find_latest_bid_card(self, user_id: str, project_type: Optional[str] = None) -> Optional[str]:
    """Find the most recent bid card for a user, optionally filtered by project type"""
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
    
    print("Generated CIA lookup methods:")
    print(code)
    
    return code

def test_with_real_data():
    """Test with actual database data"""
    print("\n[STEP 4] Testing with real data")
    print("-"*50)
    
    # Get a recent bid card
    recent = db.client.table('bid_cards').select('*').order('created_at', desc=True).limit(1).execute()
    
    if recent.data:
        bid_card = recent.data[0]
        print(f"Found recent bid card: {bid_card['bid_card_number']}")
        print(f"  - homeowner_id: {bid_card.get('homeowner_id', 'N/A')}")
        print(f"  - project_type: {bid_card.get('project_type', 'N/A')}")
        print(f"  - created_at: {bid_card.get('created_at', 'N/A')}")
        
        # Try to trace back to user
        if bid_card.get('homeowner_id'):
            homeowner = db.client.table('homeowners').select('user_id').eq('id', bid_card['homeowner_id']).single().execute()
            if homeowner.data:
                print(f"  - user_id: {homeowner.data['user_id']}")
                
                # Now test our lookup
                found_cards = find_user_bid_cards(homeowner.data['user_id'])
                print(f"\nLookup test: Found {len(found_cards)} bid cards for this user")

def main():
    print("\n" + "="*70)
    print("CIA BID CARD LOOKUP FIX")
    print("="*70)
    
    # Analyze schema
    sample = analyze_bid_card_schema()
    
    # Test lookup methods
    if sample:
        test_user_id = "test-user-123"  # This would fail, but shows the method
        find_user_bid_cards(test_user_id)
    
    # Generate fix
    create_cia_lookup_method()
    
    # Test with real data
    test_with_real_data()
    
    print("\n" + "="*70)
    print("SOLUTION SUMMARY")
    print("="*70)
    print("\n1. Bid cards are linked via homeowner_id, not user_id")
    print("2. CIA needs to: user_id -> homeowner_id -> bid_cards")
    print("3. The lookup should order by created_at desc to get most recent")
    print("4. CIA should use this lookup BEFORE triggering project decision logic")

if __name__ == "__main__":
    main()