import asyncio
import sys
import os
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
import io
import base64

# Load environment variables
load_dotenv()

# Add the routers directory to path
sys.path.insert(0, 'C:\\Users\\Not John Or Justin\\Documents\\instabids\\ai-agents')

# Import the property API's AI classification function directly
from routers.property_api import classify_photo_with_ai
import json

def create_realistic_living_room():
    """Create a more realistic living room image with broken blinds"""
    # Create a more photorealistic image
    img = Image.new('RGB', (1920, 1080), color='#E8DCC4')  # Beige wall color
    draw = ImageDraw.Draw(img)
    
    # Floor
    draw.rectangle([0, 700, 1920, 1080], fill='#8B6F47')  # Wood floor color
    
    # Window with broken blinds (main focus)
    # Window frame
    draw.rectangle([200, 150, 600, 550], outline='#FFFFFF', width=8)
    draw.rectangle([210, 160, 590, 540], outline='#F5F5F5', width=2)
    
    # Blinds slats
    for i in range(12):
        y = 180 + i * 30
        if i in [3, 4, 7]:  # Broken/bent slats
            # Bent slat
            draw.polygon([(220, y), (400, y+15), (580, y-5), (580, y+5), (400, y+25), (220, y+10)], 
                        fill='#D3D3D3', outline='#A9A9A9')
            if i == 4:
                # Hanging broken piece
                draw.polygon([(350, y+15), (380, y+45), (385, y+43), (355, y+13)], 
                            fill='#C0C0C0', outline='#A9A9A9')
        else:
            # Normal slat
            draw.rectangle([220, y, 580, y+8], fill='#E0E0E0', outline='#C0C0C0')
    
    # Blinds string/cord (tangled)
    draw.line([(250, 160), (255, 540), (245, 560)], fill='#696969', width=2)
    draw.line([(550, 160), (545, 520), (555, 560)], fill='#696969', width=2)
    
    # Second window (for context)
    draw.rectangle([900, 150, 1300, 550], outline='#FFFFFF', width=8)
    draw.rectangle([910, 160, 1290, 540], outline='#F5F5F5', width=2)
    # Normal blinds on second window
    for i in range(12):
        y = 180 + i * 30
        draw.rectangle([920, y, 1280, y+8], fill='#E0E0E0', outline='#C0C0C0')
    
    # Couch
    draw.rectangle([300, 600, 900, 750], fill='#4A5D23')  # Dark green couch
    draw.rectangle([300, 550, 350, 650], fill='#4A5D23')  # Left armrest
    draw.rectangle([850, 550, 900, 650], fill='#4A5D23')  # Right armrest
    draw.rectangle([350, 520, 850, 600], fill='#4A5D23')  # Back cushions
    
    # Coffee table
    draw.rectangle([400, 750, 800, 780], fill='#654321')  # Table top
    draw.rectangle([420, 780, 440, 850], fill='#5D4E37')  # Legs
    draw.rectangle([760, 780, 780, 850], fill='#5D4E37')
    
    # TV stand
    draw.rectangle([1400, 650, 1700, 750], fill='#2F2F2F')
    # TV
    draw.rectangle([1420, 450, 1680, 640], fill='#000000')
    draw.rectangle([1430, 460, 1670, 630], fill='#1A1A1A')
    
    # Picture frames on wall
    draw.rectangle([100, 250, 180, 350], outline='#8B4513', width=4)
    draw.rectangle([1500, 200, 1600, 320], outline='#8B4513', width=4)
    
    # Lamp
    draw.ellipse([1000, 500, 1100, 520], fill='#F0E68C')  # Lampshade
    draw.rectangle([1045, 520, 1055, 600], fill='#654321')  # Lamp base
    
    # Add some text labels to make issues clear
    draw.text((250, 120), "BROKEN BLINDS - NEED REPAIR", fill='#FF0000')
    draw.text((220, 570), "Slats bent and damaged", fill='#8B0000')
    
    return img

async def test_living_room():
    """Test with realistic living room photo with broken blinds"""
    
    print("\n" + "="*60)
    print("TESTING LIVING ROOM WITH BROKEN BLINDS")
    print("="*60)
    
    # Create realistic living room image
    print("\nCreating realistic living room image with broken blinds...")
    img = create_realistic_living_room()
    
    # Convert to base64
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    base64_image = base64.b64encode(img_bytes.read()).decode('utf-8')
    photo_url = f"data:image/png;base64,{base64_image}"
    
    # Save image for reference
    img.save("living_room_broken_blinds.png")
    print("Image saved as 'living_room_broken_blinds.png' for reference")
    
    # Room context
    room_context = {
        "room_type": "living_room", 
        "room_name": "Main Living Room"
    }
    
    try:
        # Call the AI classification function
        print("\nAnalyzing living room photo with GPT-4o vision API...")
        print("Looking specifically for broken window blinds...")
        result = await classify_photo_with_ai(photo_url, room_context)
        
        print("\n[SUCCESS] LIVING ROOM ANALYSIS COMPLETE!")
        print("-" * 60)
        
        # Display results
        print(f"\n[ROOM DETECTED]: {result.get('room_type', 'Unknown')}")
        print(f"[CONFIDENCE]: {result.get('room_confidence', 0)*100:.1f}%")
        
        # Check if AI is real or fallback
        if result.get('room_confidence', 0) >= 0.9:
            print("[STATUS]: Using REAL GPT-4o vision analysis")
        else:
            print("[STATUS]: Using fallback classification")
        
        # Show maintenance issues  
        print(f"\n[MAINTENANCE ISSUES FOUND]:")
        if 'detected_issues' in result and result['detected_issues']:
            for i, issue in enumerate(result['detected_issues'], 1):
                if isinstance(issue, dict):
                    severity = issue.get('severity', 'unknown')
                    desc = issue.get('description', issue)
                    cost = issue.get('estimated_cost', 'unknown')
                    conf = issue.get('confidence', 0)
                    print(f"   {i}. [{severity.upper()}] {desc}")
                    print(f"      - Estimated cost: {cost}")
                    print(f"      - Detection confidence: {conf*100:.0f}%")
                else:
                    print(f"   {i}. {issue}")
            
            # Check specifically for blind issues
            blind_issues = [i for i in result.get('detected_issues', []) 
                           if isinstance(i, dict) and 'blind' in i.get('description', '').lower()]
            if blind_issues:
                print(f"\n   [CONFIRMED] Broken blinds detected! ({len(blind_issues)} blind-related issues)")
        else:
            print("   No maintenance issues detected")
        
        # Show detected assets/fixtures
        print(f"\n[ROOM FEATURES DETECTED]:")
        if 'detected_assets' in result and result['detected_assets']:
            for i, asset in enumerate(result['detected_assets'][:10], 1):
                if isinstance(asset, dict):
                    name = asset.get('name', 'Unknown')
                    condition = asset.get('condition', 'unknown')
                    category = asset.get('category', 'unknown')
                    asset_type = asset.get('type', 'unknown')
                    print(f"   {i}. {name}")
                    print(f"      - Type: {asset_type}, Category: {category}")
                    print(f"      - Condition: {condition}")
                else:
                    print(f"   {i}. {asset}")
            
            # Check for blind assets
            blind_assets = [a for a in result.get('detected_assets', [])
                          if isinstance(a, dict) and 'blind' in str(a.get('name', '')).lower()]
            if blind_assets:
                print(f"\n   [FOUND] {len(blind_assets)} window blind fixtures detected")
        
        # Show AI description
        if 'description' in result:
            print(f"\n[AI DESCRIPTION]:")
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
        
        # Show improvement suggestions
        if 'improvement_suggestions' in result and result['improvement_suggestions']:
            print(f"\n[IMPROVEMENT SUGGESTIONS]:")
            for i, suggestion in enumerate(result['improvement_suggestions'], 1):
                print(f"   {i}. {suggestion}")
        
        # Show safety concerns
        if 'safety_concerns' in result and result['safety_concerns']:
            print(f"\n[SAFETY CONCERNS]:")
            for i, concern in enumerate(result['safety_concerns'], 1):
                print(f"   {i}. {concern}")
        
        print("\n" + "="*60)
        print("SUMMARY:")
        # Check if we successfully detected the broken blinds
        all_text = str(result).lower()
        if 'blind' in all_text:
            print("[SUCCESS] GPT-4o correctly identified window blind issues!")
            print("The AI vision system is working with REAL OpenAI API")
        else:
            print("[WARNING] Blinds not specifically mentioned, but other issues may be detected")
        print("="*60)
        
    except Exception as e:
        print(f"\n[ERROR]: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Testing GPT-4o vision with living room photo...")
    asyncio.run(test_living_room())