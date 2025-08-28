"""
CIA Schemas - Clean Pydantic models for the 12 InstaBids data points
"""
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class UrgencyLevel(str, Enum):
    """Urgency levels for projects"""
    EMERGENCY = "emergency"
    URGENT = "urgent" 
    WEEK = "week"
    MONTH = "month"
    FLEXIBLE = "flexible"


class BidCardUpdate(BaseModel):
    """The 12 InstaBids data points we extract from conversation"""
    
    # Core project info
    project_type: Optional[str] = Field(None, description="Kitchen, bathroom, lawn, roofing, etc.")
    urgency: Optional[UrgencyLevel] = Field(None, description="How urgent is the project")
    scope_details: Optional[str] = Field(None, description="Detailed description of work needed")
    
    # Location
    location: Optional[str] = Field(None, description="Address or zip code")
    zip_code: Optional[str] = Field(None, description="Just the zip code if available")
    
    # Budget (only if volunteered)
    budget_min: Optional[float] = Field(None, description="Minimum budget if mentioned")
    budget_max: Optional[float] = Field(None, description="Maximum budget if mentioned")
    
    # Timeline
    timeline: Optional[str] = Field(None, description="When they want it done")
    timeline_flexibility: Optional[bool] = Field(None, description="Can timeline be adjusted")
    
    # Property details
    property_type: Optional[str] = Field(None, description="Single family, condo, commercial, etc.")
    property_size: Optional[str] = Field(None, description="Square footage or rooms if mentioned")
    
    # Requirements
    special_requirements: Optional[str] = Field(None, description="Permits, HOA, access issues")
    materials: Optional[str] = Field(None, description="Specific material preferences")
    
    # Contact
    email: Optional[str] = Field(None, description="Email for bid delivery")
    phone: Optional[str] = Field(None, description="Phone if provided")
    
    # Preferences
    contractor_preferences: Optional[str] = Field(None, description="Small/large company, local, etc.")
    contractor_count: Optional[int] = Field(None, description="How many bids they want")
    
    # Additional
    additional_notes: Optional[str] = Field(None, description="Any other relevant info")

    def to_bid_card_fields(self) -> dict:
        """Convert to format expected by PotentialBidCardManager"""
        # Map our clean fields to the database field names
        field_mapping = {
            "project_type": "primary_trade",
            "scope_details": "user_scope_notes",
            "zip_code": "zip_code",
            "budget_min": "budget_range_min",
            "budget_max": "budget_range_max",
            "urgency": "urgency_level",
            "timeline": "estimated_timeline",
            "timeline_flexibility": "timeline_flexibility",
            "contractor_preferences": "contractor_size_preference",
            "materials": "materials_specified",
            "special_requirements": "special_requirements",
            "email": "email_address",
            "property_type": "property_type",
            "contractor_count": "contractor_count_needed"
        }
        
        result = {}
        data = self.dict(exclude_none=True)
        
        for our_field, db_field in field_mapping.items():
            if our_field in data:
                result[db_field] = data[our_field]
                
        # Also include unmapped fields
        for field, value in data.items():
            if field not in field_mapping and value is not None:
                result[field] = value
                
        return result

    def calculate_completion(self) -> int:
        """Calculate % of critical fields filled"""
        # Define which fields are critical
        critical_fields = [
            "project_type", "urgency", "scope_details", "location"
        ]
        
        # Count how many critical fields are filled
        filled_critical = sum(
            1 for field in critical_fields 
            if getattr(self, field) is not None
        )
        
        # Count total non-None fields
        all_fields = [
            field for field in self.dict() 
            if getattr(self, field) is not None
        ]
        
        # Weight critical fields more heavily
        critical_score = (filled_critical / len(critical_fields)) * 60
        other_score = (len(all_fields) / 12) * 40
        
        return min(int(critical_score + other_score), 100)