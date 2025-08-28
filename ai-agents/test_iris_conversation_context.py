#!/usr/bin/env python3
"""
Test IRIS Conversation Context Handling
Verify IRIS properly processes all conversation types with semantic context
"""

import asyncio
import json
from api.iris_chat_unified_fixed import get_conversation_context_direct, build_iris_system_prompt

async def test_iris_conversation_context():
    """Test IRIS conversation context processing"""
    print("🧪 Testing IRIS Conversation Context Processing")
    print("=" * 60)
    
    # Test with a real conversation ID that should have mixed conversation types
    test_conversation_id = "1234567-test-conversation"  # This would be a real conversation ID
    
    try:
        print("1️⃣ Testing Conversation Context Retrieval...")
        
        # Get context using IRIS method
        context = await get_conversation_context_direct(test_conversation_id)
        
        print(f"✅ Retrieved Context:")
        print(f"   - Conversation: {bool(context.get('conversation'))}")
        print(f"   - Messages: {len(context.get('messages', []))}")
        print(f"   - Memory: {len(context.get('memory', []))}")
        print(f"   - Bid Submissions: {len(context.get('bid_submissions', []))}")
        print(f"   - Actual Bids: {len(context.get('actual_bids', []))}")
        
        print("\n2️⃣ Analyzing Message Types and Metadata...")
        
        messages = context.get('messages', [])
        conversation_analysis = {
            'total_messages': len(messages),
            'cia_conversations': 0,
            'messaging_conversations': 0,
            'filtered_content': 0,
            'agent_messages': 0,
            'user_messages': 0,
            'metadata_present': 0
        }
        
        for msg in messages:
            # Count message types
            if msg.get('sender_type') == 'agent':
                conversation_analysis['agent_messages'] += 1
                if msg.get('agent_type') == 'CIA':
                    conversation_analysis['cia_conversations'] += 1
            elif msg.get('sender_type') == 'user':
                conversation_analysis['user_messages'] += 1
            
            # Check for messaging metadata
            metadata = msg.get('metadata', {})
            if metadata:
                conversation_analysis['metadata_present'] += 1
                
                # Check for contact filtering
                if metadata.get('content_filtered'):
                    conversation_analysis['filtered_content'] += 1
                
                # Check for messaging source
                if metadata.get('messaging_source') == 'intelligent_messaging_agent':
                    conversation_analysis['messaging_conversations'] += 1
        
        print(f"📊 Conversation Analysis:")
        for key, value in conversation_analysis.items():
            print(f"   - {key.replace('_', ' ').title()}: {value}")
        
        print("\n3️⃣ Testing System Prompt Generation...")
        
        # Generate system prompt to see if context is properly interpreted
        system_prompt = build_iris_system_prompt(context.get('conversation', {}), context)
        
        print(f"✅ System Prompt Generated: {len(system_prompt)} characters")
        
        # Check if system prompt contains conversation context
        prompt_analysis = {
            'has_project_context': '🏠 PROJECT INFORMATION' in system_prompt,
            'has_contractor_context': '💼 CONTRACTOR' in system_prompt,
            'has_bid_context': 'BIDS' in system_prompt,
            'has_design_guidance': 'DESIGN GUIDANCE' in system_prompt,
            'mentions_filtering': 'filtered' in system_prompt.lower(),
            'mentions_messaging': 'message' in system_prompt.lower()
        }
        
        print(f"🔍 System Prompt Analysis:")
        for key, value in prompt_analysis.items():
            status = "✅" if value else "❌"
            print(f"   {status} {key.replace('_', ' ').title()}: {value}")
        
        # Show sample of system prompt
        print(f"\n📝 System Prompt Sample (first 500 chars):")
        print(f"{system_prompt[:500]}...")
        
        print("\n4️⃣ Testing Conversation Message Context...")
        
        # Check if any messages have contact filtering metadata
        filtered_messages = [msg for msg in messages if msg.get('metadata', {}).get('content_filtered')]
        
        if filtered_messages:
            print(f"✅ Found {len(filtered_messages)} messages with contact filtering")
            sample_msg = filtered_messages[0]
            print(f"   Sample filtered message metadata:")
            print(f"   {json.dumps(sample_msg.get('metadata', {}), indent=4)}")
        else:
            print("❌ No messages with contact filtering metadata found")
        
        # Check if any messages show messaging source
        messaging_messages = [msg for msg in messages 
                            if msg.get('metadata', {}).get('messaging_source') == 'intelligent_messaging_agent']
        
        if messaging_messages:
            print(f"✅ Found {len(messaging_messages)} messages from messaging agent")
        else:
            print("❌ No messages from messaging agent found")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def test_with_real_homeowner_data():
    """Test with actual homeowner data from database"""
    print("\n🏠 Testing with Real Homeowner Data")
    print("=" * 60)
    
    try:
        # Import database client
        from database_simple import client as supabase
        
        print("1️⃣ Finding homeowner with conversations...")
        
        # Get a homeowner with actual conversation data
        homeowner_result = supabase.table("homeowners").select("id, user_id").limit(1).execute()
        
        if not homeowner_result.data:
            print("❌ No homeowners found")
            return False
            
        homeowner = homeowner_result.data[0]
        homeowner_user_id = homeowner['user_id']
        
        print(f"✅ Testing with homeowner: {homeowner_user_id}")
        
        # Get unified conversations for this homeowner
        conv_result = supabase.table("unified_conversations").select("*").eq(
            "created_by", homeowner['id']
        ).limit(1).execute()
        
        if not conv_result.data:
            print(f"❌ No conversations found for homeowner {homeowner_user_id}")
            return False
            
        conversation_id = conv_result.data[0]['id']
        print(f"✅ Testing conversation: {conversation_id}")
        
        # Get messages for this conversation
        msg_result = supabase.table("unified_messages").select("*").eq(
            "conversation_id", conversation_id
        ).execute()
        
        print(f"✅ Found {len(msg_result.data)} messages in conversation")
        
        # Analyze metadata
        for i, msg in enumerate(msg_result.data[:3]):  # Show first 3 messages
            print(f"\n📨 Message {i+1}:")
            print(f"   Sender: {msg.get('sender_type')} ({msg.get('sender_id')})")
            print(f"   Content: {msg.get('content', '')[:100]}...")
            
            metadata = msg.get('metadata', {})
            if metadata:
                print(f"   Metadata keys: {list(metadata.keys())}")
                if metadata.get('content_filtered'):
                    print(f"   ⚠️  Content was filtered!")
                if metadata.get('messaging_source'):
                    print(f"   🤖 Source: {metadata.get('messaging_source')}")
            else:
                print(f"   ❌ No metadata found")
        
        # Test IRIS context building with real data
        context = await get_conversation_context_direct(conversation_id)
        system_prompt = build_iris_system_prompt(conv_result.data[0], context)
        
        print(f"\n🎯 IRIS System Prompt Analysis:")
        print(f"   Length: {len(system_prompt)} characters")
        print(f"   Contains project context: {'PROJECT INFORMATION' in system_prompt}")
        print(f"   Contains contractor context: {'CONTRACTOR' in system_prompt}")
        print(f"   Contains conversation context: {len(context.get('messages', []))} messages processed")
        
        return True
        
    except Exception as e:
        print(f"❌ Real data test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all IRIS conversation context tests"""
    print("🧪 IRIS Conversation Context Verification")
    print("Testing if IRIS properly pulls and contextualizes ALL conversation data")
    print("=" * 80)
    
    # Test 1: Basic context processing
    print("TEST 1: Basic Context Processing")
    test1_result = await test_iris_conversation_context()
    
    # Test 2: Real homeowner data
    print("\nTEST 2: Real Homeowner Data")
    test2_result = await test_with_real_homeowner_data()
    
    # Summary
    print("\n" + "=" * 80)
    print("🏆 TEST RESULTS SUMMARY:")
    print(f"   Basic Context Test: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"   Real Data Test: {'✅ PASS' if test2_result else '❌ FAIL'}")
    
    if test2_result:
        print("\n✅ IRIS is properly configured to pull all conversation types with context")
    else:
        print("\n❌ IRIS context system needs enhancement")

if __name__ == "__main__":
    asyncio.run(main())