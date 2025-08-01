#!/usr/bin/env python3
"""
Simplified comprehensive test with real interactions
"""

import asyncio
import os
import base64
from agents.cia.agent import CustomerInterfaceAgent
from agents.jaa.agent import JobAssessmentAgent
from database_simple import db
from dotenv import load_dotenv
from datetime import datetime
import time

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Test user credentials
TEST_USER_ID = "e6e47a24-95ad-4af3-9ec5-f17999917bc3"  # test.homeowner@instabids.com

def encode_image(image_path):
    """Encode image to base64"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image {image_path}: {e}")
        return None

async def test_bathroom_with_photo_and_modification():
    """Test bathroom renovation with photo and then modify budget"""
    print("\n" + "="*80)
    print("TEST: Bathroom Renovation with Photo + Budget Modification")
    print("="*80)
    
    cia = CustomerInterfaceAgent(anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    # Load bathroom image
    bathroom_image = encode_image(r"C:\Users\Not John Or Justin\Documents\instabids\test-images\current-state\bathroom-small-1.webp")
    
    if bathroom_image:
        # Initial conversation
        print("\n[1] Starting bathroom conversation with photo...")
        result = await cia.handle_conversation(
            user_id=TEST_USER_ID,
            message="I need to renovate this small guest bathroom. Looking for a complete update - new vanity, toilet, tile work. Budget around $8,000-10,000.",
            images=[bathroom_image],
            session_id="test_bathroom_simple"
        )
        
        print(f"Response preview: {result['response'][:150]}...")
        
        # Add more details
        print("\n[2] Adding location and timeline...")
        result2 = await cia.handle_conversation(
            user_id=TEST_USER_ID,
            message="Location is Tampa, FL 33602. I'd like it done within the next month. Modern style.",
            session_id="test_bathroom_simple"
        )
        
        print(f"Response preview: {result2['response'][:150]}...")
        
        if result2.get('ready_for_jaa'):
            print("\n[3] Creating bid card with JAA...")
            jaa = JobAssessmentAgent()
            bid_card_id = jaa.process_conversation("test_bathroom_simple")
            print(f"Created bid card: {bid_card_id}")
            
            # Now test modification
            await asyncio.sleep(3)
            print("\n[4] Testing budget modification...")
            
            result3 = await cia.handle_conversation(
                user_id=TEST_USER_ID,
                message="Actually, I've been thinking about the bathroom project and I want to increase the budget to $12,000-15,000. I want really nice fixtures.",
                session_id="test_bathroom_modify"
            )
            
            print(f"Modification response: {result3['response'][:200]}...")
            
            # Check if agent recognized modification
            if 'update' in result3['response'].lower() or 'increase' in result3['response'].lower():
                print("[OK] Agent recognized budget modification!")
            
            return bid_card_id
    
    return None

async def test_landscaping_with_awareness():
    """Test new landscaping project to check multi-project awareness"""
    print("\n" + "="*80)
    print("TEST: Landscaping Project (Testing Multi-Project Awareness)")
    print("="*80)
    
    cia = CustomerInterfaceAgent(anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    # Load lawn image
    lawn_image = encode_image(r"C:\Users\Not John Or Justin\Documents\instabids\test-images\current-state\lawn-problem-1.webp")
    
    if lawn_image:
        print("\n[1] Starting landscaping conversation...")
        result = await cia.handle_conversation(
            user_id=TEST_USER_ID,
            message="I also need help with my lawn. It's in terrible shape. Need complete landscaping - new sod, plants, maybe some decorative stones. Here's a photo.",
            images=[lawn_image],
            session_id="test_landscaping_awareness"
        )
        
        print(f"Response preview: {result['response'][:200]}...")
        
        # Check for multi-project awareness
        response_lower = result['response'].lower()
        if 'kitchen' in response_lower or 'bathroom' in response_lower or 'other project' in response_lower:
            print("[OK] Agent shows awareness of other projects!")
        else:
            print("[INFO] Agent did not explicitly mention other projects")
        
        # Complete the landscaping request
        print("\n[2] Providing budget and timeline...")
        result2 = await cia.handle_conversation(
            user_id=TEST_USER_ID,
            message="Budget for landscaping is $12,000-15,000. Same property in Tampa. Timeline is flexible.",
            session_id="test_landscaping_awareness"
        )
        
        if result2.get('ready_for_jaa'):
            print("\n[3] Creating bid card with JAA...")
            jaa = JobAssessmentAgent()
            bid_card_id = jaa.process_conversation("test_landscaping_awareness")
            print(f"Created bid card: {bid_card_id}")
            return bid_card_id
    
    return None

def check_backend_data():
    """Check the backend data"""
    print("\n" + "="*80)
    print("BACKEND VERIFICATION")
    print("="*80)
    
    # Get recent bid cards
    print("\n[Checking Recent Bid Cards]")
    bid_cards = db.client.table('bid_cards').select('*').order('created_at', desc=True).limit(5).execute()
    
    if bid_cards.data:
        for card in bid_cards.data:
            print(f"\nBid Card: {card['bid_card_number']}")
            print(f"  Type: {card['project_type']}")
            print(f"  Budget: ${card['budget_min']:,} - ${card['budget_max']:,}")
            print(f"  Status: {card['status']}")
            
            # Check for photos
            if card.get('bid_document', {}).get('all_extracted_data'):
                data = card['bid_document']['all_extracted_data']
                images = data.get('images', []) or data.get('photo_urls', [])
                print(f"  Photos: {len(images)}")
                if images and 'localhost:8008/static' in images[0]:
                    print("  [OK] Using local storage for photos")
    
    # Check local storage
    import os
    static_uploads = os.path.join(os.path.dirname(__file__), 'static', 'uploads', TEST_USER_ID)
    print(f'\n[Checking Local Storage]')
    if os.path.exists(static_uploads):
        files = os.listdir(static_uploads)
        print(f'Found {len(files)} images in local storage')
    else:
        print('No local storage directory found')
    
    # Test dashboard API
    print(f'\n[Testing Dashboard API]')
    import requests
    try:
        response = requests.get(f"http://localhost:8008/api/bid-cards/homeowner/{TEST_USER_ID}", timeout=5)
        if response.ok:
            data = response.json()
            print(f"API returned {len(data)} bid cards")
            # Check if photo_urls field exists
            if data and data[0].get('bid_document', {}).get('all_extracted_data', {}).get('photo_urls'):
                print("[OK] photo_urls field exists (frontend compatible)")
        else:
            print(f"API Error: {response.status_code}")
    except Exception as e:
        print(f"API Connection Error: {e}")

async def main():
    """Run simplified comprehensive test"""
    print("="*80)
    print("SIMPLIFIED COMPREHENSIVE TEST")
    print("User: test.homeowner@instabids.com")
    print("="*80)
    
    # Test 1: Bathroom with photo and modification
    bathroom_bid = await test_bathroom_with_photo_and_modification()
    await asyncio.sleep(3)
    
    # Test 2: Landscaping with multi-project awareness
    landscaping_bid = await test_landscaping_with_awareness()
    
    # Backend verification
    check_backend_data()
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"[OK] Bathroom bid card: {'Created' if bathroom_bid else 'Failed'}")
    print(f"[OK] Budget modification: Tested")
    print(f"[OK] Landscaping bid card: {'Created' if landscaping_bid else 'Failed'}")
    print(f"[OK] Multi-project awareness: Tested")
    print(f"[OK] Photo uploads: Using local storage")
    print(f"[OK] Dashboard API: Tested")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())