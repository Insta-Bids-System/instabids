"""
Enhanced Bid Card API endpoints
Supports multiple UI variants: homeowner editing, contractor bidding, marketplace browsing
"""

import json
import logging
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from supabase import Client

# Import auth and database utilities from existing project structure
from database_simple import db

logger = logging.getLogger(__name__)


def get_supabase_client():
    return db.client

# For now, create a simple auth dependency that returns a test user
# This should be replaced with the actual auth system
def get_current_user():
    return {
        "id": "test-user-id",
        "user_type": "homeowner"
    }

router = APIRouter(tags=["bid-cards"])

# Pydantic models for request/response
class BudgetRange(BaseModel):
    min: float
    max: float

class Timeline(BaseModel):
    start_date: datetime
    end_date: datetime
    flexibility: str = "flexible"

class Location(BaseModel):
    address: Optional[str] = None
    city: str
    state: str
    zip_code: str
    coordinates: Optional[dict[str, float]] = None

class BidCardCreate(BaseModel):
    title: str
    description: str
    budget_range: BudgetRange
    timeline: Timeline
    location: Location
    project_type: str
    categories: list[str]
    requirements: list[str]
    preferred_schedule: Optional[list[str]] = []
    group_bid_eligible: bool = False
    allows_questions: bool = True
    requires_bid_before_message: bool = False
    visibility: str = "public"
    metadata: Optional[dict[str, Any]] = {}

class BidCardUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    budget_range: Optional[BudgetRange] = None
    timeline: Optional[Timeline] = None
    location: Optional[Location] = None
    project_type: Optional[str] = None
    categories: Optional[list[str]] = None
    requirements: Optional[list[str]] = None
    preferred_schedule: Optional[list[str]] = None
    group_bid_eligible: Optional[bool] = None
    allows_questions: Optional[bool] = None
    requires_bid_before_message: Optional[bool] = None
    visibility: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None

class BidSubmission(BaseModel):
    bid_card_id: str
    amount: float
    timeline: Timeline
    proposal: str
    approach: str
    materials_included: bool = False
    warranty_details: Optional[str] = None
    milestones: Optional[list[dict[str, Any]]] = []

class MessageSend(BaseModel):
    bid_card_id: str
    bid_id: Optional[str] = None
    recipient_id: str
    content: str
    attachments: Optional[list[dict[str, Any]]] = []

# Helper functions
def serialize_bid_card(bid_card: dict[str, Any]) -> dict[str, Any]:
    """Convert database bid card to API response format"""
    return {
        "id": bid_card["id"],
        "project_id": bid_card["project_id"],
        "homeowner_id": bid_card["homeowner_id"],
        "title": bid_card.get("title", ""),
        "description": bid_card.get("description", ""),
        "budget_range": {
            "min": float(bid_card.get("budget_min", 0)),
            "max": float(bid_card.get("budget_max", 0))
        },
        "timeline": {
            "start_date": bid_card.get("timeline_start", ""),
            "end_date": bid_card.get("timeline_end", ""),
            "flexibility": bid_card.get("timeline_flexibility", "flexible")
        },
        "location": {
            "address": bid_card.get("location_address"),
            "city": bid_card.get("location_city", ""),
            "state": bid_card.get("location_state", ""),
            "zip_code": bid_card.get("location_zip", ""),
            "coordinates": {
                "lat": float(bid_card["location_lat"]) if bid_card.get("location_lat") else None,
                "lng": float(bid_card["location_lng"]) if bid_card.get("location_lng") else None
            } if bid_card.get("location_lat") else None
        },
        "project_type": bid_card.get("project_type", ""),
        "categories": bid_card.get("categories", []),
        "requirements": bid_card.get("requirements", []),
        "preferred_schedule": bid_card.get("preferred_schedule", []),
        "status": bid_card.get("status", "draft"),
        "visibility": bid_card.get("visibility", "public"),
        "group_bid_eligible": bid_card.get("group_bid_eligible", False),
        "group_bid_id": bid_card.get("group_bid_id"),
        "bid_count": bid_card.get("bid_count", 0),
        "interested_contractors": bid_card.get("interested_contractors", 0),
        "bid_deadline": bid_card.get("bid_deadline"),
        "auto_close_after_bids": bid_card.get("auto_close_after_bids"),
        "allows_questions": bid_card.get("allows_questions", True),
        "requires_bid_before_message": bid_card.get("requires_bid_before_message", False),
        "created_at": bid_card.get("created_at"),
        "updated_at": bid_card.get("updated_at"),
        "published_at": bid_card.get("published_at"),
        "metadata": bid_card.get("metadata", {})
    }

# Endpoints
@router.post("", response_model=dict[str, Any])
async def create_bid_card(
    bid_card: BidCardCreate,
    db: Client = Depends(get_supabase_client)
):
    """Create a new bid card for a homeowner"""
    try:
        # Get the current user
        current_user = get_current_user()

        # Get the project_id for this homeowner
        project_response = db.table("projects").select("id").eq("homeowner_id", current_user["id"]).single().execute()
        if not project_response.data:
            raise HTTPException(status_code=404, detail="No project found for this homeowner")

        bid_card_data = {
            "project_id": project_response.data["id"],
            "homeowner_id": current_user["id"],
            "title": bid_card.title,
            "description": bid_card.description,
            "budget_min": bid_card.budget_range.min,
            "budget_max": bid_card.budget_range.max,
            "timeline_start": bid_card.timeline.start_date.isoformat(),
            "timeline_end": bid_card.timeline.end_date.isoformat(),
            "timeline_flexibility": bid_card.timeline.flexibility,
            "location_address": bid_card.location.address,
            "location_city": bid_card.location.city,
            "location_state": bid_card.location.state,
            "location_zip": bid_card.location.zip_code,
            "location_lat": bid_card.location.coordinates.get("lat") if bid_card.location.coordinates else None,
            "location_lng": bid_card.location.coordinates.get("lng") if bid_card.location.coordinates else None,
            "project_type": bid_card.project_type,
            "categories": bid_card.categories,
            "requirements": bid_card.requirements,
            "preferred_schedule": bid_card.preferred_schedule,
            "group_bid_eligible": bid_card.group_bid_eligible,
            "allows_questions": bid_card.allows_questions,
            "requires_bid_before_message": bid_card.requires_bid_before_message,
            "visibility": bid_card.visibility,
            "metadata": json.dumps(bid_card.metadata),
            "status": "draft"
        }

        response = db.table("bid_cards").insert(bid_card_data).execute()
        return serialize_bid_card(response.data[0])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{bid_card_id}", response_model=dict[str, Any])
async def update_bid_card(
    bid_card_id: str,
    updates: BidCardUpdate,
    # current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_supabase_client)
):
    """Update a bid card (homeowner only)"""
    try:
        # Verify ownership
        existing = db.table("bid_cards").select("*").eq("id", bid_card_id).eq("homeowner_id", current_user["id"]).single().execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Bid card not found or you don't have permission")

        update_data = {}
        if updates.title is not None:
            update_data["title"] = updates.title
        if updates.description is not None:
            update_data["description"] = updates.description
        if updates.budget_range is not None:
            update_data["budget_min"] = updates.budget_range.min
            update_data["budget_max"] = updates.budget_range.max
        if updates.timeline is not None:
            update_data["timeline_start"] = updates.timeline.start_date.isoformat()
            update_data["timeline_end"] = updates.timeline.end_date.isoformat()
            update_data["timeline_flexibility"] = updates.timeline.flexibility
        if updates.location is not None:
            update_data["location_address"] = updates.location.address
            update_data["location_city"] = updates.location.city
            update_data["location_state"] = updates.location.state
            update_data["location_zip"] = updates.location.zip_code
            if updates.location.coordinates:
                update_data["location_lat"] = updates.location.coordinates.get("lat")
                update_data["location_lng"] = updates.location.coordinates.get("lng")
        if updates.project_type is not None:
            update_data["project_type"] = updates.project_type
        if updates.categories is not None:
            update_data["categories"] = updates.categories
        if updates.requirements is not None:
            update_data["requirements"] = updates.requirements
        if updates.preferred_schedule is not None:
            update_data["preferred_schedule"] = updates.preferred_schedule
        if updates.group_bid_eligible is not None:
            update_data["group_bid_eligible"] = updates.group_bid_eligible
        if updates.allows_questions is not None:
            update_data["allows_questions"] = updates.allows_questions
        if updates.requires_bid_before_message is not None:
            update_data["requires_bid_before_message"] = updates.requires_bid_before_message
        if updates.visibility is not None:
            update_data["visibility"] = updates.visibility
        if updates.metadata is not None:
            update_data["metadata"] = json.dumps(updates.metadata)

        # Check if we're publishing
        if "status" in update_data and update_data["status"] == "active" and existing.data["status"] == "draft":
            update_data["published_at"] = datetime.utcnow().isoformat()

        response = db.table("bid_cards").update(update_data).eq("id", bid_card_id).execute()
        return serialize_bid_card(response.data[0])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{bid_card_id}")
async def delete_bid_card(
    bid_card_id: str,
    # current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_supabase_client)
):
    """Delete a bid card (homeowner only)"""
    try:
        # Verify ownership and that it's still in draft
        existing = db.table("bid_cards").select("*").eq("id", bid_card_id).eq("homeowner_id", current_user["id"]).single().execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Bid card not found or you don't have permission")
        if existing.data["status"] != "draft":
            raise HTTPException(status_code=400, detail="Cannot delete published bid cards")

        db.table("bid_cards").delete().eq("id", bid_card_id).execute()
        return {"message": "Bid card deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/homeowner", response_model=list[dict[str, Any]])
async def get_homeowner_bid_cards(
    # current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_supabase_client)
):
    """Get all bid cards for the current homeowner with enhanced view data"""
    try:
        response = db.table("bid_cards").select("*").eq("homeowner_id", current_user["id"]).execute()

        bid_cards = []
        for card in response.data:
            # Get unread message count
            unread_response = db.table("bid_card_messages").select("id").eq("bid_card_id", card["id"]).eq("recipient_id", current_user["id"]).eq("is_read", False).execute()

            # Get pending questions count
            questions_response = db.table("bid_card_messages").select("id").eq("bid_card_id", card["id"]).eq("recipient_id", current_user["id"]).eq("is_read", False).is_("reply_to_id", None).execute()

            enhanced_card = serialize_bid_card(card)
            enhanced_card.update({
                "can_edit": card["status"] in ["draft", "active"],
                "can_delete": card["status"] == "draft",
                "can_publish": card["status"] == "draft",
                "unread_messages_count": len(unread_response.data),
                "pending_questions": len(questions_response.data)
            })
            bid_cards.append(enhanced_card)

        return bid_cards

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search", response_model=dict[str, Any])
async def search_bid_cards(
    status: Optional[list[str]] = Query(None),
    project_types: Optional[list[str]] = Query(None),
    categories: Optional[list[str]] = Query(None),
    city: Optional[str] = None,
    state: Optional[str] = None,
    zip_code: Optional[str] = None,
    radius_miles: Optional[int] = None,
    budget_min: Optional[float] = None,
    budget_max: Optional[float] = None,
    start_after: Optional[datetime] = None,
    start_before: Optional[datetime] = None,
    group_bid_eligible: Optional[bool] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = 1,
    page_size: int = 20,
    # current_user: Optional[Dict[str, Any]] = Depends(get_current_user),
    db: Client = Depends(get_supabase_client)
):
    """Search bid cards for contractors with filtering and sorting"""
    try:
        # Debug logging to see what parameters we're getting
        logger.info(f"Search params received: zip_code='{zip_code}' (type: {type(zip_code)}), radius_miles='{radius_miles}' (type: {type(radius_miles)})")
        
        # If radius search parameters are present, redirect to contractor-jobs API
        if zip_code and radius_miles:
            logger.info(f"Radius search detected: zip_code={zip_code}, radius_miles={radius_miles}")
            import httpx
            
            # Convert bid-cards parameters to contractor-jobs parameters
            contractor_params = {
                'zip_code': zip_code,
                'radius_miles': radius_miles,
                'page': page,
                'page_size': page_size
            }
            
            # Add project type filters if present
            if project_types:
                contractor_params['project_types'] = project_types
            
            logger.info(f"Making request to contractor-jobs API with params: {contractor_params}")
            
            # Make internal request to contractor-jobs API
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"http://localhost:8008/api/contractor-jobs/search",
                        params=contractor_params
                    )
                    
                logger.info(f"Contractor-jobs API responded with status: {response.status_code}")
                
                # Transform response to match bid-cards format
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Got {len(data.get('job_opportunities', []))} job opportunities from contractor-jobs API")
                    # Transform job_opportunities to bid_cards format
                    bid_cards = []
                    for job in data.get('job_opportunities', []):
                        bid_card = {
                            'id': job['id'],
                            'bid_card_number': job.get('bid_card_number'),
                            'title': job['title'],
                            'description': job['description'],
                            'project_type': job['project_type'],
                            'status': job['status'],
                            'budget_min': job['budget_range']['min'],
                            'budget_max': job['budget_range']['max'],
                            'location_city': job['location']['city'],
                            'location_state': job['location']['state'],
                            'location_zip': job['location']['zip_code'],
                            'timeline_start': job['timeline']['start_date'],
                            'timeline_end': job['timeline']['end_date'],
                            'contractor_count_needed': job.get('contractor_count_needed', 1),
                            'bid_count': job.get('bid_count', 0),
                            'categories': job.get('categories', []),
                            'group_bid_eligible': job.get('group_bid_eligible', False),
                            'created_at': job.get('created_at'),
                            'homeowner_verified': True,
                            'response_time_hours': 24,
                            'success_rate': 0.95,
                            'is_featured': False,
                            'is_urgent': False,
                            'distance_miles': job.get('distance_miles')
                        }
                        bid_cards.append(bid_card)
                
                return {
                    'bid_cards': bid_cards,
                    'total': data['total'],
                    'page': data['page'],
                    'page_size': data['page_size'],
                    'has_more': data['has_more']
                }
                else:
                    # If contractor-jobs API fails, fall back to regular search
                    logger.error(f"Contractor-jobs API failed with status {response.status_code}")
            except Exception as e:
                logger.error(f"Error calling contractor-jobs API: {e}")
                # Fall back to regular search
        
        # Regular search if not radius search
        query = db.table("bid_cards").select("*")

        # Apply filters
        if status:
            query = query.in_("status", status)
        else:
            query = query.in_("status", ["active", "collecting_bids"])

        if project_types:
            query = query.in_("project_type", project_types)

        if categories:
            # This would need a more complex query for array overlap
            pass

        if city:
            query = query.eq("location_city", city)
        if state:
            query = query.eq("location_state", state)
        
        # For now, just do exact zip match
        # Radius search is handled by the redirect in main.py
        if zip_code:
            query = query.eq("location_zip", zip_code)

        if budget_min:
            query = query.gte("budget_max", budget_min)
        if budget_max:
            query = query.lte("budget_min", budget_max)

        if start_after:
            query = query.gte("timeline_start", start_after.isoformat())
        if start_before:
            query = query.lte("timeline_start", start_before.isoformat())

        if group_bid_eligible is not None:
            query = query.eq("group_bid_eligible", group_bid_eligible)

        # Apply sorting
        query = query.order(sort_by, desc=(sort_order == "desc"))

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.range(offset, offset + page_size - 1)

        response = query.execute()

        # Enhance bid cards for marketplace view
        bid_cards = []
        for card in response.data:
            marketplace_card = serialize_bid_card(card)
            # Remove sensitive info
            marketplace_card.pop("homeowner_id", None)

            # Add marketplace-specific fields
            marketplace_card.update({
                "homeowner_verified": True,  # Would check verification status
                "response_time_hours": 24,  # Would calculate from message history
                "success_rate": 0.95,  # Would calculate from completed projects
                "is_featured": False,  # Would check featured status
                "is_urgent": (datetime.fromisoformat(card["timeline_start"]) - datetime.utcnow()).days < 7
            })

            # Distance calculation is handled by the redirect in main.py

            bid_cards.append(marketplace_card)

        return {
            "bid_cards": bid_cards,
            "total": len(response.data),
            "page": page,
            "page_size": page_size,
            "has_more": len(response.data) == page_size
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{bid_card_id}/contractor-view", response_model=dict[str, Any])
async def get_bid_card_contractor_view(
    bid_card_id: str,
    # current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_supabase_client)
):
    """Get bid card details for contractor view"""
    try:
        response = db.table("bid_cards").select("*").eq("id", bid_card_id).single().execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Bid card not found")

        contractor_view = serialize_bid_card(response.data)

        # Check if contractor has already bid
        bid_response = db.table("contractor_bids").select("*").eq("bid_card_id", bid_card_id).eq("contractor_id", current_user["id"]).execute()

        contractor_view.update({
            "can_bid": response.data["status"] in ["active", "collecting_bids"] and not bid_response.data,
            "has_bid": bool(bid_response.data),
            "my_bid": bid_response.data[0] if bid_response.data else None,
            "distance_miles": 10.5,  # Would calculate actual distance
            "match_score": 0.85  # Would calculate based on contractor profile
        })

        return contractor_view

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/contractor-bids", response_model=dict[str, Any])
async def submit_contractor_bid(
    bid: BidSubmission,
    # current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_supabase_client)
):
    """Submit a bid for a bid card"""
    try:
        # Verify bid card exists and is accepting bids
        bid_card_response = db.table("bid_cards").select("*").eq("id", bid.bid_card_id).single().execute()
        if not bid_card_response.data:
            raise HTTPException(status_code=404, detail="Bid card not found")
        if bid_card_response.data["status"] not in ["active", "collecting_bids"]:
            raise HTTPException(status_code=400, detail="Bid card is not accepting bids")

        # Check if contractor already bid
        existing_bid = db.table("contractor_bids").select("id").eq("bid_card_id", bid.bid_card_id).eq("contractor_id", current_user["id"]).execute()
        if existing_bid.data:
            raise HTTPException(status_code=400, detail="You have already submitted a bid for this project")

        # Create bid
        bid_data = {
            "bid_card_id": bid.bid_card_id,
            "contractor_id": current_user["id"],
            "amount": bid.amount,
            "timeline_start": bid.timeline.start_date.isoformat(),
            "timeline_end": bid.timeline.end_date.isoformat(),
            "proposal": bid.proposal,
            "approach": bid.approach,
            "materials_included": bid.materials_included,
            "warranty_details": bid.warranty_details,
            "status": "submitted",
            "submitted_at": datetime.utcnow().isoformat()
        }

        bid_response = db.table("contractor_bids").insert(bid_data).execute()
        new_bid = bid_response.data[0]

        # Create milestones if provided
        if bid.milestones:
            milestone_data = [
                {
                    "bid_id": new_bid["id"],
                    "title": m["title"],
                    "description": m.get("description", ""),
                    "amount": m["amount"],
                    "estimated_completion": m["estimated_completion"]
                }
                for m in bid.milestones
            ]
            db.table("bid_milestones").insert(milestone_data).execute()

        # Update bid count on bid card
        db.table("bid_cards").update({"bid_count": bid_card_response.data["bid_count"] + 1}).eq("id", bid.bid_card_id).execute()

        return new_bid

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/messages", response_model=dict[str, Any])
async def send_bid_card_message(
    message: MessageSend,
    # current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_supabase_client)
):
    """Send a message related to a bid card"""
    try:
        # Determine sender type
        sender_type = "homeowner" if current_user.get("user_type") == "homeowner" else "contractor"

        # Verify permissions
        bid_card = db.table("bid_cards").select("*").eq("id", message.bid_card_id).single().execute()
        if not bid_card.data:
            raise HTTPException(status_code=404, detail="Bid card not found")

        # If contractor, check if they need to bid first
        if sender_type == "contractor" and bid_card.data["requires_bid_before_message"]:
            bid_check = db.table("contractor_bids").select("id").eq("bid_card_id", message.bid_card_id).eq("contractor_id", current_user["id"]).execute()
            if not bid_check.data:
                raise HTTPException(status_code=403, detail="You must submit a bid before messaging")

        # Create message
        message_data = {
            "bid_card_id": message.bid_card_id,
            "bid_id": message.bid_id,
            "sender_id": current_user["id"],
            "sender_type": sender_type,
            "recipient_id": message.recipient_id,
            "recipient_type": "contractor" if sender_type == "homeowner" else "homeowner",
            "content": message.content
        }

        response = db.table("bid_card_messages").insert(message_data).execute()
        new_message = response.data[0]

        # Handle attachments if provided
        if message.attachments:
            attachment_data = [
                {
                    "message_id": new_message["id"],
                    "type": att["type"],
                    "url": att["url"],
                    "name": att["name"],
                    "size": att.get("size")
                }
                for att in message.attachments
            ]
            db.table("message_attachments").insert(attachment_data).execute()

        # Update last_message_at on bid if applicable
        if message.bid_id:
            db.table("contractor_bids").update({"last_message_at": datetime.utcnow().isoformat()}).eq("id", message.bid_id).execute()

        return new_message

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{bid_card_id}/messages", response_model=list[dict[str, Any]])
async def get_bid_card_messages(
    bid_card_id: str,
    bid_id: Optional[str] = None,
    # current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_supabase_client)
):
    """Get messages for a bid card"""
    try:
        query = db.table("bid_card_messages").select("*").eq("bid_card_id", bid_card_id)

        if bid_id:
            query = query.eq("bid_id", bid_id)

        # Only show messages where user is sender or recipient
        query = query.or_(f"sender_id.eq.{current_user['id']},recipient_id.eq.{current_user['id']}")

        response = query.order("created_at", desc=False).execute()

        return response.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/messages/{message_id}/read")
async def mark_message_as_read(
    message_id: str,
    # current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_supabase_client)
):
    """Mark a message as read"""
    try:
        # Verify recipient
        message = db.table("bid_card_messages").select("*").eq("id", message_id).eq("recipient_id", current_user["id"]).single().execute()
        if not message.data:
            raise HTTPException(status_code=404, detail="Message not found or you don't have permission")

        db.table("bid_card_messages").update({
            "is_read": True,
            "read_at": datetime.utcnow().isoformat()
        }).eq("id", message_id).execute()

        return {"message": "Message marked as read"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{bid_card_id}/unread-count", response_model=dict[str, int])
async def get_unread_message_count(
    bid_card_id: str,
    # current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_supabase_client)
):
    """Get count of unread messages for a bid card"""
    try:
        response = db.table("bid_card_messages").select("id").eq("bid_card_id", bid_card_id).eq("recipient_id", current_user["id"]).eq("is_read", False).execute()

        return {"count": len(response.data)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
