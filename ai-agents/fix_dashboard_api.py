#!/usr/bin/env python3
"""
Fix dashboard API connectivity issues
"""

def diagnose_api_issue():
    """
    The backend is hanging when accessed from frontend
    """
    print("""
DASHBOARD API FIX:

1. The backend might be stuck in a bad state. Need to:
   - Kill all Python processes on port 8008
   - Restart the backend cleanly
   
2. Check for database connection issues:
   - The API might be timing out on Supabase queries
   - Add timeout and error handling

3. Fix the API endpoint to handle missing data gracefully:

@app.get("/api/bid-cards/homeowner/{homeowner_id}")
async def get_homeowner_bid_cards_direct(homeowner_id: str):
    try:
        # Add timeout to database queries
        from asyncio import timeout
        
        async with timeout(5):  # 5 second timeout
            # Get conversations for this user
            conversations_result = db.client.table('agent_conversations').select('thread_id').eq('user_id', homeowner_id).execute()
            
            if not conversations_result.data:
                return []  # Return empty array, not error
            
            # Get thread IDs
            thread_ids = [conv['thread_id'] for conv in conversations_result.data]
            
            # Get bid cards linked to these conversations
            result = db.client.table('bid_cards').select("*").in_('cia_thread_id', thread_ids).order('created_at', desc=True).execute()
            
            # Process bid cards to ensure all required fields
            bid_cards = []
            for card in (result.data or []):
                # Ensure photo_urls field exists
                if card.get('bid_document') and card['bid_document'].get('all_extracted_data'):
                    extracted = card['bid_document']['all_extracted_data']
                    # Map images to photo_urls for frontend compatibility
                    if 'images' in extracted and 'photo_urls' not in extracted:
                        extracted['photo_urls'] = extracted['images']
                
                bid_cards.append(card)
            
            return bid_cards
            
    except TimeoutError:
        print(f"[API] Timeout getting bid cards for {homeowner_id}")
        raise HTTPException(status_code=504, detail="Database query timeout")
    except Exception as e:
        print(f"[API] Error getting bid cards: {e}")
        raise HTTPException(status_code=500, detail=str(e))

4. Add health check endpoint:

@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}
""")


if __name__ == "__main__":
    diagnose_api_issue()