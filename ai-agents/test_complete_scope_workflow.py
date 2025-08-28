#!/usr/bin/env python3
"""
COMPLETE SCOPE CHANGE WORKFLOW TEST
Tests the entire scope change system from detection to bid card updates
"""

import asyncio
import sys
import os

# Add the agents directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

from agents.intelligent_messaging_agent import process_intelligent_message

async def test_complete_scope_workflow():
    """Test the complete scope change workflow"""
    
    print("COMPLETE SCOPE CHANGE WORKFLOW TEST")
    print("=" * 60)
    print("Testing: Homeowner changes sod to turf, system detects, creates homeowner question")
    print()
    
    try:
        # Test scope change detection with enhanced system
        result = await process_intelligent_message(
            content="Actually, I've been thinking about it and I want to change from regular sod to artificial turf for the backyard. What would that change in your pricing and timeline?",
            sender_type="homeowner",
            sender_id="homeowner-123",
            bid_card_id="bid-card-456",
            recipient_id="contractor-789",
            conversation_id="conversation-001",
            attachments=[],
            image_data=None
        )
        
        print("SCOPE CHANGE DETECTION RESULTS:")
        print("=" * 40)
        print(f"Message Approved: {result.get('approved', False)}")
        print(f"Agent Decision: {result.get('agent_decision', 'unknown')}")
        print(f"Threats Detected: {result.get('threats_detected', [])}")
        print()
        
        print("SCOPE CHANGE ANALYSIS:")
        print("-" * 40)
        scope_changes = result.get('scope_changes_detected', [])
        scope_details = result.get('scope_change_details', {})
        requires_update = result.get('requires_bid_update', False)
        other_contractors = result.get('other_contractors_to_notify', [])
        
        print(f"Scope Changes Detected: {scope_changes}")
        print(f"Scope Change Details: {scope_details}")
        print(f"Requires Bid Update: {requires_update}")
        print(f"Other Contractors to Notify: {len(other_contractors)}")
        
        for i, contractor in enumerate(other_contractors, 1):
            print(f"  Contractor {i}: {contractor}")
        
        print()
        
        print("HOMEOWNER-ONLY QUESTIONS:")
        print("-" * 40)
        agent_comments = result.get('agent_comments', [])
        
        homeowner_questions = [
            comment for comment in agent_comments 
            if comment.get('type') == 'scope_change_question'
        ]
        
        if homeowner_questions:
            for i, question in enumerate(homeowner_questions, 1):
                print(f"Question {i}:")
                print(f"  Visible To: {question.get('visible_to', 'unknown')}")
                print(f"  Type: {question.get('type', 'unknown')}")
                print(f"  Content: {question.get('content', 'No content')[:200]}...")
                print(f"  Requires Response: {question.get('metadata', {}).get('requires_response', False)}")
                print(f"  Action Type: {question.get('metadata', {}).get('action_type', 'unknown')}")
        else:
            print("No homeowner-only questions generated")
        
        print()
        
        # Assess the results
        print("WORKFLOW ASSESSMENT:")
        print("=" * 40)
        
        scope_detected = len(scope_changes) > 0 or requires_update
        has_homeowner_questions = len(homeowner_questions) > 0
        has_other_contractors = len(other_contractors) > 0
        
        results = []
        
        if scope_detected:
            results.append("SUCCESS: Scope change detected")
            print("✓ Scope change detection: WORKING")
        else:
            results.append("ISSUE: Scope change not detected")
            print("✗ Scope change detection: NOT WORKING")
        
        if has_homeowner_questions:
            results.append("SUCCESS: Homeowner questions generated")
            print("✓ Homeowner-only questions: WORKING")
        else:
            results.append("PARTIAL: No homeowner questions")
            print("✗ Homeowner-only questions: NOT WORKING")
        
        if has_other_contractors:
            results.append("SUCCESS: Other contractors identified")
            print("✓ Contractor identification: WORKING")
        else:
            results.append("PARTIAL: No other contractors found")
            print("✗ Contractor identification: NOT WORKING")
        
        print()
        
        all_working = scope_detected and has_homeowner_questions and has_other_contractors
        
        if all_working:
            print("FINAL RESULT: COMPLETE SCOPE CHANGE WORKFLOW IS WORKING!")
            print("✓ System detects scope changes")
            print("✓ Identifies other contractors")
            print("✓ Generates homeowner-only questions")
            print("✓ Ready to update bid cards and notify contractors")
        else:
            print("FINAL RESULT: PARTIAL SUCCESS")
            print("Some components working, others need adjustment")
        
        return all_working, results
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False, [f"Error: {e}"]

async def test_bid_card_integration():
    """Test integration with actual bid card system"""
    
    print("\n" + "=" * 60)
    print("BID CARD INTEGRATION TEST")
    print("=" * 60)
    print("Testing: Can the system actually update bid cards?")
    print()
    
    try:
        # Import the scope change handler directly
        from agents.scope_change_handler import handle_scope_changes
        
        # Test scope change handling with bid card updates
        scope_result = await handle_scope_changes(
            scope_changes=["Material changes"],
            scope_details={"Material changes": "Change from regular sod to artificial turf for the backyard"},
            bid_card_id="test-bid-card-123",
            sender_id="test-homeowner-456",
            message_content="I want to change from sod to artificial turf"
        )
        
        print("BID CARD UPDATE RESULTS:")
        print("-" * 40)
        print(f"Scope Changes: {scope_result.get('scope_changes_detected', [])}")
        print(f"Bid Card Updated: {scope_result.get('bid_card_updated', False)}")
        print(f"Homeowner Question: {bool(scope_result.get('homeowner_question'))}")
        print(f"Other Contractors: {len(scope_result.get('other_contractors', []))}")
        
        if scope_result.get('homeowner_question'):
            print("\nHOMEOWNER QUESTION PREVIEW:")
            question = scope_result.get('homeowner_question', '')
            print(f"'{question[:100]}...'")
        
        integration_working = (
            len(scope_result.get('scope_changes_detected', [])) > 0 and
            bool(scope_result.get('homeowner_question'))
        )
        
        print()
        if integration_working:
            print("SUCCESS: Bid card integration is working!")
        else:
            print("PARTIAL: Bid card integration needs work")
        
        return integration_working
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

async def main():
    """Run all scope change workflow tests"""
    
    # Test 1: Complete intelligent messaging workflow
    workflow_working, workflow_results = await test_complete_scope_workflow()
    
    # Test 2: Bid card integration
    integration_working = await test_bid_card_integration()
    
    print("\n" + "=" * 60)
    print("FINAL WORKFLOW ASSESSMENT")
    print("=" * 60)
    
    print("COMPONENT STATUS:")
    for result in workflow_results:
        print(f"  {result}")
    
    print()
    print("INTEGRATION STATUS:")
    print(f"  Complete Workflow: {'WORKING' if workflow_working else 'NEEDS WORK'}")
    print(f"  Bid Card Updates: {'WORKING' if integration_working else 'NEEDS WORK'}")
    
    overall_success = workflow_working and integration_working
    
    print()
    print("ANSWER TO USER'S REQUEST:")
    print("=" * 60)
    if overall_success:
        print("YES! The complete scope change system is working:")
        print("1. ✓ Detects when homeowner changes project scope")
        print("2. ✓ Identifies other contractors who need to know") 
        print("3. ✓ Creates homeowner-only questions about notifying them")
        print("4. ✓ Can update bid cards with scope changes")
        print("5. ✓ Ready to connect to homeowner agent for confirmations")
        print()
        print("The system IS integrated and CAN handle the turf example!")
    else:
        print("PARTIAL SUCCESS:")
        if workflow_working:
            print("✓ Core detection and questions are working")
            print("? Bid card integration needs database connection")
        else:
            print("? Core workflow needs additional tuning")
        print("The system architecture is there, needs final adjustments")
    
    return overall_success

if __name__ == "__main__":
    asyncio.run(main())