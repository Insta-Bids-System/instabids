#!/usr/bin/env python3
"""
Debug NEW JAA Agent - Find which field is too long
"""

import asyncio
import os
import sys
import uuid
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.cia.agent import CustomerInterfaceAgent
from agents.jaa.new_agent import NewJobAssessmentAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

async def debug_field_lengths():
    """Debug which field is causing VARCHAR(20) error"""
    print("DEBUGGING NEW JAA FIELD LENGTHS")
    print("=" * 50)
    
    # Initialize CIA
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    cia = CustomerInterfaceAgent(anthropic_key)
    
    # Use proper UUID
    user_id = "00000000-0000-0000-0000-000000000000"
    
    # Get CIA to ready state
    result = await cia.handle_conversation(
        user_id=user_id,
        message="I need a new roof installed on my house in 12345 zip code"
    )
    
    if result and result.get('ready_for_jaa'):
        session_id = result['session_id']
        
        # Initialize NEW JAA
        jaa = NewJobAssessmentAgent()
        
        # Load conversation and extract data (but don't save)
        conversation_result = jaa.supabase.table('agent_conversations').select("*").eq('thread_id', session_id).execute()
        conversation_record = conversation_result.data[0]
        conversation_state = json.loads(conversation_record['state'])
        
        # Extract bid card data
        bid_card_data = jaa.extractor.extract_bid_card_data({'state': conversation_state})
        
        # Check field lengths
        timestamp = datetime.now().strftime("%m%d%H%M%S")
        bid_card_number = f"BC{timestamp}"
        complexity_score = jaa._calculate_complexity_score(bid_card_data)
        
        print("FIELD LENGTH ANALYSIS:")
        print("-" * 30)
        
        fields_to_check = {
            'bid_card_number': bid_card_number,
            'project_type': bid_card_data['project_type'],
            'urgency_level': bid_card_data['urgency_level'],
            'cia_thread_id': session_id[-20:],  # Show truncated version
            'cia_thread_id_full': session_id,   # Show full version for comparison
            'status': 'ready_for_distribution'
        }
        
        for field_name, field_value in fields_to_check.items():
            length = len(str(field_value))
            status = "OK" if length <= 20 else "TOO LONG"
            print(f"{field_name}: '{field_value}' ({length} chars) - {status}")
        
        # Check if urgency_level is the issue
        print(f"\nDETAILS:")
        print(f"urgency_level value: '{bid_card_data['urgency_level']}'")
        print(f"project_type value: '{bid_card_data['project_type']}'")
        print(f"service_type value: '{bid_card_data['service_type']}'")
        
        # Check other potential string fields
        other_fields = [
            'service_type', 'timeline_urgency', 'budget_context', 
            'property_type', 'frequency'
        ]
        
        print(f"\nOTHER FIELDS:")
        for field in other_fields:
            if field in bid_card_data:
                value = bid_card_data[field]
                length = len(str(value))
                status = "OK" if length <= 20 else "TOO LONG"
                print(f"{field}: '{value}' ({length} chars) - {status}")
        
        return True
    else:
        print("Failed to get CIA ready for JAA")
        return False

async def main():
    success = await debug_field_lengths()
    return success

if __name__ == "__main__":
    asyncio.run(main())