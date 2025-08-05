"""Enhanced admin routes with full bid card lifecycle data"""
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException

from database_simple import db


router = APIRouter(prefix="/api/admin", tags=["admin-enhanced"])

@router.get("/bid-cards-enhanced")
async def get_enhanced_bid_cards(limit: int = 50):
    """Get bid cards with full lifecycle data"""
    try:
        # Get base bid cards
        bid_cards_result = db.client.table("bid_cards").select(
            "*, "
            "homeowner_name, homeowner_email, homeowner_phone, "
            "urgency_level, complexity_score, timeline_weeks"
        ).order("created_at", desc=True).limit(limit).execute()

        if not bid_cards_result.data:
            return {"bid_cards": []}

        enhanced_cards = []

        for card in bid_cards_result.data:
            bid_card_id = card["id"]

            # Get campaign data
            campaign_result = db.client.table("outreach_campaigns").select(
                "max_contractors, contractors_targeted, contractors_responded, status"
            ).eq("bid_card_id", bid_card_id).execute()

            campaign_data = campaign_result.data[0] if campaign_result.data else {}

            # Get outreach metrics
            outreach_result = db.client.table("contractor_outreach_attempts").select(
                "channel, status"
            ).eq("bid_card_id", bid_card_id).execute()

            outreach_metrics = {
                "total_attempts": len(outreach_result.data or []),
                "email_sent": sum(1 for o in (outreach_result.data or []) if o.get("channel") == "email"),
                "forms_sent": sum(1 for o in (outreach_result.data or []) if o.get("channel") == "form"),
                "sms_sent": sum(1 for o in (outreach_result.data or []) if o.get("channel") == "sms"),
                "successful_deliveries": sum(1 for o in (outreach_result.data or []) if o.get("status") == "sent")
            }

            # Get view count
            views_result = db.client.table("bid_card_views").select(
                "viewed_at"
            ).eq("bid_card_id", bid_card_id).order("viewed_at", desc=True).execute()

            views_count = len(views_result.data or [])
            last_viewed = views_result.data[0]["viewed_at"] if views_result.data else None

            # Calculate next check-in based on campaign progress
            if campaign_data:
                progress = (campaign_data.get("contractors_responded", 0) /
                           max(campaign_data.get("max_contractors", 1), 1))
                if progress < 0.25:
                    next_checkin = datetime.now() + timedelta(hours=6)
                elif progress < 0.5:
                    next_checkin = datetime.now() + timedelta(hours=12)
                elif progress < 0.75:
                    next_checkin = datetime.now() + timedelta(days=1)
                else:
                    next_checkin = None
            else:
                next_checkin = datetime.now() + timedelta(hours=4)

            # Enhance the bid card data
            enhanced_card = {
                **card,
                "campaign": campaign_data,
                "outreach": outreach_metrics,
                "views_count": views_count,
                "last_viewed": last_viewed,
                "next_checkin": next_checkin.isoformat() if next_checkin else None
            }

            enhanced_cards.append(enhanced_card)

        return {"bid_cards": enhanced_cards}

    except Exception as e:
        print(f"[ADMIN ENHANCED] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bid-card/{bid_card_id}/timeline")
async def get_bid_card_timeline(bid_card_id: str):
    """Get complete timeline of events for a bid card"""
    events = []

    # Get creation event
    card_result = db.client.table("bid_cards").select(
        "created_at, status, homeowner_name"
    ).eq("id", bid_card_id).single().execute()

    if card_result.data:
        events.append({
            "timestamp": card_result.data["created_at"],
            "type": "created",
            "description": f"Bid card created by {card_result.data['homeowner_name']}",
            "status": "completed"
        })

    # Get discovery events
    discovery_result = db.client.table("discovery_runs").select(
        "created_at, contractors_found"
    ).eq("bid_card_id", bid_card_id).execute()

    for discovery in (discovery_result.data or []):
        events.append({
            "timestamp": discovery["created_at"],
            "type": "discovery",
            "description": f"Found {discovery['contractors_found']} contractors",
            "status": "completed"
        })

    # Get outreach events
    outreach_result = db.client.table("contractor_outreach_attempts").select(
        "created_at, channel, status, contractor_lead_id"
    ).eq("bid_card_id", bid_card_id).execute()

    for outreach in (outreach_result.data or []):
        events.append({
            "timestamp": outreach["created_at"],
            "type": "outreach",
            "description": f"{outreach['channel']} sent to contractor",
            "status": outreach["status"]
        })

    # Sort events by timestamp
    events.sort(key=lambda x: x["timestamp"])

    return {"timeline": events}
