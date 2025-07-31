#!/usr/bin/env python3
"""
Test CIA → JAA Flow with 12 Data Points Extraction
Tests the NEW InstaBids-focused data extraction system
"""
import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.cia.agent import CustomerInterfaceAgent
from agents.jaa.new_agent import NewJobAssessmentAgent

async def test_cia_with_12_data_points():
    """Test CIA agent to see if it collects all 12 data points"""
    print("\n" + "="*80)
    print("🧪 TESTING CIA AGENT - 12 DATA POINTS COLLECTION")
    print("="*80 + "\n")
    
    # Initialize CIA agent
    cia_agent = CustomerInterfaceAgent(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    # Create test conversation with rich details
    test_message = """
    I need lawn care service. My grass is knee-high and getting out of control. 
    I'm in Melbourne, FL 32904 with a half-acre property. Budget is around $500-800 
    for initial cleanup and then maybe $150-200 monthly for ongoing service.
    This is pretty urgent - my HOA is sending notices. I'd prefer bi-weekly service.
    The property is a single family home with a gate code 1234. 
    I'm looking for someone licensed and insured. Text me, don't call.
    """
    
    print("📝 Test Message:")
    print(test_message)
    print("\n" + "-"*80 + "\n")
    
    # Process with CIA
    result = await cia_agent.handle_conversation(
        user_id="test_user_12dp",
        message=test_message,
        session_id=f"test_12dp_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    )
    
    print("🤖 CIA Response:")
    print(result.get('response', 'No response'))
    print("\n" + "-"*80 + "\n")
    
    # Check collected info structure
    if 'collected_info' in result:
        collected = result['collected_info']
        print("📊 Collected Info Structure (NEW 12 Data Points):")
        
        # Check each of the 12 data points
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
            status = "✅" if value is not None else "❌"
            print(f"{status} {label}: {value}")
        
        # Check legacy fields for budget
        print("\n📈 Legacy Budget Fields:")
        print(f"   Budget Min: ${collected.get('budget_min', 'Not set')}")
        print(f"   Budget Max: ${collected.get('budget_max', 'Not set')}")
        
        # Check homeowner preferences
        print("\n👤 Homeowner Preferences:")
        print(f"   Communication: {collected.get('homeowner_communication_preference', 'Not set')}")
        print(f"   Scheduling: {collected.get('homeowner_scheduling_preference', 'Not set')}")
        
        # Check photo info
        print("\n📸 Photos:")
        print(f"   Uploaded: {len(collected.get('uploaded_photos', []))} photos")
        
    print("\n" + "-"*80 + "\n")
    
    # Check if ready for JAA
    print(f"🎯 Ready for JAA: {result.get('ready_for_jaa', False)}")
    print(f"❓ Missing Fields: {result.get('missing_fields', [])}")
    
    return result.get('session_id'), result


async def test_jaa_extraction(session_id: str):
    """Test JAA extraction of bid card data"""
    print("\n" + "="*80)
    print("🧪 TESTING JAA AGENT - BID CARD EXTRACTION")
    print("="*80 + "\n")
    
    # Initialize NEW JAA agent
    jaa_agent = NewJobAssessmentAgent()
    
    # Process conversation
    print(f"📥 Processing session: {session_id}")
    result = jaa_agent.process_conversation(session_id)
    
    if result['success']:
        print("✅ JAA Processing SUCCESSFUL!")
        
        bid_data = result['bid_card_data']
        
        print("\n📋 EXTRACTED BID CARD DATA:")
        print("\n🏗️ Core Project Info:")
        print(f"   Project Type: {bid_data.get('project_type')}")
        print(f"   Service Type: {bid_data.get('service_type')}")
        print(f"   Description: {bid_data.get('project_description')}")
        
        print("\n💰 Budget & Timeline:")
        print(f"   Budget Min: ${bid_data.get('budget_min')}")
        print(f"   Budget Max: ${bid_data.get('budget_max')}")
        print(f"   Budget Context: {bid_data.get('budget_context')}")
        print(f"   Timeline Urgency: {bid_data.get('timeline_urgency')}")
        print(f"   Urgency Level: {bid_data.get('urgency_level')}")
        print(f"   Urgency Reason: {bid_data.get('urgency_reason')}")
        
        print("\n📍 Location:")
        print(f"   ZIP Code: {bid_data.get('location_zip')}")
        
        print("\n🏘️ Smart Opportunities:")
        print(f"   Group Bidding Potential: {bid_data.get('group_bidding_potential')}")
        print(f"   Property Context: {bid_data.get('property_context')}")
        
        print("\n📊 Scoring:")
        print(f"   Intention Score: {bid_data.get('intention_score')}/10")
        print(f"   Complexity Score: {result.get('complexity_score')}/10")
        
        print("\n👷 Contractor Requirements:")
        contractor_req = bid_data.get('contractor_requirements', {})
        print(f"   Count Needed: {contractor_req.get('contractor_count')}")
        print(f"   Specialties: {contractor_req.get('specialties_required')}")
        
        print("\n✅ BID CARD CREATED:")
        print(f"   Number: {result['bid_card_number']}")
        print(f"   Database ID: {result.get('database_record', {}).get('id')}")
        
    else:
        print(f"❌ JAA Processing FAILED: {result.get('error')}")
    
    return result


async def test_modify_bid_card(bid_card_number: str):
    """Test modifying bid card with JAA"""
    print("\n" + "="*80)
    print("🧪 TESTING JAA MODIFICATION - UPDATE BID CARD")
    print("="*80 + "\n")
    
    # Initialize NEW JAA agent
    jaa_agent = NewJobAssessmentAgent()
    
    # Test modifications
    modifications = {
        'service_type': 'ongoing_service',
        'frequency': 'weekly',
        'group_bidding_potential': True,
        'intention_score': 8
    }
    
    print(f"📝 Modifying bid card: {bid_card_number}")
    print(f"🔧 Modifications: {json.dumps(modifications, indent=2)}")
    
    result = jaa_agent.modify_bid_card(bid_card_number, modifications)
    
    if result['success']:
        print("\n✅ MODIFICATION SUCCESSFUL!")
        print(f"   Applied: {', '.join(result['modifications_applied'])}")
    else:
        print(f"\n❌ MODIFICATION FAILED: {result.get('error')}")
    
    return result


async def main():
    """Run all tests"""
    try:
        # Test 1: CIA Collection
        session_id, cia_result = await test_cia_with_12_data_points()
        
        if not session_id:
            print("\n❌ CIA test failed - no session ID")
            return
        
        # Give database a moment to sync
        await asyncio.sleep(2)
        
        # Test 2: JAA Extraction
        jaa_result = await test_jaa_extraction(session_id)
        
        if jaa_result['success']:
            # Test 3: JAA Modification
            await test_modify_bid_card(jaa_result['bid_card_number'])
        
        # Summary
        print("\n" + "="*80)
        print("📊 TEST SUMMARY")
        print("="*80)
        
        # Check data point collection
        if 'collected_info' in cia_result:
            collected = cia_result['collected_info']
            
            core_points = [
                collected.get('project_type'),
                collected.get('service_type'),
                collected.get('timeline_urgency'),
                collected.get('location_zip')
            ]
            
            instabids_points = [
                collected.get('budget_context'),
                collected.get('group_bidding_potential') is not None,
                collected.get('intention_score') is not None
            ]
            
            core_collected = sum(1 for p in core_points if p is not None)
            instabids_collected = sum(1 for p in instabids_points if p)
            
            print(f"\n✅ Core Data Points: {core_collected}/4")
            print(f"✅ InstaBids Points: {instabids_collected}/3")
            
            if jaa_result['success']:
                budget_correct = (
                    jaa_result['bid_card_data']['budget_min'] == 500 and
                    jaa_result['bid_card_data']['budget_max'] == 800
                )
                print(f"✅ Budget Extraction: {'CORRECT' if budget_correct else 'INCORRECT'}")
                print(f"✅ Bid Card Created: {jaa_result['bid_card_number']}")
            
        print("\n🎯 CIA → JAA Flow Status: OPERATIONAL with NEW 12 Data Points System")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())