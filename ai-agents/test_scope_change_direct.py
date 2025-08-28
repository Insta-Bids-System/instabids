#!/usr/bin/env python3
"""
DIRECT SCOPE CHANGE DETECTION TEST
Tests scope change detection by calling the intelligent messaging agent directly
"""

import asyncio
import sys
import os

# Add the agents directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

from agents.intelligent_messaging_agent import process_intelligent_message

async def test_scope_change_direct():
    """Test scope change detection directly with the agent"""
    
    print("DIRECT SCOPE CHANGE DETECTION TEST")
    print("=" * 60)
    print("Testing scope change detection via direct agent call")
    print()
    
    # Test 1: Clear scope change - sod to turf
    print("TEST 1: Sod to Artificial Turf Change")
    print("-" * 40)
    
    try:
        result = await process_intelligent_message(
            content="Actually, I've been thinking about it more and I'd like to change from regular sod to artificial turf for the backyard. What would that change in your pricing?",
            sender_type="homeowner",
            sender_id="test-homeowner-123",
            bid_card_id="test-bid-card-456",
            recipient_id="test-contractor-789",
            conversation_id="test-conversation-001",
            attachments=[],
            image_data=None
        )
        
        print(f"Message: 'sod to artificial turf change'")
        print(f"Approved: {result.get('approved', False)}")
        print(f"Decision: {result.get('agent_decision', 'unknown')}")
        print(f"Threats: {result.get('threats_detected', [])}")
        
        # Check scope change detection
        scope_changes = result.get('scope_changes_detected', [])
        scope_details = result.get('scope_change_details', {})
        requires_update = result.get('requires_bid_update', False)
        contractors_to_notify = result.get('other_contractors_to_notify', [])
        
        print()
        print("SCOPE CHANGE ANALYSIS:")
        print(f"  Scope Changes Detected: {scope_changes}")
        print(f"  Scope Details: {scope_details}")
        print(f"  Requires Bid Update: {requires_update}")
        print(f"  Contractors to Notify: {contractors_to_notify}")
        
        # Check agent comments for homeowner-only questions
        agent_comments = result.get('agent_comments', [])
        homeowner_questions = [comment for comment in agent_comments if comment.get('type') == 'scope_change_question']
        
        if homeowner_questions:
            print()
            print("HOMEOWNER-ONLY QUESTIONS:")
            for question in homeowner_questions:
                print(f"  Question: '{question.get('content', '')}'")
                print(f"  Visibility: {question.get('visibility', 'unknown')}")
        
        scope_detected = len(scope_changes) > 0 or requires_update
        homeowner_question_exists = len(homeowner_questions) > 0
        
        print()
        if scope_detected:
            print("✅ SUCCESS: Scope change detected!")
            if homeowner_question_exists:
                print("✅ SUCCESS: Homeowner-only question generated!")
            else:
                print("⚠️ PARTIAL: Scope detected but no homeowner question")
        else:
            print("❌ ISSUE: Scope change not detected")
            
        return scope_detected, homeowner_question_exists
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, False

async def test_material_change():
    """Test material change detection"""
    
    print("\n" + "=" * 60)
    print("TEST 2: Material Change Detection")
    print("-" * 40)
    
    try:
        result = await process_intelligent_message(
            content="I want to switch from granite countertops to quartz. How does that affect the price and timeline?",
            sender_type="homeowner", 
            sender_id="test-homeowner-123",
            bid_card_id="test-bid-card-456",
            recipient_id="test-contractor-789",
            conversation_id="test-conversation-002",
            attachments=[],
            image_data=None
        )
        
        print(f"Message: 'granite to quartz countertops'")
        
        scope_changes = result.get('scope_changes_detected', [])
        requires_update = result.get('requires_bid_update', False)
        agent_comments = result.get('agent_comments', [])
        
        print(f"Scope Changes: {scope_changes}")
        print(f"Requires Update: {requires_update}")
        print(f"Agent Comments: {len(agent_comments)}")
        
        scope_detected = len(scope_changes) > 0 or requires_update
        
        if scope_detected:
            print("✅ SUCCESS: Material change detected!")
        else:
            print("❌ ISSUE: Material change not detected")
            
        return scope_detected
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def main():
    """Run all scope change tests"""
    
    # Test direct scope change detection
    scope_detected, homeowner_question = await test_scope_change_direct()
    
    # Test material change
    material_detected = await test_material_change()
    
    print("\n" + "=" * 60)
    print("SCOPE CHANGE DETECTION - FINAL RESULTS")
    print("=" * 60)
    
    print(f"Scope Change Detection: {'WORKING' if scope_detected else 'NOT WORKING'}")
    print(f"Homeowner-Only Questions: {'WORKING' if homeowner_question else 'NOT WORKING'}")
    print(f"Material Change Detection: {'WORKING' if material_detected else 'NOT WORKING'}")
    
    all_working = scope_detected and homeowner_question and material_detected
    
    print()
    if all_working:
        print("🎉 SUCCESS: Full scope change detection is working!")
        print("✅ AI can detect project scope changes")
        print("✅ System generates homeowner-only questions")
        print("✅ Ready to notify other contractors about changes")
    elif scope_detected:
        print("⚠️ PARTIAL: Scope change detection working but needs refinement")
        print("Basic detection works, homeowner questions may need adjustment")
    else:
        print("❌ ISSUE: Scope change detection not working")
        print("The feature exists in code but may need GPT prompt adjustment")
    
    return all_working

if __name__ == "__main__":
    asyncio.run(main())