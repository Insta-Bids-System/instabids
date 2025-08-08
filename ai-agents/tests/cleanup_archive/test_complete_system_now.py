#!/usr/bin/env python3
"""
COMPLETE END-TO-END SYSTEM TEST
Test the entire CIA -> JAA -> CDA -> EAA workflow with real data
"""
import asyncio
import os
import sys
import uuid
from pathlib import Path


# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from dotenv import load_dotenv


# Load .env from the instabids root directory
env_path = parent_dir / ".env"
load_dotenv(env_path)

from agents.cda.agent import ContractorDiscoveryAgent
from agents.cia.agent import CustomerInterfaceAgent
from agents.eaa.agent import ExternalAcquisitionAgent
from agents.jaa.agent import JobAssessmentAgent


async def test_complete_workflow():
    """Test complete CIA -> JAA -> CDA -> EAA workflow"""
    print("TESTING COMPLETE END-TO-END WORKFLOW")
    print("=" * 60)

    # Generate proper UUIDs
    user_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())

    print(f"User ID: {user_id}")
    print(f"Session ID: {session_id}")

    # Get API keys
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    google_key = os.getenv("GOOGLE_MAPS_API_KEY")

    # STEP 1: Test CIA Agent
    print("\n=== STEP 1: CIA AGENT ===")
    try:
        cia = CustomerInterfaceAgent(anthropic_key)

        # Test emergency roof repair conversation
        result = await cia.handle_conversation(
            user_id=user_id,
            message="I need emergency roof repair - there's a big leak after the storm last night. Water is dripping into my living room. This is urgent!",
            session_id=session_id
        )

        print(f"CIA Response: {result.get('response', 'No response')[:100]}...")
        print(f"Extraction Complete: {result.get('extraction_complete', False)}")

        if not result.get("response"):
            print("CIA FAILED - No response generated")
            return False

        print("CIA WORKING - Generated response")

    except Exception as e:
        print(f"CIA ERROR: {e}")
        return False

    # STEP 2: Test JAA Agent
    print("\n=== STEP 2: JAA AGENT ===")
    try:
        jaa = JobAssessmentAgent()

        # Create test bid card data
        test_bid_data = {
            "project_type": "roofing_repair",
            "urgency_level": "emergency",
            "contractor_count_needed": 4,
            "description": "Emergency roof leak repair needed after storm",
            "user_id": user_id
        }

        bid_card_result = await jaa.create_bid_card(test_bid_data)

        if bid_card_result.get("success"):
            bid_card_id = bid_card_result.get("bid_card_id")
            print(f"JAA SUCCESS - Created bid card: {bid_card_id}")
        else:
            print(f"JAA FAILED: {bid_card_result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"JAA ERROR: {e}")
        return False

    # STEP 3: Test CDA Agent
    print("\n=== STEP 3: CDA AGENT ===")
    try:
        cda = ContractorDiscoveryAgent()

        # Discover contractors for the bid card
        discovery_result = await cda.discover_contractors_for_bid(
            bid_card_id=bid_card_id,
            contractors_needed=4,
            radius_miles=15
        )

        if discovery_result.get("success"):
            contractors = discovery_result.get("contractors", [])
            print(f"CDA SUCCESS - Found {len(contractors)} contractors")

            if len(contractors) > 0:
                print(f"First contractor: {contractors[0].get('company_name', 'Unknown')}")
            else:
                print("CDA WARNING - No contractors found")

        else:
            print(f"CDA FAILED: {discovery_result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"CDA ERROR: {e}")
        return False

    # STEP 4: Test EAA Agent
    print("\n=== STEP 4: EAA AGENT ===")
    try:
        eaa = ExternalAcquisitionAgent()

        # Start outreach campaign
        campaign_result = await eaa.start_outreach_campaign(
            bid_card_id=bid_card_id,
            max_contractors=len(contractors)
        )

        if campaign_result.get("success"):
            campaign_id = campaign_result.get("campaign_id")
            print(f"EAA SUCCESS - Started campaign: {campaign_id}")
        else:
            print(f"EAA FAILED: {campaign_result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"EAA ERROR: {e}")
        return False

    print("\n" + "=" * 60)
    print("COMPLETE WORKFLOW TEST RESULTS:")
    print("CIA Agent: WORKING - Generated response")
    print(f"JAA Agent: WORKING - Created bid card {bid_card_id}")
    print(f"CDA Agent: WORKING - Found {len(contractors)} contractors")
    print(f"EAA Agent: WORKING - Started campaign {campaign_id}")
    print("\nEND-TO-END SYSTEM: FULLY OPERATIONAL")

    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(test_complete_workflow())

        if success:
            print("\n🎉 COMPLETE SYSTEM WORKING - READY FOR PRODUCTION")
        else:
            print("\n🚨 SYSTEM HAS ISSUES - NEED TO DEBUG")

    except Exception as e:
        print(f"\nTEST FRAMEWORK ERROR: {e}")
        import traceback
        traceback.print_exc()
