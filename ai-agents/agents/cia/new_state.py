"""CIA (Customer Interface Agent) NEW State Definitions"""
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


class NewCollectedInfo(TypedDict):
    """NEW 12 Data Points Structure - InstaBids Focused"""

    # CORE PROJECT INFO
    project_type: Optional[str]  # roof, lawn, kitchen, bathroom, etc.
    service_type: Optional[Literal[
        "installation",      # New roof, kitchen remodel, new appliances
        "repair",           # Fix existing wall, repair lawn, fix appliance
        "ongoing_service",  # Pool cleaning, lawn care, housekeeping
        "handyman",         # Small jobs, labor only, help moving things
        "appliance_repair", # Washer, dryer, computer, specific object repair
        "labor_only"        # Just need someone with tools/skills for task
    ]]
    project_description: Optional[str]  # Detailed work needed

    # CONTEXT & MOTIVATION
    budget_context: Optional[str]  # "got quotes", "exploring", "have range", "dream project"
    timeline_urgency: Optional[Literal["emergency", "urgent", "flexible", "planning"]]
    urgency_reason: Optional[str]  # WHY the timeline exists (HOA, damage, etc.)
    location_zip: Optional[str]    # Zip code minimum

    # SMART OPPORTUNITIES
    group_bidding_potential: Optional[bool]  # Could neighbors benefit?
    group_bidding_interest: Optional[str]    # User's interest level in group pricing
    property_context: Optional[str]          # Only if relevant to project

    # SUPPORTING INFO
    material_preferences: Optional[str]      # Only if mentioned naturally
    uploaded_photos: list[str]               # Critical for accurate quotes
    photo_analyses: list[PhotoAnalysis]      # AI analysis of uploaded images
    special_requirements: Optional[str]      # Permits, HOA, access constraints

    # INTERNAL SCORING
    intention_score: Optional[int]           # 1-10 motivation assessment

    # LEGACY FIELDS (for compatibility)
    address: Optional[str]                   # Full address if provided
    property_type: Optional[str]             # House, condo, etc.
    timeline_start: Optional[str]            # Specific start date if given
    budget_min: Optional[float]              # If specific budget mentioned
    budget_max: Optional[float]              # If specific budget mentioned
    urgency: Optional[str]                   # Mapped from timeline_urgency


class ConversationState(TypedDict):
    """Complete conversation state for CIA"""
    # Session Info
    user_id: str
    session_id: str
    project_id: Optional[str]

    # Conversation
    messages: list[Message]
    current_phase: Literal["intro", "discovery", "details", "photos", "review", "complete"]

    # NEW: Collected Data Structure
    collected_info: NewCollectedInfo

    # Flow Control
    missing_fields: list[str]
    conversation_summary: str
    ready_for_jaa: bool

    # InstaBids Specific
    instabids_value_mentioned: bool          # Did we mention our advantages?
    group_bidding_discussed: bool            # Did we explore group opportunities?
    competitor_context: Optional[str]        # Did they mention other platforms?

    # Metadata
    created_at: str
    updated_at: str
    total_messages: int

    # Control Flow
    should_end: bool
    needs_human_review: bool
    error: Optional[str]


# UPDATED: Required fields - focusing on essentials only
REQUIRED_FIELDS_MINIMAL = [
    "project_type",
    "service_type",
    "project_description",
    "location_zip"
]

# OPTIONAL: Full completeness fields
COMPLETE_FIELDS = [
    "project_type",
    "service_type",
    "project_description",
    "budget_context",
    "timeline_urgency",
    "location_zip",
    "uploaded_photos",  # At least 1 photo preferred
    "intention_score"
]

# Service type classification mapping
SERVICE_TYPE_KEYWORDS = {
    "installation": [
        "new", "install", "replace", "remodel", "renovation", "addition",
        "build", "construction", "upgrade", "putting in"
    ],
    "repair": [
        "repair", "fix", "broken", "damaged", "not working", "problem with",
        "issue with", "crack", "leak", "hole", "restore"
    ],
    "ongoing_service": [
        "weekly", "monthly", "regular", "maintenance", "cleaning", "service",
        "ongoing", "every", "routine", "schedule"
    ],
    "handyman": [
        "small job", "quick fix", "help with", "handyman", "odd job",
        "little repair", "minor", "simple"
    ],
    "appliance_repair": [
        "washer", "dryer", "dishwasher", "refrigerator", "oven", "stove",
        "microwave", "air conditioner", "furnace", "water heater"
    ],
    "labor_only": [
        "just need someone", "labor only", "help moving", "need muscle",
        "someone with tools", "just the work", "no materials"
    ]
}

# Group bidding appropriate project types
GROUP_BIDDING_PROJECTS = [
    "roofing", "lawn care", "driveway", "fence", "exterior painting",
    "gutter cleaning", "pressure washing", "tree removal", "landscaping"
]

# Phase transitions (simplified)
PHASE_TRANSITIONS = {
    "intro": "discovery",
    "discovery": "details",
    "details": "photos",
    "photos": "review",
    "review": "complete"
}

# Intention score criteria
INTENTION_SCORE_FACTORS = {
    "high_urgency": +3,        # Emergency or urgent timeline
    "specific_timeline": +2,   # Mentions specific dates
    "budget_ready": +2,        # Has budget or got quotes
    "decision_authority": +1,  # Can make decisions
    "photos_uploaded": +1,     # Uploaded project photos
    "detailed_description": +1, # Gave detailed project info
    "exploring_only": -2,      # Just looking around
    "far_future": -1,          # Timeline is months away
    "budget_uncertain": -1     # No idea about costs
}
