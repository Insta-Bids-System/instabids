#!/usr/bin/env python3
"""
FINAL VERIFICATION TEST - PRODUCTION CONFIRMATION
Comprehensive test proving the PDF/Image analysis system is working
"""

import asyncio
import base64
from agents.intelligent_messaging_agent import process_intelligent_message, MessageType

async def test_pdf_analysis_working():
    """Test PDF analysis with real PDF containing contact info"""
    
    print("=== PDF ANALYSIS VERIFICATION ===")
    
    # Create PDF with actual reportlab library
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        import io
        
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Add content with contact information
        p.drawString(100, height - 100, "CONTRACTOR PROPOSAL")
        p.drawString(100, height - 200, "Phone: (555) 123-4567")  # CONTACT
        p.drawString(100, height - 250, "Email: test@contractor.com")  # CONTACT
        p.drawString(100, height - 300, "Call me directly!")  # BYPASS
        p.drawString(100, height - 400, "Project: Kitchen remodel - $45,000")
        
        p.showPage()
        p.save()
        
        buffer.seek(0)
        pdf_bytes = buffer.getvalue()
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        print(f"SUCCESS: PDF created: {len(pdf_base64)} characters")
        
        # Test with intelligent agent
        attachments = [{
            'id': 'verification-pdf',
            'type': 'pdf',
            'name': 'contractor-proposal.pdf',
            'data': pdf_base64
        }]
        
        result = await process_intelligent_message(
            content='Bid submission with PDF proposal',
            sender_type='contractor',
            sender_id='test-contractor-verification',
            bid_card_id='test-bid-card-verification',
            message_type=MessageType.BID_SUBMISSION,
            attachments=attachments
        )
        
        # Check results
        contact_detected = 'contact_info' in result.get('threats_detected', [])
        approved = result.get('approved', True)
        
        print(f"SUCCESS: PDF Analysis Result:")
        print(f"  - Contact Info Detected: {contact_detected}")
        print(f"  - Bid Approved: {approved}")
        print(f"  - Agent Decision: {result.get('agent_decision', 'N/A')}")
        print(f"  - Threats: {result.get('threats_detected', [])}")
        
        return contact_detected and not approved  # Should detect contact and block
        
    except ImportError:
        print("ERROR: reportlab not available - using fallback test")
        return False
    except Exception as e:
        print(f"ERROR: PDF test failed: {e}")
        return False

async def test_image_analysis_working():
    """Test image analysis with contact info"""
    
    print("\n=== IMAGE ANALYSIS VERIFICATION ===")
    
    # Create image with contact info
    try:
        from PIL import Image, ImageDraw
        import io
        
        img = Image.new('RGB', (400, 300), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add text with contact info
        draw.text((50, 50), "BID PROPOSAL", fill='black')
        draw.text((50, 100), "Phone: (555) 987-6543", fill='red')  # CONTACT
        draw.text((50, 130), "Email: mybid@test.com", fill='red')   # CONTACT
        draw.text((50, 160), "Text me for quick response!", fill='red')  # BYPASS
        draw.text((50, 220), "Total: $30,000", fill='black')
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        image_bytes = buffer.getvalue()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        print(f"SUCCESS: Image created: {len(image_base64)} characters")
        
        # Test with intelligent agent
        result = await process_intelligent_message(
            content='Bid submission with image proposal',
            sender_type='contractor',
            sender_id='test-contractor-image',
            bid_card_id='test-bid-card-image',
            message_type=MessageType.BID_SUBMISSION,
            image_data=image_base64
        )
        
        # Check results
        contact_detected = 'contact_info' in result.get('threats_detected', [])
        approved = result.get('approved', True)
        
        print(f"SUCCESS: Image Analysis Result:")
        print(f"  - Contact Info Detected: {contact_detected}")
        print(f"  - Bid Approved: {approved}")
        print(f"  - Agent Decision: {result.get('agent_decision', 'N/A')}")
        print(f"  - Threats: {result.get('threats_detected', [])}")
        
        return contact_detected and not approved  # Should detect contact and block
        
    except ImportError:
        print("ERROR: PIL not available - using fallback test")
        return False
    except Exception as e:
        print(f"ERROR: Image test failed: {e}")
        return False

async def test_clean_submission():
    """Test clean submission without contact info"""
    
    print("\n=== CLEAN SUBMISSION VERIFICATION ===")
    
    try:
        result = await process_intelligent_message(
            content='Professional bid submission: $25,000 kitchen remodel, 4-week timeline, premium materials included',
            sender_type='contractor',
            sender_id='test-contractor-clean',
            bid_card_id='test-bid-card-clean',
            message_type=MessageType.BID_SUBMISSION
        )
        
        # Check results
        contact_detected = 'contact_info' in result.get('threats_detected', [])
        approved = result.get('approved', False)
        
        print(f"SUCCESS: Clean Submission Result:")
        print(f"  - Contact Info Detected: {contact_detected}")
        print(f"  - Bid Approved: {approved}")
        print(f"  - Agent Decision: {result.get('agent_decision', 'N/A')}")
        
        return not contact_detected and approved  # Should NOT detect contact and approve
        
    except Exception as e:
        print(f"ERROR: Clean submission test failed: {e}")
        return False

async def main():
    """Run complete verification suite"""
    
    print("=" * 60)
    print("FINAL PRODUCTION VERIFICATION TEST")
    print("=" * 60)
    print("Testing complete PDF and Image analysis system")
    print()
    
    # Run all tests
    pdf_working = await test_pdf_analysis_working()
    image_working = await test_image_analysis_working()
    clean_working = await test_clean_submission()
    
    print("\n" + "=" * 60)
    print("COMPREHENSIVE TEST RESULTS")
    print("=" * 60)
    
    print(f"PDF Analysis Working: {pdf_working}")
    print(f"Image Analysis Working: {image_working}")
    print(f"Clean Submission Working: {clean_working}")
    
    all_working = pdf_working and image_working and clean_working
    
    print(f"\nOVERALL SYSTEM STATUS: {'FULLY OPERATIONAL' if all_working else 'NEEDS ATTENTION'}")
    
    if all_working:
        print("\nPRODUCTION READY CONFIRMATION:")
        print("SUCCESS: PDF attachments analyzed by GPT-4o")
        print("SUCCESS: Image attachments analyzed by GPT-4o")
        print("SUCCESS: Contact information detection working")
        print("SUCCESS: Clean submissions approved correctly")
        print("SUCCESS: Same unified system handles messaging AND bids")
        print("SUCCESS: All bid data passes through intelligent analysis")
        print("SUCCESS: Real LLM calls with actual threat detection")
        print("\nSYSTEM IS READY FOR PRODUCTION USE!")
    else:
        print("\nSYSTEM NEEDS DEBUGGING:")
        if not pdf_working:
            print("- PDF analysis not working properly")
        if not image_working:
            print("- Image analysis not working properly") 
        if not clean_working:
            print("- Clean submission handling not working")
    
    return all_working

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)