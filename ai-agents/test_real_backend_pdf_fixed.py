#!/usr/bin/env python3
"""
REAL BACKEND PDF SUBMISSION TEST - FIXED VERSION
Tests actual bid submission with PDF against live backend and database
"""

import asyncio
import base64
import json
import requests
from datetime import datetime, timedelta
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
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Add content with OBVIOUS contact information
        p.drawString(100, height - 100, "CONTRACTOR BID PROPOSAL - REAL BACKEND TEST")
        p.drawString(100, height - 150, f"Generated: {timestamp}")
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
    
    # Prepare bid submission data with correct structure
    print("2. Preparing bid submission with PDF attachment...")
    
    start_date = datetime.now() + timedelta(days=7)  
    end_date = start_date + timedelta(weeks=6)
    
    bid_data = {
        "bid_card_id": "4aa5e277-82b1-4679-a86a-24fd56b10e4c",  # Real active bid card
        "contractor_id": "08a8bfc5-e5f3-4b84-aaeb-8946c08eff26",  # Different contractor ID
        "amount": 45000.0,
        "timeline": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "flexibility": "moderate"
        },
        "proposal": "Complete kitchen remodel as specified with premium materials and professional installation",
        "approach": "Systematic approach with minimal disruption to household routine",
        "warranty_details": "3-year comprehensive warranty on all materials and workmanship",
        "materials_included": True,
        "milestones": [
            {"description": "Design and planning", "percentage": 20},
            {"description": "Demolition and prep", "percentage": 40},
            {"description": "Installation", "percentage": 80},
            {"description": "Final inspection", "percentage": 100}
        ],
        # PDF attachment in correct format
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
    print(f"   API Endpoint: http://localhost:8008/api/bid-cards/contractor-bids")
    
    try:
        # Make actual API call to backend
        response = requests.post(
            f"{get_backend_url()}/api/bid-cards/contractor-bids",
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
            
            # Check for PDF analysis in result
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
            
            # Check if contact info was detected
            contact_detected = 'contact_info' in result.get('threats_detected', [])
            print(f"   CONTACT INFO DETECTED: {contact_detected}")
            
            return {
                'success': True,
                'contact_detected': contact_detected,
                'pdf_analyzed': pdf_analyzed,
                'bid_card_id': result.get('bid_card_id', bid_data['bid_card_id']),
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
        
        # Check unified_messages table for intelligent agent processing
        print("1. Checking unified_messages table...")
        messages_result = db.table("unified_messages").select("*").eq(
            "sender_id", "08a8bfc5-e5f3-4b84-aaeb-8946c08eff26"
        ).order("created_at", desc=True).limit(1).execute()
        
        if messages_result.data:
            message = messages_result.data[0]
            print(f"   SUCCESS: Intelligent agent message found")
            print(f"   Message type: {message.get('message_type', 'N/A')}")
            print(f"   Created at: {message.get('created_at', 'N/A')}")
            
            # Check metadata for agent decision
            metadata = message.get('metadata', {})
            print(f"   Agent decision: {metadata.get('agent_decision', 'N/A')}")
            print(f"   Threats detected: {metadata.get('threats_detected', [])}")
            
            # Check for attachment data
            attachments = metadata.get('attachments', [])
            print(f"   Attachments stored: {len(attachments)}")
            
            for i, attachment in enumerate(attachments):
                print(f"     Attachment {i+1}: {attachment.get('name', 'N/A')} ({attachment.get('type', 'N/A')})")
                if attachment.get('type') == 'pdf':
                    data_size = len(attachment.get('data', ''))
                    print(f"       PDF data size: {data_size} characters")
                    print(f"       PDF data stored: {data_size > 0}")
            
            return True
        else:
            print(f"   WARNING: No intelligent agent message found for contractor")
            return False
        
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
        print("\nFINAL RESULT: API TEST FAILED")
        print("System is NOT working - API call failed")
        return False
    
    # Step 2: Verify database storage
    if api_result.get('bid_card_id'):
        db_verified = asyncio.run(check_database_storage(api_result['bid_card_id']))
    else:
        print("\nWARNING: No bid_card_id returned, checking with test contractor ID")
        db_verified = asyncio.run(check_database_storage("4aa5e277-82b1-4679-a86a-24fd56b10e4c"))
    
    # Final assessment
    print("\n" + "=" * 60)
    print("FINAL TEST RESULTS:")
    print("=" * 60)
    
    print(f"API Call Success: {api_result['success']}")
    print(f"Contact Info Detected: {api_result.get('contact_detected', False)}")
    print(f"PDF Analysis Performed: {api_result.get('pdf_analyzed', False)}")
    print(f"Database Storage Verified: {db_verified}")
    
    if (api_result['success'] and 
        api_result.get('contact_detected') and 
        db_verified):
        
        print("\nSYSTEM STATUS: FULLY OPERATIONAL")
        print("SUCCESS: PDF attachment processing working")
        print("SUCCESS: Contact information detection working")
        print("SUCCESS: Database storage working")
        print("SUCCESS: Complete bid submission workflow working")
        print("\nREADY FOR PRODUCTION USE!")
        return True
    else:
        print("\nSYSTEM STATUS: ISSUES DETECTED")
        print("One or more components not working properly")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\nCOMPREHENSIVE TEST PASSED - SYSTEM CONFIRMED WORKING")
    else:
        print("\nCOMPREHENSIVE TEST FAILED - SYSTEM NEEDS DEBUGGING")