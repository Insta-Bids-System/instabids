import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the routers directory to path
sys.path.insert(0, 'C:\\Users\\Not John Or Justin\\Documents\\instabids\\ai-agents')

# Import the property API's AI classification function directly
from routers.property_api import classify_photo_with_ai
import json

async def test_real_photo():
    """Test with user's actual WhatsApp photo"""
    
    print("\n" + "="*60)
    print("TESTING WITH REAL WHATSAPP PHOTO")
    print("="*60)
    
    # User's actual WhatsApp photo path
    photo_path = "C:\\Users\\Not John Or Justin\\Downloads\\WhatsApp Image 2024-11-18 at 09.50.45_4e948e8f.jpg"
    
    # Check if file exists
    if not os.path.exists(photo_path):
        print(f"\n[ERROR] Photo not found at: {photo_path}")
        print("Please ensure the WhatsApp photo is in the Downloads folder")
        return
    
    # Convert to base64 data URL
    import base64
    with open(photo_path, 'rb') as f:
        image_data = f.read()
        base64_image = base64.b64encode(image_data).decode('utf-8')
        # Assume JPEG for WhatsApp photos
        photo_url = f"data:image/jpeg;base64,{base64_image}"
    
    # Mock room context
    room_context = {
        "room_type": "living_room",
        "room_name": "Living Room"
    }
    
    try:
        # Call the AI classification function
        print("\nAnalyzing your WhatsApp photo with GPT-4o vision API...")
        print("Looking for broken blinds and other maintenance issues...")
        result = await classify_photo_with_ai(photo_url, room_context)
        
        print("\n[SUCCESS] PHOTO ANALYSIS COMPLETE!")
        print("-" * 60)
        
        # Display results
        print(f"\n[ROOM DETECTED]: {result.get('room_type', 'Unknown')}")
        print(f"[CONFIDENCE]: {result.get('room_confidence', 0)*100:.1f}%")
        
        # Show maintenance issues  
        if 'detected_issues' in result and result['detected_issues']:
            print(f"\n[MAINTENANCE ISSUES FOUND] ({len(result['detected_issues'])}):")
            for i, issue in enumerate(result['detected_issues'], 1):
                if isinstance(issue, dict):
                    severity = issue.get('severity', 'unknown')
                    desc = issue.get('description', issue)
                    cost = issue.get('estimated_cost', 'unknown')
                    print(f"   {i}. [{severity.upper()}] {desc}")
                    print(f"      Estimated cost: {cost}")
                else:
                    print(f"   {i}. {issue}")
        else:
            print("\n[WARNING] No maintenance issues detected")
        
        # Show detected assets/fixtures
        if 'detected_assets' in result and result['detected_assets']:
            print(f"\n[ROOM FEATURES DETECTED] ({len(result['detected_assets'])}):")
            for i, asset in enumerate(result['detected_assets'][:10], 1):
                if isinstance(asset, dict):
                    name = asset.get('name', 'Unknown')
                    condition = asset.get('condition', 'unknown')
                    category = asset.get('category', 'unknown')
                    print(f"   {i}. {name} ({category}) - Condition: {condition}")
                else:
                    print(f"   {i}. {asset}")
        
        # Show AI description
        if 'description' in result:
            print(f"\n[AI DESCRIPTION]:")
            # Word wrap the description for readability
            desc = result['description']
            import textwrap
            wrapped = textwrap.wrap(desc, width=70)
            for line in wrapped:
                print(f"   {line}")
        
        # Show maintenance recommendations
        if 'maintenance_opportunities' in result and result['maintenance_opportunities']:
            print(f"\n[RECOMMENDED MAINTENANCE]:")
            for i, task in enumerate(result['maintenance_opportunities'], 1):
                print(f"   {i}. {task}")
        
        # Show safety concerns
        if 'safety_concerns' in result and result['safety_concerns']:
            print(f"\n[SAFETY CONCERNS]:")
            for i, concern in enumerate(result['safety_concerns'], 1):
                print(f"   {i}. {concern}")
        
        print("\n" + "="*60)
        print("ANALYSIS COMPLETE - REAL GPT-4O VISION API WORKING!")
        print("="*60)
        
    except Exception as e:
        print(f"\n[ERROR]: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Testing real WhatsApp photo analysis...")
    asyncio.run(test_real_photo())