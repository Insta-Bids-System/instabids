# Project Categorization - Shared Tool System

## Overview
Instead of a dedicated categorization agent, we implement project categorization as a **shared tool** that both CIA and IRIS agents can use in-conversation. This provides intelligent, confidence-based categorization without spinning up separate services.

## Architecture Decision
**Decision**: Shared tool approach instead of standalone agent
**Rationale**: 
- Don't need separate service just to fill 2 fields
- Natural conversational UX 
- Confidence-based quality control
- Both agents can use the same logic

## Core Functionality

### When to Categorize
- On new/edited bid card title/description/project_type
- When IRIS adds photo-derived scope hints
- Only recalculates when inputs have changed
- Skips if fields are already locked/manually set

### Confidence-Based Behavior
- **Confidence ≥ 0.7**: Saves categorization and confirms to user
- **Confidence < 0.7**: Asks ONE clarifying question instead of guessing
- Example: "Is this a full kitchen gut or just new countertops?"

### Tool Schema
```json
{
  "type": "object",
  "properties": {
    "service_category": {
      "type": "string",
      "enum": ["Installation", "Repair", "Replacement", "Renovation", "Maintenance", "Ongoing", "Emergency", "Labor Only", "Consultation", "Events", "Rentals", "Lifestyle & Wellness", "Professional/Digital", "AI Solutions"]
    },
    "project_scope": {
      "type": "string", 
      "enum": ["single_trade", "multi_trade", "full_renovation"]
    },
    "required_capabilities": {
      "type": "array",
      "items": {"type": "string"}
    },
    "normalized_project_type": {
      "type": "string"
    },
    "confidence_score": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    }
  },
  "required": ["service_category", "project_scope", "confidence_score"]
}
```

## System Prompt for Agents

Add this to CIA and IRIS agent system prompts:

```
CATEGORIZATION TOOL USAGE:

You have access to a categorize_project tool for standardizing home improvement projects.

INPUTS YOU MAY RECEIVE:
- project_type (string, may be vague like "general")
- title (short string) 
- description (short paragraph)
- photo-derived hints (if available)

YOUR CATEGORIZATION JOB:
1) Normalize and categorize the project:
   - service_category ∈ {Installation, Repair, Replacement, Renovation, Maintenance, Ongoing, Emergency, Labor Only, Consultation, Events, Rentals, Lifestyle & Wellness, Professional/Digital, AI Solutions}
   - project_scope ∈ {single_trade, multi_trade, full_renovation}
   - required_capabilities: short list of trades (e.g., roofing, plumbing, electrical, cabinetry, drywall)
   - normalized_project_type: snake_case canonical name (e.g., kitchen_renovation)

2) Confidence Management:
   - Output confidence_score ∈ [0,1] for overall categorization
   - If confidence_score < 0.7, DO NOT save – ask ONE concise clarifying question
   - Only save when confidence ≥ 0.7

CATEGORIZATION RULES:
- Prefer description over project_type if they conflict
- Treat common synonyms as identical (e.g., "artificial turf" = "synthetic grass" = "fake grass")
- Infer scope from clues (multiple trades ⇒ multi_trade; full gut ⇒ full_renovation)
- Be consistent; don't invent capabilities not implied by inputs
- Return function call when confident; ask one question when unsure

CONVERSATIONAL UX:
- When you successfully categorize: "Tagged as Renovation, multi_trade (0.86 confidence). Need permits?"
- When unsure: Ask ONE specific question to clarify scope/category
- Keep it natural and brief
```

## Tool Implementation

### Tool Definition
```python
CATEGORIZATION_TOOL = {
    "type": "function",
    "function": {
        "name": "categorize_project",
        "description": "Categorize a home improvement project from project_type/title/description",
        "parameters": {
            # Schema above
        }
    }
}
```

### Tool Handler Function
```python
async def handle_categorize_project(
    bid_card_id: str,
    project_type: str,
    title: str, 
    description: str,
    tool_call_args: dict
) -> dict:
    """Handle categorize_project tool call"""
    
    confidence = tool_call_args.get("confidence_score", 0)
    
    if confidence >= 0.7:
        # Save categorization to database
        await upsert_bid_card_fields(bid_card_id, {
            "service_category": tool_call_args["service_category"],
            "project_scope": tool_call_args["project_scope"], 
            "required_capabilities": tool_call_args.get("required_capabilities", []),
            "normalized_project_type": tool_call_args.get("normalized_project_type")
        })
        
        return {
            "success": True,
            "message": f"Tagged: {tool_call_args['service_category']}, {tool_call_args['project_scope']} ({confidence:.2f})"
        }
    else:
        # Don't save low confidence categorizations
        return {
            "success": False,
            "message": "Confidence too low - ask clarifying question instead"
        }
```

## Test Cases

1. **Kitchen Project**: "Kitchen Remodel" + "Complete renovation with cabinets, countertops"
2. **Turf Variations**: "artificial turf" vs "synthetic grass" vs "fake grass" → same category
3. **Ambiguous**: "general" + "Test Project" → should ask clarifying question  
4. **Emergency**: "roofing" + "Storm damage repair urgently needed"
5. **Scope Decision**: "General – Bathroom refresh" → multi_trade vs single_trade

## Integration Points

### CIA Agent Integration
- Add categorization tool to CIA's available tools
- Trigger on new potential bid card creation
- Trigger when homeowner provides more project details

### IRIS Agent Integration  
- Add categorization tool to IRIS's available tools
- Trigger when photo analysis reveals project scope
- Trigger when inspiration board items suggest project type

### Database Integration
- Upsert fields only when confidence ≥ 0.7
- Don't overwrite manual/locked categorizations
- Track categorization metadata (confidence, timestamp, source)

## Deployment Strategy

### Phase 1: Shadow Write
- Save as `suggested_service_category`, `suggested_project_scope`
- Monitor confidence scores and accuracy
- Don't affect production categorization yet

### Phase 2: Production Write  
- Once validated, write to official fields when confidence ≥ 0.8
- Add manual override capability
- Add audit trail for categorization changes

## Benefits

1. **Natural UX**: Categorization happens in conversation, not as separate step
2. **Quality Control**: Confidence thresholds prevent bad categorizations
3. **Shared Logic**: Both agents use identical categorization rules
4. **Self-Improving**: Can ask clarifying questions to increase accuracy
5. **Lightweight**: No separate services or complex orchestration
6. **Consistent**: Handles synonyms and variations intelligently

## File Structure
```
agents/project_categorization/
├── README.md (this file)
├── tool_definition.py (shared tool schema)
├── handler.py (tool execution logic)
└── tests/
    ├── test_categorization_tool.py
    └── test_cases.json
```