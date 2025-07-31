#!/usr/bin/env python3
"""
Debug data flow between CIA and JAA
"""
import asyncio
import httpx
from datetime import datetime
import json

async def debug_data_flow():
    """Trace data through CIA -> DB -> JAA"""
    
    base_url = "http://localhost:8000"
    
    # Check if server is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/")
            if response.status_code != 200:
                print("Server not running! Start with: python main.py")
                return
    except:
        print("Server not running! Start with: python main.py")
        return
    
    print("="*60)
    print("DEBUGGING CIA -> DATABASE -> JAA DATA FLOW")
    print("="*60)
    
    # Single test message with budget
    test_message = "My budget is $500-800 for lawn care in Melbourne, FL 32904"
    
    session_id = None
    
    # Step 1: Send to CIA
    print("\n1. SENDING TO CIA")
    print("-" * 40)
    print(f"Message: {test_message}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{base_url}/api/cia/chat",
            json={
                "message": test_message,
                "session_id": session_id
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            session_id = result["session_id"]
            
            print(f"\nCIA Response:")
            print(f"  Session ID: {session_id}")
            print(f"  Response: {result['response'][:80]}...")
            
            # Check state in response
            if 'state' in result:
                state = result['state']
                collected_info = state.get('collected_info', {})
                print(f"\nCIA Collected Info:")
                print(f"  budget_min: {collected_info.get('budget_min')}")
                print(f"  budget_max: {collected_info.get('budget_max')}")
                print(f"  project_type: {collected_info.get('project_type')}")
                print(f"  address: {collected_info.get('address')}")
                
                # Show raw JSON
                print(f"\nRaw collected_info JSON:")
                print(json.dumps(collected_info, indent=2))
        else:
            print(f"ERROR: {response.status_code}")
            print(response.text)
            return
    
    # Step 2: Check what's in database
    print("\n\n2. CHECKING DATABASE")
    print("-" * 40)
    
    # Import database module to check directly
    from database_simple import db
    
    # Load conversation from database
    saved_conversation = await db.load_conversation_state(session_id)
    
    if saved_conversation:
        print(f"Found conversation in database!")
        
        # Check the structure
        print(f"\nDatabase record keys: {list(saved_conversation.keys())}")
        
        # Get state
        db_state = saved_conversation.get('state', {})
        db_collected_info = db_state.get('collected_info', {})
        
        print(f"\nDatabase Collected Info:")
        print(f"  budget_min: {db_collected_info.get('budget_min')}")
        print(f"  budget_max: {db_collected_info.get('budget_max')}")
        print(f"  project_type: {db_collected_info.get('project_type')}")
        
        # Check if it's stored as JSON string or dict
        if isinstance(db_state, str):
            print("\nWARNING: State is stored as string, not dict!")
            try:
                db_state_parsed = json.loads(db_state)
                print("Parsed state from string")
            except:
                print("Failed to parse state string")
    else:
        print("No conversation found in database!")
        print("This explains why JAA gets wrong values - CIA isn't saving to DB!")
    
    # Step 3: Call JAA
    print("\n\n3. CALLING JAA")
    print("-" * 40)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{base_url}/api/jaa/process/{session_id}"
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\nJAA Response:")
            
            # Handle nested response format
            if 'bid_card' in result:
                bid_card = result['bid_card']
                print(f"  Bid Card Number: {bid_card.get('bid_card_number')}")
                print(f"  Project Type: {bid_card.get('project_type')}")
                print(f"  Budget Min: {bid_card.get('budget_min')}")
                print(f"  Budget Max: {bid_card.get('budget_max')}")
                print(f"  Urgency: {bid_card.get('urgency_level')}")
                
                # Show where JAA got the data
                print(f"\nJAA Debug Info:")
                print(f"  CIA Thread ID: {bid_card.get('cia_thread_id')}")
        else:
            print(f"ERROR: {response.status_code}")
            print(response.text)
    
    print("\n" + "="*60)
    print("DATA FLOW ANALYSIS COMPLETE")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(debug_data_flow())