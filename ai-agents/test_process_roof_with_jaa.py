#!/usr/bin/env python3
"""
Manually trigger JAA to process the roof conversation
"""

import asyncio
import os
from agents.jaa.agent import JobAssessmentAgent
from database_simple import db
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

async def process_roof_with_jaa():
    """Process the roof conversation with JAA"""
    print("Processing roof conversation with JAA...")
    
    # Get the roof conversation
    result = db.client.table('agent_conversations').select('*').eq('thread_id', 'test_roof_urgent').execute()
    
    if not result.data:
        print("No roof conversation found!")
        return
        
    conv = result.data[0]
    print(f"Found conversation: {conv['thread_id']}")
    print(f"State: Ready for JAA")
    
    # Initialize JAA
    jaa = JobAssessmentAgent()
    
    # Process with JAA
    bid_card_id = await jaa.process_conversation(conv['thread_id'])
    
    if bid_card_id:
        print(f"\n✅ JAA successfully created bid card: {bid_card_id}")
        
        # Get the bid card details
        bid_card = db.client.table('bid_cards').select('*').eq('id', bid_card_id).execute()
        if bid_card.data:
            card = bid_card.data[0]
            print(f"\nRoof Repair Bid Card:")
            print(f"- Number: {card['bid_card_number']}")
            print(f"- Type: {card['project_type']}")
            print(f"- Budget: ${card['budget_min']:,} - ${card['budget_max']:,}")
            print(f"- Urgency: {card['urgency_level']}")
            print(f"- Status: {card['status']}")
    else:
        print("❌ JAA failed to create bid card")

if __name__ == "__main__":
    asyncio.run(process_roof_with_jaa())