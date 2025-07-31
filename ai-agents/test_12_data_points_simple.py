#!/usr/bin/env python3
"""
Test CIA → JAA Flow with 12 Data Points Extraction (Simple version)
"""
import asyncio
import json
import os
from datetime import datetime
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.cia.agent import CustomerInterfaceAgent
from agents.jaa.new_agent import NewJobAssessmentAgent


async def test_cia_collection():
    """Test CIA agent collection of 12 data points"""
    print("\n" + "="*80)
    print("TESTING CIA AGENT - 12 DATA POINTS COLLECTION")
    print("="*80 + "\n")
    
    # Initialize CIA agent
    cia_agent = CustomerInterfaceAgent(anthropic_api_key=os.getenv('ANTHROPIC_API_KEY', 'demo_key'))
    
    # Test message with all details
    test_message = """
    I need lawn care service. My grass is knee-high and getting out of control. 
    I'm in Melbourne, FL 32904 with a half-acre property. Budget is around $500-800 
    for initial cleanup and then maybe $150-200 monthly for ongoing service.
    This is pretty urgent - my HOA is sending notices. I'd prefer bi-weekly service.
    The property is a single family home with a gate code 1234. 
    I'm looking for someone licensed and insured. Text me, don't call.
    """
    
    print("Test Message:")
    print(test_message)
    print("\n" + "-"*80 + "\n")
    
    # Process with CIA
    result = await cia_agent.handle_conversation(
        user_id="test_user_12dp",
        message=test_message,
        session_id=f"test_12dp_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    )
    
    print("CIA Response:")
    print(result.get('response', 'No response'))
    print("\n" + "-"*80 + "\n")
    
    # Check collected info
    if 'collected_info' in result:
        collected = result['collected_info']
        print("Collected Info Structure (NEW 12 Data Points):")
        
        # Check each data point
        data_points = [
            ("1. Project Type", collected.get('project_type')),
            ("2. Service Type", collected.get('service_type')),
            ("3. Project Description", collected.get('project_description')),
            ("4. Budget Context", collected.get('budget_context')),
            ("5. Timeline Urgency", collected.get('timeline_urgency')),
            ("6. Urgency Reason", collected.get('urgency_reason')),
            ("7. Location ZIP", collected.get('location_zip')),
            ("8. Group Bidding Potential", collected.get('group_bidding_potential')),
            ("9. Property Context", collected.get('property_context')),
            ("10. Material Preferences", collected.get('material_preferences')),
            ("11. Special Requirements", collected.get('special_requirements')),
            ("12. Intention Score", collected.get('intention_score')),
        ]
        
        for label, value in data_points:
            status = "[OK]" if value is not None else "[MISSING]"
            print(f"{status} {label}: {value}")
        
        # Check budget fields
        print("\nBudget Fields:")
        print(f"   Budget Min: ${collected.get('budget_min', 'Not set')}")
        print(f"   Budget Max: ${collected.get('budget_max', 'Not set')}")
    
    print(f"\nReady for JAA: {result.get('ready_for_jaa', False)}")
    print(f"Missing Fields: {result.get('missing_fields', [])}")
    
    return result.get('session_id')


def test_jaa_extraction(session_id):
    """Test JAA extraction"""
    print("\n" + "="*80)
    print("TESTING JAA AGENT - BID CARD EXTRACTION")
    print("="*80 + "\n")
    
    # Initialize NEW JAA agent
    jaa_agent = NewJobAssessmentAgent()
    
    # Process conversation
    print(f"Processing session: {session_id}")
    result = jaa_agent.process_conversation(session_id)
    
    if result['success']:
        print("JAA Processing SUCCESSFUL!")
        
        bid_data = result['bid_card_data']
        
        print("\nEXTRACTED BID CARD DATA:")
        print(f"   Project Type: {bid_data.get('project_type')}")
        print(f"   Service Type: {bid_data.get('service_type')}")
        print(f"   Budget Min: ${bid_data.get('budget_min')}")
        print(f"   Budget Max: ${bid_data.get('budget_max')}")
        print(f"   Timeline Urgency: {bid_data.get('timeline_urgency')}")
        print(f"   Group Bidding: {bid_data.get('group_bidding_potential')}")
        print(f"   Intention Score: {bid_data.get('intention_score')}/10")
        print(f"\nBid Card Number: {result['bid_card_number']}")
        
        return result['bid_card_number']
    else:
        print(f"JAA Processing FAILED: {result.get('error')}")
        return None


async def main():
    """Run tests"""
    try:
        # Test CIA
        session_id = await test_cia_collection()
        
        if session_id:
            # Wait for database
            await asyncio.sleep(2)
            
            # Test JAA
            bid_card_number = test_jaa_extraction(session_id)
            
            if bid_card_number:
                print("\n" + "="*80)
                print("TEST SUMMARY: CIA -> JAA Flow WORKING")
                print("="*80)
            else:
                print("\nJAA extraction failed")
        else:
            print("\nCIA collection failed")
            
    except Exception as e:
        print(f"\nTest error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())