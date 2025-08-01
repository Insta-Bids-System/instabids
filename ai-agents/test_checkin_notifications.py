#!/usr/bin/env python3
"""
Test Check-in System and Notifications
Shows how the system monitors campaigns and would notify agents
"""

import asyncio
from datetime import datetime, timedelta
import uuid
from typing import Dict, Any

# Add parent directory
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.orchestration.enhanced_campaign_orchestrator import EnhancedCampaignOrchestrator, CampaignRequest
from agents.orchestration.check_in_manager import CampaignCheckInManager
import database_simple

async def simulate_campaign_with_responses():
    """Create a campaign and simulate contractor responses"""
    
    print("=" * 80)
    print("TESTING CHECK-IN SYSTEM WITH SIMULATED RESPONSES")
    print("=" * 80)
    
    # Initialize components
    orchestrator = EnhancedCampaignOrchestrator()
    check_in_manager = CampaignCheckInManager()
    db = database_simple
    
    # Step 1: Create a campaign that needs 4 bids in 6 hours (URGENT)
    print("\nSTEP 1: Creating Urgent Campaign")
    print("-" * 60)
    
    campaign_request = CampaignRequest(
        bid_card_id=str(uuid.uuid4()),
        project_type='plumbing_repair',
        location={'city': 'Miami', 'state': 'FL'},
        timeline_hours=6,  # URGENT - 6 hours
        urgency_level='urgent',
        bids_needed=4
    )
    
    print(f"Campaign Request:")
    print(f"  Need: {campaign_request.bids_needed} bids")
    print(f"  Timeline: {campaign_request.timeline_hours} hours")
    print(f"  Urgency: URGENT")
    
    # Create campaign
    result = await orchestrator.create_intelligent_campaign(campaign_request)
    campaign_id = result['campaign_id']
    
    print(f"\nCampaign Created: {campaign_id}")
    print(f"Strategy: Contact {result['strategy']['total_contractors']} contractors")
    print(f"Expected Responses: {result['strategy']['expected_responses']:.1f}")
    
    # Step 2: Show scheduled check-ins
    print("\n" + "="*60)
    print("SCHEDULED CHECK-INS")
    print("="*60)
    
    check_ins = db.client.table('campaign_check_ins').select('*').eq('campaign_id', campaign_id).execute()
    
    for check_in in check_ins.data:
        scheduled_time = datetime.fromisoformat(check_in['scheduled_for'].replace('Z', '+00:00'))
        print(f"\nCheck-in #{check_in['check_in_number']}:")
        print(f"  Scheduled: {scheduled_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"  Progress: {check_in['expected_progress']}%")
        print(f"  Status: {check_in['status']}")
    
    # Step 3: Simulate some contractor responses
    print("\n" + "="*60)
    print("SIMULATING CONTRACTOR RESPONSES")
    print("="*60)
    
    # Let's say 2 contractors respond quickly
    print("\nHour 1: Simulating 2 contractor responses...")
    
    # Simulate responses by updating campaign
    response_data = {
        'responses_received': 2,
        'last_response_at': datetime.utcnow().isoformat()
    }
    
    db.client.table('outreach_campaigns').update(response_data).eq('id', campaign_id).execute()
    
    print("  ✓ 2 contractors responded")
    print("  Current: 2/4 bids received (50%)")
    
    # Step 4: Run first check-in
    print("\n" + "="*60)
    print("RUNNING FIRST CHECK-IN (25% of timeline)")
    print("="*60)
    
    # Get the first check-in
    first_check_in = check_ins.data[0] if check_ins.data else None
    if first_check_in:
        # Process check-in
        check_in_result = await check_in_manager.process_check_in(campaign_id, first_check_in['id'])
        
        print(f"\nCheck-in Results:")
        print(f"  Status: {check_in_result['status']}")
        print(f"  Progress: {check_in_result['metrics']['response_rate']:.0%}")
        print(f"  Recommendation: {check_in_result['recommendation']['action']}")
        
        if check_in_result['recommendation']['action'] == 'escalate':
            print(f"  📢 NOTIFICATION: System recommends adding more contractors!")
            print(f"  Reason: {check_in_result['recommendation']['reason']}")
    
    # Step 5: Show what would happen at each check-in
    print("\n" + "="*60)
    print("CHECK-IN NOTIFICATION FLOW")
    print("="*60)
    
    print("\n🔔 How Notifications Would Work:")
    print("\n1. At 25% of timeline (1.5 hours):")
    print("   - System checks: Do we have 25% of needed bids?")
    print("   - If NO → Notification to add Tier 2 contractors")
    print("   - If YES → Continue monitoring")
    
    print("\n2. At 50% of timeline (3 hours):")
    print("   - System checks: Do we have 50% of needed bids?")
    print("   - If NO → Notification to add Tier 3 contractors")
    print("   - If YES → Continue monitoring")
    
    print("\n3. At 75% of timeline (4.5 hours):")
    print("   - System checks: Are we on track?")
    print("   - If NO → URGENT notification, may extend deadline")
    print("   - If YES → Final push")
    
    # Step 6: Show how to integrate with Claude
    print("\n" + "="*60)
    print("HOW TO ADD CLAUDE/LLM INTELLIGENCE")
    print("="*60)
    
    print("\n🧠 Where Claude SHOULD be integrated:")
    
    print("\n1. EMAIL WRITING (Currently templated):")
    print("   Instead of: 'We have a {project_type} project...'")
    print("   Claude writes: Unique, persuasive email for each contractor")
    
    print("\n2. CHECK-IN DECISIONS (Currently rule-based):")
    print("   Instead of: if responses < threshold: escalate")
    print("   Claude decides: Based on contractor quality, timing, project complexity")
    
    print("\n3. BROWSER FORM FILLING (Currently scripted):")
    print("   Instead of: Fixed form mapping")
    print("   Claude adapts: Understands any form layout and fills intelligently")
    
    print("\n4. NOTIFICATION MESSAGES:")
    print("   Claude writes: 'Based on current response rate, I recommend...'")
    
    return True

async def test_real_time_monitoring():
    """Show how real-time monitoring would work"""
    
    print("\n" + "="*80)
    print("REAL-TIME MONITORING SIMULATION")
    print("="*80)
    
    print("\n🔄 Current System Flow:")
    print("1. Campaign starts → Check-ins scheduled")
    print("2. Time passes → Check-in triggers")
    print("3. System evaluates → Makes recommendation")
    print("4. IF escalation needed → Notification sent")
    
    print("\n📱 What notifications would look like:")
    print("\n[1.5 hours into campaign]")
    print("🔔 NOTIFICATION: Campaign Update")
    print("   Campaign: Plumbing Repair - Miami")
    print("   Progress: 1/4 bids received (25%)")
    print("   Recommendation: Add 5 more Tier 2 contractors")
    print("   Action Required: Approve additional outreach")
    
    print("\n[3 hours into campaign]")
    print("🔔 URGENT: Campaign Behind Schedule")
    print("   Campaign: Plumbing Repair - Miami")
    print("   Progress: 2/4 bids received (50%)")
    print("   Timeline: 3 hours remaining")
    print("   Recommendation: Switch to aggressive mode")
    print("   - Add 10 Tier 3 contractors")
    print("   - Consider extending deadline")
    
    print("\n💡 To make this REAL with Claude:")
    print("1. Add Claude API calls at each decision point")
    print("2. Pass campaign context to Claude")
    print("3. Let Claude write notifications")
    print("4. Let Claude decide escalation strategy")

if __name__ == "__main__":
    print("Testing Check-in System and Notifications...")
    
    # Run tests
    asyncio.run(simulate_campaign_with_responses())
    asyncio.run(test_real_time_monitoring())
    
    print("\n" + "="*80)
    print("HOW TO TEST WITH FAKE BIDS")
    print("="*80)
    
    print("\nTo simulate bid submissions:")
    print("1. Update 'responses_received' in outreach_campaigns table")
    print("2. Run check-in processing")
    print("3. See escalation recommendations")
    
    print("\nSQL to fake responses:")
    print("UPDATE outreach_campaigns")
    print("SET responses_received = 2")
    print("WHERE id = 'your-campaign-id';")
    
    print("\nThe system will then trigger notifications!")