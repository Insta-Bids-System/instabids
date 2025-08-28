#!/usr/bin/env python3
"""
REAL BACKEND PDF SUBMISSION TEST
Tests actual bid submission with PDF against live backend and database
"""

import asyncio
import base64
import json
import requests
from datetime import datetime
import database_simple
from config.service_urls import get_backend_url

async def create_test_pdf_with_contact():
    """Create a test PDF with contact information"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        import io
        
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Add content with OBVIOUS contact information
        p.drawString(100, height - 100, "CONTRACTOR BID PROPOSAL - REAL TEST")
        p.drawString(100, height - 150, f"Generated: {datetime.now()}")
        p.drawString(100, height - 200, "Project: Kitchen Remodel")
        p.drawString(100, height - 250, "")
        p.drawString(100, height - 300, "CONTACT INFORMATION:")
        p.drawString(100, height - 350, "Phone: (555) 999-8888")  # OBVIOUS CONTACT
        p.drawString(100, height - 400, "Email: testcontractor@realtest.com")  # OBVIOUS CONTACT  
        p.drawString(100, height - 450, "Text me for immediate response!")  # BYPASS ATTEMPT
        p.drawString(100, height - 500, "")
        p.drawString(100, height - 550, "Proposal: $45,000 total project cost")
        p.drawString(100, height - 600, "Timeline: 6 weeks completion")
        p.drawString(100, height - 650, "Warranty: 3 years full warranty")
        
        p.showPage()
        p.save()
        
        buffer.seek(0)
        pdf_bytes = buffer.getvalue()
        return base64.b64encode(pdf_bytes).decode('utf-8')
        
    except ImportError:
        print("ERROR: reportlab not available")
        return None

def test_backend_api_call():
    """Test the actual backend API with PDF attachment"""
    
    print("=== REAL BACKEND API TEST ===")
    print("Testing actual bid submission API with PDF attachment")
    print()
    
    # Create test PDF
    print("1. Creating test PDF with contact information...")
    pdf_data = asyncio.run(create_test_pdf_with_contact())
    
    if not pdf_data:
        print("ERROR: Could not create PDF")
        return False
    
    print(f"   PDF created: {len(pdf_data)} characters")
    
    # Prepare bid submission data
    print("2. Preparing bid submission with PDF attachment...")
    
    bid_data = {
        "project_type": "Kitchen remodel", 
        "project_description": "Complete kitchen renovation with premium materials",
        "location_city": "Test City",
        "location_state": "TX", 
        "budget_min": 40000.0,
        "budget_max": 50000.0,
        "timeline": "6 weeks",
        "user_id": "test-homeowner-real",
        
        # Bid submission details
        "contractor_id": "test-contractor-pdf-real",
        "amount": 45000.0,
        "proposal": "Complete kitchen remodel as specified with premium materials and professional installation",
        "approach": "Systematic approach with minimal disruption to household routine",
        "warranty_details": "3-year comprehensive warranty on all materials and workmanship",
        "timeline": "6 weeks from start to completion",
        
        # PDF attachment
        "attachments": [
            {
                "id": "real-pdf-test",
                "type": "pdf", 
                "name": "contractor-real-proposal.pdf",
                "data": pdf_data
            }
        ]
    }
    
    print("3. Submitting bid via REAL backend API...")
    print(f"   API Endpoint: http://localhost:8008/api/bid-cards/submit-bid")
    
    try:
        # Make actual API call to backend
        response = requests.post(
            f"{get_backend_url()}/api/bid-cards/submit-bid",
            json=bid_data,
            timeout=120  # 2 minutes timeout for GPT-4o processing
        )
        
        print(f"   HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("   SUCCESS: Bid submission accepted by backend")
            
            # Check intelligent agent results
            print("\n4. INTELLIGENT AGENT ANALYSIS RESULTS:")
            print(f"   Agent Decision: {result.get('agent_decision', 'N/A')}")
            print(f"   Approved: {result.get('approved', 'N/A')}")
            print(f"   Threats Detected: {result.get('threats_detected', [])}")
            print(f"   Confidence Score: {result.get('confidence_score', 'N/A')}")
            print(f"   Bid Saved: {result.get('bid_saved', 'N/A')}")
            
            # Check for PDF analysis
            pdf_analyzed = False
            for key, value in result.items():
                if 'pdf' in key.lower() and 'analysis' in key.lower():
                    pdf_analyzed = True
                    print(f"   PDF Analysis Found: {key}")
                    if isinstance(value, dict):
                        print(f"     Contact Detected: {value.get('contact_info_detected', 'N/A')}")
                        if value.get('phones'):
                            print(f"     Phones Found: {value['phones']}")
                        if value.get('emails'):
                            print(f"     Emails Found: {value['emails']}")
            
            if not pdf_analyzed:
                print("   WARNING: No PDF analysis results found in response")
            
            # Check if contact info was detected
            contact_detected = 'contact_info' in result.get('threats_detected', [])
            print(f"   CONTACT INFO DETECTED: {contact_detected}")
            
            return {
                'success': True,
                'contact_detected': contact_detected,
                'pdf_analyzed': pdf_analyzed,
                'bid_card_id': result.get('bid_card_id'),
                'full_result': result
            }
            
        else:
            print(f"   ERROR: API call failed")
            print(f"   Response: {response.text}")
            return {'success': False, 'error': response.text}
            
    except Exception as e:
        print(f"   ERROR: Exception during API call - {e}")
        return {'success': False, 'error': str(e)}

async def check_database_storage(bid_card_id):
    """Check if the bid and PDF data was actually saved to database"""
    
    print("\n=== DATABASE VERIFICATION ===")
    print("Checking if bid and PDF data was saved to Supabase database")
    
    try:
        db = database_simple.get_client()
        
        # Check if bid card was created/updated
        print("1. Checking bid_cards table...")
        bid_result = db.table("bid_cards").select("*").eq("id", bid_card_id).execute()
        
        if bid_result.data:
            bid_card = bid_result.data[0]
            print(f"   ✅ Bid card found: {bid_card_id}")
            print(f"   Status: {bid_card.get('status', 'N/A')}")
            print(f"   Bids received: {bid_card.get('bid_document', {}).get('bids_received_count', 0)}")
            
            # Check for submitted bids in bid_document
            submitted_bids = bid_card.get('bid_document', {}).get('submitted_bids', [])
            print(f"   Submitted bids count: {len(submitted_bids)}")
            
            if submitted_bids:
                latest_bid = submitted_bids[-1]
                print(f"   Latest bid amount: ${latest_bid.get('bid_amount', 'N/A')}")
                print(f"   Latest bid contractor: {latest_bid.get('contractor_id', 'N/A')}")
        else:
            print(f"   ❌ Bid card NOT found: {bid_card_id}")
            return False
        
        # Check unified_messages table for intelligent agent processing
        print("2. Checking unified_messages table...")
        messages_result = db.table("unified_messages").select("*").eq(
            "sender_id", "test-contractor-pdf-real"
        ).order("created_at", desc=True).limit(1).execute()
        
        if messages_result.data:
            message = messages_result.data[0]
            print(f"   ✅ Intelligent agent message found")
            print(f"   Message type: {message.get('message_type', 'N/A')}")
            print(f"   Agent decision: {message.get('metadata', {}).get('agent_decision', 'N/A')}")
            print(f"   Threats detected: {message.get('metadata', {}).get('threats_detected', [])}")
            
            # Check for attachment data
            attachments = message.get('metadata', {}).get('attachments', [])
            print(f"   Attachments stored: {len(attachments)}")
            
            for i, attachment in enumerate(attachments):
                print(f"     Attachment {i+1}: {attachment.get('name', 'N/A')} ({attachment.get('type', 'N/A')})")
                if attachment.get('type') == 'pdf':
                    print(f"       PDF data size: {len(attachment.get('data', ''))} characters")
        else:
            print(f"   ❌ No intelligent agent message found")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ERROR: Database check failed - {e}")
        return False

def main():
    """Run complete real backend test"""
    
    print("STARTING COMPREHENSIVE REAL BACKEND TEST")
    print("=" * 60)
    print("This test will:")
    print("1. Create a real PDF with contact information")
    print("2. Submit it via the actual backend API")
    print("3. Verify intelligent agent analysis occurred") 
    print("4. Confirm data was saved to Supabase database")
    print("5. Provide concrete proof the system works")
    print()
    
    # Step 1: Test API call
    api_result = test_backend_api_call()
    
    if not api_result['success']:
        print("\n❌ FINAL RESULT: API TEST FAILED")
        print("System is NOT working - API call failed")
        return False
    
    # Step 2: Verify database storage
    if api_result.get('bid_card_id'):
        db_verified = asyncio.run(check_database_storage(api_result['bid_card_id']))
    else:
        print("\nWARNING: No bid_card_id returned, skipping database verification")
        db_verified = False
    
    # Final assessment
    print("\n" + "=" * 60)
    print("FINAL TEST RESULTS:")
    print("=" * 60)
    
    print(f"✅ API Call Success: {api_result['success']}")
    print(f"✅ Contact Info Detected: {api_result.get('contact_detected', False)}")
    print(f"✅ PDF Analysis Performed: {api_result.get('pdf_analyzed', False)}")
    print(f"✅ Database Storage Verified: {db_verified}")
    
    if (api_result['success'] and 
        api_result.get('contact_detected') and 
        api_result.get('pdf_analyzed') and 
        db_verified):
        
        print("\n🎯 SYSTEM STATUS: FULLY OPERATIONAL")
        print("✅ PDF attachment processing working")
        print("✅ Contact information detection working")
        print("✅ Database storage working")
        print("✅ Complete bid submission workflow working")
        print("\n🚀 READY FOR PRODUCTION USE!")
        return True
    else:
        print("\n❌ SYSTEM STATUS: ISSUES DETECTED")
        print("One or more components not working properly")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🏆 COMPREHENSIVE TEST PASSED - SYSTEM CONFIRMED WORKING")
    else:
        print("\n⚠️  COMPREHENSIVE TEST FAILED - SYSTEM NEEDS DEBUGGING")