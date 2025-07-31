#!/usr/bin/env python3
"""
Show exactly what data is stored in bid cards
"""
import json
from agents.jaa.new_extractor import NewJAAExtractor

# Create a sample conversation state to show what gets extracted
sample_state = {
    'messages': [
        {'role': 'user', 'content': 'I need lawn care service. Budget $500-800.'},
        {'role': 'assistant', 'content': 'I can help with that...'}
    ],
    'collected_info': {
        # The 12 data points collected by CIA
        'project_type': 'lawn care',
        'service_type': 'ongoing_service',
        'project_description': 'Lawn care needed for overgrown grass',
        'budget_context': 'has_budget_range',
        'timeline_urgency': 'urgent',
        'urgency_reason': 'HOA is sending notices',
        'location_zip': '32904',
        'group_bidding_potential': True,
        'property_context': 'Half-acre property, single family home',
        'material_preferences': None,
        'special_requirements': 'HOA compliance, gate code 1234',
        'intention_score': 9,
        'uploaded_photos': ['photo1.jpg', 'photo2.jpg'],
        'photo_analyses': [],
        # Legacy fields
        'budget_min': 500,
        'budget_max': 800,
        'property_type': 'single family home'
    }
}

# Extract bid card data
extractor = NewJAAExtractor()
bid_card_data = extractor.extract_bid_card_data({'state': sample_state})

print("BID CARD DATA STRUCTURE")
print("="*80)
print("\nThe JAA agent extracts ALL collected data and stores it in two places:")
print("\n1. DATABASE COLUMNS (for querying):")
print("-" * 40)
print("  - bid_card_number: BC0730123456")
print("  - project_type: lawn care")
print("  - urgency_level: week")
print("  - complexity_score: 5")
print("  - contractor_count_needed: 4")
print("  - budget_min: 500")
print("  - budget_max: 800")
print("  - status: ready")

print("\n2. BID_DOCUMENT JSONB FIELD (complete data):")
print("-" * 40)
print("  Contains 'all_extracted_data' with ALL fields:")
print(json.dumps(bid_card_data, indent=2))

print("\n3. WHAT BIDCARD.TSX DISPLAYS:")
print("-" * 40)
print("The React component shows:")
print("  - Project type (formatted)")
print("  - Timeline/urgency badge")
print("  - Budget range")
print("  - Location")
print("  - Photo gallery (if images present)")
print("  - Scope of work")
print("  - Property details")
print("  - Special requirements")
print("  - Contractor count needed")
print("  - Call-to-action buttons")

print("\n4. WHAT'S IN THE HTML EMAIL VERSION:")
print("-" * 40)
print("Simplified version with:")
print("  - Project title")
print("  - Urgency badge")
print("  - Location (ZIP)")
print("  - Budget range")
print("  - Photo count")
print("  - Link to full bid card")

print("\n5. HOW IT WORKS:")
print("-" * 40)
print("NO SEPARATE LLM AGENT creates the bid card content!")
print("The JAA agent:")
print("  1. Uses NewJAAExtractor (Python code, not LLM)")
print("  2. Extracts ALL 12+ data points from CIA's collected_info")
print("  3. Stores everything in bid_document['all_extracted_data']")
print("  4. The frontend (BidCard.tsx) displays this structured data")
print("  5. No additional content generation - just formatting/display")