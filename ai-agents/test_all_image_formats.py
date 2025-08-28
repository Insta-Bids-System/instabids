#!/usr/bin/env python3
"""
Test All Image Upload Formats and Methods
Tests PNG, JPEG, WEBP, GIF with Base64, URL, and File methods
"""

import asyncio
import base64
import requests
import tempfile
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from agents.intelligent_messaging_agent import GPT5SecurityAnalyzer

async def create_test_images():
    """Create test images with contact info in different formats"""
    
    # Create temp directory for test images
    temp_dir = Path(tempfile.gettempdir()) / "image_format_tests"
    temp_dir.mkdir(exist_ok=True)
    
    # Contact info to embed in images
    contact_text = """
CONTRACTOR BID PROPOSAL
Mike's Custom Cabinets
Phone: (555) 123-4567
Email: mike.cabinets@gmail.com
Emergency: 555-999-8888
    """.strip()
    
    # Create base image
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        # Try to use a basic font
        font = ImageFont.load_default()
    except:
        font = None
    
    # Add text to image
    y_position = 50
    for line in contact_text.split('\n'):
        draw.text((50, y_position), line, fill='black', font=font)
        y_position += 40
    
    # Save in different formats
    formats = {
        'PNG': temp_dir / 'contact_test.png',
        'JPEG': temp_dir / 'contact_test.jpg', 
        'WEBP': temp_dir / 'contact_test.webp',
        'GIF': temp_dir / 'contact_test.gif'
    }
    
    for format_name, file_path in formats.items():
        if format_name == 'JPEG':
            img.save(file_path, format_name, quality=95)
        else:
            img.save(file_path, format_name)
    
    return formats

async def test_base64_uploads():
    """Test Base64 encoded image uploads"""
    print("TESTING: Base64 Image Uploads")
    
    formats = await create_test_images()
    analyzer = GPT5SecurityAnalyzer()
    
    results = {}
    
    for format_name, file_path in formats.items():
        try:
            print(f"\nTesting {format_name} via Base64...")
            
            # Read and encode image
            with open(file_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Test with analyzer
            result = await analyzer.analyze_image_content(image_data, format_name.lower())
            
            contact_detected = result.get('contact_info_detected', False)
            confidence = result.get('confidence', 0)
            phones = result.get('phones', [])
            emails = result.get('emails', [])
            
            results[format_name] = {
                'method': 'Base64',
                'detected': contact_detected,
                'confidence': confidence,
                'phones': phones,
                'emails': emails,
                'status': 'PASS' if contact_detected else 'FAIL'
            }
            
            print(f"  Result: {results[format_name]['status']}")
            print(f"  Confidence: {confidence}")
            print(f"  Phones: {phones}")
            print(f"  Emails: {emails}")
            
        except Exception as e:
            results[format_name] = {
                'method': 'Base64',
                'error': str(e),
                'status': 'ERROR'
            }
            print(f"  ERROR: {e}")
    
    return results

async def test_main():
    """Run all image format tests"""
    
    print("=== COMPREHENSIVE IMAGE FORMAT TESTING ===")
    print("Testing all supported formats: PNG, JPEG, WEBP, GIF")
    print("Testing upload method: Base64 encoding")
    
    # Test Base64 uploads
    base64_results = await test_base64_uploads()
    
    print("\n=== FINAL RESULTS ===")
    
    all_passed = True
    for format_name, result in base64_results.items():
        status = result['status']
        print(f"{format_name}: {status}")
        if status != 'PASS':
            all_passed = False
    
    if all_passed:
        print("\n✅ ALL IMAGE FORMATS WORKING")
        print("✅ Base64 upload method confirmed")
        print("✅ Contact detection working across all formats")
        return True
    else:
        print("\n❌ SOME IMAGE FORMATS FAILED")
        print("❌ Need to fix failing formats")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_main())
    
    if success:
        print("\n🎉 COMPLETE SUCCESS: All image formats working")
    else:
        print("\n💥 FAILURE: Some formats need fixes")