#!/usr/bin/env python3
"""
Fix bid card modification functionality
"""

def fix_modification_handling():
    """
    The issue: CIA agent can't find existing bid cards to modify
    """
    print("""
FIX FOR BID CARD MODIFICATIONS:

1. In CIA agent's _handle_modification_requests method:
   - Query bid_cards table by user_id AND project_type
   - Match on keywords like "kitchen", "bathroom", etc.

2. Add this logic:

async def find_existing_bid_card(self, user_id: str, message: str):
    # Extract project type from message
    project_keywords = {
        'kitchen': 'kitchen_remodel',
        'bathroom': 'bathroom_renovation',
        'lawn': 'lawn_maintenance',
        'landscaping': 'landscaping',
        'roof': 'roofing'
    }
    
    message_lower = message.lower()
    for keyword, project_type in project_keywords.items():
        if keyword in message_lower:
            # Find bid cards for this user and project type
            conversations = self.supabase.table('agent_conversations').select('thread_id').eq('user_id', user_id).execute()
            
            if conversations.data:
                thread_ids = [c['thread_id'] for c in conversations.data]
                
                # Get bid cards linked to these conversations
                bid_cards = self.supabase.table('bid_cards').select('*').in_('cia_thread_id', thread_ids).eq('project_type', project_type).execute()
                
                if bid_cards.data:
                    return bid_cards.data[0]  # Return first matching bid card
    
    return None

3. Then update the bid card:

if existing_bid_card:
    # Extract new budget from message
    new_budget = extract_budget_from_message(message)
    
    # Update bid card
    update_result = self.supabase.table('bid_cards').update({
        'budget_min': new_budget['min'],
        'budget_max': new_budget['max'],
        'updated_at': datetime.now().isoformat()
    }).eq('id', existing_bid_card['id']).execute()
    
    print(f"[CIA] Updated bid card {existing_bid_card['bid_card_number']} with new budget")
""")


if __name__ == "__main__":
    fix_modification_handling()