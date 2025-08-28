#!/usr/bin/env python3
"""
DIRECT AGENT TEST - ABSOLUTE TRUTH
Tests the intelligent messaging agent directly to isolate what works
"""

import asyncio
import base64
from datetime import datetime
from agents.intelligent_messaging_agent import process_intelligent_message, MessageType

def create_real_pdf():
    """Create a real PDF with contact information"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        import io
        
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Add content with contact information
        p.drawString(100, height - 100, f"DIRECT AGENT TEST - {timestamp}")
        p.drawString(100, height - 150, "BID SUBMISSION WITH CONTACT INFO")
        p.drawString(100, height - 200, "")
        p.drawString(100, height - 250, "CONTACT DETAILS:")
        p.drawString(100, height - 300, "Phone: (555) 777-8888")
        p.drawString(100, height - 350, "Email: directtest@example.com")
        p.drawString(100, height - 400, "Call me for fast response!")
        p.drawString(100, height - 450, "")
        p.drawString(100, height - 500, "Bid: $40,000 kitchen renovation")
        
        p.showPage()
        p.save()
        
        buffer.seek(0)
        pdf_bytes = buffer.getvalue()
        return base64.b64encode(pdf_bytes).decode('utf-8')
        
    except ImportError:
        return None

async def test_direct_agent_with_pdf():
    """Test agent directly with PDF attachment"""
    
    print("=== DIRECT AGENT TEST WITH PDF ===")
    
    pdf_data = create_real_pdf()
    if not pdf_data:
        print("SKIPPING: No reportlab")
        return False
        
    print(f"PDF created: {len(pdf_data)} characters")
    
    attachments = [{
        'id': 'direct-test-pdf',
        'type': 'pdf',
        'name': 'direct-test-proposal.pdf',
        'data': pdf_data
    }]
    
    bid_data = {
        "amount": 40000.0,
        "timeline": "2025-02-15 to 2025-03-30",
        "proposal": "Complete kitchen renovation with premium finishes",
        "approach": "Professional installation with minimal disruption",
        "warranty_details": "2 year warranty on all work"
    }
    
    print("Calling intelligent messaging agent directly...")
    
    try:
        result = await process_intelligent_message(
            content="Bid submission: $40,000 kitchen renovation with detailed PDF proposal",
            sender_type="contractor",
            sender_id="direct-test-contractor",
            bid_card_id="direct-test-bid-card",
            message_type=MessageType.BID_SUBMISSION,
            attachments=attachments,
            bid_data=bid_data
        )
        
        print("AGENT RESPONSE:")
        print(f"  Approved: {result.get('approved')}")
        print(f"  Agent Decision: {result.get('agent_decision')}")
        print(f"  Threats Detected: {result.get('threats_detected')}")
        print(f"  Confidence Score: {result.get('confidence_score')}")
        print(f"  Bid Saved: {result.get('bid_saved')}")
        print(f"  Error: {result.get('error')}")
        
        # Check for PDF analysis
        pdf_analyzed = False
        for key, value in result.items():
            if 'pdf_analysis' in key:
                pdf_analyzed = True
                print(f"  PDF Analysis: {key}")
                if isinstance(value, dict):
                    print(f"    Contact Detected: {value.get('contact_info_detected')}")
                    print(f"    Phones: {value.get('phones', [])}")
                    print(f"    Emails: {value.get('emails', [])}")
        
        contact_detected = 'contact_info' in result.get('threats_detected', [])
        
        return {
            'success': True,
            'contact_detected': contact_detected,
            'pdf_analyzed': pdf_analyzed,
            'approved': result.get('approved'),
            'bid_saved': result.get('bid_saved')
        }
        
    except Exception as e:
        print(f"AGENT ERROR: {e}")
        return {'success': False, 'error': str(e)}

async def test_direct_agent_clean():
    """Test agent with clean bid (no contact info)"""
    
    print("\n=== DIRECT AGENT TEST - CLEAN BID ===")
    
    bid_data = {
        "amount": 35000.0,
        "timeline": "2025-03-01 to 2025-04-15",
        "proposal": "Professional kitchen remodel with high-quality materials",
        "approach": "Systematic approach following best practices",
        "warranty_details": "Full warranty coverage included"
    }
    
    try:
        result = await process_intelligent_message(
            content="Professional bid submission: $35,000 kitchen remodel with 6-week timeline",
            sender_type="contractor",
            sender_id="clean-test-contractor",
            bid_card_id="clean-test-bid-card",
            message_type=MessageType.BID_SUBMISSION,
            bid_data=bid_data
        )
        
        print("CLEAN BID RESPONSE:")
        print(f"  Approved: {result.get('approved')}")
        print(f"  Agent Decision: {result.get('agent_decision')}")
        print(f"  Threats Detected: {result.get('threats_detected')}")
        print(f"  Bid Saved: {result.get('bid_saved')}")
        
        contact_detected = 'contact_info' in result.get('threats_detected', [])
        
        return {
            'success': True,
            'contact_detected': contact_detected,
            'approved': result.get('approved'),
            'bid_saved': result.get('bid_saved')
        }
        
    except Exception as e:
        print(f"CLEAN BID ERROR: {e}")
        return {'success': False, 'error': str(e)}

async def main():
    """Run direct agent tests"""
    
    print("=" * 60)
    print("DIRECT AGENT TEST - ABSOLUTE TRUTH")
    print("=" * 60)
    print("Testing intelligent messaging agent directly")
    print("This will show exactly what works and what doesn't")
    print()
    
    # Test with PDF attachment
    pdf_result = await test_direct_agent_with_pdf()
    
    # Test clean submission
    clean_result = await test_direct_agent_clean()
    
    print("\n" + "=" * 60)
    print("DIRECT TEST RESULTS - FACTS ONLY")
    print("=" * 60)
    
    if pdf_result['success']:
        print("PDF TEST: SUCCESS")
        print(f"  Contact detected: {pdf_result['contact_detected']}")
        print(f"  PDF analyzed: {pdf_result['pdf_analyzed']}")
        print(f"  Bid approved: {pdf_result['approved']}")
        print(f"  Bid saved: {pdf_result['bid_saved']}")
    else:
        print("PDF TEST: FAILED")
        print(f"  Error: {pdf_result.get('error')}")
        
    if clean_result['success']:
        print("CLEAN TEST: SUCCESS")
        print(f"  Contact detected: {clean_result['contact_detected']}")
        print(f"  Bid approved: {clean_result['approved']}")
        print(f"  Bid saved: {clean_result['bid_saved']}")
    else:
        print("CLEAN TEST: FAILED")
        print(f"  Error: {clean_result.get('error')}")
    
    # Overall assessment
    pdf_working = (pdf_result['success'] and pdf_result['contact_detected'] 
                   and not pdf_result['approved'])
    clean_working = (clean_result['success'] and not clean_result['contact_detected'] 
                     and clean_result['approved'])
    
    print(f"\nOVERALL ASSESSMENT:")
    print(f"PDF Analysis Working: {pdf_working}")
    print(f"Clean Processing Working: {clean_working}")
    
    if pdf_working and clean_working:
        print("\nRESULT: CORE AGENT FUNCTIONALITY WORKS")
        print("- PDF contact detection: WORKING")
        print("- Clean bid approval: WORKING") 
        print("- Integration issues may exist in API layer")
    else:
        print("\nRESULT: CORE AGENT HAS PROBLEMS")
        
    return pdf_working and clean_working

if __name__ == "__main__":
    success = asyncio.run(main())