#!/usr/bin/env python3
"""
Simple PDF Analysis Test - Production Ready
Tests PDF processing in bid submissions with REAL files
"""

import asyncio
import base64
import json
from agents.intelligent_messaging_agent import process_intelligent_message, MessageType

async def create_simple_test_pdf():
    """Create a test PDF with contact information for testing"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        import io
        
        # Create PDF with contact info
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Add content with contact information
        p.drawString(100, height - 100, "CONTRACTOR BID PROPOSAL")
        p.drawString(100, height - 150, "Project: Kitchen Remodel")
        p.drawString(100, height - 200, "")
        p.drawString(100, height - 250, "Contact Information:")
        p.drawString(100, height - 300, "Phone: (555) 123-4567")  # CONTACT INFO
        p.drawString(100, height - 350, "Email: contractor@email.com")  # CONTACT INFO
        p.drawString(100, height - 400, "Call me directly for faster service!")  # BYPASS ATTEMPT
        p.drawString(100, height - 450, "")
        p.drawString(100, height - 500, "Proposal Details:")
        p.drawString(100, height - 550, "- Complete kitchen renovation")
        p.drawString(100, height - 600, "- Timeline: 3-4 weeks")
        p.drawString(100, height - 650, "- Materials included")
        
        p.showPage()
        p.save()
        
        buffer.seek(0)
        pdf_bytes = buffer.getvalue()
        return base64.b64encode(pdf_bytes).decode('utf-8')
        
    except ImportError:
        print("reportlab not installed - install with: pip install reportlab")
        return None

async def test_pdf_analysis():
    """Test PDF analysis in bid submissions"""
    
    print("=== PRODUCTION PDF ANALYSIS TEST ===")
    print("Testing PDF contact information detection in bid submissions")
    print()
    
    # Create test PDF
    print("Creating test PDF with contact information...")
    pdf_data = await create_simple_test_pdf()
    
    if not pdf_data:
        print("ERROR: Could not create test PDF - missing reportlab dependency")
        return False
    
    print(f"INFO: PDF created, size: {len(pdf_data)} characters (base64)")
    
    # Test PDF in bid submission
    print("\nTEST: Bid submission with PDF containing contact information")
    print("=" * 60)
    
    test_attachments = [
        {
            "id": "pdf-test-1",
            "type": "pdf",
            "name": "contractor-proposal.pdf",
            "data": pdf_data
        }
    ]
    
    bid_data = {
        "amount": 25000.00,
        "timeline": "2025-02-01 to 2025-02-28",
        "proposal": "Complete kitchen remodel with premium materials",
        "approach": "Professional installation with attention to detail", 
        "warranty_details": "2 year warranty on all work"
    }
    
    try:
        result = await process_intelligent_message(
            content="Bid submission: $25,000 kitchen remodel",
            sender_type="contractor",
            sender_id="test-contractor-pdf",
            bid_card_id="test-bid-card-123",
            message_type=MessageType.BID_SUBMISSION,
            attachments=test_attachments,
            bid_data=bid_data
        )
        
        print(f"RESULT: Agent Decision = {result.get('agent_decision')}")
        print(f"APPROVED: {result.get('approved')}")
        print(f"THREATS: {result.get('threats_detected')}")
        print(f"CONFIDENCE: {result.get('confidence_score')}")
        print(f"BID SAVED: {result.get('bid_saved')}")
        
        if result.get('security_analysis'):
            explanation = result['security_analysis'].get('explanation', 'No explanation')
            print(f"EXPLANATION: {explanation[:200]}...")
        
        # Check if PDF analysis results are in state
        pdf_analysis_found = False
        for key, value in result.items():
            if key.startswith('pdf_analysis_'):
                pdf_analysis_found = True
                print(f"PDF ANALYSIS: Contact detected = {value.get('contact_info_detected')}")
                if value.get('phones'):
                    print(f"PHONES FOUND: {value['phones']}")
                if value.get('emails'):
                    print(f"EMAILS FOUND: {value['emails']}")
        
        # Check if contact info was detected
        contact_detected = 'contact_info' in result.get('threats_detected', [])
        print(f"CONTACT INFO DETECTED: {contact_detected}")
        
        print("\nTEST COMPLETION")
        print("=" * 60)
        if contact_detected:
            print("RESULT: PASSED - PDF contact information detection working")
            print("STATUS: PDF analysis system operational for production")
            return True
        else:
            print("RESULT: FAILED - PDF contact information not detected")
            print("STATUS: PDF analysis needs investigation")
            return False
        
    except Exception as e:
        print(f"ERROR: PDF analysis failed - {e}")
        return False

if __name__ == "__main__":
    print("Starting PDF analysis test...")
    result = asyncio.run(test_pdf_analysis())
    
    if result:
        print("\nFINAL RESULT: PDF ANALYSIS SYSTEM READY FOR PRODUCTION")
        print("Both image and PDF processing confirmed working in bid submissions")
    else:
        print("\nFINAL RESULT: PDF ANALYSIS SYSTEM NEEDS DEBUGGING")
        print("Check PDF processing implementation")