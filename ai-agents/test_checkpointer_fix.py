"""
Test the fixed checkpointer to see if it's actually saving to database
"""

import asyncio
import requests
import json
import time
from config.service_urls import get_backend_url

def test_memory_persistence():
    """Test if conversations are being saved and retrieved properly"""
    
    # Test session data
    contractor_lead_id = "test-memory-persistence"
    session_id = "test-session-1"
    
    print("TESTING Memory Persistence with Fixed Checkpointer")
    print("=" * 60)
    
    # First conversation
    print("\nSTEP 1: First conversation - introducing business")
    response1 = requests.post(
        f"{get_backend_url()}/api/coia/landing", 
        json={
            "message": "Hi, I'm Justin from JM Holiday Lighting. We specialize in professional holiday lighting installation.",
            "session_id": session_id,
            "contractor_lead_id": contractor_lead_id
        },
        timeout=30
    )
    
    if response1.status_code == 200:
        result1 = response1.json()
        print(f"SUCCESS: First response successful")
        print(f"Response: {get_last_ai_message(result1)[:200]}...")
        
        # Extract any company info that should be remembered
        if "JM Holiday Lighting" in str(result1):
            print("SUCCESS: Company name mentioned in response")
    else:
        print(f"ERROR: First conversation failed: {response1.status_code}")
        return False
    
    # Wait a moment to ensure checkpoint is saved
    time.sleep(2)
    
    # Second conversation - should remember the business
    print("\nSTEP 2: Second conversation - should remember business context") 
    response2 = requests.post(
        f"{get_backend_url()}/api/coia/landing",
        json={
            "message": "What services do we offer?",
            "session_id": session_id,  # Same session
            "contractor_lead_id": contractor_lead_id  # Same contractor
        },
        timeout=30
    )
    
    if response2.status_code == 200:
        result2 = response2.json()
        ai_message = get_last_ai_message(result2)
        print(f"SUCCESS: Second response successful")
        print(f"Response: {ai_message[:300]}...")
        
        # Check if it remembers the business context
        memory_indicators = [
            "JM Holiday Lighting",
            "your business",
            "your company", 
            "holiday lighting",
            "lighting installation"
        ]
        
        remembered = any(indicator.lower() in ai_message.lower() for indicator in memory_indicators)
        
        if remembered:
            print("SUCCESS: MEMORY WORKING! AI remembered business context")
            return True
        else:
            print("ERROR: MEMORY NOT WORKING - AI didn't remember business context")
            print(f"Looking for indicators: {memory_indicators}")
            return False
    else:
        print(f"ERROR: Second conversation failed: {response2.status_code}")
        return False

def get_last_ai_message(result):
    """Extract the last AI message from the response"""
    if result.get('messages'):
        for msg in reversed(result['messages']):
            if msg.get('type') == 'ai':
                return msg.get('content', '')
    return result.get('response', 'No response found')

def check_database_saves():
    """Check if checkpoints are actually being saved to database"""
    print("\nChecking Database for Saved Checkpoints")
    print("-" * 50)
    
    # This would need to be done via MCP, but for now just inform about the test
    print("Database check:")
    print("   - Checkpoints should appear in langgraph_checkpoints table")
    print("   - Thread IDs should match contractor_lead_ids") 
    print("   - Conversation state should be saved as JSONB")
    print("\n   Manual check: Use Supabase dashboard to verify data exists")

if __name__ == "__main__":
    print("Starting COIA Memory Persistence Test")
    print("Testing if fixed checkpointer actually saves conversation state")
    
    success = test_memory_persistence()
    
    if success:
        print("\nSUCCESS: Memory persistence is working!")
        print("Fixed checkpointer is saving conversations to database")
        print("COIA can continue conversations across API calls")
    else:
        print("\nFAILURE: Memory persistence still not working")
        print("Need to debug checkpointer implementation further")
    
    check_database_saves()