"""
GPT-5 Intelligent Messaging Agent for InstaBids
BUSINESS CRITICAL: This agent is the linchpin preventing contact information sharing
Author: Agent 3 (Homeowner UX)  
Date: February 8, 2025
"""

import asyncio
import base64
import os
import re
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict, Union

from dotenv import load_dotenv
from langgraph.graph import END, StateGraph
from openai import AsyncOpenAI
from supabase import Client, create_client

load_dotenv()

# Initialize clients
supabase_url = os.getenv("SUPABASE_URL", "https://xrhgrthdcaymxuqcgrmj.supabase.co")
supabase_key = os.getenv("SUPABASE_ANON_KEY", "")
supabase: Client = create_client(supabase_url, supabase_key)

# Force load the correct OpenAI key from .env file, not system env
from pathlib import Path
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if line.startswith('OPENAI_API_KEY='):
                correct_api_key = line.split('=', 1)[1].strip()
                break
else:
    correct_api_key = os.getenv("OPENAI_API_KEY")

openai_client = AsyncOpenAI(
    api_key=correct_api_key
)


class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    SYSTEM = "system"
    AGENT_COMMENT = "agent_comment"


class SecurityThreat(str, Enum):
    CONTACT_INFO = "contact_info"
    SOCIAL_MEDIA = "social_media"
    EXTERNAL_MEETING = "external_meeting"
    PAYMENT_BYPASS = "payment_bypass"
    PLATFORM_BYPASS = "platform_bypass"


class ProjectScopeChange(str, Enum):
    MATERIAL_CHANGE = "material_change"     # "mulch instead of rocks"
    SIZE_CHANGE = "size_change"             # "actually make it bigger"
    FEATURE_ADDITION = "feature_addition"   # "also add a pergola"
    FEATURE_REMOVAL = "feature_removal"     # "skip the fence"
    TIMELINE_CHANGE = "timeline_change"     # "need it done sooner"
    BUDGET_CHANGE = "budget_change"         # "increase budget to $20k"


class AgentAction(str, Enum):
    BLOCK = "block"
    REDACT = "redact"
    WARN = "warn"
    COMMENT = "comment"
    ALLOW = "allow"


class IntelligentMessageState(TypedDict):
    """Enhanced state for intelligent message processing"""
    # Original message data
    original_content: str
    sender_type: str  # 'homeowner' or 'contractor'
    sender_id: str
    recipient_id: Optional[str]
    bid_card_id: str
    conversation_id: Optional[str]
    message_type: MessageType
    
    # Multimedia content
    attachments: List[Dict[str, Any]]
    image_data: Optional[str]  # Base64 encoded
    image_analysis: Optional[str]
    
    # GPT-5 Analysis Results
    security_analysis: Dict[str, Any]
    threats_detected: List[SecurityThreat]
    agent_decision: AgentAction
    confidence_score: float
    
    # Processed content
    filtered_content: str
    agent_comments: List[Dict[str, Any]]  # Private comments for parties
    homeowner_questions: List[str]
    suggested_actions: List[str]
    
    # Context and intelligence
    project_context: Dict[str, Any]
    conversation_history: List[Dict[str, Any]]
    contractor_reputation: Optional[Dict[str, Any]]
    
    # 🆕 PROJECT SCOPE CHANGE DETECTION
    scope_changes_detected: List[ProjectScopeChange]
    scope_change_details: Dict[str, Any]
    requires_bid_update: bool
    other_contractors_to_notify: List[str]
    
    # Final routing
    approved_for_delivery: bool
    delivery_instructions: Dict[str, Any]
    follow_up_required: bool


class GPT5SecurityAnalyzer:
    """GPT-5 powered security analysis for all message content"""
    
    def __init__(self):
        self.client = openai_client  # Use the correctly initialized client
    
    async def analyze_message_security(
        self, 
        content: str, 
        sender_type: str,
        project_context: Dict[str, Any],
        conversation_history: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive GPT-5 analysis of message security
        CRITICAL: This must catch ALL attempts to share contact information
        """
        
        system_prompt = """You are an AI security agent protecting a construction marketplace platform. Your job is CRITICAL to business success.

ABSOLUTE RULES:
1. NO contact information can EVER pass through (phone, email, address, social media)
2. NO external meeting arrangements (coffee, phone calls, site visits without platform)
3. NO payment discussions outside the platform
4. NO attempts to move conversation off-platform

🆕 PROJECT SCOPE CHANGE DETECTION:
You must ALSO detect when conversations indicate project scope changes that might require notifying other contractors:
- Material changes ("mulch instead of rocks", "granite countertops instead of laminate")
- Size changes ("make it bigger", "reduce the size by half")
- Feature additions ("also add a pergola", "include a fence around it")
- Feature removals ("skip the deck", "don't need the stairs")
- Timeline changes ("need it done by next week", "can wait until spring")
- Budget changes ("increase budget to $25k", "need to cut costs")

You must analyze EVERY message with extreme vigilance. Users will try creative methods to bypass filters:
- Spelling out numbers ("five-five-five-one-two-three")  
- Using symbols (5.5.5-1.2.3.4)
- Code words ("Call my office line")
- Embedded contact info in images or documents
- Subtle meeting suggestions ("Let's grab coffee to discuss")

CONTEXT: This is a construction project marketplace. Homeowners post projects, contractors bid. All communication MUST stay on platform for safety, legal protection, and business model.

Respond with detailed analysis including:
1. threats_detected: List of specific security issues found
2. confidence_score: 0-1 confidence in your analysis  
3. explanation: Detailed reasoning
4. recommended_action: BLOCK, REDACT, WARN, or ALLOW
5. suggested_response: What to tell the user if blocked/redacted
6. alternative_message: Safe version if content can be salvaged
7. scope_changes_detected: List of project scope changes identified
8. scope_change_details: Details about each scope change
9. requires_contractor_notification: Whether other contractors should be notified
"""

        user_prompt = f"""
ANALYZE THIS MESSAGE FOR SECURITY THREATS:

Original Message: "{content}"
Sender Type: {sender_type}
Project Context: {project_context.get('project_type', 'unknown')} - ${project_context.get('budget_min', 0)}-${project_context.get('budget_max', 0)}

Conversation History (last 3 messages):
{self._format_conversation_history(conversation_history or [])}

Provide your security analysis in JSON format.
"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",  # Using GPT-4o (GPT-5 not yet available)
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,  # Low temperature for consistency
            )
            
            result = response.choices[0].message.content
            import json
            return json.loads(result)  # Parse JSON response safely
            
        except Exception as e:
            print(f"GPT-5 Analysis Error: {e}")
            # Fallback to high-security mode if GPT-5 fails
            return self._fallback_analysis(content)
    
    async def analyze_image_content(self, image_data: str, image_format: str = "png") -> Dict[str, Any]:
        """
        Analyze images for embedded contact information
        CRITICAL: Users often embed phone numbers or addresses in images
        """
        
        system_prompt = """You are analyzing images for hidden contact information. Users may try to share phone numbers, emails, addresses, or social media handles embedded in images.

Look for:
- Phone numbers written anywhere in the image
- Email addresses
- Business cards or contact cards
- Addresses or location information  
- Social media usernames or QR codes
- Any text that could be contact information

This is CRITICAL for business success. Be extremely thorough."""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": [
                        {"type": "text", "text": "Analyze this image for any contact information:"},
                        {"type": "image_url", "image_url": f"data:image/{image_format};base64,{image_data}"}
                    ]}
                ],
                response_format={"type": "json_object"}
            )
            
            import json
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Image Analysis Error: {e}")
            return {
                "contact_info_detected": True,  # Conservative - block if unsure
                "confidence": 0.5,
                "explanation": "Image analysis failed - blocking for safety"
            }
    
    def _format_conversation_history(self, history: List[Dict[str, Any]]) -> str:
        """Format recent conversation for context"""
        if not history:
            return "No previous messages"
        
        formatted = []
        for msg in history[-3:]:  # Last 3 messages
            sender = msg.get('sender_type', 'unknown')
            content = msg.get('content', '')[:100] + "..." if len(msg.get('content', '')) > 100 else msg.get('content', '')
            formatted.append(f"{sender}: {content}")
        
        return "\n".join(formatted)
    
    def _fallback_analysis(self, content: str) -> Dict[str, Any]:
        """High-security fallback if GPT-5 is unavailable"""
        # Ultra-conservative regex patterns
        contact_patterns = [
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # Phone numbers
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b(?:meet|call|text|email|phone|contact)\b',  # Meeting words
            r'\b\d{1,5}\s+\w+\s+(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln)\b',  # Addresses
        ]
        
        threats = []
        for pattern in contact_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                threats.append("contact_info")
        
        return {
            "threats_detected": threats,
            "confidence_score": 0.8,
            "explanation": "Fallback analysis detected potential contact information",
            "recommended_action": "BLOCK" if threats else "ALLOW",
            "suggested_response": "Please keep all communication on the InstaBids platform for your protection.",
            "alternative_message": None
        }


class ProjectContextManager:
    """Loads and manages project context for intelligent decisions"""
    
    async def get_project_context(self, bid_card_id: str) -> Dict[str, Any]:
        """Load comprehensive project context"""
        try:
            # Get bid card details
            bid_card_response = supabase.table("bid_cards").select("*").eq("id", bid_card_id).execute()
            bid_card = bid_card_response.data[0] if bid_card_response.data else {}
            
            # Get contractor count and interactions  
            conversations_response = supabase.table("conversations").select("*").eq("bid_card_id", bid_card_id).execute()
            conversations = conversations_response.data or []
            
            return {
                "project_type": bid_card.get("project_type", "unknown"),
                "budget_min": bid_card.get("budget_min", 0),
                "budget_max": bid_card.get("budget_max", 0),
                "urgency_level": bid_card.get("urgency_level", "standard"),
                "contractor_count": len(conversations),
                "project_status": bid_card.get("status", "active"),
                "created_at": bid_card.get("created_at"),
                "conversations": conversations
            }
            
        except Exception as e:
            print(f"Error loading project context: {e}")
            return {"error": str(e)}


class IntelligentSecurityNode:
    """Main GPT-5 powered security analysis node"""
    
    def __init__(self):
        self.analyzer = GPT5SecurityAnalyzer()
        self.context_manager = ProjectContextManager()
    
    async def analyze_security(self, state: IntelligentMessageState) -> IntelligentMessageState:
        """Comprehensive security analysis using GPT-5"""
        
        # Load project context
        state["project_context"] = await self.context_manager.get_project_context(state["bid_card_id"])
        
        # Analyze text content
        security_analysis = await self.analyzer.analyze_message_security(
            content=state["original_content"],
            sender_type=state["sender_type"],
            project_context=state["project_context"],
            conversation_history=state.get("conversation_history", [])
        )
        
        state["security_analysis"] = security_analysis
        state["confidence_score"] = security_analysis.get("confidence_score", 0.0)
        
        # Analyze image content if present
        if state.get("image_data"):
            image_analysis = await self.analyzer.analyze_image_content(state["image_data"])
            state["image_analysis"] = image_analysis
            
            # Combine text and image threat analysis
            if image_analysis.get("contact_info_detected"):
                state["security_analysis"]["threats_detected"].append("contact_info")
        
        # Determine threats and action
        threats = security_analysis.get("threats_detected", [])
        state["threats_detected"] = [SecurityThreat(t) for t in threats if t in [e.value for e in SecurityThreat]]
        
        # Determine agent action based on threats
        if threats:
            if "contact_info" in threats or "platform_bypass" in threats:
                state["agent_decision"] = AgentAction.BLOCK
            else:
                state["agent_decision"] = AgentAction.REDACT
        else:
            state["agent_decision"] = AgentAction.ALLOW
        
        return state


class ScopeChangeDetectionNode:
    """Detects project scope changes and creates homeowner questions"""
    
    async def analyze_scope_changes(self, state: IntelligentMessageState) -> IntelligentMessageState:
        """Analyze message for project scope changes"""
        
        # Extract scope change data from GPT-5 analysis
        security_analysis = state.get("security_analysis", {})
        scope_changes = security_analysis.get("scope_changes_detected", [])
        scope_details = security_analysis.get("scope_change_details", {})
        requires_notification = security_analysis.get("requires_contractor_notification", False)
        
        state["scope_changes_detected"] = scope_changes
        state["scope_change_details"] = scope_details
        state["requires_bid_update"] = len(scope_changes) > 0
        
        # If homeowner is making scope changes, create agent questions
        if (state["sender_type"] == "homeowner" and 
            len(scope_changes) > 0 and 
            requires_notification):
            
            # Get other contractors for this bid card
            other_contractors = await self._get_other_contractors(
                state["bid_card_id"], 
                state.get("conversation_id")
            )
            
            state["other_contractors_to_notify"] = other_contractors
            
            # Create agent question for homeowner
            scope_question = self._create_scope_change_question(scope_changes, scope_details, other_contractors)
            
            if scope_question:
                # Add to agent comments as a question for the homeowner
                if "agent_comments" not in state:
                    state["agent_comments"] = []
                
                state["agent_comments"].append({
                    "visible_to": "homeowner",
                    "user_id": state["sender_id"],
                    "content": scope_question,
                    "type": "scope_change_question",
                    "timestamp": datetime.now().isoformat(),
                    "metadata": {
                        "scope_changes": scope_changes,
                        "other_contractors": other_contractors,
                        "requires_response": True
                    }
                })
        
        return state
    
    async def _get_other_contractors(self, bid_card_id: str, current_conversation_id: Optional[str]) -> List[str]:
        """Get list of other contractors involved in this bid card"""
        try:
            # Get all conversations for this bid card except the current one
            conversations = supabase.table("conversations").select("contractor_id, contractor_alias").eq(
                "bid_card_id", bid_card_id
            ).execute()
            
            other_contractors = []
            for conv in conversations.data or []:
                if conv.get("id") != current_conversation_id:
                    other_contractors.append({
                        "contractor_id": conv["contractor_id"],
                        "contractor_alias": conv.get("contractor_alias", "Contractor")
                    })
            
            return other_contractors
            
        except Exception as e:
            print(f"Error getting other contractors: {e}")
            return []
    
    def _create_scope_change_question(self, scope_changes: List[str], scope_details: Dict[str, Any], other_contractors: List[Dict[str, str]]) -> str:
        """Create intelligent question for homeowner about scope changes"""
        
        if not scope_changes or not other_contractors:
            return ""
        
        # Count other contractors
        contractor_count = len(other_contractors)
        contractor_names = [c.get("contractor_alias", "Contractor") for c in other_contractors]
        
        # Create context-aware question based on scope change type
        change_descriptions = []
        for change in scope_changes:
            if change == "material_change":
                change_descriptions.append("material preference changes")
            elif change == "size_change":
                change_descriptions.append("size modifications")
            elif change == "feature_addition":
                change_descriptions.append("additional features")
            elif change == "feature_removal":
                change_descriptions.append("removed features")
            elif change == "timeline_change":
                change_descriptions.append("timeline adjustments")
            elif change == "budget_change":
                change_descriptions.append("budget changes")
        
        changes_text = " and ".join(change_descriptions)
        
        # Create personalized question
        if contractor_count == 1:
            contractor_text = f"{contractor_names[0]}"
        elif contractor_count == 2:
            contractor_text = f"{contractor_names[0]} and {contractor_names[1]}"
        else:
            contractor_text = f"{', '.join(contractor_names[:-1])}, and {contractor_names[-1]}"
        
        question = f"💡 I noticed you mentioned {changes_text} in your conversation. "
        question += f"You have {contractor_count} other contractor{'s' if contractor_count > 1 else ''} "
        question += f"({contractor_text}) who might need to know about these changes to provide accurate bids. "
        question += f"Would you like me to notify them about the updated project scope?"
        
        return question


class AgentCommentNode:
    """Creates private agent comments for specific parties"""
    
    async def create_agent_comments(self, state: IntelligentMessageState) -> IntelligentMessageState:
        """Generate intelligent agent comments based on situation"""
        
        comments = []
        
        if state["agent_decision"] == AgentAction.BLOCK:
            # Comment for the sender
            sender_comment = {
                "visible_to": state["sender_type"],
                "user_id": state["sender_id"],
                "content": f"🤖 Your message was blocked for containing contact information. Please keep all communication on InstaBids for your protection and to ensure the best service.",
                "type": "warning",
                "timestamp": datetime.now().isoformat()
            }
            comments.append(sender_comment)
            
            # Comment for the recipient
            recipient_type = "homeowner" if state["sender_type"] == "contractor" else "contractor"
            recipient_comment = {
                "visible_to": recipient_type,
                "user_id": state.get("recipient_id", "system"),
                "content": f"🤖 The {state['sender_type']} attempted to share contact information. I've redirected them to continue the conversation here on the platform.",
                "type": "info",
                "timestamp": datetime.now().isoformat()
            }
            comments.append(recipient_comment)
        
        elif state["agent_decision"] == AgentAction.REDACT:
            # Explain what was redacted
            redacted_comment = {
                "visible_to": state["sender_type"],
                "user_id": state["sender_id"],
                "content": f"🤖 I've removed some content from your message for safety. The rest of your message has been delivered.",
                "type": "info", 
                "timestamp": datetime.now().isoformat()
            }
            comments.append(redacted_comment)
        
        # Add intelligent project suggestions if appropriate
        if state["sender_type"] == "homeowner" and len(comments) == 0:
            # Check if homeowner could benefit from suggestions
            project_context = state.get("project_context", {})
            if project_context.get("contractor_count", 0) > 3:
                suggestion_comment = {
                    "visible_to": "homeowner",
                    "user_id": state["sender_id"],
                    "content": f"💡 You have {project_context.get('contractor_count')} contractors interested. Would you like me to help you compare their bids or ask them specific questions?",
                    "type": "suggestion",
                    "timestamp": datetime.now().isoformat()
                }
                comments.append(suggestion_comment)
        
        state["agent_comments"] = comments
        return state


class ContentProcessingNode:
    """Process and filter content based on agent decision"""
    
    async def process_content(self, state: IntelligentMessageState) -> IntelligentMessageState:
        """Process content based on security analysis"""
        
        if state["agent_decision"] == AgentAction.BLOCK:
            state["filtered_content"] = ""
            state["approved_for_delivery"] = False
            
        elif state["agent_decision"] == AgentAction.REDACT:
            # Use GPT-5 suggested alternative or fall back to regex
            alt_message = state["security_analysis"].get("alternative_message")
            if alt_message:
                state["filtered_content"] = alt_message
            else:
                state["filtered_content"] = self._regex_redact(state["original_content"])
            state["approved_for_delivery"] = True
            
        else:  # ALLOW
            state["filtered_content"] = state["original_content"]
            state["approved_for_delivery"] = True
        
        return state
    
    def _regex_redact(self, content: str) -> str:
        """Fallback regex redaction"""
        patterns = [
            (r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', '[PHONE REMOVED]'),
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL REMOVED]'),
        ]
        
        filtered = content
        for pattern, replacement in patterns:
            filtered = re.sub(pattern, replacement, filtered, flags=re.IGNORECASE)
        
        return filtered


class MessagePersistenceNode:
    """Enhanced message persistence with agent comments"""
    
    async def save_message_and_comments(self, state: IntelligentMessageState) -> IntelligentMessageState:
        """Save message and agent comments to database"""
        
        if not state.get("approved_for_delivery"):
            # Still log blocked messages for analysis
            await self._log_blocked_message(state)
            return state
        
        try:
            # Save main message
            message_data = {
                "conversation_id": state["conversation_id"],
                "sender_type": state["sender_type"],
                "sender_id": state["sender_id"],
                "content": state["original_content"],
                "filtered_content": state["filtered_content"],
                "message_type": state["message_type"].value,
                "created_at": datetime.now().isoformat()
            }
            
            message_result = supabase.table("messages").insert(message_data).execute()
            message_id = message_result.data[0]["id"] if message_result.data else None
            
            # Save agent comments
            for comment in state.get("agent_comments", []):
                comment_data = {
                    "message_id": message_id,
                    "visible_to_type": comment["visible_to"],
                    "visible_to_id": comment["user_id"],
                    "content": comment["content"],
                    "comment_type": comment["type"],
                    "created_at": comment["timestamp"]
                }
                
                supabase.table("agent_comments").insert(comment_data).execute()
            
            state["message_id"] = message_id
            
        except Exception as e:
            print(f"Error saving message: {e}")
            state["message_id"] = None
        
        return state
    
    async def _log_blocked_message(self, state: IntelligentMessageState):
        """Log blocked messages for security analysis"""
        try:
            log_data = {
                "bid_card_id": state["bid_card_id"],
                "sender_type": state["sender_type"],
                "sender_id": state["sender_id"],
                "original_content": state["original_content"],
                "threats_detected": [t.value for t in state.get("threats_detected", [])],
                "confidence_score": state.get("confidence_score", 0.0),
                "blocked_at": datetime.now().isoformat()
            }
            
            supabase.table("blocked_messages_log").insert(log_data).execute()
            
        except Exception as e:
            print(f"Error logging blocked message: {e}")


def create_intelligent_messaging_graph() -> StateGraph:
    """Create the enhanced LangGraph workflow"""
    
    # Initialize nodes
    security_node = IntelligentSecurityNode()
    scope_node = ScopeChangeDetectionNode()
    comment_node = AgentCommentNode()
    content_node = ContentProcessingNode()
    persistence_node = MessagePersistenceNode()
    
    # Create workflow
    workflow = StateGraph(IntelligentMessageState)
    
    # Add nodes
    workflow.add_node("analyze_security", security_node.analyze_security)
    workflow.add_node("detect_scope_changes", scope_node.analyze_scope_changes)  # 🆕 NEW NODE
    workflow.add_node("create_comments", comment_node.create_agent_comments)  
    workflow.add_node("process_content", content_node.process_content)
    workflow.add_node("save_message", persistence_node.save_message_and_comments)
    
    # Define enhanced flow with scope change detection
    workflow.add_edge("analyze_security", "detect_scope_changes")
    workflow.add_edge("detect_scope_changes", "create_comments")
    workflow.add_edge("create_comments", "process_content")
    workflow.add_edge("process_content", "save_message")
    workflow.add_edge("save_message", END)
    
    # Set entry point
    workflow.set_entry_point("analyze_security")
    
    return workflow.compile()


# Create the intelligent messaging agent
intelligent_messaging_agent = create_intelligent_messaging_graph()


async def process_intelligent_message(
    content: str,
    sender_type: str,
    sender_id: str,
    bid_card_id: str,
    recipient_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    attachments: List[Dict[str, Any]] = None,
    image_data: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main entry point for intelligent message processing
    BUSINESS CRITICAL: This prevents contact information sharing
    """
    
    initial_state = IntelligentMessageState(
        original_content=content,
        sender_type=sender_type,
        sender_id=sender_id,
        recipient_id=recipient_id,
        bid_card_id=bid_card_id,
        conversation_id=conversation_id,
        message_type=MessageType.IMAGE if image_data else MessageType.TEXT,
        attachments=attachments or [],
        image_data=image_data,
        image_analysis=None,
        security_analysis={},
        threats_detected=[],
        agent_decision=AgentAction.ALLOW,
        confidence_score=0.0,
        filtered_content=content,
        agent_comments=[],
        homeowner_questions=[],
        suggested_actions=[],
        project_context={},
        conversation_history=[],
        contractor_reputation=None,
        # 🆕 NEW SCOPE CHANGE FIELDS
        scope_changes_detected=[],
        scope_change_details={},
        requires_bid_update=False,
        other_contractors_to_notify=[],
        approved_for_delivery=True,
        delivery_instructions={},
        follow_up_required=False
    )
    
    # Run through the intelligent workflow
    final_state = await intelligent_messaging_agent.ainvoke(initial_state)
    
    return {
        "message_id": final_state.get("message_id"),
        "approved": final_state.get("approved_for_delivery", False),
        "filtered_content": final_state.get("filtered_content", ""),
        "agent_decision": final_state.get("agent_decision", AgentAction.ALLOW).value,
        "threats_detected": [t.value for t in final_state.get("threats_detected", [])],
        "agent_comments": final_state.get("agent_comments", []),
        "confidence_score": final_state.get("confidence_score", 0.0),
        # 🆕 NEW SCOPE CHANGE INFORMATION
        "scope_changes_detected": final_state.get("scope_changes_detected", []),
        "scope_change_details": final_state.get("scope_change_details", {}),
        "requires_bid_update": final_state.get("requires_bid_update", False),
        "other_contractors_to_notify": final_state.get("other_contractors_to_notify", [])
    }


# Example usage and testing
if __name__ == "__main__":
    async def test_intelligent_messaging():
        """Test the intelligent messaging agent"""
        
        # Test 1: Contact info sharing attempt
        print("Test 1: Contact info sharing...")
        result1 = await process_intelligent_message(
            content="Hi! I love your project. Can you call me at 555-123-4567 to discuss details?",
            sender_type="contractor",
            sender_id="test-contractor-123",
            bid_card_id="test-bid-card-123"
        )
        
        print(f"Approved: {result1['approved']}")
        print(f"Decision: {result1['agent_decision']}")
        print(f"Threats: {result1['threats_detected']}")
        print(f"Comments: {len(result1['agent_comments'])}")
        print()
        
        # Test 2: Legitimate project discussion
        print("Test 2: Legitimate discussion...")
        result2 = await process_intelligent_message(
            content="I can install the kitchen cabinets for $15,000. The timeline would be 2 weeks. Do you have specific color preferences?",
            sender_type="contractor", 
            sender_id="test-contractor-456",
            bid_card_id="test-bid-card-123"
        )
        
        print(f"Approved: {result2['approved']}")
        print(f"Decision: {result2['agent_decision']}")
        print(f"Filtered content: {result2['filtered_content']}")
        
    # Run tests
    asyncio.run(test_intelligent_messaging())