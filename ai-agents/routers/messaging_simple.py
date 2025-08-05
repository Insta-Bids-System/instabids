"""
Fixed Messaging API with Proper Conversation Targeting
Ensures messages go to the correct contractor conversation 100% of the time
"""

import re
import uuid
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, File, Form, UploadFile

import database_simple


router = APIRouter(prefix="/api/messages", tags=["messaging"])

async def upload_file_to_storage(file_data: bytes, file_name: str, content_type: str, bucket: str = "project-images") -> str:
    """Upload file to Supabase Storage and return public URL"""
    try:
        db = database_simple.get_client()

        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_name = f"messages/{timestamp}_{uuid.uuid4().hex[:8]}_{file_name}"

        # Upload to Supabase Storage
        db.storage.from_(bucket).upload(
            unique_name,
            file_data,
            {
                "content-type": content_type,
                "cache-control": "3600",
                "upsert": "false"
            }
        )

        # Get public URL
        public_url = db.storage.from_(bucket).get_public_url(unique_name)
        return public_url

    except Exception as e:
        raise Exception(f"Failed to upload file: {e!s}")

def filter_content(content: str) -> dict[str, Any]:
    """Simple regex-based content filtering"""
    try:
        filtered_content = content
        filter_reasons = []

        # Phone number patterns
        phone_pattern = r"\b\d{3}[-.\\s]?\d{3}[-.\\s]?\d{4}\b"
        if re.search(phone_pattern, content):
            filtered_content = re.sub(phone_pattern, "[PHONE REMOVED]", filtered_content)
            filter_reasons.append({
                "pattern": "phone",
                "category": "contact_info",
                "severity": "high",
                "matched_text": re.search(phone_pattern, content).group()
            })

        # Email patterns
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        if re.search(email_pattern, content):
            filtered_content = re.sub(email_pattern, "[EMAIL REMOVED]", filtered_content)
            filter_reasons.append({
                "pattern": "email",
                "category": "contact_info",
                "severity": "high",
                "matched_text": re.search(email_pattern, content).group()
            })

        # Contact request patterns
        contact_patterns = [
            (r"call me at", "[CONTACT REQUEST REMOVED]"),
            (r"text me at", "[CONTACT REQUEST REMOVED]"),
            (r"reach me at", "[CONTACT REQUEST REMOVED]"),
            (r"contact me at", "[CONTACT REQUEST REMOVED]")
        ]

        for pattern, replacement in contact_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                match = re.search(pattern, content, re.IGNORECASE)
                filtered_content = re.sub(pattern, replacement, filtered_content, flags=re.IGNORECASE)
                filter_reasons.append({
                    "pattern": pattern,
                    "category": "contact_request",
                    "severity": "high",
                    "matched_text": match.group() if match else pattern,
                    "replacement": replacement
                })

        return {
            "original_content": content,
            "filtered_content": filtered_content,
            "content_filtered": len(filter_reasons) > 0,
            "filter_reasons": filter_reasons
        }

    except Exception as e:
        return {
            "original_content": content,
            "filtered_content": content,
            "content_filtered": False,
            "filter_reasons": [],
            "error": str(e)
        }

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection using existing pattern
        db = database_simple.get_client()
        result = db.table("conversations").select("count").limit(1).execute()

        return {
            "success": True,
            "status": "healthy",
            "message": "Fixed messaging system ready",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.post("/send")
async def send_message(request: dict[str, Any]):
    """
    Send a message with proper conversation targeting
    
    Required fields:
    - bid_card_id: The bid card this message relates to
    - sender_id: ID of the sender (homeowner or contractor)
    - sender_type: "homeowner" or "contractor"
    - content: Message content
    
    Optional fields:
    - conversation_id: Explicit conversation to send to (RECOMMENDED for homeowners)
    - target_contractor_id: For homeowners, specify which contractor to message
    - metadata: Additional message metadata
    """
    try:
        # Validate required fields
        required_fields = ["content", "sender_type", "sender_id", "bid_card_id"]
        for field in required_fields:
            if field not in request:
                return {"success": False, "error": f"Missing required field: {field}"}

        # Filter content
        filter_result = filter_content(request["content"])

        db = database_simple.get_client()

        # FIXED LOGIC: Proper conversation targeting
        conversation_id = None

        # Option 1: Explicit conversation_id provided (BEST - 100% accurate)
        if request.get("conversation_id"):
            # Verify the conversation exists and belongs to this bid card
            conv_check = db.table("conversations").select("*").eq(
                "id", request["conversation_id"]
            ).eq("bid_card_id", request["bid_card_id"]).execute()

            if conv_check.data:
                conversation_id = request["conversation_id"]
            else:
                return {"success": False, "error": "Invalid conversation_id for this bid card"}

        # Option 2: Homeowner sending to specific contractor
        elif request["sender_type"] == "homeowner" and request.get("target_contractor_id"):
            # Find the specific conversation between this homeowner and contractor
            conv_result = db.table("conversations").select("*").eq(
                "bid_card_id", request["bid_card_id"]
            ).eq("homeowner_id", request["sender_id"]).eq(
                "contractor_id", request["target_contractor_id"]
            ).execute()

            if conv_result.data:
                conversation_id = conv_result.data[0]["id"]
            else:
                # Create new conversation with specific contractor
                new_conv = {
                    "bid_card_id": request["bid_card_id"],
                    "homeowner_id": request["sender_id"],
                    "contractor_id": request["target_contractor_id"],
                    "contractor_alias": f"Contractor {request['target_contractor_id'][:1].upper()}",
                    "status": "active"
                }
                create_result = db.table("conversations").insert(new_conv).execute()
                if create_result.data:
                    conversation_id = create_result.data[0]["id"]

        # Option 3: Contractor sending message (they only have one conversation per bid card)
        elif request["sender_type"] == "contractor":
            # Find contractor's conversation for this bid card
            conv_result = db.table("conversations").select("*").eq(
                "bid_card_id", request["bid_card_id"]
            ).eq("contractor_id", request["sender_id"]).execute()

            if conv_result.data:
                conversation_id = conv_result.data[0]["id"]
            else:
                # Create new conversation (contractor initiating)
                # Need to determine homeowner_id from bid_card
                bid_card_result = db.table("bid_cards").select("homeowner_id").eq(
                    "id", request["bid_card_id"]
                ).execute()

                if bid_card_result.data:
                    homeowner_id = bid_card_result.data[0]["homeowner_id"]
                    new_conv = {
                        "bid_card_id": request["bid_card_id"],
                        "homeowner_id": homeowner_id,
                        "contractor_id": request["sender_id"],
                        "contractor_alias": "Contractor",
                        "status": "active"
                    }
                    create_result = db.table("conversations").insert(new_conv).execute()
                    if create_result.data:
                        conversation_id = create_result.data[0]["id"]
                else:
                    return {"success": False, "error": "Invalid bid_card_id"}

        # Option 4: Homeowner without target (ERROR - ambiguous)
        else:
            return {
                "success": False,
                "error": "Homeowner must specify target_contractor_id or conversation_id to ensure proper message routing"
            }

        if not conversation_id:
            return {"success": False, "error": "Could not determine conversation"}

        # Save message to the correct conversation
        message_data = {
            "conversation_id": conversation_id,
            "sender_type": request["sender_type"],
            "sender_id": request["sender_id"],
            "original_content": filter_result["original_content"],
            "filtered_content": filter_result["filtered_content"],
            "content_filtered": filter_result["content_filtered"],
            "filter_reasons": filter_result["filter_reasons"],
            "message_type": request.get("message_type", "text"),
            "metadata": request.get("metadata", {}),
            "is_read": False
        }

        message_result = db.table("messaging_system_messages").insert(message_data).execute()

        if message_result.data:
            # Update conversation's last_message_at
            db.table("conversations").update({
                "last_message_at": message_result.data[0]["created_at"]
            }).eq("id", conversation_id).execute()

            return {
                "success": True,
                "id": message_result.data[0]["id"],
                "conversation_id": conversation_id,
                "sender_type": request["sender_type"],
                "sender_id": request["sender_id"],
                "filtered_content": filter_result["filtered_content"],
                "content_filtered": filter_result["content_filtered"],
                "filter_reasons": filter_result["filter_reasons"],
                "message_type": request.get("message_type", "text"),
                "is_read": False,
                "created_at": message_result.data[0]["created_at"]
            }
        else:
            return {"success": False, "error": "Failed to save message"}

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to send message: {e!s}"
        }

@router.get("/conversations")
async def get_conversations(user_type: str, user_id: str, bid_card_id: Optional[str] = None):
    """
    Get conversations for a user
    
    Parameters:
    - user_type: "homeowner" or "contractor"
    - user_id: The user's ID
    - bid_card_id: Optional - filter by specific bid card
    """
    try:
        db = database_simple.get_client()

        query = db.table("conversations").select("*")

        if user_type == "homeowner":
            query = query.eq("homeowner_id", user_id)
        else:
            query = query.eq("contractor_id", user_id)

        if bid_card_id:
            query = query.eq("bid_card_id", bid_card_id)

        result = query.order("last_message_at", desc=True).execute()

        return {
            "success": True,
            "conversations": result.data or []
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "conversations": []
        }

@router.get("/conversations/{bid_card_id}")
async def get_conversations_for_bid_card(bid_card_id: str, user_type: str, user_id: str):
    """Get all conversations for a specific bid card and user"""
    try:
        db = database_simple.get_client()

        query = db.table("conversations").select("*").eq("bid_card_id", bid_card_id)

        if user_type == "homeowner":
            query = query.eq("homeowner_id", user_id)
        else:
            query = query.eq("contractor_id", user_id)

        result = query.order("last_message_at", desc=True).execute()

        return {
            "success": True,
            "conversations": result.data or []
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "conversations": []
        }

@router.get("/{conversation_id}")
async def get_messages(conversation_id: str):
    """Get all messages in a conversation with attachments"""
    try:
        db = database_simple.get_client()

        # Get messages
        messages_result = db.table("messaging_system_messages").select("*").eq(
            "conversation_id", conversation_id
        ).order("created_at", desc=False).execute()

        messages = messages_result.data or []

        # For each message, get its attachments
        for message in messages:
            attachments_result = db.table("message_attachments").select("*").eq(
                "message_id", message["id"]
            ).order("created_at", desc=False).execute()

            message["attachments"] = attachments_result.data or []

        return {
            "success": True,
            "messages": messages
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "messages": []
        }

@router.put("/{message_id}/read")
async def mark_message_read(message_id: str):
    """Mark a message as read"""
    try:
        db = database_simple.get_client()

        result = db.table("messaging_system_messages").update({
            "is_read": True
        }).eq("id", message_id).execute()

        return {
            "success": True,
            "message": "Message marked as read"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to mark message as read: {e!s}"
        }

# File upload endpoints remain the same...
@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    message_id: str = Form(...),
    conversation_id: str = Form(...),
    sender_type: str = Form(...),
    sender_id: str = Form(...)
):
    """Upload image attachment for a message"""
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            return {"success": False, "error": "File must be an image"}

        # Read file data
        file_data = await file.read()

        # Upload to storage
        file_url = await upload_file_to_storage(
            file_data,
            file.filename or "image.jpg",
            file.content_type,
            "project-images"
        )

        # Save attachment record to database
        db = database_simple.get_client()
        attachment_data = {
            "message_id": message_id,
            "type": "image",
            "url": file_url,
            "name": file.filename or "image.jpg",
            "size": len(file_data)
        }

        result = db.table("message_attachments").insert(attachment_data).execute()

        if result.data:
            return {
                "success": True,
                "attachment_id": result.data[0]["id"],
                "url": file_url,
                "type": "image",
                "name": file.filename,
                "size": len(file_data)
            }
        else:
            return {"success": False, "error": "Failed to save attachment record"}

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to upload image: {e!s}"
        }

@router.post("/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    message_id: str = Form(...),
    conversation_id: str = Form(...),
    sender_type: str = Form(...),
    sender_id: str = Form(...)
):
    """Upload document attachment for a message"""
    try:
        # Validate file type (allow common document types)
        allowed_types = [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ]

        if file.content_type not in allowed_types:
            return {"success": False, "error": "File type not allowed"}

        # Read file data
        file_data = await file.read()

        # Upload to storage (use project-documents bucket for documents)
        file_url = await upload_file_to_storage(
            file_data,
            file.filename or "document.pdf",
            file.content_type,
            "project-documents"
        )

        # Save attachment record to database
        db = database_simple.get_client()
        attachment_data = {
            "message_id": message_id,
            "type": "document",
            "url": file_url,
            "name": file.filename or "document.pdf",
            "size": len(file_data)
        }

        result = db.table("message_attachments").insert(attachment_data).execute()

        if result.data:
            return {
                "success": True,
                "attachment_id": result.data[0]["id"],
                "url": file_url,
                "type": "document",
                "name": file.filename,
                "size": len(file_data)
            }
        else:
            return {"success": False, "error": "Failed to save attachment record"}

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to upload document: {e!s}"
        }
