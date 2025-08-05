#!/usr/bin/env python3
"""
Complete CDA Flow Test - Shows how all 3 tiers work with radius search
"""

import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(__file__))

from utils.radius_search_fixed import get_zip_codes_in_radius

def demonstrate_complete_flow():
    """Demonstrate the complete CDA contractor discovery flow"""
    
    print("\n" + "="*70)
    print("COMPLETE CDA CONTRACTOR DISCOVERY FLOW WITH RADIUS SEARCH")
    print("="*70)
    
    # Test scenario
    print("\nSCENARIO: Lawn care project in Coconut Creek, FL (33442)")
    print("Need: 5 contractors")
    print("Radius: 10 miles")
    
    # Show zip codes in radius
    zip_codes = get_zip_codes_in_radius("33442", 10)
    print(f"\n[RADIUS] 10-mile radius covers {len(zip_codes)} zip codes")
    print(f"Zip codes: {zip_codes[:10]}...")
    
    # Simulate Tier 1
    print("\n" + "-"*70)
    print("TIER 1: INTERNAL CONTRACTOR DATABASE")
    print("-"*70)
    print("Action: Search our database for lawn care contractors")
    print(f"Searching: All {len(zip_codes)} zip codes within 10 miles")
    print("SQL Query: WHERE zip_code IN (33442, 33441, 33064, ... 28 total)")
    print("Result: Found 2 contractors")
    print("  1. GreenThumb Lawn Care (33442) - 0 miles")
    print("  2. Precision Landscaping (33441) - 4 miles")
    print("\nNeed 3 more contractors, proceeding to Tier 2...")
    
    # Simulate Tier 2
    print("\n" + "-"*70)
    print("TIER 2: PREVIOUSLY CONTACTED CONTRACTORS")
    print("-"*70)
    print("Action: Search contractors we've reached out to before")
    print(f"Searching: Previous outreach within {len(zip_codes)} zip codes")
    print("SQL Query: WHERE contractor_zip IN (33442, 33441, ... 28 total)")
    print("Result: Found 1 contractor")
    print("  3. Coastal Lawn Services (33064) - 3.9 miles")
    print("\nTotal: 3 contractors, need 2 more, proceeding to Tier 3...")
    
    # Simulate Tier 3
    print("\n" + "-"*70)
    print("TIER 3: GOOGLE WEB SEARCH")
    print("-"*70)
    print("Action: Search Google Maps for new contractors")
    print("\nIMPORTANT: How Google Search Works:")
    print("  - ONE API call with radius parameter")
    print("  - NOT searching each zip code individually")
    print("  - Google handles the geographic filtering")
    
    print("\nGoogle Maps API Request:")
    print("  URL: https://maps.googleapis.com/maps/api/place/textsearch/json")
    print("  Parameters:")
    print("    query: 'lawn care contractors'")
    print("    location: '26.3142, -80.2665' (lat/lng of 33442)")
    print("    radius: 16093 (10 miles in meters)")
    print("    key: [API_KEY]")
    
    print("\nGoogle Response: Found 12 contractors within 10 miles")
    print("  4. Superior Lawn Care (33073) - 4.1 miles")
    print("  5. A+ Landscaping (33486) - 4.9 miles")
    print("  6. Green Masters (33432) - 5.2 miles")
    print("  7. Tropical Lawns (33066) - 5.8 miles")
    print("  ... and 5 more")
    
    # Final selection
    print("\n" + "="*70)
    print("FINAL SELECTION USING AI SCORING")
    print("="*70)
    print("\nTotal contractors found: 15")
    print("  - Tier 1 (Internal): 2")
    print("  - Tier 2 (Previous): 1")
    print("  - Tier 3 (Google): 12")
    
    print("\nAI scores each contractor based on:")
    print("  - Distance from project")
    print("  - Reviews and ratings")
    print("  - Specialization match")
    print("  - Availability")
    print("  - Price range")
    
    print("\nFinal 5 contractors selected:")
    print("  1. GreenThumb Lawn Care (Internal) - Score: 95")
    print("  2. Precision Landscaping (Internal) - Score: 88")
    print("  3. Superior Lawn Care (Google) - Score: 86")
    print("  4. Coastal Lawn Services (Previous) - Score: 84")
    print("  5. A+ Landscaping (Google) - Score: 82")
    
    # Efficiency comparison
    print("\n" + "="*70)
    print("EFFICIENCY COMPARISON")
    print("="*70)
    
    print("\nOLD SYSTEM (Exact Zip Match Only):")
    print("  - Would only find contractors in 33442")
    print("  - Miss 27 other nearby zip codes")
    print("  - Likely find 0-1 internal contractors")
    print("  - Immediately jump to web search")
    print("  - Poor contractor pool")
    
    print("\nNEW SYSTEM (Radius Search):")
    print("  - Searches 28 zip codes within 10 miles")
    print("  - Finds more internal contractors first")
    print("  - Better reuse of previous contacts")
    print("  - Google search is geographically focused")
    print("  - Rich contractor pool for selection")
    
    print("\n" + "="*70)
    print("ANSWERS TO YOUR QUESTIONS")
    print("="*70)
    
    print("""
Q: Is it now running Google searches through all those zip codes?
A: NO! It uses ONE Google API call with a radius parameter.
   Google automatically searches the entire circular area.

Q: Is it just running it through one?
A: It runs ONE search centered on the bid card location with a 
   radius that covers all nearby zip codes automatically.

Q: If we don't find enough people, are we running it a 2nd time?
A: The system can expand the radius if needed:
   - First try: 5-10 mile radius
   - If not enough: Expand to 15 miles
   - Maximum: 25 miles
   But each search is still ONE API call, just with larger radius.

Q: How does it work with finding the contractors we want?
A: 1. Tier 1 searches internal DB within radius
   2. Tier 2 searches previous contacts within radius  
   3. Tier 3 uses Google with same radius
   4. AI scores ALL contractors found
   5. Selects best 5 based on scores

The radius ensures we get geographically relevant contractors
while the AI scoring ensures we select the best matches!
""")

if __name__ == "__main__":
    demonstrate_complete_flow()