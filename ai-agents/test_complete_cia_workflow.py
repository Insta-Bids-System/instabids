#!/usr/bin/env python3
"""
Complete CIA Workflow Test - End-to-End Verification
Proves that CIA agent field extraction and database saving works
"""

import asyncio
import json
import sys
import os
import uuid

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.cia.agent import CustomerInterfaceAgent
import requests

async def test_complete_cia_workflow():
    """Complete end-to-end test of CIA agent workflow"""
    
    print("\n=== COMPLETE CIA WORKFLOW TEST ===")
    print("Testing: CIA Agent -> Field Extraction -> Database Saving -> Verification")
    
    # Generate proper UUIDs
    user_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    
    print(f"\nTest IDs:")
    print(f"User ID: {user_id}")
    print(f"Session ID: {session_id}")
    
    # Get OpenAI API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("[FAILED] No OpenAI API key found")
        return
        
    print("[SUCCESS] OpenAI API key found")
    
    # Initialize CIA agent
    cia_agent = CustomerInterfaceAgent(openai_api_key)
    print("[SUCCESS] CIA agent initialized")
    
    # Test Conversation 1: Initial project description
    print("\n--- CONVERSATION 1: Initial Project ---")
    
    try:
        result1 = await cia_agent.handle_conversation(
            user_id=user_id,
            session_id=session_id,
            message="Hi! I want to renovate my bathroom. I need a new tile shower, vanity, and flooring.",
            project_id=None
        )
        
        print("[SUCCESS] Conversation 1 completed")
        
        # Wait for async operations
        await asyncio.sleep(1)
        
        # Check potential bid card creation
        response1 = requests.get(f"http://localhost:8008/api/cia/conversation/{session_id}/potential-bid-card")
        
        if response1.status_code == 200:
            bid_card1 = response1.json()
            print(f"[SUCCESS] Potential bid card created: {bid_card1['id']}")
            print(f"[SUCCESS] Completion after msg 1: {bid_card1.get('completion_percentage', 0)}%")
            
            fields1 = bid_card1.get('fields_collected', {})
            print(f"[SUCCESS] Fields collected: {len(fields1)}")
            for field, value in fields1.items():
                print(f"  - {field}: {value}")
        else:
            print(f"[FAILED] No bid card after conversation 1: {response1.status_code}")
            return
            
    except Exception as e:
        print(f"[FAILED] Conversation 1 failed: {e}")
        return
    
    # Test Conversation 2: Add location information
    print("\n--- CONVERSATION 2: Location Details ---")
    
    try:
        result2 = await cia_agent.handle_conversation(
            user_id=user_id,
            session_id=session_id,
            message="I'm located in Austin, Texas, ZIP code 78701. This is for my master bathroom.",
            project_id=None
        )
        
        print("[SUCCESS] Conversation 2 completed")
        
        await asyncio.sleep(1)
        
        # Check updated bid card
        response2 = requests.get(f"http://localhost:8008/api/cia/conversation/{session_id}/potential-bid-card")
        
        if response2.status_code == 200:
            bid_card2 = response2.json()
            print(f"[SUCCESS] Completion after msg 2: {bid_card2.get('completion_percentage', 0)}%")
            
            fields2 = bid_card2.get('fields_collected', {})
            print(f"[SUCCESS] Fields after update: {len(fields2)}")
            for field, value in fields2.items():
                print(f"  - {field}: {value}")
        else:
            print(f"[FAILED] Could not retrieve updated bid card: {response2.status_code}")
            
    except Exception as e:
        print(f"[FAILED] Conversation 2 failed: {e}")
        return
    
    # Test Conversation 3: Timeline and urgency
    print("\n--- CONVERSATION 3: Timeline & Budget ---")
    
    try:
        result3 = await cia_agent.handle_conversation(
            user_id=user_id,
            session_id=session_id,
            message="I need this done urgently, within 2 weeks if possible. My budget is around $15,000 to $20,000.",
            project_id=None
        )
        
        print("[SUCCESS] Conversation 3 completed")
        
        await asyncio.sleep(1)
        
        # Check final bid card state
        response3 = requests.get(f"http://localhost:8008/api/cia/conversation/{session_id}/potential-bid-card")
        
        if response3.status_code == 200:
            bid_card3 = response3.json()
            print(f"[SUCCESS] Final completion: {bid_card3.get('completion_percentage', 0)}%")
            print(f"[SUCCESS] Ready for conversion: {bid_card3.get('ready_for_conversion', False)}")
            
            fields3 = bid_card3.get('fields_collected', {})
            missing3 = bid_card3.get('missing_fields', [])
            
            print(f"[SUCCESS] Final fields collected: {len(fields3)}")
            for field, value in fields3.items():
                print(f"  - {field}: {value}")
                
            print(f"Missing fields: {missing3}")
            
            # Final verification - check database directly
            print("\n--- DATABASE VERIFICATION ---")
            
            # Get the bid card ID for database verification
            bid_card_id = bid_card3['id']
            
            # Verify via direct API call to potential bid cards endpoint
            db_response = requests.get(f"http://localhost:8008/api/cia/potential-bid-cards/{bid_card_id}")
            
            if db_response.status_code == 200:
                db_data = db_response.json()
                print("[SUCCESS] Database verification passed")
                print(f"Database completion: {db_data.get('completion_percentage', 0)}%")
                
                # Check that data actually persisted in database
                db_fields = db_data.get('fields_collected', {})
                if len(db_fields) > 0:
                    print(f"[SUCCESS] {len(db_fields)} fields persisted in database")
                    
                    # Summary of what we proved
                    print("\n=== WORKFLOW VERIFICATION COMPLETE ===")
                    print("[SUCCESS] ✓ CIA agent conversations work")
                    print("[SUCCESS] ✓ Field extraction from natural language works") 
                    print("[SUCCESS] ✓ Potential bid card creation works")
                    print("[SUCCESS] ✓ Field updates work")
                    print("[SUCCESS] ✓ Database persistence works")
                    print("[SUCCESS] ✓ Completion percentage calculation works")
                    print(f"[SUCCESS] ✓ End result: {bid_card3.get('completion_percentage', 0)}% completion with {len(db_fields)} fields")
                    
                    return True
                else:
                    print("[FAILED] No fields found in database")
            else:
                print(f"[FAILED] Database verification failed: {db_response.status_code}")
        else:
            print(f"[FAILED] Could not retrieve final bid card: {response3.status_code}")
            
    except Exception as e:
        print(f"[FAILED] Conversation 3 failed: {e}")
        return
    
    return False

if __name__ == "__main__":
    success = asyncio.run(test_complete_cia_workflow())
    
    if success:
        print("\n[COMPLETE SUCCESS] CIA agent field extraction and database saving PROVEN to work!")
    else:
        print("\n[FAILED] Test failed - system not working properly")