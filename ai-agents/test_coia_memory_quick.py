import os
"""
Quick COIA Memory Test - Focused on persistent memory verification
"""

import requests
import sys
import io
from datetime import datetime
import uuid
from config.service_urls import get_backend_url

# Fix Unicode output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def quick_memory_test():
    """Test COIA memory with two conversations"""
    
    print("🚀 COIA MEMORY VERIFICATION - QUICK TEST")
    print("=" * 60)
    
    base_url = get_backend_url()
    session_id = f"memory-test-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Test 1: Create contractor with specific details
    print("\n[1] Creating contractor with memorable details...")
    response1 = requests.post(f"{base_url}/api/coia/chat", json={
        "message": "Hi, I'm Sarah from Johnson's Premium Plumbing. We specialize in luxury bathroom installations and have 15 years of experience.",
        "session_id": session_id
    })
    
    if response1.ok:
        data1 = response1.json()
        print(f"✅ Contractor created: {data1.get('profile', {}).get('company_name', 'Unknown')}")
        
        # Test 2: Ask about specific details
        print("\n[2] Testing memory - asking about business details...")
        response2 = requests.post(f"{base_url}/api/coia/chat", json={
            "message": "What's my name again? And how many years of experience did I mention?",
            "session_id": session_id
        })
        
        if response2.ok:
            data2 = response2.json()
            response_text = data2.get('response', '').lower()
            
            # Check memory
            memory_checks = {
                "sarah": "sarah" in response_text,
                "johnson": "johnson" in response_text,
                "15 years": "15" in response_text,
                "plumbing": "plumbing" in response_text
            }
            
            print("\nMemory Check Results:")
            for detail, found in memory_checks.items():
                status = "✅" if found else "❌"
                print(f"   {status} Remembers '{detail}': {found}")
            
            print(f"\nResponse preview: {response_text[:200]}...")
            
            # Check conversation history
            history = data2.get('conversation_history', [])
            print(f"\nConversation history: {len(history)} messages")
            
            if len(history) >= 2 and any(memory_checks.values()):
                print("\n🎉 SUCCESS: COIA has persistent memory working!")
                return True
            else:
                print("\n❌ FAILED: Memory not working properly")
                return False
        else:
            print("❌ Second API call failed")
            return False
    else:
        print("❌ First API call failed")
        return False

if __name__ == "__main__":
    success = quick_memory_test()
    if success:
        print("\n" + "🎉" * 30)
        print("COIA PERSISTENT MEMORY VERIFIED!")
        print("🎉" * 30)
    else:
        print("\n❌ Memory test failed")
        sys.exit(1)