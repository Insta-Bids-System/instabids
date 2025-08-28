"""
Clean categorization system without synonym mappings
Shows how the system would work with pure LLM intelligence
"""

# OPTION 1: Pure LLM - Let GPT handle everything
CATEGORIZATION_TOOL_CLEAN = {
    "type": "function",
    "function": {
        "name": "categorize_project",
        "description": "Categorize home improvement project into standardized taxonomy using your intelligence",
        "parameters": {
            "type": "object",
            "properties": {
                "service_category": {
                    "type": "string",
                    "enum": [
                        "Installation", "Repair", "Replacement", "Renovation", 
                        "Maintenance", "Ongoing", "Emergency", "Labor Only",
                        "Consultation", "Events", "Rentals", 
                        "Lifestyle & Wellness", "Professional/Digital", "AI Solutions"
                    ],
                    "description": "The primary type of service being requested"
                },
                "project_type": {
                    "type": "string",
                    "description": "Create a clear, normalized project type in snake_case (e.g. 'artificial_turf_repair')"
                },
                "project_scope": {
                    "type": "string", 
                    "enum": ["single_trade", "multi_trade", "full_renovation"],
                    "description": "The complexity/scope level of the project"
                },
                "confidence_score": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "description": "Confidence level in the categorization (0.0 to 1.0)"
                }
            },
            "required": ["service_category", "project_type", "project_scope", "confidence_score"]
        }
    }
}

async def handle_categorize_project_clean(
    bid_card_id: str,
    project_data: dict,
    tool_call_args: dict
) -> dict:
    """
    Clean categorization handler - no synonym mapping, pure LLM
    """
    
    # Get what the LLM provided
    service_category = tool_call_args.get("service_category")
    project_type = tool_call_args.get("project_type")  # LLM creates this
    confidence = tool_call_args.get("confidence_score", 0)
    
    # Basic validation only
    if confidence < 0.7:
        return {
            "success": False,
            "message": f"Confidence too low ({confidence:.2f}) - ask clarifying question"
        }
    
    # Save directly to database - no enhancement, no synonym checking
    if bid_card_id:
        await save_categorization_direct(bid_card_id, tool_call_args)
    
    return {
        "success": True,
        "message": f"Tagged: {service_category}, {project_type} ({confidence:.2f} confidence)"
    }

# OPTION 2: Hybrid - LLM + Simple Cleanup
def clean_project_type(user_input: str) -> str:
    """
    Simple cleanup without synonym mappings
    Just normalize the user's words into snake_case
    """
    # Basic cleaning
    cleaned = user_input.lower()
    cleaned = cleaned.replace(" and ", "_")
    cleaned = cleaned.replace(" ", "_")
    cleaned = cleaned.replace("-", "_")
    cleaned = cleaned.replace("'", "")
    
    # Remove common words that don't add meaning
    stop_words = ["i", "need", "want", "looking", "for", "my", "a", "an", "the"]
    words = [w for w in cleaned.split("_") if w not in stop_words and len(w) > 1]
    
    return "_".join(words[:3])  # Limit to 3 meaningful words

# Examples of what this would produce:
examples = [
    "I need my fake grass repaired",
    "Install artificial turf",
    "Kitchen renovation",
    "Fix my broken garage door",
    "Replace water heater"
]

print("EXAMPLES OF CLEAN SYSTEM:")
for example in examples:
    clean_type = clean_project_type(example)
    print(f"'{example}' -> '{clean_type}'")

print("\nPROS:")
print("- No massive synonym dictionary to maintain")
print("- LLM handles 90% of the intelligence")
print("- Simple, fast, reliable")
print("- Naturally handles new project types")

print("\nCONS:")
print("- Might create slight variations ('fake_grass_repair' vs 'artificial_turf_repair')")
print("- No pre-built intelligence for edge cases")

if __name__ == "__main__":
    pass