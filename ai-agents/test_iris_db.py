#!/usr/bin/env python3
"""Test IRIS database operations"""

import sys
import os
sys.path.append('/app')
os.chdir('/app')

from agents.iris.services.photo_manager import PhotoManager
from agents.iris.workflows.image_workflow import ImageWorkflow
from datetime import datetime
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_iris_database():
    """Test IRIS database operations"""
    
    # Test photo storage
    pm = PhotoManager()
    print('Testing photo storage...')
    
    # Test user ID - must be a valid UUID
    user_id = 'bf612f23-e74f-4e87-88ed-2bb458c47843'  # Valid UUID format
    
    # Test property photo storage
    try:
        photo_id = pm.store_to_property_photos(
            user_id=user_id,
            image_data='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=',
            filename='test_roof.png',
            session_id='debug-session',
            room_type='roof',
            tags=['repair', 'roof', 'emergency']
        )
        print(f'✅ Photo storage result: {photo_id}')
    except Exception as e:
        print(f'❌ Photo storage error: {e}')
        import traceback
        traceback.print_exc()
    
    # Test repair item creation
    try:
        from database import db
        
        # Check if potential_bid_cards table exists
        tables = db.client.table('potential_bid_cards').select('id').limit(1).execute()
        print(f'✅ Potential bid cards table accessible: {bool(tables.data is not None)}')
        
        # Try to create a potential bid card with all required fields
        new_bid_card = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'project_type': 'repair',
            'title': 'Roof repair needed',
            'project_description': 'Emergency roof repair from storm damage',
            'room_location': 'roof',
            'urgency_level': 'emergency',
            'primary_trade': 'roofing',  # Required field
            'status': 'draft',
            'created_by': 'iris_agent',
            'created_at': datetime.now().isoformat()
        }
        
        result = db.client.table('potential_bid_cards').insert(new_bid_card).execute()
        if result.data:
            print(f'✅ Repair card created: {result.data[0]["id"]}')
        else:
            print('❌ Failed to create repair card - no data returned')
            
    except Exception as e:
        print(f'❌ Repair card creation error: {e}')
        import traceback
        traceback.print_exc()
    
    # Now query to verify
    print("\nVerifying database entries...")
    try:
        from database import db
        
        # Check properties
        prop_result = db.client.table('properties').select('*').eq('user_id', user_id).execute()
        print(f"Properties for user: {len(prop_result.data) if prop_result.data else 0}")
        
        # Check potential_bid_cards
        cards_result = db.client.table('potential_bid_cards').select('*').eq('user_id', user_id).execute()
        print(f"Potential bid cards for user: {len(cards_result.data) if cards_result.data else 0}")
        
        if cards_result.data:
            for card in cards_result.data:
                print(f"  - {card['title']}: {card['urgency_level']}")
                
    except Exception as e:
        print(f"❌ Verification error: {e}")

if __name__ == "__main__":
    test_iris_database()