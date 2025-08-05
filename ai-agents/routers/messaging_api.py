"""
Messaging API endpoints for homeowner-contractor communication
Integrates with LangGraph messaging agent for content filtering
"""

import os
import sys
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database_simple
from agents.messaging_agent import MessageType, process_broadcast, process_message


def get_supabase_client():
    return database_simple.get_client()
from supabase import Client


router = APIRouter(prefix="/api/messages", tags=["messaging"])

@router.get("/health")
async def health_check():
    """Health check endpoint for messaging system"""
    try:
        # Test database connection
        db = database_simple.get_client()
        # Simple query to test connection
        result = db.table("conversations").select("count").limit(1).execute()
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# Pydantic models for request/response
class SendMessageRequest(BaseModel):
    content: str
    sender_type: str  # 'homeowner' or 'contractor'
    sender_id: str
    bid_card_id: str
    conversation_id: Optional[str] = None
    message_type: Optional[str] = "text"
    metadata: Optional[dict[str, Any]] = None


class BroadcastMessageRequest(BaseModel):
    content: str
    sender_type: str
    sender_id: str
    bid_card_id: str
    recipient_type: str  # 'all_contractors', 'bidding_contractors', 'selected_contractors'
    recipient_ids: Optional[list[str]] = None


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    sender_type: str
    sender_id: str
    filtered_content: str
    content_filtered: bool
    filter_reasons: list[dict[str, Any]]
    message_type: str
    is_read: bool
    created_at: str


class ConversationResponse(BaseModel):
    id: str
    bid_card_id: str
    homeowner_id: str
    contractor_id: str
    contractor_alias: str
    status: str
    last_message_at: Optional[str]
    homeowner_unread_count: int
    contractor_unread_count: int
    created_at: str
    updated_at: str


class MarkReadRequest(BaseModel):
    message_ids: list[str]
    reader_type: str  # 'homeowner' or 'contractor'


@router.post("/send", response_model=MessageResponse)
async def send_message(
    request: SendMessageRequest,
    db: Client = Depends(get_supabase_client)
):
    """Send a message with automatic content filtering"""

    try:
        # Get homeowner_id from bid_card if available, or use sender_id if sender is homeowner
        homeowner_id = None
        try:
            bid_card = db.table("bid_cards").select("homeowner_id").eq("id", request.bid_card_id).single().execute()
            if bid_card.data:
                homeowner_id = bid_card.data.get("homeowner_id")
        except:
            pass

        # If homeowner_id is not available and sender is homeowner, use sender_id
        if not homeowner_id and request.sender_type == "homeowner":
            homeowner_id = request.sender_id
        elif not homeowner_id:
            # Use placeholder for contractor messages or when no homeowner info is available
            homeowner_id = "00000000-0000-0000-0000-000000000000"

        # Process message through LangGraph agent
        result = await process_message(
            content=request.content,
            sender_type=request.sender_type,
            sender_id=request.sender_id,
            bid_card_id=request.bid_card_id,
            conversation_id=request.conversation_id,
            message_type=MessageType(request.message_type),
            metadata=request.metadata,
            homeowner_id=homeowner_id
        )

        # Get the saved message from database
        print(f"MessagingAPI: LangGraph result keys: {list(result.keys())}")
        print(f"MessagingAPI: Looking for message_id in result: {'message_id' in result}")

        if "message_id" in result:
            print(f"MessagingAPI: Found message_id: {result['message_id']}")
            message = db.table("messaging_system_messages").select("*").eq("id", result["message_id"]).single().execute()

            return MessageResponse(
                id=message.data["id"],
                conversation_id=message.data["conversation_id"],
                sender_type=message.data["sender_type"],
                sender_id=message.data["sender_id"],
                filtered_content=message.data["filtered_content"],
                content_filtered=message.data["content_filtered"],
                filter_reasons=message.data["filter_reasons"],
                message_type=message.data["message_type"],
                is_read=message.data["is_read"],
                created_at=message.data["created_at"]
            )
        else:
            print(f"MessagingAPI: message_id not found in result, keys available: {list(result.keys())}")
            raise HTTPException(status_code=500, detail="Failed to save message")

    except Exception as e:
        print(f"ERROR in send_message: {e!s}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Message processing failed: {e!s}")


@router.post("/broadcast")
async def send_broadcast_message(
    request: BroadcastMessageRequest,
    db: Client = Depends(get_supabase_client)
):
    """Send a broadcast message to multiple recipients"""

    try:
        result = await process_broadcast(
            content=request.content,
            sender_type=request.sender_type,
            sender_id=request.sender_id,
            bid_card_id=request.bid_card_id,
            recipient_type=request.recipient_type,
            recipient_ids=request.recipient_ids
        )

        return {
            "broadcast_id": result["broadcast_id"],
            "filtered_content": result["filtered_content"],
            "content_filtered": result["content_filtered"],
            "filter_reasons": result["filter_reasons"],
            "total_recipients": result["total_recipients"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{bid_card_id}", response_model=list[ConversationResponse])
async def get_conversations(
    bid_card_id: str,
    user_type: str = Query(..., description="'homeowner' or 'contractor'"),
    user_id: str = Query(..., description="User ID"),
    db: Client = Depends(get_supabase_client)
):
    """Get all conversations for a bid card"""

    try:
        query = db.table("conversations").select("*").eq("bid_card_id", bid_card_id)

        if user_type == "homeowner":
            query = query.eq("homeowner_id", user_id)
        else:
            query = query.eq("contractor_id", user_id)

        conversations = query.order("last_message_at", desc=True).execute()

        return [ConversationResponse(**conv) for conv in conversations.data]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversation/{conversation_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    conversation_id: str,
    limit: int = Query(50, description="Number of messages to return"),
    offset: int = Query(0, description="Offset for pagination"),
    db: Client = Depends(get_supabase_client)
):
    """Get messages for a conversation"""

    try:
        messages = db.table("messaging_system_messages").select("*").eq(
            "conversation_id", conversation_id
        ).order(
            "created_at", desc=True
        ).range(offset, offset + limit - 1).execute()

        return [MessageResponse(
            id=msg["id"],
            conversation_id=msg["conversation_id"],
            sender_type=msg["sender_type"],
            sender_id=msg["sender_id"],
            filtered_content=msg["filtered_content"],
            content_filtered=msg["content_filtered"],
            filter_reasons=msg["filter_reasons"],
            message_type=msg["message_type"],
            is_read=msg["is_read"],
            created_at=msg["created_at"]
        ) for msg in messages.data]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mark-read")
async def mark_messages_read(
    request: MarkReadRequest,
    db: Client = Depends(get_supabase_client)
):
    """Mark messages as read and update unread counts"""

    try:
        # Mark messages as read
        db.table("messaging_system_messages").update({"is_read": True}).in_("id", request.message_ids).execute()

        # Get conversation IDs from messages
        messages = db.table("messaging_system_messages").select("conversation_id").in_("id", request.message_ids).execute()
        conversation_ids = list(set([msg["conversation_id"] for msg in messages.data]))

        # Reset unread count for the reader
        for conv_id in conversation_ids:
            if request.reader_type == "homeowner":
                db.table("conversations").update(
                    {"homeowner_unread_count": 0}
                ).eq("id", conv_id).execute()
            else:
                db.table("conversations").update(
                    {"contractor_unread_count": 0}
                ).eq("id", conv_id).execute()

        return {"success": True, "messages_marked": len(request.message_ids)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/broadcast/{broadcast_id}/status")
async def get_broadcast_status(
    broadcast_id: str,
    db: Client = Depends(get_supabase_client)
):
    """Get status of a broadcast message"""

    try:
        broadcast = db.table("broadcast_messages").select("*").eq("id", broadcast_id).single().execute()

        # Get read receipts
        receipts = db.table("broadcast_read_receipts").select("*").eq(
            "broadcast_message_id", broadcast_id
        ).execute()

        return {
            "broadcast": broadcast.data,
            "read_count": len(receipts.data),
            "read_receipts": receipts.data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/broadcast/{broadcast_id}/mark-read")
async def mark_broadcast_read(
    broadcast_id: str,
    reader_id: str,
    db: Client = Depends(get_supabase_client)
):
    """Mark a broadcast message as read by a recipient"""

    try:
        # Create read receipt
        receipt = {
            "broadcast_message_id": broadcast_id,
            "recipient_id": reader_id
        }

        db.table("broadcast_read_receipts").upsert(receipt).execute()

        # Update read count
        db.rpc("increment_broadcast_read_count", {"broadcast_id": broadcast_id}).execute()

        return {"success": True}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/unread-count")
async def get_unread_count(
    user_type: str = Query(..., description="'homeowner' or 'contractor'"),
    user_id: str = Query(..., description="User ID"),
    bid_card_id: Optional[str] = Query(None, description="Optional bid card filter"),
    db: Client = Depends(get_supabase_client)
):
    """Get total unread message count for a user"""

    try:
        query = db.table("conversations").select("homeowner_unread_count, contractor_unread_count")

        if user_type == "homeowner":
            query = query.eq("homeowner_id", user_id)
        else:
            query = query.eq("contractor_id", user_id)

        if bid_card_id:
            query = query.eq("bid_card_id", bid_card_id)

        conversations = query.execute()

        total_unread = 0
        for conv in conversations.data:
            if user_type == "homeowner":
                total_unread += conv["homeowner_unread_count"]
            else:
                total_unread += conv["contractor_unread_count"]

        return {
            "total_unread": total_unread,
            "conversations_with_unread": len([c for c in conversations.data if
                (c["homeowner_unread_count"] > 0 if user_type == "homeowner"
                 else c["contractor_unread_count"] > 0)])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket endpoint would go here for real-time messaging
# This requires additional setup with FastAPI WebSocket support
