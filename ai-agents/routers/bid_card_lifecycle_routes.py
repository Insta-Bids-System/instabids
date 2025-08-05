#!/usr/bin/env python3
"""
Bid Card Lifecycle API Routes
Complete bid card tracking system based on 41-table ecosystem analysis
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from database_simple import db


router = APIRouter(prefix="/api/bid-cards", tags=["bid-card-lifecycle"])

class BidCardLifecycleResponse(BaseModel):
    """Complete bid card lifecycle data"""
    bid_card: dict[str, Any]
    discovery: dict[str, Any]
    campaigns: list[dict[str, Any]]
    outreach: dict[str, Any]
    engagement: dict[str, Any]
    bids: list[dict[str, Any]]
    timeline: list[dict[str, Any]]
    metrics: dict[str, Any]

class ContractorDiscoveryData(BaseModel):
    """Contractor discovery and caching data"""
    discovery_runs: list[dict[str, Any]]
    discovery_cache: dict[str, Any]
    potential_contractors: list[dict[str, Any]]
    contractor_leads: list[dict[str, Any]]

class CampaignProgressData(BaseModel):
    """Campaign orchestration and progress data"""
    campaigns: list[dict[str, Any]]
    check_ins: list[dict[str, Any]]
    campaign_contractors: list[dict[str, Any]]
    manual_tasks: list[dict[str, Any]]

class OutreachAnalysisData(BaseModel):
    """Multi-channel outreach analysis"""
    outreach_attempts: list[dict[str, Any]]
    channel_breakdown: dict[str, int]
    success_rates: dict[str, float]
    response_tracking: list[dict[str, Any]]

class EngagementMetrics(BaseModel):
    """Engagement and interaction metrics"""
    views: list[dict[str, Any]]
    engagement_events: list[dict[str, Any]]
    email_tracking: list[dict[str, Any]]
    contractor_responses: list[dict[str, Any]]

async def get_database():
    """Dependency to get database connection"""
    return db

@router.get("/{bid_card_id}/lifecycle", response_model=BidCardLifecycleResponse)
async def get_bid_card_lifecycle(
    bid_card_id: str,
    database = Depends(get_database)
):
    """
    Get complete lifecycle data for a bid card
    Includes all 8 stages: Creation → Discovery → Campaign → Outreach → Engagement → Bids → Follow-up → Completion
    """
    try:
        # Stage 1: Get core bid card data
        bid_card_result = database.client.table("bid_cards").select("*").eq("id", bid_card_id).execute()
        if not bid_card_result.data:
            raise HTTPException(status_code=404, detail="Bid card not found")

        bid_card = bid_card_result.data[0]

        # Stage 2: Get discovery data
        try:
            discovery_data = await get_discovery_data(bid_card_id, database) or {}
        except Exception as e:
            print(f"Discovery data error: {e}")
            discovery_data = {}

        # Stage 3: Get campaign data
        try:
            campaign_data = await get_campaign_data(bid_card_id, database) or []
        except Exception as e:
            print(f"Campaign data error: {e}")
            campaign_data = []

        # Stage 4: Get outreach data
        try:
            outreach_data = await get_outreach_data(bid_card_id, database) or {}
        except Exception as e:
            print(f"Outreach data error: {e}")
            outreach_data = {}

        # Stage 5: Get engagement data
        try:
            engagement_data = await get_engagement_data(bid_card_id, database) or {}
        except Exception as e:
            print(f"Engagement data error: {e}")
            engagement_data = {}

        # Stage 6: Get submitted bids
        try:
            bids_data = await get_bids_data(bid_card) or []
        except Exception as e:
            print(f"Bids data error: {e}")
            bids_data = []

        # Stage 7: Get timeline
        try:
            timeline_data = await build_timeline(bid_card_id, database) or []
        except Exception as e:
            print(f"Timeline data error: {e}")
            timeline_data = []

        # Stage 8: Calculate metrics
        try:
            metrics_data = await calculate_metrics(bid_card, discovery_data, campaign_data, outreach_data, engagement_data, bids_data) or {}
        except Exception as e:
            print(f"Metrics data error: {e}")
            metrics_data = {}

        return BidCardLifecycleResponse(
            bid_card=bid_card,
            discovery=discovery_data,
            campaigns=campaign_data,
            outreach=outreach_data,
            engagement=engagement_data,
            bids=bids_data,
            timeline=timeline_data,
            metrics=metrics_data
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving lifecycle data: {e!s}")

@router.get("/{bid_card_id}/discovery", response_model=ContractorDiscoveryData)
async def get_bid_card_discovery(
    bid_card_id: str,
    database = Depends(get_database)
):
    """Get contractor discovery results and caching data"""
    discovery_data = await get_discovery_data(bid_card_id, database)

    return ContractorDiscoveryData(
        discovery_runs=discovery_data.get("discovery_runs", []),
        discovery_cache=discovery_data.get("discovery_cache", {}),
        potential_contractors=discovery_data.get("potential_contractors", []),
        contractor_leads=discovery_data.get("contractor_leads", [])
    )

@router.get("/{bid_card_id}/campaigns", response_model=CampaignProgressData)
async def get_bid_card_campaigns(
    bid_card_id: str,
    database = Depends(get_database)
):
    """Get campaign orchestration and progress data"""
    campaign_data = await get_campaign_data(bid_card_id, db)

    return CampaignProgressData(
        campaigns=campaign_data.get("campaigns", []),
        check_ins=campaign_data.get("check_ins", []),
        campaign_contractors=campaign_data.get("campaign_contractors", []),
        manual_tasks=campaign_data.get("manual_tasks", [])
    )

@router.get("/{bid_card_id}/outreach", response_model=OutreachAnalysisData)
async def get_bid_card_outreach(
    bid_card_id: str,
    database = Depends(get_database)
):
    """Get multi-channel outreach analysis"""
    outreach_data = await get_outreach_data(bid_card_id, db)

    return OutreachAnalysisData(
        outreach_attempts=outreach_data.get("outreach_attempts", []),
        channel_breakdown=outreach_data.get("channel_breakdown", {}),
        success_rates=outreach_data.get("success_rates", {}),
        response_tracking=outreach_data.get("response_tracking", [])
    )

@router.get("/{bid_card_id}/engagement", response_model=EngagementMetrics)
async def get_bid_card_engagement(
    bid_card_id: str,
    database = Depends(get_database)
):
    """Get engagement and interaction metrics"""
    engagement_data = await get_engagement_data(bid_card_id, db)

    return EngagementMetrics(
        views=engagement_data.get("views", []),
        engagement_events=engagement_data.get("engagement_events", []),
        email_tracking=engagement_data.get("email_tracking", []),
        contractor_responses=engagement_data.get("contractor_responses", [])
    )

@router.get("/{bid_card_id}/timeline")
async def get_bid_card_timeline(
    bid_card_id: str,
    database = Depends(get_database)
):
    """Get complete chronological timeline"""
    timeline = await build_timeline(bid_card_id, db)
    return {"timeline": timeline}

# Helper functions for data retrieval

async def get_discovery_data(bid_card_id: str, database) -> dict[str, Any]:
    """Get contractor discovery data from multiple tables"""

    # Get discovery runs
    discovery_runs = database.client.table("discovery_runs").select("*").eq("bid_card_id", bid_card_id).execute()

    # Get discovery cache
    discovery_cache_result = database.client.table("contractor_discovery_cache").select("*").eq("bid_card_id", bid_card_id).execute()
    discovery_cache = discovery_cache_result.data[0] if discovery_cache_result.data else {}

    # Get bid card project type for contractor filtering
    bid_card = database.client.table("bid_cards").select("project_type").eq("id", bid_card_id).execute()
    project_type = bid_card.data[0]["project_type"] if bid_card.data else None

    # Get potential contractors by project type
    potential_contractors = []
    if project_type:
        potential_contractors_result = database.client.table("potential_contractors").select("*").eq("project_type", project_type).limit(20).execute()
        potential_contractors = potential_contractors_result.data or []

    # Get contractor leads from discovery runs
    contractor_leads = []
    if discovery_runs.data:
        for run in discovery_runs.data:
            leads_result = database.client.table("contractor_leads").select("*").eq("discovery_run_id", run["id"]).execute()
            contractor_leads.extend(leads_result.data or [])
    
    # ALSO get contractor leads from outreach attempts (for bid cards without discovery runs)
    if not contractor_leads:  # Only if no leads found from discovery runs
        outreach_attempts = database.client.table("contractor_outreach_attempts").select("contractor_lead_id").eq("bid_card_id", bid_card_id).execute()
        if outreach_attempts.data:
            contractor_lead_ids = list(set([attempt["contractor_lead_id"] for attempt in outreach_attempts.data if attempt["contractor_lead_id"]]))
            if contractor_lead_ids:
                # Get contractor leads by IDs
                for lead_id in contractor_lead_ids:
                    lead_result = database.client.table("contractor_leads").select("*").eq("id", lead_id).execute()
                    if lead_result.data:
                        contractor_leads.extend(lead_result.data)

    return {
        "discovery_runs": discovery_runs.data or [],
        "discovery_cache": discovery_cache,
        "potential_contractors": potential_contractors,
        "contractor_leads": contractor_leads
    }

async def get_campaign_data(bid_card_id: str, database) -> list[dict[str, Any]]:
    """Get campaign orchestration data"""

    # Get outreach campaigns
    campaigns_result = database.client.table("outreach_campaigns").select("*").eq("bid_card_id", bid_card_id).execute()
    campaigns = campaigns_result.data or []

    # For each campaign, get check-ins and contractors
    for campaign in campaigns:
        campaign_id = campaign["id"]

        # Get campaign check-ins
        check_ins_result = database.client.table("campaign_check_ins").select("*").eq("campaign_id", campaign_id).execute()
        campaign["check_ins"] = check_ins_result.data or []

        # Get campaign contractors
        contractors_result = database.client.table("campaign_contractors").select("*").eq("campaign_id", campaign_id).execute()
        campaign["campaign_contractors"] = contractors_result.data or []

        # Get manual follow-up tasks
        tasks_result = database.client.table("manual_followup_tasks").select("*").eq("campaign_id", campaign_id).execute()
        campaign["manual_tasks"] = tasks_result.data or []

    return campaigns

async def get_outreach_data(bid_card_id: str, database) -> dict[str, Any]:
    """Get multi-channel outreach data and analysis"""

    # Get all outreach attempts
    outreach_result = database.client.table("contractor_outreach_attempts").select("*").eq("bid_card_id", bid_card_id).execute()
    outreach_attempts = outreach_result.data or []

    # Calculate channel breakdown
    channel_breakdown = {}
    success_rates = {}

    for attempt in outreach_attempts:
        channel = attempt.get("channel", "unknown")
        status = attempt.get("status", "unknown")

        # Count by channel
        channel_breakdown[channel] = channel_breakdown.get(channel, 0) + 1

        # Calculate success rates
        if channel not in success_rates:
            success_rates[channel] = {"total": 0, "successful": 0}

        success_rates[channel]["total"] += 1
        if status in ["delivered", "responded", "successful"]:
            success_rates[channel]["successful"] += 1

    # Calculate success percentages
    for channel in success_rates:
        total = success_rates[channel]["total"]
        successful = success_rates[channel]["successful"]
        success_rates[channel]["percentage"] = (successful / total * 100) if total > 0 else 0

    # Get response tracking
    response_tracking_result = database.client.table("contractor_responses").select("*").eq("bid_card_id", bid_card_id).execute()
    response_tracking = response_tracking_result.data or []

    return {
        "outreach_attempts": outreach_attempts,
        "channel_breakdown": channel_breakdown,
        "success_rates": success_rates,
        "response_tracking": response_tracking
    }

async def get_engagement_data(bid_card_id: str, database) -> dict[str, Any]:
    """Get engagement and interaction data"""

    # Get bid card views
    views_result = database.client.table("bid_card_views").select("*").eq("bid_card_id", bid_card_id).execute()
    views = views_result.data or []

    # Get engagement events
    engagement_result = database.client.table("bid_card_engagement_events").select("*").eq("bid_card_id", bid_card_id).execute()
    engagement_events = engagement_result.data or []

    # Get email tracking events
    email_tracking_result = database.client.table("email_tracking_events").select("*").execute()
    # Filter by related contractors (would need more complex join in production)
    email_tracking = email_tracking_result.data or []

    # Get contractor responses
    responses_result = database.client.table("contractor_responses").select("*").eq("bid_card_id", bid_card_id).execute()
    contractor_responses = responses_result.data or []

    return {
        "views": views,
        "engagement_events": engagement_events,
        "email_tracking": email_tracking,
        "contractor_responses": contractor_responses
    }

async def get_bids_data(bid_card: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract submitted bids from bid_document JSONB field"""
    
    try:
        bid_document = bid_card.get("bid_document", {})
        submitted_bids = bid_document.get("submitted_bids", [])

        # Add calculated fields
        for bid in submitted_bids:
            try:
                if "submitted_at" in bid:
                    submitted_at = bid["submitted_at"]
                    if isinstance(submitted_at, str):
                        submitted_at = submitted_at.replace("Z", "+00:00")
                        submission_date = datetime.fromisoformat(submitted_at)
                        bid["days_since_submission"] = (datetime.now() - submission_date).days
                    else:
                        bid["days_since_submission"] = 0
                else:
                    bid["days_since_submission"] = 0
                    
                bid["is_recent"] = bid["days_since_submission"] <= 1
                bid["bid_rank"] = None  # Will be calculated after sorting
            except Exception:
                # Skip invalid date fields
                bid["days_since_submission"] = 0
                bid["is_recent"] = False
                bid["bid_rank"] = None

        # Sort by bid amount and add rankings
        sorted_bids = sorted(submitted_bids, key=lambda x: x.get("bid_amount", 0))
        for i, bid in enumerate(sorted_bids):
            bid["bid_rank"] = i + 1
            bid["is_lowest"] = i == 0
            bid["is_highest"] = i == len(sorted_bids) - 1

        return sorted_bids
    except Exception:
        # Return empty list if any error occurs
        return []

async def build_timeline(bid_card_id: str, database) -> list[dict[str, Any]]:
    """Build complete chronological timeline from all related tables"""

    timeline_events = []

    # Get bid card creation
    bid_card = database.client.table("bid_cards").select("*").eq("id", bid_card_id).execute()
    if bid_card.data:
        timeline_events.append({
            "timestamp": bid_card.data[0]["created_at"],
            "event_type": "bid_card_created",
            "description": f"Bid card {bid_card.data[0]['bid_card_number']} created",
            "details": {
                "project_type": bid_card.data[0]["project_type"],
                "urgency": bid_card.data[0]["urgency_level"],
                "contractors_needed": bid_card.data[0]["contractor_count_needed"]
            }
        })

    # Get discovery runs
    discovery_runs = database.client.table("discovery_runs").select("*").eq("bid_card_id", bid_card_id).execute()
    for run in discovery_runs.data or []:
        timeline_events.append({
            "timestamp": run["created_at"],
            "event_type": "contractor_discovery",
            "description": "Contractor discovery run completed",
            "details": {
                "contractors_found": run.get("total_contractors_found", 0),
                "query_used": run.get("search_query", "")
            }
        })

    # Get campaign events
    campaigns = database.client.table("outreach_campaigns").select("*").eq("bid_card_id", bid_card_id).execute()
    for campaign in campaigns.data or []:
        timeline_events.append({
            "timestamp": campaign["created_at"],
            "event_type": "campaign_created",
            "description": f"Outreach campaign '{campaign['name']}' created",
            "details": {
                "max_contractors": campaign.get("max_contractors", 0),
                "contractors_targeted": campaign.get("contractors_targeted", 0)
            }
        })

        if campaign.get("completed_at"):
            timeline_events.append({
                "timestamp": campaign["completed_at"],
                "event_type": "campaign_completed",
                "description": "Campaign completed",
                "details": {
                    "responses_received": campaign.get("responses_received", 0),
                    "hot_leads_generated": campaign.get("hot_leads_generated", 0)
                }
            })

    # Get outreach attempts
    outreach = database.client.table("contractor_outreach_attempts").select("*").eq("bid_card_id", bid_card_id).execute()
    for attempt in outreach.data or []:
        timeline_events.append({
            "timestamp": attempt["sent_at"],
            "event_type": "outreach_sent",
            "description": f"Outreach sent via {attempt['channel']}",
            "details": {
                "channel": attempt["channel"],
                "status": attempt.get("status", "unknown"),
                "contractor_id": attempt.get("contractor_lead_id")
            }
        })

    # Get bid submissions from bid_document
    if bid_card.data:
        bid_document = bid_card.data[0].get("bid_document", {})
        submitted_bids = bid_document.get("submitted_bids", [])

        for bid in submitted_bids:
            timeline_events.append({
                "timestamp": bid["submitted_at"],
                "event_type": "bid_submitted",
                "description": f"Bid submitted by {bid['contractor_name']}",
                "details": {
                    "bid_amount": bid["bid_amount"],
                    "contractor_name": bid["contractor_name"],
                    "submission_method": bid.get("submission_method", "unknown"),
                    "timeline_days": bid.get("timeline_days", 0)
                }
            })

    # Sort timeline by timestamp
    timeline_events.sort(key=lambda x: x["timestamp"])

    return timeline_events

async def calculate_metrics(bid_card, discovery_data, campaign_data, outreach_data, engagement_data, bids_data) -> dict[str, Any]:
    """Calculate comprehensive metrics"""

    # Basic metrics
    bids_received = len(bids_data)
    bids_needed = bid_card.get("contractor_count_needed", 0)
    completion_percentage = (bids_received / bids_needed * 100) if bids_needed > 0 else 0

    # Discovery metrics
    contractors_discovered = len(discovery_data.get("potential_contractors", []))

    # Outreach metrics
    outreach_attempts = len(outreach_data.get("outreach_attempts", []))
    channel_breakdown = outreach_data.get("channel_breakdown", {})

    # Engagement metrics
    total_views = len(engagement_data.get("views", []))
    total_engagements = len(engagement_data.get("engagement_events", []))

    # Bid metrics
    if bids_data:
        bid_amounts = [bid["bid_amount"] for bid in bids_data if "bid_amount" in bid]
        avg_bid = sum(bid_amounts) / len(bid_amounts) if bid_amounts else 0
        min_bid = min(bid_amounts) if bid_amounts else 0
        max_bid = max(bid_amounts) if bid_amounts else 0
        bid_spread = max_bid - min_bid if bid_amounts else 0
    else:
        avg_bid = min_bid = max_bid = bid_spread = 0

    # Timeline metrics
    created_at = datetime.fromisoformat(bid_card["created_at"].replace("Z", "+00:00"))
    age_hours = (datetime.now() - created_at).total_seconds() / 3600

    return {
        "completion": {
            "bids_received": bids_received,
            "bids_needed": bids_needed,
            "completion_percentage": completion_percentage,
            "is_complete": bid_card.get("status") == "bids_complete"
        },
        "discovery": {
            "contractors_discovered": contractors_discovered,
            "discovery_runs": len(discovery_data.get("discovery_runs", []))
        },
        "outreach": {
            "total_attempts": outreach_attempts,
            "channels_used": len(channel_breakdown),
            "channel_breakdown": channel_breakdown,
            "success_rates": outreach_data.get("success_rates", {})
        },
        "engagement": {
            "total_views": total_views,
            "total_engagements": total_engagements,
            "engagement_rate": (total_engagements / total_views * 100) if total_views > 0 else 0
        },
        "bids": {
            "average_bid": avg_bid,
            "minimum_bid": min_bid,
            "maximum_bid": max_bid,
            "bid_spread": bid_spread,
            "bid_range_percentage": (bid_spread / avg_bid * 100) if avg_bid > 0 else 0
        },
        "timeline": {
            "age_hours": age_hours,
            "age_days": age_hours / 24,
            "is_recent": age_hours <= 24,
            "created_at": bid_card["created_at"]
        }
    }
