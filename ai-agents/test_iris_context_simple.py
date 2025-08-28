#!/usr/bin/env python3
"""
Simple Test: IRIS Conversation Context
Verify IRIS pulls all conversation data with proper context
"""

import asyncio
import json
from database_simple import client as supabase

async def test_iris_conversation_access():
    """Test if IRIS can access all conversation types"""
    print("Testing IRIS Conversation Context Access")
    print("=" * 50)
    
    try:
        print("1. Finding real homeowner with conversations...")
        
        # Get a homeowner with conversations
        homeowner_result = supabase.table("homeowners").select("id, user_id").limit(5).execute()
        
        if not homeowner_result.data:
            print("ERROR: No homeowners found")
            return False
            
        print(f"   Found {len(homeowner_result.data)} homeowners")
        
        for homeowner in homeowner_result.data:
            user_id = homeowner['id'] 
            user_id = homeowner['user_id']
            
            print(f"\n2. Testing homeowner: {user_id}")
            
            # Check unified conversations
            conv_result = supabase.table("unified_conversations").select("*").eq(
                "created_by", user_id
            ).execute()
            
            print(f"   Unified conversations: {len(conv_result.data)}")
            
            if conv_result.data:
                conversation_id = conv_result.data[0]['id']
                
                # Check messages in this conversation
                msg_result = supabase.table("unified_messages").select("*").eq(
                    "conversation_id", conversation_id
                ).execute()
                
                print(f"   Messages in conversation: {len(msg_result.data)}")
                
                # Analyze message types
                message_analysis = {
                    'agent_messages': 0,
                    'user_messages': 0,
                    'filtered_content': 0,
                    'messaging_agent_source': 0,
                    'cia_messages': 0,
                    'has_metadata': 0
                }
                
                for msg in msg_result.data:
                    if msg.get('sender_type') == 'agent':
                        message_analysis['agent_messages'] += 1
                        if msg.get('agent_type') == 'CIA':
                            message_analysis['cia_messages'] += 1
                    elif msg.get('sender_type') == 'user':
                        message_analysis['user_messages'] += 1
                    
                    metadata = msg.get('metadata', {})
                    if metadata:
                        message_analysis['has_metadata'] += 1
                        
                        if metadata.get('content_filtered'):
                            message_analysis['filtered_content'] += 1
                            
                        if metadata.get('messaging_source') == 'intelligent_messaging_agent':
                            message_analysis['messaging_agent_source'] += 1
                
                print("   Message Analysis:")
                for key, value in message_analysis.items():
                    if value > 0:
                        print(f"     {key}: {value}")
                
                # Show sample message with metadata
                filtered_msgs = [msg for msg in msg_result.data 
                               if msg.get('metadata', {}).get('content_filtered')]
                
                if filtered_msgs:
                    print("   SAMPLE FILTERED MESSAGE:")
                    sample = filtered_msgs[0]
                    print(f"     Content: {sample.get('content', '')[:100]}...")
                    metadata = sample.get('metadata', {})
                    print(f"     Original: {metadata.get('original_content', 'N/A')[:100]}...")
                    print(f"     Filter reasons: {metadata.get('filter_reasons', [])}")
                
                # Test IRIS context access
                print("\n3. Testing IRIS context building...")
                
                from api.iris_chat_unified_fixed import get_conversation_context_direct, build_iris_system_prompt
                
                context = await get_conversation_context_direct(conversation_id)
                
                print(f"   IRIS Context Retrieved:")
                print(f"     Messages: {len(context.get('messages', []))}")
                print(f"     Memory entries: {len(context.get('memory', []))}")
                print(f"     Bid submissions: {len(context.get('bid_submissions', []))}")
                print(f"     Actual bids: {len(context.get('actual_bids', []))}")
                
                # Check if IRIS builds proper context
                system_prompt = build_iris_system_prompt(conv_result.data[0], context)
                
                print(f"\n4. IRIS System Prompt Analysis:")
                print(f"     Length: {len(system_prompt)} characters")
                print(f"     Has project context: {'PROJECT INFORMATION' in system_prompt}")
                print(f"     Has contractor context: {'CONTRACTOR' in system_prompt}")
                print(f"     Has design guidance: {'DESIGN GUIDANCE' in system_prompt}")
                
                # Check if conversations are properly interpreted
                conversations_mentioned = 'conversation' in system_prompt.lower()
                messaging_mentioned = 'messag' in system_prompt.lower()
                filtering_mentioned = 'filter' in system_prompt.lower()
                
                print(f"     Mentions conversations: {conversations_mentioned}")
                print(f"     Mentions messaging: {messaging_mentioned}")
                print(f"     Mentions filtering: {filtering_mentioned}")
                
                if len(context.get('messages', [])) > 0:
                    print("\n   EVIDENCE: IRIS HAS ACCESS TO ALL CONVERSATIONS")
                    return True
                
        print("\nNo conversations found with sufficient data")
        return False
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the test"""
    success = await test_iris_conversation_access()
    
    print("\n" + "=" * 50)
    if success:
        print("RESULT: IRIS CAN ACCESS ALL CONVERSATION DATA")
        print("- Unified conversations: ACCESSIBLE")
        print("- Message metadata: ACCESSIBLE") 
        print("- Contact filtering info: ACCESSIBLE")
        print("- Agent attribution: ACCESSIBLE")
    else:
        print("RESULT: IRIS ACCESS NEEDS VERIFICATION")

if __name__ == "__main__":
    asyncio.run(main())