"""
Contractor Proposals API Router
Manages contractor bid submissions and proposal retrieval for homeowners
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
import uuid
import json

try:
    from database_simple import db
except ImportError:
    from database import SupabaseDB
    db = SupabaseDB()

router = APIRouter(prefix="/api/contractor-proposals", tags=["contractor-proposals"])


class ContractorProposal(BaseModel):
    bid_card_id: str
    contractor_id: str
    contractor_name: str
    contractor_company: Optional[str] = None
    bid_amount: float
    timeline_days: int
    proposal_text: str
    attachments: Optional[List[Dict[str, Any]]] = None


@router.post("/submit")
async def submit_proposal(proposal: ContractorProposal):
    """Submit a contractor proposal/bid for a bid card"""
    try:
        # Check if contractor already submitted a proposal for this bid card
        existing = db.client.table("contractor_proposals").select("*").eq(
            "bid_card_id", proposal.bid_card_id
        ).eq("contractor_id", proposal.contractor_id).execute()
        
        if existing.data:
            return {
                "success": False,
                "message": "You have already submitted a proposal for this project"
            }
        
        # Create proposal record
        proposal_data = {
            "id": str(uuid.uuid4()),
            "bid_card_id": proposal.bid_card_id,
            "contractor_id": proposal.contractor_id,
            "contractor_name": proposal.contractor_name,
            "contractor_company": proposal.contractor_company,
            "bid_amount": proposal.bid_amount,
            "timeline_days": proposal.timeline_days,
            "proposal_text": proposal.proposal_text,
            "attachments": proposal.attachments or [],
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = db.client.table("contractor_proposals").insert(proposal_data).execute()
        
        if result.data:
            # Update bid card's bid count
            bid_card_result = db.client.table("bid_cards").select("*").eq(
                "id", proposal.bid_card_id
            ).execute()
            
            bid_card = {"data": bid_card_result.data[0] if bid_card_result.data else None}
            
            if bid_card.data:
                current_bids = bid_card.data.get("bid_document", {}).get("submitted_bids", [])
                current_bids.append({
                    "contractor_id": proposal.contractor_id,
                    "contractor_name": proposal.contractor_name,
                    "bid_amount": proposal.bid_amount,
                    "timeline_days": proposal.timeline_days,
                    "created_at": datetime.utcnow().isoformat()
                })
                
                update_data = {
                    "bid_document": {
                        **bid_card.data.get("bid_document", {}),
                        "submitted_bids": current_bids,
                        "bids_received_count": len(current_bids)
                    },
                    "bid_count": len(current_bids),
                    "updated_at": datetime.utcnow().isoformat()
                }
                
                # Check if target met
                target = bid_card.data.get("contractor_count_needed", 4)
                if len(current_bids) >= target:
                    update_data["status"] = "bids_complete"
                    update_data["bid_document"]["bids_target_met"] = True
                
                db.client.table("bid_cards").update(update_data).eq(
                    "id", proposal.bid_card_id
                ).execute()
            
            return {
                "success": True,
                "message": "Proposal submitted successfully",
                "proposal_id": proposal_data["id"]
            }
        else:
            return {
                "success": False,
                "message": "Failed to submit proposal"
            }
            
    except Exception as e:
        print(f"Error submitting proposal: {e}")
        return {
            "success": False,
            "message": f"Error submitting proposal: {str(e)}"
        }


@router.get("/bid-card/{bid_card_id}")
async def get_bid_card_proposals(bid_card_id: str):
    """Get all proposals for a specific bid card"""
    try:
        result = db.client.table("contractor_proposals").select("*").eq(
            "bid_card_id", bid_card_id
        ).order("created_at", desc=True).execute()
        
        return result.data or []
        
    except Exception as e:
        print(f"Error fetching proposals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/contractor/{contractor_id}")
async def get_contractor_proposals(contractor_id: str):
    """Get all proposals submitted by a specific contractor"""
    try:
        result = db.client.table("contractor_proposals").select(
            "*, bid_cards!inner(bid_card_number, project_type, title, status)"
        ).eq(
            "contractor_id", contractor_id
        ).order("created_at", desc=True).execute()
        
        return result.data or []
        
    except Exception as e:
        print(f"Error fetching contractor proposals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-attachment")
async def upload_proposal_attachment(
    file: UploadFile = File(...),
    proposal_id: str = Form(...),
    contractor_id: str = Form(...)
):
    """Upload an attachment for a proposal"""
    try:
        # Validate file type
        allowed_types = [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "image/jpeg",
            "image/png",
            "image/jpg"
        ]
        
        if file.content_type not in allowed_types:
            return {
                "success": False,
                "message": f"File type {file.content_type} not allowed"
            }
        
        # Read file data
        file_data = await file.read()
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_name = f"proposals/{proposal_id}/{timestamp}_{file.filename}"
        
        # Upload to Supabase Storage
        db.client.storage.from_("project-images").upload(
            unique_name,
            file_data,
            {
                "content-type": file.content_type,
                "cache-control": "3600",
                "upsert": "false"
            }
        )
        
        # Get public URL
        public_url = db.client.storage.from_("project-images").get_public_url(unique_name)
        
        # Update proposal with attachment
        proposal = db.client.table("contractor_proposals").select("*").eq(
            "id", proposal_id
        ).eq("contractor_id", contractor_id).single().execute()
        
        if proposal.data:
            attachments = proposal.data.get("attachments", [])
            attachments.append({
                "name": file.filename,
                "url": public_url,
                "type": file.content_type,
                "size": len(file_data),
                "uploaded_at": datetime.utcnow().isoformat()
            })
            
            db.client.table("contractor_proposals").update({
                "attachments": attachments,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", proposal_id).execute()
            
            return {
                "success": True,
                "message": "Attachment uploaded successfully",
                "url": public_url
            }
        else:
            return {
                "success": False,
                "message": "Proposal not found"
            }
            
    except Exception as e:
        print(f"Error uploading attachment: {e}")
        return {
            "success": False,
            "message": f"Error uploading attachment: {str(e)}"
        }


@router.put("/{proposal_id}/status")
async def update_proposal_status(proposal_id: str, status: str, homeowner_id: str):
    """Update the status of a proposal (accept/reject)"""
    try:
        if status not in ["accepted", "rejected"]:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        # Verify homeowner owns the bid card
        proposal = db.client.table("contractor_proposals").select(
            "*, bid_cards!inner(id)"
        ).eq("id", proposal_id).single().execute()
        
        if not proposal.data:
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        # Update proposal status
        result = db.client.table("contractor_proposals").update({
            "status": status,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", proposal_id).execute()
        
        if result.data:
            # If accepting, update bid card status
            if status == "accepted":
                db.client.table("bid_cards").update({
                    "status": "awarded",
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("id", proposal.data["bid_card_id"]).execute()
            
            return {
                "success": True,
                "message": f"Proposal {status} successfully"
            }
        else:
            return {
                "success": False,
                "message": "Failed to update proposal status"
            }
            
    except Exception as e:
        print(f"Error updating proposal status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint for proposals API"""
    return {
        "success": True,
        "status": "healthy",
        "message": "Contractor proposals API is running",
        "timestamp": datetime.utcnow().isoformat()
    }