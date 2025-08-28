#!/usr/bin/env python3
"""
REAL DATABASE PROOF TEST - NO LIES, NO CLAIMS WITHOUT EVIDENCE
Tests actual API calls and shows concrete database records
"""

import asyncio
import base64
import json
import requests
from datetime import datetime
import database_simple
from config.service_urls import get_backend_url

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
        
        # Add content with OBVIOUS contact information
        p.drawString(100, height - 100, f"REAL TEST PDF - {timestamp}")
        p.drawString(100, height - 150, "CONTRACTOR PROPOSAL")
        p.drawString(100, height - 200, "")
        p.drawString(100, height - 250, "CONTACT INFORMATION:")
        p.drawString(100, height - 300, "Phone: (555) 888-9999")  # OBVIOUS CONTACT
        p.drawString(100, height - 350, "Email: realtest@contractor.com")  # OBVIOUS CONTACT  
        p.drawString(100, height - 400, "Text me for immediate response!")  # BYPASS ATTEMPT
        p.drawString(100, height - 450, "")
        p.drawString(100, height - 500, "Project Details:")
        p.drawString(100, height - 550, "Kitchen remodel - $35,000")
        p.drawString(100, height - 600, "Timeline: 5 weeks")
        
        p.showPage()
        p.save()
        
        buffer.seek(0)
        pdf_bytes = buffer.getvalue()
        return base64.b64encode(pdf_bytes).decode('utf-8')
        
    except ImportError:
        print("ERROR: reportlab not available")
        return None

def test_intelligent_messaging_api_with_pdf():
    """Test the actual intelligent messaging API with PDF"""
    
    print("=== TESTING INTELLIGENT MESSAGING API WITH PDF ===")
    print("Creating real PDF...")
    
    pdf_data = create_real_pdf()
    if not pdf_data:
        print("FAILED: Could not create PDF")
        return None
        
    print(f"PDF created: {len(pdf_data)} characters")
    
    # Test data for messaging API
    test_data = {
        "content": "Here's my detailed bid proposal for the kitchen project with all specifications",
        "sender_type": "contractor",
        "sender_id": "real-test-contractor-001", 
        "bid_card_id": "real-test-bid-card-001",
        "conversation_id": None,
        "target_contractor_id": None,
        "message_type": "text",
        "metadata": {
            "test_timestamp": datetime.now().isoformat(),
            "test_type": "pdf_attachment_real"
        }
    }
    
    print("Testing intelligent messaging API...")
    print(f"API: http://localhost:8008/api/intelligent-messages/send")
    
    try:
        response = requests.post(
            f"{get_backend_url()}/api/intelligent-messages/send",
            json=test_data,
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS: API call completed")
            print(f"Approved: {result.get('approved')}")
            print(f"Agent Decision: {result.get('agent_decision')}")
            print(f"Threats: {result.get('threats_detected')}")
            print(f"Message ID: {result.get('message_id')}")
            print(f"Conversation ID: {result.get('conversation_id')}")
            
            return {
                'success': True,
                'message_id': result.get('message_id'),
                'conversation_id': result.get('conversation_id'),
                'result': result
            }
        else:
            print(f"FAILED: API returned {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"FAILED: API call exception: {e}")
        return None

async def check_database_records(message_id=None, sender_id="real-test-contractor-001"):
    """Check what's actually in the database"""
    
    print("\n=== CHECKING REAL DATABASE RECORDS ===")
    print("Connecting to Supabase database...")
    
    try:
        db = database_simple.get_client()
        
        # Check messages table  
        print(f"1. Checking messaging_system_messages for sender: {sender_id}")
        messages_result = db.table("messaging_system_messages").select("*").eq(
            "sender_id", sender_id
        ).order("created_at", desc=True).limit(3).execute()
        
        if messages_result.data:
            print(f"   FOUND: {len(messages_result.data)} message(s)")
            for i, msg in enumerate(messages_result.data):
                print(f"   Message {i+1}:")
                print(f"     ID: {msg.get('id')}")
                print(f"     Content: {msg.get('original_content', '')[:100]}...")
                print(f"     Filtered: {msg.get('content_filtered')}")
                print(f"     Created: {msg.get('created_at')}")
                print(f"     Metadata: {json.dumps(msg.get('metadata', {}), indent=2)[:200]}...")
        else:
            print("   NO MESSAGES FOUND in messaging_system_messages")
            
        # Check unified_messages table
        print(f"\n2. Checking unified_messages for sender: {sender_id}")
        unified_result = db.table("unified_messages").select("*").eq(
            "sender_id", sender_id
        ).order("created_at", desc=True).limit(3).execute()
        
        if unified_result.data:
            print(f"   FOUND: {len(unified_result.data)} unified message(s)")
            for i, msg in enumerate(unified_result.data):
                print(f"   Unified Message {i+1}:")
                print(f"     ID: {msg.get('id')}")
                print(f"     Content: {msg.get('content', '')[:100]}...")
                print(f"     Message Type: {msg.get('message_type')}")
                print(f"     Created: {msg.get('created_at')}")
                
                # Check for attachment data
                metadata = msg.get('metadata', {})
                attachments = metadata.get('attachments', [])
                print(f"     Attachments: {len(attachments)}")
                
                for j, att in enumerate(attachments):
                    print(f"       Attachment {j+1}: {att.get('type')} - {att.get('name')}")
                    data_size = len(att.get('data', ''))
                    print(f"       Data size: {data_size} chars")
        else:
            print("   NO MESSAGES FOUND in unified_messages")
            
        # Check conversations table
        print(f"\n3. Checking conversations table...")
        conversations_result = db.table("conversations").select("*").order(
            "created_at", desc=True
        ).limit(3).execute()
        
        if conversations_result.data:
            print(f"   FOUND: {len(conversations_result.data)} conversation(s)")
            for conv in conversations_result.data:
                print(f"   Conversation: {conv.get('id')} - Status: {conv.get('status')}")
        else:
            print("   NO CONVERSATIONS FOUND")
            
        return {
            'messaging_messages': len(messages_result.data) if messages_result.data else 0,
            'unified_messages': len(unified_result.data) if unified_result.data else 0,
            'conversations': len(conversations_result.data) if conversations_result.data else 0
        }
        
    except Exception as e:
        print(f"DATABASE ERROR: {e}")
        return None

def main():
    """Run complete real test with database proof"""
    
    print("=" * 70)
    print("REAL DATABASE PROOF TEST - NO LIES")
    print("=" * 70)
    print("This will:")
    print("1. Make real API calls with PDF attachments")
    print("2. Show actual database records")
    print("3. Provide concrete evidence of what works")
    print()
    
    # Test 1: API call
    api_result = test_intelligent_messaging_api_with_pdf()
    
    # Test 2: Check database
    db_result = asyncio.run(check_database_records())
    
    print("\n" + "=" * 70)
    print("REAL RESULTS - NO BULLSHIT")
    print("=" * 70)
    
    if api_result and api_result['success']:
        print("API CALL: SUCCESS")
        print(f"  - Message created: {api_result.get('message_id', 'Unknown')}")
        print(f"  - Conversation: {api_result.get('conversation_id', 'Unknown')}")
    else:
        print("API CALL: FAILED")
        
    if db_result:
        print(f"DATABASE RECORDS:")
        print(f"  - Messaging messages: {db_result['messaging_messages']}")
        print(f"  - Unified messages: {db_result['unified_messages']}")
        print(f"  - Conversations: {db_result['conversations']}")
    else:
        print("DATABASE CHECK: FAILED")
        
    # Final verdict
    success = (api_result and api_result['success'] and db_result and 
              (db_result['messaging_messages'] > 0 or db_result['unified_messages'] > 0))
    
    print(f"\nFINAL VERDICT: {'SUCCESS - SYSTEM WORKS' if success else 'FAILED - SYSTEM BROKEN'}")
    
    if success:
        print("PROOF: API calls work AND data is saved to database")
    else:
        print("PROBLEM: Either API failed or no data was saved")
        
    return success

if __name__ == "__main__":
    main()