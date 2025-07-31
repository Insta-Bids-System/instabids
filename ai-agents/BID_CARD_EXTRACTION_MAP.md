# Bid Card Extraction Map: CIA Conversation → JAA Bid Card

## What JAA Extracts from CIA Conversations

### 1. **Project Type** (Required)
- Extract from: User mentions of work type
- Examples: "lawn care", "kitchen remodel", "bathroom renovation", "roofing"
- Default: "General Home Improvement"

### 2. **Budget Range** (Required)
- Extract from: Dollar amounts mentioned
- Format: budget_min and budget_max
- Examples: "$500-800", "around $25k", "budget is 50000"
- Default: $5,000 - $15,000

### 3. **Timeline/Urgency** (Required)
- Extract from: Time mentions, urgency words
- Categories: emergency (ASAP), urgent (1 week), month, flexible
- Examples: "need it done ASAP", "by next month", "no rush"

### 4. **Location** (Required)
- Extract from: Address, city, zip code mentions
- Format: "32904 Melbourne Florida"
- Components: zip_code, city, state

### 5. **Project Scope/Description**
- Extract from: Detailed descriptions of work needed
- Examples: "knee-high grass", "new cabinets and countertops"
- Used for: Understanding complexity

### 6. **Property Details**
- Size: "half acre", "2000 sq ft", "3 bedroom"
- Type: "single family", "condo", "commercial"
- Access: "gate code", "HOA restrictions"

### 7. **Materials/Preferences**
- Extract from: Specific mentions of materials
- Examples: "quartz countertops", "hardwood floors", "vinyl siding"

### 8. **Images/Photos**
- Count: Number of uploaded photos
- Analysis: What's visible in photos (damage, current state)
- Storage: URLs to Supabase storage

### 9. **Special Requirements**
- Permits needed
- Licensed contractor requirements
- Insurance requirements
- Special equipment needed

### 10. **Homeowner Preferences**
- Communication: "text preferred", "call me"
- Scheduling: "weekends only", "mornings best"
- Decision style: Multiple quotes vs quick decision

### 11. **Concerns/Issues**
- Extract from: Problem mentions
- Examples: "water damage", "electrical issues", "structural concerns"

### 12. **Contractor Requirements**
- Number needed: Based on project size/complexity
- Specialties: "need licensed electrician", "roofing specialist"
- Experience level: Based on complexity score

## JAA Processing Flow

```
1. Load CIA conversation from Supabase
   ↓
2. Extract all 12 data points above
   ↓
3. Calculate complexity score (1-10)
   ↓
4. Determine contractor count needed
   ↓
5. Generate professional bid card document
   ↓
6. Save to bid_cards table
```

## Bid Card Output Structure

```json
{
  "bid_card_number": "BC-20250128123456",
  "project_type": "Lawn Care",
  "urgency_level": "emergency",
  "complexity_score": 3,
  "contractor_count_needed": 2,
  "budget_min": 500,
  "budget_max": 800,
  "location": {
    "address": "32904 Melbourne Florida",
    "property_type": "single family",
    "property_size": "half acre"
  },
  "project_details": {
    "current_condition": "Knee-high grass, overgrown",
    "desired_outcome": "Initial cleanup and regular maintenance",
    "special_requirements": [],
    "access_notes": ""
  },
  "timeline": {
    "start": "ASAP",
    "completion": "Within 1 week"
  },
  "images": {
    "count": 0,
    "urls": [],
    "analysis": []
  },
  "homeowner_profile": {
    "communication_preference": "text",
    "scheduling_preference": "flexible",
    "decision_style": "quick"
  },
  "bid_document": {
    "professional_summary": "...",
    "scope_of_work": "...",
    "contractor_guidance": "..."
  }
}
```

## Key Extraction Challenges

1. **Budget parsing**: Handle ranges ("500-800"), approximations ("around 25k"), single values
2. **Timeline parsing**: Convert natural language to dates/urgency levels
3. **Location parsing**: Extract components from various formats
4. **Image handling**: Store URLs, potentially analyze with vision API
5. **Implicit information**: Infer details not explicitly stated

The JAA's job is to be a smart parser that converts conversational data into structured, actionable bid cards for contractors.