#!/usr/bin/env python3
"""Test IRIS with actual user account"""

import requests
import json
import base64

def test_iris_repair():
    """Test IRIS repair detection with real user"""
    
    # Your actual user ID  
    user_id = "01087874-747b-4159-8735-5ebb8715ff84"
    
    # Create a small test image (1x1 pixel PNG)
    test_image_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    
    # Test payload - this should trigger repair detection
    payload = {
        "user_id": user_id,
        "session_id": "test-session-real-user",
        "message": "URGENT: My roof has major storm damage and is leaking badly. Need repair immediately!",
        "images": [{
            "filename": "roof_damage.png",
            "data": test_image_data
        }],
        "board_room_type": "roof"  # Explicitly set room type
    }
    
    print("🧪 Testing IRIS repair detection with your account...")
    print(f"User ID: {user_id}")
    print(f"Message: {payload['message']}")
    
    try:
        response = requests.post(
            "http://localhost:8008/api/iris/unified-chat",
            json=payload,
            timeout=30
        )
        
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result.get('success')}")
            print(f"📝 Response: {result.get('response', '')[:200]}...")
            print(f"🖼️  Images processed: {result.get('images_processed', 0)}")
            
            # Check image analysis
            image_analysis = result.get('image_analysis', {})
            if image_analysis:
                print(f"🔧 Repair needed: {image_analysis.get('repair_needed')}")
                print(f"⚡ Urgency: {image_analysis.get('urgency_level')}")
                print(f"🏠 Room: {image_analysis.get('room_type')}")
                print(f"📊 Issues detected: {image_analysis.get('detected_issues_count', 0)}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def verify_data_created():
    """Verify photos and repair cards were created"""
    
    user_id = "01087874-747b-4159-8735-5ebb8715ff84"
    
    print("\n🔍 Verifying data was created...")
    
    # Check for new repair-type photos
    try:
        import sys
        sys.path.append('/app')
        from database import db
        
        # Check for repair photos
        photos = db.client.table('property_photos').select('*').eq('photo_type', 'repair').execute()
        repair_photos = [p for p in photos.data if p.get('ai_classification', {}).get('session') == 'test-session-real-user'] if photos.data else []
        print(f"📸 Repair photos found: {len(repair_photos)}")
        
        # Check for potential bid cards
        cards = db.client.table('potential_bid_cards').select('*').eq('user_id', user_id).execute()
        print(f"🔧 Potential bid cards: {len(cards.data) if cards.data else 0}")
        
        if cards.data:
            for card in cards.data:
                print(f"  - {card['title']}: {card['urgency_level']}")
                
    except Exception as e:
        print(f"❌ Verification failed: {e}")

if __name__ == "__main__":
    test_iris_repair()
    verify_data_created()