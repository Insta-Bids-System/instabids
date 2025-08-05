"""CIA (Customer Interface Agent) State Definitions"""
from typing import Literal, Optional, TypedDict


class PhotoAnalysis(TypedDict):
    """Analysis results from uploaded photos"""
    url: str
    description: str
    identified_issues: list[str]
    estimated_scope: str
    areas_of_concern: list[str]
    confidence: float


class Message(TypedDict):
    """Chat message structure"""
    role: Literal["user", "assistant", "system"]
    content: str
    images: Optional[list[str]]  # URLs to images
    metadata: Optional[dict]


class CollectedInfo(TypedDict):
    """All collected project information"""
    # Basic Project Info
    project_type: Optional[str]
    project_description: Optional[str]
    current_condition: Optional[str]
    desired_outcome: Optional[str]

    # Timeline
    timeline_start: Optional[str]
    timeline_end: Optional[str]
    urgency: Optional[Literal["emergency", "urgent", "flexible", "planning"]]

    # Budget
    budget_min: Optional[float]
    budget_max: Optional[float]
    budget_flexibility: Optional[bool]

    # Property Details
    address: Optional[str]
    property_type: Optional[str]
    property_size: Optional[str]

    # Additional Details
    material_preferences: Optional[str]
    previous_work: Optional[str]
    access_constraints: Optional[str]
    decision_maker: Optional[str]
    contact_preferences: Optional[dict]

    # Photos
    uploaded_photos: list[str]
    photo_analyses: list[PhotoAnalysis]


class ConversationState(TypedDict):
    """Complete conversation state for CIA"""
    # Session Info
    user_id: str
    session_id: str
    project_id: Optional[str]

    # Conversation
    messages: list[Message]
    current_phase: Literal["intro", "discovery", "details", "photos", "review", "complete"]

    # Collected Data
    collected_info: CollectedInfo

    # Tracking
    missing_fields: list[str]
    conversation_summary: str
    ready_for_jaa: bool

    # Metadata
    created_at: str
    updated_at: str
    total_messages: int

    # Control Flow
    should_end: bool
    needs_human_review: bool
    error: Optional[str]


# Required fields for project submission
REQUIRED_FIELDS = [
    "project_type",
    "project_description",
    "timeline_start",
    "urgency",
    "budget_min",
    "budget_max",
    "address",
    "property_type"
]

# Phase transitions
PHASE_TRANSITIONS = {
    "intro": "discovery",
    "discovery": "details",
    "details": "photos",
    "photos": "review",
    "review": "complete"
}
