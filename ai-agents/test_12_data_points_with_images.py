#!/usr/bin/env python3
"""
Test CIA → JAA Flow with Images
"""
import asyncio
import json
import os
from datetime import datetime
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.cia.agent import CustomerInterfaceAgent
from agents.jaa.new_agent import NewJobAssessmentAgent


async def test_cia_with_images():
    """Test CIA agent with image handling"""
    print("\n" + "="*80)
    print("TESTING CIA AGENT WITH IMAGES")
    print("="*80 + "\n")
    
    # Use existing user from database
    user_id = "bda3ab78-e034-4be7-8285-1b7be1bf1387"
    print(f"Using existing user ID: {user_id}")
    
    # Initialize CIA agent
    cia_agent = CustomerInterfaceAgent(anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    # Test message with images mentioned
    test_message = """
    I need my kitchen remodeled. The cabinets are falling apart and the countertops 
    are cracked. I'm in Orlando, FL 32801. Budget is around $15,000-20,000.
    Need this done within 2 months. I've uploaded 3 photos showing the damage.
    Looking for a complete cabinet replacement and new granite countertops.
    """
    
    # Simulate uploaded photos (in real usage, these would be actual URLs)
    test_photos = [
        "https://example.com/kitchen_photo_1.jpg",
        "https://example.com/kitchen_photo_2.jpg", 
        "https://example.com/kitchen_photo_3.jpg"
    ]
    
    print("Test Message:")
    print(test_message)
    print(f"\nSimulated Photos: {len(test_photos)} images")
    print("\n" + "-"*80 + "\n")
    
    # Create a session with photos in the initial state
    session_id = f"test_images_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Manually set up the conversation with photos
    # In real usage, the CIA agent would receive these through the API
    result = await cia_agent.handle_conversation(
        user_id=user_id,
        message=test_message,
        session_id=session_id,
        uploaded_photos=test_photos  # This would be passed from the frontend
    )
    
    print("CIA Response (truncated):")
    response = result.get('response', 'No response')
    print(response[:400] + "..." if len(response) > 400 else response)
    print("\n" + "-"*80 + "\n")
    
    # Check collected info including images
    if 'collected_info' in result:
        collected = result['collected_info']
        print("COLLECTED DATA WITH IMAGES:")
        print("-" * 40)
        
        # Check core data points
        print(f"Project Type: {collected.get('project_type')}")
        print(f"Service Type: {collected.get('service_type')}")
        print(f"Budget Min: ${collected.get('budget_min')}")
        print(f"Budget Max: ${collected.get('budget_max')}")
        print(f"Timeline Urgency: {collected.get('timeline_urgency')}")
        
        # Check images
        print(f"\nUPLOADED PHOTOS: {len(collected.get('uploaded_photos', []))}")
        for i, photo in enumerate(collected.get('uploaded_photos', [])):
            print(f"   Photo {i+1}: {photo}")
        
        # Check photo analysis (if any)
        print(f"\nPHOTO ANALYSES: {len(collected.get('photo_analyses', []))}")
        for analysis in collected.get('photo_analyses', []):
            print(f"   - {analysis}")
    
    return session_id


def test_jaa_image_extraction(session_id):
    """Test JAA extraction including images"""
    print("\n" + "="*80)
    print("TESTING JAA AGENT - IMAGE EXTRACTION")
    print("="*80 + "\n")
    
    # Initialize NEW JAA agent
    jaa_agent = NewJobAssessmentAgent()
    
    # Process conversation
    print(f"Processing session: {session_id}")
    result = jaa_agent.process_conversation(session_id)
    
    if result['success']:
        print("JAA Processing SUCCESSFUL!")
        print("-" * 40)
        
        bid_data = result['bid_card_data']
        
        print("\nEXTRACTED BID CARD DATA:")
        print(f"   Project Type: {bid_data.get('project_type')}")
        print(f"   Service Type: {bid_data.get('service_type')}")
        print(f"   Budget: ${bid_data.get('budget_min')}-${bid_data.get('budget_max')}")
        
        # Check images in bid card
        print(f"\nIMAGES IN BID CARD:")
        images = bid_data.get('images', [])
        print(f"   Total Images: {len(images)}")
        for i, img in enumerate(images):
            print(f"   Image {i+1}: {img}")
        
        # Check if images made it to the database record
        if 'database_record' in result:
            db_record = result['database_record']
            bid_doc = db_record.get('bid_document', {})
            all_data = bid_doc.get('all_extracted_data', {})
            
            print(f"\nIMAGES IN DATABASE:")
            db_images = all_data.get('images', [])
            print(f"   Stored in bid_document: {len(db_images)} images")
            
            # Check if we need a photo_urls field for BidCard.tsx
            print(f"\nCHECKING BIDCARD.TSX COMPATIBILITY:")
            print(f"   - BidCard expects: photo_urls[]")
            print(f"   - JAA provides: images[]")
            print(f"   - Match: {'YES' if 'images' in all_data else 'NEEDS MAPPING'}")
        
        return result['bid_card_number'], bid_data
    else:
        print(f"JAA Processing FAILED: {result.get('error')}")
        return None, None


def generate_html_bid_card(bid_data):
    """Generate HTML version of bid card for email/SMS"""
    print("\n" + "="*80)
    print("GENERATING HTML BID CARD")
    print("="*80 + "\n")
    
    # Extract data
    project_type = bid_data.get('project_type', 'Project')
    urgency = bid_data.get('urgency_level', 'flexible')
    budget_min = bid_data.get('budget_min', 0)
    budget_max = bid_data.get('budget_max', 0)
    location = bid_data.get('location', {})
    images = bid_data.get('images', [])
    
    # Generate HTML (email-safe version)
    html = f"""
    <div style="border: 1px solid #e5e7eb; border-radius: 8px; padding: 24px; background-color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, sans-serif; max-width: 600px;">
        <h2 style="font-size: 24px; margin-bottom: 16px; color: #111827;">
            {project_type.replace('_', ' ').title()}
        </h2>
        
        <div style="margin-bottom: 16px;">
            <span style="background-color: #fef3c7; color: #92400e; padding: 4px 12px; border-radius: 4px; font-size: 14px;">
                {'Urgent - Within 7 Days' if urgency == 'week' else 'Within 60 Days'}
            </span>
        </div>
        
        <p style="color: #6b7280; margin-bottom: 16px;">
            📍 {location.get('city', 'City')}, {location.get('state', 'FL')} • 
            💰 ${budget_min:,}-${budget_max:,} • 
            👥 4 contractors needed
        </p>
    """
    
    # Add images if available
    if images:
        html += f"""
        <div style="margin-bottom: 16px;">
            <p style="color: #6b7280; font-size: 14px;">📸 {len(images)} photos included</p>
        </div>
        """
    
    html += """
        <a href="https://instabids.com/bid-cards/BC123456" 
           style="display: inline-block; background-color: #2563eb; color: #ffffff; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: 600;">
            View Full Details & Photos →
        </a>
    </div>
    """
    
    print("Generated HTML bid card for email/SMS:")
    print(html)
    
    return html


async def main():
    """Run image tests"""
    try:
        print("\n" + "="*80)
        print("TESTING IMAGE HANDLING IN BID CARDS")
        print("="*80)
        
        # Test CIA with images
        session_id = await test_cia_with_images()
        
        if session_id:
            # Wait for database sync
            print("\nWaiting for database sync...")
            await asyncio.sleep(3)
            
            # Test JAA extraction
            bid_card_number, bid_data = test_jaa_image_extraction(session_id)
            
            if bid_card_number and bid_data:
                # Generate HTML version
                html_card = generate_html_bid_card(bid_data)
                
                print("\n" + "="*80)
                print("TEST SUMMARY: IMAGE HANDLING")
                print("="*80)
                print("\nIMAGE FLOW STATUS:")
                print("   [?] CIA receives uploaded photos")
                print("   [?] Photos stored in collected_info")
                print("   [?] JAA extracts photos to bid card")
                print("   [?] Photos available in bid_document")
                print("   [?] HTML bid card can display photo count")
                print("\nNOTE: The current system expects photo URLs to be provided")
                print("when the homeowner uploads them through the frontend.")
            else:
                print("\nJAA extraction failed")
        else:
            print("\nCIA collection failed")
            
    except Exception as e:
        print(f"\nTest error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())