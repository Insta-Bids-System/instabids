#!/usr/bin/env python3
"""
Simple Document Testing - No External Dependencies
Tests text content analysis for document-like content
"""

import asyncio
from agents.intelligent_messaging_agent import GPT5SecurityAnalyzer

async def test_document_content():
    """Test document-style content analysis"""
    
    print("TESTING: Document Content Analysis")
    
    # Simulate different document types with contact info
    test_documents = {
        "BID_PROPOSAL": """
CONTRACTOR BID PROPOSAL
Mike's Custom Cabinets - Licensed & Insured

Project: Kitchen Cabinet Installation
Client: Sarah Johnson  
Date: August 8, 2025

SCOPE OF WORK:
• Remove existing cabinets
• Install 15 linear feet of upper cabinets
• Install 20 linear feet of base cabinets

TOTAL: $14,800

Contact Information:
Phone: (555) 123-4567
Email: mike.cabinets@gmail.com
Emergency: 555-999-8888
        """,
        
        "BUSINESS_CARD": """
Mike Johnson
Senior Project Manager
Mike's Custom Cabinets LLC

📱 Call: (555) 123-4567
📧 Email: mike.cabinets@gmail.com  
🌐 Web: www.mikescabinets.com
📍 123 Main St, Springfield
        """,
        
        "INVOICE": """
INVOICE #2025-001
Mike's Custom Cabinets

Bill To: Sarah Johnson
Project: Kitchen Renovation

Labor: $5,000
Materials: $9,800
Total: $14,800

Questions? Call (555) 123-4567
Email: billing@mikescabinets.com
        """
    }
    
    analyzer = GPT5SecurityAnalyzer()
    results = {}
    
    for doc_name, content in test_documents.items():
        try:
            print(f"\nTesting {doc_name} content...")
            
            # Use the text analysis method
            result = await analyzer.analyze_message_security(
                content=content,
                sender_type="contractor",
                project_context={"project_type": "kitchen", "budget_min": 10000},
                conversation_history=[]
            )
            
            threats = result.get('threats_detected', [])
            contact_detected = 'contact_info' in threats or len(threats) > 0
            confidence = result.get('confidence_score', 0)
            action = result.get('recommended_action', 'ALLOW')
            
            results[doc_name] = {
                'detected': contact_detected,
                'confidence': confidence,
                'threats': threats,
                'action': action,
                'status': 'BLOCKED' if action == 'BLOCK' else 'ALLOWED'
            }
            
            print(f"  Action: {action}")
            print(f"  Threats: {threats}")
            print(f"  Confidence: {confidence}")
            print(f"  Status: {results[doc_name]['status']}")
            
        except Exception as e:
            results[doc_name] = {
                'error': str(e),
                'status': 'ERROR'
            }
            print(f"  ERROR: {e}")
    
    return results

async def main():
    """Run document content tests"""
    
    print("=== DOCUMENT CONTENT ANALYSIS TESTING ===")
    
    results = await test_document_content()
    
    print("\n=== FINAL RESULTS ===")
    
    blocked_count = 0
    total_count = len(results)
    
    for doc_name, result in results.items():
        status = result['status']
        print(f"{doc_name}: {status}")
        
        if status == 'BLOCKED':
            blocked_count += 1
    
    print(f"\nBlocked (Contact Info Detected): {blocked_count}/{total_count}")
    
    if blocked_count == total_count:
        print("SUCCESS: All documents with contact info were blocked")
        return True
    else:
        print("PARTIAL: Some contact info may have been missed")
        return blocked_count > 0

if __name__ == "__main__":
    success = asyncio.run(main())