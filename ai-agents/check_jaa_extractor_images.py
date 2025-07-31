#!/usr/bin/env python3
"""
Check if JAA's new_extractor handles images
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the actual extractor JAA uses
from agents.jaa.new_extractor import NewJAAExtractor

# Create test data with images
test_conversation = {
    'state': {
        'messages': [
            {'role': 'user', 'content': 'I need kitchen remodel with new cabinets'},
            {'role': 'assistant', 'content': 'I can help with that'}
        ],
        'collected_info': {
            'project_type': 'kitchen',
            'service_type': 'installation',
            'budget_min': 15000,
            'budget_max': 20000,
            'uploaded_photos': [
                'https://example.com/kitchen1.jpg',
                'https://example.com/kitchen2.jpg',
                'https://example.com/kitchen3.jpg'
            ],
            'photo_analyses': [
                {
                    'url': 'https://example.com/kitchen1.jpg',
                    'description': 'Kitchen with damaged cabinets',
                    'identified_issues': ['Water damage on lower cabinets'],
                    'estimated_scope': 'Full cabinet replacement needed',
                    'areas_of_concern': ['Potential mold behind cabinets'],
                    'confidence': 0.85
                }
            ]
        }
    }
}

# Test extraction
extractor = NewJAAExtractor()
result = extractor.extract_bid_card_data(test_conversation)

print("JAA EXTRACTOR IMAGE HANDLING TEST")
print("="*50)
print("\nInput photos:", test_conversation['state']['collected_info']['uploaded_photos'])
print("\nExtracted bid card data keys:", list(result.keys()))
print("\nImage-related fields in result:")
for key in result:
    if 'image' in key.lower() or 'photo' in key.lower() or key == 'images':
        print(f"  {key}: {result[key]}")

# Check if images field exists
if 'images' in result:
    print(f"\nSUCCESS: JAA extracts images! Count: {len(result['images'])}")
else:
    print("\nFAILED: JAA does not extract images field")

# Check for photo_urls (what BidCard.tsx expects)
if 'photo_urls' in result:
    print("SUCCESS: JAA provides photo_urls for BidCard.tsx")
else:
    print("NOTE: JAA provides 'images' but BidCard.tsx expects 'photo_urls'")
    print("      May need mapping in the frontend or bid card generation")