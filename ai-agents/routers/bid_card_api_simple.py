"""
Simplified Bid Card API for testing
This version works without authentication
"""

from datetime import datetime
from typing import Any, Optional
import uuid

from fastapi import APIRouter, HTTPException, Query, File, UploadFile, Form
from pydantic import BaseModel
import json

from database_simple import db


router = APIRouter(tags=["bid-cards"])

# Pydantic models for bid submission
class BidMilestone(BaseModel):
    title: str
    description: str
    amount: float
    estimated_completion: str

class BidSubmissionRequest(BaseModel):
    bid_card_id: str
    contractor_id: str = "22222222-2222-2222-2222-222222222222"  # Default test contractor
    amount: float
    timeline_start: str
    timeline_end: str
    proposal: str
    approach: str
    materials_included: bool = False
    warranty_details: Optional[str] = None
    milestones: Optional[list[BidMilestone]] = []
    # Note: File attachments will be handled separately via multipart form data

class BidAttachment(BaseModel):
    name: str
    type: str
    size: int
    url: str

# Simplified search endpoint that works without auth
@router.get("/search", response_model=dict[str, Any])
async def search_bid_cards(
    status: Optional[list[str]] = Query(None),
    city: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    zip_code: Optional[str] = Query(None),
    radius_miles: Optional[int] = Query(25, description="Radius in miles for location search"),
    page: int = 1,
    page_size: int = 20
):
    """
    Search bid cards with location filtering
    
    Location Parameters:
    - location_city: Filter by city name
    - location_state: Filter by state code (CA, TX, FL, etc.)
    - location_zip_code: Filter by ZIP code
    - radius_miles: Radius for location search (default: 25 miles)
    
    Note: Currently implements exact matching. In production, radius_miles would
    use geocoding to find all locations within the specified radius.
    """
    try:
        print(f"Search params: city={city}, state={state}, zip={zip_code}, radius={radius_miles}")
        
        supabase_client = db.client
        query = supabase_client.table("bid_cards").select("*")

        # Apply basic filters
        if status:
            query = query.in_("status", status)
        else:
            query = query.in_("status", ["active", "collecting_bids"])

        # Location filtering with radius support
        if zip_code and radius_miles:
            # Redirect to contractor-jobs API for radius search
            print(f"Radius search detected: redirecting to contractor-jobs API with zip_code={zip_code}, radius_miles={radius_miles}")
            import httpx
            
            try:
                # Prepare parameters for contractor-jobs API
                contractor_params = {
                    'zip_code': zip_code,
                    'radius_miles': radius_miles,
                    'page': page,
                    'page_size': page_size
                }
                
                print(f"Making request to contractor-jobs API with params: {contractor_params}")
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        "http://localhost:8008/api/contractor-jobs/search",
                        params=contractor_params
                    )
                
                print(f"Contractor-jobs API responded with status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"Got {len(data.get('job_opportunities', []))} job opportunities from contractor-jobs API")
                    
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
                            'budget_range': {
                                'min': job['budget_range']['min'],
                                'max': job['budget_range']['max']
                            },
                            'timeline': {
                                'start_date': job['timeline']['start_date'],
                                'end_date': job['timeline']['end_date']
                            },
                            'location': {
                                'city': job['location']['city'],
                                'state': job['location']['state'],
                                'zip_code': job['location']['zip_code']
                            },
                            'categories': job.get('categories', []),
                            'bid_count': job.get('bid_count', 0),
                            'contractor_count_needed': job.get('contractor_count_needed', 1),
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
                    print(f"Contractor-jobs API failed with status {response.status_code}")
                    # Fall back to regular search
            except Exception as e:
                print(f"Error calling contractor-jobs API: {e}")
                # Fall back to regular search
        elif city and state:
            # Exact city/state match when no radius specified
            print(f"Applying city+state filter: {city}, {state}")
            query = query.eq("location_city", city).eq("location_state", state)
        elif city:
            print(f"Applying city filter: {city}")
            query = query.eq("location_city", city)
        elif state:
            print(f"Applying state filter: {state}")
            query = query.eq("location_state", state)
        elif zip_code:
            # Exact zip match when no radius specified
            print(f"Applying zip filter: {zip_code}")
            query = query.eq("location_zip", zip_code)

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.range(offset, offset + page_size - 1)

        response = query.execute()

        # Transform bid cards for response
        bid_cards = []
        for card in response.data:
            # Create simplified bid card object
            bid_card = {
                "id": card["id"],
                "title": card.get("title", "Untitled Project"),
                "description": card.get("description", ""),
                "status": card.get("status", "active"),
                "budget_range": {
                    "min": float(card.get("budget_min", 1000)),
                    "max": float(card.get("budget_max", 10000))
                },
                "timeline": {
                    "start_date": card.get("timeline_start", datetime.now().isoformat()),
                    "end_date": card.get("timeline_end", datetime.now().isoformat())
                },
                "location": {
                    "city": card.get("location_city", "Unknown"),
                    "state": card.get("location_state", "Unknown"),
                    "zip_code": card.get("location_zip", "00000")
                },
                "project_type": card.get("project_type", "general"),
                "categories": card.get("categories", []),
                "bid_count": card.get("bid_count", 0),
                "created_at": card.get("created_at"),
                "is_urgent": False,
                "is_featured": False,
                "group_bid_eligible": card.get("group_bid_eligible", False)
            }
            
            # Add distance information if radius search was used
            if zip_code and radius_miles:
                from ..utils.simple_radius_search import calculate_distance_miles
                try:
                    card_zip = card.get("location_zip")
                    if card_zip:
                        distance = calculate_distance_miles(zip_code, str(card_zip))
                        if distance is not None:
                            bid_card["distance_miles"] = distance
                except Exception as e:
                    print(f"Error calculating distance for card {card['id']}: {e}")
            
            bid_cards.append(bid_card)
        
        # Sort by distance if distance information is available
        if zip_code and radius_miles and bid_cards:
            bid_cards = sorted(bid_cards, key=lambda x: x.get("distance_miles", 999))

        return {
            "bid_cards": bid_cards,
            "total": len(bid_cards),
            "page": page,
            "page_size": page_size,
            "has_more": len(bid_cards) == page_size
        }

    except Exception as e:
        print(f"Error in search_bid_cards: {e!s}")
        # Return empty result instead of error for testing
        return {
            "bid_cards": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
            "has_more": False
        }

# Test endpoint to create sample bid cards
@router.post("/test-data")
async def create_test_bid_cards():
    """Create test bid cards for development"""
    try:
        supabase_client = db.client

        # First check if we have a test project
        project_response = supabase_client.table("projects").select("id").limit(1).execute()
        if not project_response.data:
            # Create a test project
            project_data = {
                "homeowner_id": "test-homeowner-id",
                "title": "Test Project",
                "status": "active"
            }
            project_response = supabase_client.table("projects").insert(project_data).execute()

        project_id = project_response.data[0]["id"]

        # Create sample bid cards
        sample_cards = [
            {
                "project_id": project_id,
                "homeowner_id": "test-homeowner-id",
                "title": "Kitchen Renovation - Modern Update",
                "description": "Complete kitchen renovation including new cabinets, countertops, and appliances. Looking for experienced contractors.",
                "status": "active",
                "budget_min": 25000,
                "budget_max": 45000,
                "timeline_start": datetime.now().isoformat(),
                "timeline_end": (datetime.now().replace(month=datetime.now().month + 2)).isoformat(),
                "location_city": "Los Angeles",
                "location_state": "CA",
                "location_zip": "90001",
                "project_type": "renovation",
                "categories": ["kitchen", "plumbing", "electrical"],
                "group_bid_eligible": True,
                "bid_count": 3
            },
            {
                "project_id": project_id,
                "homeowner_id": "test-homeowner-id",
                "title": "Bathroom Remodel - Master Suite",
                "description": "Master bathroom remodel with new fixtures, tiling, and modern design.",
                "status": "collecting_bids",
                "budget_min": 15000,
                "budget_max": 25000,
                "timeline_start": datetime.now().isoformat(),
                "timeline_end": (datetime.now().replace(month=datetime.now().month + 1)).isoformat(),
                "location_city": "San Francisco",
                "location_state": "CA",
                "location_zip": "94102",
                "project_type": "renovation",
                "categories": ["bathroom", "plumbing", "tiling"],
                "group_bid_eligible": False,
                "bid_count": 5
            },
            {
                "project_id": project_id,
                "homeowner_id": "test-homeowner-id",
                "title": "Roof Replacement - Urgent",
                "description": "Need immediate roof replacement due to storm damage. Insurance claim approved.",
                "status": "active",
                "budget_min": 8000,
                "budget_max": 15000,
                "timeline_start": datetime.now().isoformat(),
                "timeline_end": (datetime.now().replace(day=datetime.now().day + 14)).isoformat(),
                "location_city": "Austin",
                "location_state": "TX",
                "location_zip": "78701",
                "project_type": "repair",
                "categories": ["roofing", "emergency"],
                "group_bid_eligible": False,
                "bid_count": 8
            }
        ]

        # Insert sample bid cards
        for card in sample_cards:
            supabase_client.table("bid_cards").insert(card).execute()

        return {"message": f"Created {len(sample_cards)} test bid cards"}

    except Exception as e:
        print(f"Error creating test data: {e!s}")
        return {"error": str(e)}

@router.get("/homeowner/{user_id}")
async def get_homeowner_bid_cards(user_id: str):
    """Get all bid cards for a specific homeowner"""
    try:
        # Use the same database connection pattern as the search endpoint
        supabase_client = db.client
        
        # Get all bid cards - for now, get all since we don't have homeowner filtering yet
        response = supabase_client.table("bid_cards").select("*").order("created_at", desc=True).execute()
        
        if not response or not response.data:
            print(f"No bid cards found for homeowner {user_id}")
            return []
        
        print(f"Raw database response: {len(response.data)} bid cards found")
        
        # Transform bid cards for homeowner dashboard - similar to search endpoint
        bid_cards = []
        for card in response.data:
            # Safely parse bid document to get contractor bids
            bid_document = card.get("bid_document") or {}
            submitted_bids = bid_document.get("submitted_bids") or []
            all_extracted_data = bid_document.get("all_extracted_data") or {}
            
            # Create basic bid card structure first
            bid_card = {
                "id": card.get("id", ""),
                "bid_card_number": card.get("bid_card_number", ""),
                "title": card.get("title") or all_extracted_data.get("project_description", "Untitled Project")[:50],
                "project_type": card.get("project_type", ""),
                "urgency_level": card.get("urgency_level", ""),
                "status": card.get("status", ""),
                "budget_min": card.get("budget_min", 0),
                "budget_max": card.get("budget_max", 0),
                "contractor_count_needed": card.get("contractor_count_needed", 0),
                "bids_received_count": card.get("bids_received_count", 0),
                "bids_target_met": card.get("bids_target_met", False),
                "complexity_score": card.get("complexity_score", 0),
                "created_at": card.get("created_at", ""),
                "cia_thread_id": card.get("cia_thread_id", ""),
                # Additional homeowner dashboard specific fields
                "bid_document": bid_document,
                "submitted_bids": submitted_bids,
                "description": all_extracted_data.get("project_description", ""),
                "location": all_extracted_data.get("location", {}),
                "timeline_urgency": all_extracted_data.get("timeline_urgency", ""),
                "material_preferences": all_extracted_data.get("material_preferences", []),
                "special_requirements": all_extracted_data.get("special_requirements", []),
                "images": all_extracted_data.get("images", [])
            }
            bid_cards.append(bid_card)
        
        print(f"Transformed {len(bid_cards)} bid cards for homeowner {user_id}")
        return bid_cards
        
    except Exception as e:
        print(f"Error getting homeowner bid cards: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@router.post("/submit-bid")
async def submit_contractor_bid(bid_data: BidSubmissionRequest):
    """Submit a contractor bio with support for attachments"""
    try:
        supabase_client = db.client
        
        # Validate bid card exists and is accepting bids
        bid_card_response = supabase_client.table("bid_cards").select("*").eq("id", bid_data.bid_card_id).execute()
        if not bid_card_response.data:
            raise HTTPException(status_code=404, detail="Bid card not found")
        
        bid_card = bid_card_response.data[0]
        if bid_card.get("status") not in ["active", "collecting_bids"]:
            raise HTTPException(status_code=400, detail="Bid card is not accepting bids")
        
        # Check if contractor has already submitted a bid
        existing_bid_response = supabase_client.table("contractor_bids").select("id").eq("bid_card_id", bid_data.bid_card_id).eq("contractor_id", bid_data.contractor_id).execute()
        if existing_bid_response.data:
            raise HTTPException(status_code=400, detail="Contractor has already submitted a bid for this project")
        
        # Prepare bid data
        bid_insert_data = {
            "bid_card_id": bid_data.bid_card_id,
            "contractor_id": bid_data.contractor_id,
            "amount": bid_data.amount,
            "timeline_start": bid_data.timeline_start,
            "timeline_end": bid_data.timeline_end,
            "proposal": bid_data.proposal,
            "approach": bid_data.approach,
            "materials_included": bid_data.materials_included,
            "warranty_details": bid_data.warranty_details,
            "status": "submitted",
            "submitted_at": datetime.now().isoformat(),
            "additional_data": {
                "milestones": [milestone.dict() for milestone in bid_data.milestones] if bid_data.milestones else []
            }
        }
        
        # Insert the bid
        bid_response = supabase_client.table("contractor_bids").insert(bid_insert_data).execute()
        if not bid_response.data:
            raise HTTPException(status_code=500, detail="Failed to submit bid")
        
        bid_id = bid_response.data[0]["id"]
        
        # Update bid card counts
        current_bid_count = bid_card.get("bids_received_count", 0)
        new_bid_count = current_bid_count + 1
        contractor_count_needed = bid_card.get("contractor_count_needed", 1)
        
        update_data = {
            "bids_received_count": new_bid_count,
            "bids_target_met": new_bid_count >= contractor_count_needed
        }
        
        # Update status if target met
        if new_bid_count >= contractor_count_needed:
            update_data["status"] = "bids_complete"
        
        supabase_client.table("bid_cards").update(update_data).eq("id", bid_data.bid_card_id).execute()
        
        return {
            "success": True,
            "bid_id": bid_id,
            "message": "Bid submitted successfully",
            "bids_received": new_bid_count,
            "target_met": new_bid_count >= contractor_count_needed
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error submitting bid: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/submit-bid-with-files")
async def submit_contractor_bid_with_files(
    bid_data: str = Form(...),  # JSON string containing bid data
    files: list[UploadFile] = File(default=[])
):
    """Submit a contractor bid with file attachments"""
    try:
        # Parse the bid data from JSON string
        bid_request = BidSubmissionRequest.model_validate_json(bid_data)
        
        # Submit the bid first (reuse the existing logic)
        bid_result = await submit_contractor_bid(bid_request)
        bid_id = bid_result["bid_id"]
        
        # Handle file uploads if any
        uploaded_attachments = []
        if files:
            supabase_client = db.client
            
            for file in files:
                if file.filename:
                    # For now, simulate file storage - in production this would upload to Supabase Storage
                    # This is placeholder logic - real implementation would upload to Supabase bucket
                    file_url = f"https://placeholder-storage.com/bid-attachments/{bid_id}/{file.filename}"
                    
                    # Store attachment metadata in database
                    attachment_data = {
                        "contractor_bid_id": bid_id,
                        "name": file.filename,
                        "type": file.content_type.split('/')[0] if file.content_type else 'document',
                        "url": file_url,
                        "size": file.size if file.size else 0,
                        "mime_type": file.content_type
                    }
                    
                    attachment_response = supabase_client.table("contractor_proposal_attachments").insert(attachment_data).execute()
                    if attachment_response.data:
                        uploaded_attachments.append({
                            "id": attachment_response.data[0]["id"],
                            "name": file.filename,
                            "url": file_url,
                            "type": attachment_data["type"]
                        })
        
        # Return success with attachment info
        result = bid_result.copy()
        result["attachments"] = uploaded_attachments
        result["message"] = f"Bid submitted successfully with {len(uploaded_attachments)} attachments"
        
        return result
        
    except Exception as e:
        print(f"Error submitting bid with files: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{bid_card_id}/bids")
async def get_bid_card_bids(bid_card_id: str):
    """Get all bids for a specific bid card"""
    try:
        supabase_client = db.client
        
        # Get all bids for this bid card
        bids_response = supabase_client.table("contractor_bids").select("*").eq("bid_card_id", bid_card_id).execute()
        
        bids = []
        for bid in bids_response.data:
            # Get attachments for this bid
            attachments_response = supabase_client.table("contractor_proposal_attachments").select("*").eq("contractor_bid_id", bid["id"]).execute()
            
            bid_data = {
                "id": bid["id"],
                "contractor_id": bid["contractor_id"],
                "amount": float(bid["amount"]),
                "timeline": {
                    "start_date": bid["timeline_start"],
                    "end_date": bid["timeline_end"]
                },
                "proposal": bid["proposal"],
                "approach": bid["approach"],
                "materials_included": bid["materials_included"],
                "warranty_details": bid["warranty_details"],
                "status": bid["status"],
                "submitted_at": bid["submitted_at"],
                "milestones": bid.get("additional_data", {}).get("milestones", []),
                "attachments": [
                    {
                        "id": att["id"],
                        "name": att["name"],
                        "type": att["type"],
                        "url": att["url"],
                        "size": att["size"]
                    }
                    for att in attachments_response.data
                ]
            }
            bids.append(bid_data)
        
        return {
            "bid_card_id": bid_card_id,
            "bids": bids,
            "total_bids": len(bids)
        }
        
    except Exception as e:
        print(f"Error getting bid card bids: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{bid_card_id}/contractor-view", response_model=dict[str, Any])
async def get_bid_card_contractor_view(
    bid_card_id: str,
    contractor_id: str = Query(...)
):
    """Get bid card details for contractor view"""
    try:
        supabase_client = db.client

        # Get the bid card
        response = supabase_client.table("bid_cards").select("*").eq("id", bid_card_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Bid card not found")

        card = response.data[0]

        # Check if contractor has already bid
        bid_response = supabase_client.table("contractor_bids").select("*").eq("bid_card_id", bid_card_id).eq("contractor_id", contractor_id).execute()
        has_bid = bool(bid_response.data)
        my_bid = bid_response.data[0] if bid_response.data else None

        # Get project photos if they exist
        photos = []
        try:
            photo_response = supabase_client.table("project_photos").select("*").eq("project_id", card.get("project_id")).execute()
            for photo in photo_response.data:
                photos.append({
                    "id": photo["id"],
                    "url": photo["url"],
                    "thumbnail_url": photo.get("thumbnail_url", photo["url"]),
                    "caption": photo.get("caption", ""),
                    "type": photo.get("type", "photo")
                })
        except Exception as photo_error:
            print(f"Could not load photos: {photo_error}")
            # Continue without photos

        # Get inspiration board images if linked
        inspiration_images = []
        try:
            if card.get("project_id"):
                # Check for inspiration boards linked to this project
                inspiration_response = supabase_client.table("inspiration_boards").select("*").eq("project_id", card["project_id"]).execute()
                for board in inspiration_response.data:
                    images_response = supabase_client.table("inspiration_images").select("*").eq("board_id", board["id"]).execute()
                    for img in images_response.data:
                        inspiration_images.append({
                            "id": img["id"],
                            "url": img["url"],
                            "thumbnail_url": img.get("thumbnail_url", img["url"]),
                            "caption": img.get("description", "Inspiration image"),
                            "type": "inspiration"
                        })
        except Exception as inspiration_error:
            print(f"Could not load inspiration images: {inspiration_error}")

        # Combine all images
        all_images = photos + inspiration_images

        contractor_view = {
            "id": card["id"],
            "title": card.get("title", "Untitled Project"),
            "description": card.get("description", ""),
            "status": card.get("status", "active"),
            "budget_range": {
                "min": float(card.get("budget_min", 1000)),
                "max": float(card.get("budget_max", 10000))
            },
            "timeline": {
                "start_date": card.get("timeline_start", datetime.now().isoformat()),
                "end_date": card.get("timeline_end", datetime.now().isoformat()),
                "flexibility": card.get("timeline_flexibility", "flexible")
            },
            "location": {
                "address": card.get("location_address"),
                "city": card.get("location_city", "Unknown"),
                "state": card.get("location_state", "Unknown"),
                "zip_code": card.get("location_zip", "00000")
            },
            "project_type": card.get("project_type", "general"),
            "categories": card.get("categories", []),
            "requirements": card.get("requirements", []),
            "preferred_schedule": card.get("preferred_schedule", []),
            "bid_count": card.get("bid_count", 0),
            "bid_deadline": card.get("bid_deadline"),
            "allows_questions": card.get("allows_questions", True),
            "group_bid_eligible": card.get("group_bid_eligible", False),
            "created_at": card.get("created_at"),
            "images": all_images,
            "can_bid": card.get("status") in ["active", "collecting_bids"] and not has_bid,
            "has_bid": has_bid,
            "my_bid": my_bid,
            "is_urgent": False,
            "is_featured": False,
            "distance_miles": 10.5,  # Would calculate actual distance
            "match_score": 0.85,     # Would calculate based on contractor profile
            "homeowner_verified": True,
            "response_time_hours": 24
        }

        return contractor_view

    except Exception as e:
        print(f"Error in get_bid_card_contractor_view: {e!s}")
        raise HTTPException(status_code=500, detail=str(e))
