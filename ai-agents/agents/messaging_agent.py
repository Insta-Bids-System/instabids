"""
LangGraph Messaging Agent for Content Filtering
Ensures no contact information passes between homeowners and contractors
"""

import asyncio
import os
import re
from enum import Enum
from typing import Any, Optional, TypedDict

from dotenv import load_dotenv
from langgraph.graph import END, StateGraph
from supabase import Client, create_client


load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL", "https://xrhgrthdcaymxuqcgrmj.supabase.co")
supabase_key = os.getenv("SUPABASE_ANON_KEY", "")
supabase: Client = create_client(supabase_url, supabase_key)


class MessageType(str, Enum):
    TEXT = "text"
    SYSTEM = "system"
    BID_UPDATE = "bid_update"
    STATUS_CHANGE = "status_change"


class FilterReason(TypedDict):
    category: str
    pattern: str
    severity: str
    matched_text: str
    replacement: str


class MessageState(TypedDict):
    """State for the messaging agent"""
    original_content: str
    filtered_content: str
    content_filtered: bool
    filter_reasons: list[FilterReason]
    sender_type: str  # 'homeowner' or 'contractor'
    sender_id: str
    conversation_id: Optional[str]
    bid_card_id: str
    message_type: MessageType
    metadata: dict[str, Any]
    homeowner_id: Optional[str]
    message_id: Optional[str]
    created_at: Optional[str]


class ContentFilterNode:
    """Node that applies content filtering rules"""

    def __init__(self):
        self.filter_rules = self._load_filter_rules()

    def _load_filter_rules(self) -> list[dict[str, Any]]:
        """Load active filter rules from database"""
        try:
            response = supabase.table("content_filter_rules").select("*").eq("is_active", True).execute()
            return response.data
        except Exception as e:
            print(f"Error loading filter rules: {e}")
            # Return default rules if database fails
            return [
                {"rule_type": "regex", "pattern": r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b",
                 "replacement": "[PHONE REMOVED]", "severity": "high", "category": "phone"},
                {"rule_type": "regex", "pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                 "replacement": "[EMAIL REMOVED]", "severity": "high", "category": "email"},
            ]

    async def apply_filters(self, state: MessageState) -> MessageState:
        """Apply all content filter rules to the message"""
        content = state["original_content"]
        filtered_content = content
        filter_reasons = []
        content_filtered = False

        for rule in self.filter_rules:
            if rule["rule_type"] == "regex":
                pattern = re.compile(rule["pattern"], re.IGNORECASE)
                matches = pattern.findall(filtered_content)

                if matches:
                    content_filtered = True
                    for match in matches:
                        filter_reasons.append({
                            "category": rule["category"],
                            "pattern": rule["pattern"],
                            "severity": rule["severity"],
                            "matched_text": match,
                            "replacement": rule["replacement"]
                        })
                    filtered_content = pattern.sub(rule["replacement"], filtered_content)

            elif rule["rule_type"] == "keyword":
                if rule["pattern"].lower() in filtered_content.lower():
                    content_filtered = True
                    filter_reasons.append({
                        "category": rule["category"],
                        "pattern": rule["pattern"],
                        "severity": rule["severity"],
                        "matched_text": rule["pattern"],
                        "replacement": rule["replacement"]
                    })
                    # Case-insensitive replacement
                    filtered_content = re.sub(
                        re.escape(rule["pattern"]),
                        rule["replacement"],
                        filtered_content,
                        flags=re.IGNORECASE
                    )

        state["filtered_content"] = filtered_content
        state["content_filtered"] = content_filtered
        state["filter_reasons"] = filter_reasons

        return state


class ConversationManagerNode:
    """Node that manages conversations and contractor aliases"""

    async def manage_conversation(self, state: MessageState) -> MessageState:
        """Ensure conversation exists and has proper contractor alias"""

        print(f"ConversationManager: Starting with state conversation_id: {state.get('conversation_id')}")
        print(f"ConversationManager: sender_type: {state['sender_type']}, bid_card_id: {state['bid_card_id']}")

        if not state.get("conversation_id"):
            # Create or get existing conversation
            try:
                if state["sender_type"] == "contractor":
                    # Check if conversation already exists for this contractor
                    existing = supabase.table("conversations").select("*").eq(
                        "bid_card_id", state["bid_card_id"]
                    ).eq(
                        "contractor_id", state["sender_id"]
                    ).execute()

                    if existing.data:
                        conversation = existing.data[0]
                    else:
                        # Get contractor count for this bid card to assign alias
                        contractor_count = supabase.table("conversations").select("id").eq(
                            "bid_card_id", state["bid_card_id"]
                        ).execute()

                        alias_number = len(contractor_count.data) + 1
                        contractor_alias = f"Contractor {chr(64 + alias_number)}"  # A, B, C, etc.

                        placeholder_homeowner_id = state.get("homeowner_id", "00000000-0000-0000-0000-000000000000")

                        # Create new conversation
                        new_conversation = {
                            "bid_card_id": state["bid_card_id"],
                            "homeowner_id": placeholder_homeowner_id,
                            "contractor_id": state["sender_id"],
                            "contractor_alias": contractor_alias,
                            "status": "active"
                        }

                        conversation = supabase.table("conversations").insert(new_conversation).execute().data[0]

                else:  # homeowner
                    # For homeowner messages, we need a contractor to message
                    # For now, create a placeholder conversation or find existing one
                    # This should be updated when we know which contractor the homeowner is messaging

                    print(f"ConversationManager: Processing homeowner message for bid_card_id: {state['bid_card_id']}")
                    print(f"ConversationManager: State homeowner_id: {state.get('homeowner_id')}")
                    print(f"ConversationManager: State sender_id: {state.get('sender_id')}")

                    # Try to find any existing conversation for this bid card
                    existing = supabase.table("conversations").select("*").eq(
                        "bid_card_id", state["bid_card_id"]
                    ).limit(1).execute()

                    print(f"ConversationManager: Found {len(existing.data)} existing conversations")

                    if existing.data:
                        conversation = existing.data[0]
                        print(f"ConversationManager: Existing conversation ID: {conversation['id']}")
                        print(f"ConversationManager: Current homeowner_id in conversation: {conversation.get('homeowner_id')}")

                        # Update homeowner_id if it's null/missing or is a placeholder
                        current_homeowner_id = conversation.get("homeowner_id")
                        needs_update = not current_homeowner_id or current_homeowner_id == "00000000-0000-0000-0000-000000000000"
                        print(f"ConversationManager: Needs homeowner_id update: {needs_update}")

                        if needs_update:
                            homeowner_id = state.get("homeowner_id", state["sender_id"])
                            print(f"ConversationManager: Updating with homeowner_id: {homeowner_id}")

                            update_result = supabase.table("conversations").update({
                                "homeowner_id": homeowner_id
                            }).eq("id", conversation["id"]).execute()

                            print(f"ConversationManager: Update result: {update_result}")
                            conversation["homeowner_id"] = homeowner_id
                            print(f"ConversationManager: Updated conversation {conversation['id']} with homeowner_id: {homeowner_id}")
                        else:
                            print(f"ConversationManager: No update needed, homeowner_id is already set to: {current_homeowner_id}")
                    else:
                        # Create a placeholder conversation - in real usage, this would have a real contractor_id
                        placeholder_contractor_id = "00000000-0000-0000-0000-000000000001"
                        placeholder_homeowner_id = state.get("homeowner_id", state["sender_id"])

                        new_conversation = {
                            "bid_card_id": state["bid_card_id"],
                            "homeowner_id": placeholder_homeowner_id,
                            "contractor_id": placeholder_contractor_id,
                            "contractor_alias": "Contractor A",
                            "status": "active"
                        }

                        conversation = supabase.table("conversations").insert(new_conversation).execute().data[0]

                state["conversation_id"] = conversation["id"]
                print(f"ConversationManager: Set conversation_id to: {conversation['id']}")

            except Exception as e:
                print(f"Error managing conversation: {e}")
                import traceback
                traceback.print_exc()

        print(f"ConversationManager: Returning state with conversation_id: {state.get('conversation_id')}")
        return state


class MessagePersistenceNode:
    """Node that saves filtered messages to database"""

    async def save_message(self, state: MessageState) -> MessageState:
        """Save the filtered message to database"""

        print(f"MessagePersistence: Received state with conversation_id: {state.get('conversation_id')}")

        try:
            message_data = {
                "conversation_id": state["conversation_id"],
                "sender_type": state["sender_type"],
                "sender_id": state["sender_id"],
                "original_content": state["original_content"],
                "filtered_content": state["filtered_content"],
                "content_filtered": state["content_filtered"],
                "filter_reasons": state["filter_reasons"],
                "message_type": state["message_type"],
                "metadata": state.get("metadata", {}),
                "is_read": False
            }

            print(f"MessagePersistence: Inserting message data: {message_data}")
            result = supabase.table("messaging_system_messages").insert(message_data).execute()
            print(f"MessagePersistence: Insert result: {result}")

            if result.data:
                state["message_id"] = result.data[0]["id"]
                state["created_at"] = result.data[0]["created_at"]
                print(f"MessagePersistence: Successfully saved message with ID: {state['message_id']}")
            else:
                print("MessagePersistence: No data returned from insert")
                state["error"] = "No data returned from database insert"

        except Exception as e:
            print(f"MessagePersistence: Error saving message: {e}")
            import traceback
            traceback.print_exc()
            state["error"] = str(e)

        return state


class NotificationNode:
    """Node that handles real-time notifications"""

    async def send_notification(self, state: MessageState) -> MessageState:
        """Send WebSocket notification for new message"""

        # This would integrate with your WebSocket server
        # For now, we'll just mark it as notification sent
        state["notification_sent"] = True

        # In production, you'd emit WebSocket event here
        # Example: await websocket_manager.send_message(conversation_id, message_data)

        return state


def should_filter(state: MessageState) -> bool:
    """Determine if message needs filtering based on message type"""
    return state["message_type"] == MessageType.TEXT


def create_messaging_graph() -> StateGraph:
    """Create the LangGraph workflow for message processing"""

    # Initialize nodes
    filter_node = ContentFilterNode()
    conversation_node = ConversationManagerNode()
    persistence_node = MessagePersistenceNode()
    notification_node = NotificationNode()

    # Create the graph
    workflow = StateGraph(MessageState)

    # Add nodes
    workflow.add_node("manage_conversation", conversation_node.manage_conversation)
    workflow.add_node("filter_content", filter_node.apply_filters)
    workflow.add_node("save_message", persistence_node.save_message)
    workflow.add_node("send_notification", notification_node.send_notification)

    # Define the flow
    workflow.add_edge("manage_conversation", "filter_content")
    workflow.add_edge("filter_content", "save_message")
    workflow.add_edge("save_message", "send_notification")
    workflow.add_edge("send_notification", END)

    # Set entry point
    workflow.set_entry_point("manage_conversation")

    return workflow.compile()


# Create the messaging agent
messaging_agent = create_messaging_graph()


async def process_message(
    content: str,
    sender_type: str,
    sender_id: str,
    bid_card_id: str,
    conversation_id: Optional[str] = None,
    message_type: MessageType = MessageType.TEXT,
    metadata: Optional[dict[str, Any]] = None,
    homeowner_id: Optional[str] = None
) -> dict[str, Any]:
    """
    Process a message through the filtering pipeline
    
    Args:
        content: The message content to process
        sender_type: 'homeowner' or 'contractor'
        sender_id: UUID of the sender
        bid_card_id: UUID of the associated bid card
        conversation_id: Optional existing conversation ID
        message_type: Type of message
        metadata: Optional metadata
    
    Returns:
        Processed message state with filtered content and metadata
    """

    initial_state = MessageState(
        original_content=content,
        filtered_content=content,
        content_filtered=False,
        filter_reasons=[],
        sender_type=sender_type,
        sender_id=sender_id,
        conversation_id=conversation_id,
        bid_card_id=bid_card_id,
        message_type=message_type,
        metadata=metadata or {},
        homeowner_id=homeowner_id,
        message_id=None,
        created_at=None
    )

    # Process through the graph
    final_state = await messaging_agent.ainvoke(initial_state)

    return final_state


async def process_broadcast(
    content: str,
    sender_type: str,
    sender_id: str,
    bid_card_id: str,
    recipient_type: str,
    recipient_ids: Optional[list[str]] = None
) -> dict[str, Any]:
    """
    Process a broadcast message to multiple recipients
    
    Args:
        content: The message content to broadcast
        sender_type: 'homeowner' or 'contractor'
        sender_id: UUID of the sender
        bid_card_id: UUID of the associated bid card
        recipient_type: 'all_contractors', 'bidding_contractors', or 'selected_contractors'
        recipient_ids: List of recipient IDs for 'selected_contractors' type
    
    Returns:
        Broadcast message details with filtered content
    """

    # First filter the content
    filter_node = ContentFilterNode()
    filter_state = filter_node.apply_filters(MessageState(
        original_content=content,
        filtered_content=content,
        content_filtered=False,
        filter_reasons=[],
        sender_type=sender_type,
        sender_id=sender_id,
        conversation_id=None,
        bid_card_id=bid_card_id,
        message_type=MessageType.TEXT,
        metadata={}
    ))

    # Determine recipients based on type
    if recipient_type == "selected_contractors" and recipient_ids:
        total_recipients = len(recipient_ids)
    elif recipient_type == "bidding_contractors":
        # Get count of contractors who have bid
        bids = supabase.table("contractor_bids").select("contractor_id").eq(
            "bid_card_id", bid_card_id
        ).execute()
        recipient_ids = [bid["contractor_id"] for bid in bids.data]
        total_recipients = len(recipient_ids)
    else:  # all_contractors
        # This would need to be implemented based on your contractor discovery logic
        total_recipients = 0
        recipient_ids = []

    # Save broadcast message
    broadcast_data = {
        "bid_card_id": bid_card_id,
        "sender_id": sender_id,
        "sender_type": sender_type,
        "original_content": content,
        "filtered_content": filter_state["filtered_content"],
        "recipient_type": recipient_type,
        "recipient_ids": recipient_ids or [],
        "total_recipients": total_recipients,
        "read_count": 0
    }

    result = supabase.table("broadcast_messages").insert(broadcast_data).execute()

    return {
        "broadcast_id": result.data[0]["id"] if result.data else None,
        "filtered_content": filter_state["filtered_content"],
        "content_filtered": filter_state["content_filtered"],
        "filter_reasons": filter_state["filter_reasons"],
        "total_recipients": total_recipients
    }


# Example usage
if __name__ == "__main__":
    # Test the messaging agent
    async def test_messaging():
        # Test regular message with contact info
        result = await process_message(
            content="Hi, I'm interested in your project. Call me at 555-123-4567 or email john@example.com",
            sender_type="contractor",
            sender_id="test-contractor-id",
            bid_card_id="test-bid-card-id"
        )

        print("Filtered message:", result["filtered_content"])
        print("Filter reasons:", result["filter_reasons"])

        # Test broadcast message
        broadcast_result = await process_broadcast(
            content="Update: Project timeline has changed. Reach me at 555-987-6543 for details.",
            sender_type="homeowner",
            sender_id="test-homeowner-id",
            bid_card_id="test-bid-card-id",
            recipient_type="bidding_contractors"
        )

        print("\nBroadcast filtered:", broadcast_result["filtered_content"])
        print("Total recipients:", broadcast_result["total_recipients"])

    # Run the test
    asyncio.run(test_messaging())
