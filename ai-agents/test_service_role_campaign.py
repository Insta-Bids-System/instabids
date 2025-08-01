"""
Test campaign creation with service role to bypass RLS
"""
import asyncio
import uuid
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(__file__))

from agents.orchestration.enhanced_campaign_orchestrator import EnhancedCampaignOrchestrator, CampaignRequest

async def test_service_role_campaign():
    """Test creating a campaign with service role key"""
    print("\n=== Testing Campaign Creation with Service Role ===\n")
    
    # Initialize orchestrator (now uses service role internally)
    orchestrator = EnhancedCampaignOrchestrator()
    
    # Create a test campaign request
    request = CampaignRequest(
        bid_card_id=str(uuid.uuid4()),
        project_type="Kitchen Remodel",
        location={"city": "Denver", "state": "CO"},
        timeline_hours=24,  # Standard timeline
        urgency_level="standard",
        bids_needed=4,
        channels=["email", "website_form"]
    )
    
    print(f"Creating campaign for {request.project_type}...")
    print(f"Timeline: {request.timeline_hours} hours")
    print(f"Bids needed: {request.bids_needed}")
    
    # Create the campaign
    result = await orchestrator.create_intelligent_campaign(request)
    
    if result['success']:
        print("\n[SUCCESS] Campaign created with service role!")
        print(f"Campaign ID: {result['campaign_id']}")
        print(f"Total contractors: {result['total_contractors']}")
        print(f"Expected responses: {result['expected_responses']}")
        print(f"Confidence: {result['confidence']}%")
        
        # Show check-in schedule
        if 'check_in_times' in result:
            print("\nCheck-in Schedule:")
            for check_in in result['check_in_times']:
                print(f"  - {check_in['hours']} hours: {check_in['percentage']}% check")
    else:
        print(f"\n[FAILED] {result.get('error', 'Unknown error')}")
        if 'details' in result:
            print(f"Details: {result['details']}")
    
    return result

if __name__ == "__main__":
    # Run the test
    result = asyncio.run(test_service_role_campaign())
    
    print("\n" + "="*60)
    print("Test completed. Check Supabase to verify campaign was created.")
    print("If RLS error persists, we may need to adjust the RLS policy itself.")