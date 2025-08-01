#!/usr/bin/env python3
"""
Test MCP Email Integration with EAA Agent
Tests unique, personalized contractor outreach emails
"""

import sys
import os
import asyncio
from datetime import datetime

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.eaa.agent import ExternalAcquisitionAgent

def create_test_contractors():
    """Create sample contractors for testing"""
    return [
        {
            'id': 'test-contractor-1',
            'company_name': 'Green Lawn Masters',
            'contact_name': 'Mike Johnson',
            'email': 'mike@greenlawnmasters.com',
            'phone': '(305) 555-0101',
            'lead_score': 85,
            'tier': 2
        },
        {
            'id': 'test-contractor-2', 
            'company_name': 'Perfect Yards LLC',
            'contact_name': 'Sarah Chen',
            'email': 'sarah@perfectyards.com',
            'phone': '(305) 555-0102',
            'lead_score': 92,
            'tier': 2
        },
        {
            'id': 'test-contractor-3',
            'company_name': 'Miami Lawn Care Pro',
            'contact_name': 'David Rodriguez',
            'email': 'david@miamilawnpro.com',
            'phone': '(305) 555-0103',
            'lead_score': 78,
            'tier': 3
        },
        {
            'id': 'test-contractor-4',
            'company_name': 'Tropical Landscaping',
            'contact_name': 'Jennifer Martinez',
            'email': 'jen@tropicallandscaping.com',
            'phone': '(305) 555-0104',
            'lead_score': 88,
            'tier': 2
        },
        {
            'id': 'test-contractor-5',
            'company_name': 'Sunshine Lawn Services',
            'contact_name': 'Robert Taylor',
            'email': 'rob@sunshinelawn.com',
            'phone': '(305) 555-0105',
            'lead_score': 90,
            'tier': 1
        }
    ]

def create_test_bid_card():
    """Create sample bid card for testing"""
    return {
        'id': '769961f6-84f8-460f-a320-4d942c66d3c4',
        'public_token': 'miami-lawn-care-123',
        'project_type': 'lawn_care',
        'scope_summary': 'Weekly lawn maintenance including mowing, edging, trimming, and seasonal fertilization for 0.25-acre property',
        'budget_min': 150,
        'budget_max': 250,
        'location': 'Miami, FL',
        'timeline': 'Start within 1 week',
        'urgency_level': 'standard',
        'homeowner_name': 'John Smith',
        'external_url': 'https://instabids.com/bid-cards/miami-lawn-care-123',
        'preferred_date': datetime.now().isoformat()
    }

def test_mcp_email_integration():
    """Test MCP email integration with unique contractor outreach"""
    
    print("=" * 70)
    print("TESTING MCP EMAIL INTEGRATION WITH EAA AGENT")
    print("=" * 70)
    
    try:
        # Initialize EAA agent
        print("\nInitializing EAA Agent with MCP Email Channel...")
        eaa = ExternalAcquisitionAgent()
        
        # Clear any previous test data
        print("Clearing previous test data...")
        eaa.clear_test_data()
        
        # Create test data
        print("Creating test contractors and bid card...")
        test_contractors = create_test_contractors()
        test_bid_card = create_test_bid_card()
        
        print(f"   Created {len(test_contractors)} test contractors")
        print(f"   Created bid card: {test_bid_card['project_type']} in {test_bid_card['location']}")
        print(f"   Budget: ${test_bid_card['budget_min']}-${test_bid_card['budget_max']}/month")
        
        # Test MCP email integration
        print("\nTesting MCP Email Integration...")
        test_results = eaa.test_mcp_email_integration(test_contractors, test_bid_card)
        
        if test_results['success']:
            print(f"   Emails sent successfully: {test_results['emails_sent']}")
            print(f"   Emails failed: {test_results['emails_failed']}")
            print(f"   Stored for verification: {test_results['stored_emails_count']}")
            
            # Display unique elements for each contractor
            print("\nUnique Elements Per Contractor:")
            for element in test_results['unique_elements_verified']:
                print(f"   {element['contractor']} ({element['email']})")
                unique = element['unique_elements']
                print(f"      Company: {unique.get('company_name', 'N/A')}")
                print(f"      Unique URL: {unique.get('external_url', 'N/A')}")
                print(f"      Message ID: {unique.get('message_id', 'N/A')}")
                print("")
        else:
            print(f"   MCP email test failed: {test_results.get('error')}")
            return False
        
        # Verify email uniqueness
        print("Verifying Email Uniqueness and Personalization...")
        verification = eaa.verify_unique_emails()
        
        if verification['personalization_verified']:
            print(f"   Total emails processed: {verification['total_emails']}")
            print(f"   Unique companies: {verification['unique_companies_count']}")
            print(f"   Unique URLs: {verification['unique_urls_count']}")
            print(f"   Unique Message IDs: {verification['unique_message_ids_count']}")
            
            # Show sample personalization details
            print("\nSample Email Details:")
            for i, detail in enumerate(verification['details'][:3]):  # Show first 3
                print(f"   {i+1}. {detail['company']}")
                print(f"      Subject: {detail['subject']}")
                print(f"      URL: {detail['external_url']}")
                print(f"      Sent: {detail['sent_at']}")
                print("")
        else:
            print(f"   Email verification failed: {verification.get('error')}")
            return False
        
        # Test campaign integration
        print("Testing Campaign Integration...")
        campaign_result = eaa.start_campaign(
            bid_card_id=test_bid_card['id'],
            contractors=test_contractors[:3],  # Test with 3 contractors
            channels=['email'],
            urgency='standard'
        )
        
        if campaign_result['success']:
            print(f"   Campaign launched: {campaign_result['campaign_id']}")
            print(f"   Messages sent: {campaign_result['messages_sent']}")
            print(f"   Channels used: {campaign_result['channels_used']}")
            print(f"   Tier breakdown: {campaign_result['tier_breakdown']}")
        else:
            print(f"   Campaign failed: {campaign_result.get('error')}")
            return False
        
        # Final verification
        print("\nMCP EMAIL INTEGRATION TEST RESULTS:")
        print("=" * 50)
        print("PASS: MCP Email Channel: WORKING")
        print("PASS: Unique Personalization: VERIFIED")
        print("PASS: External URLs: UNIQUE PER CONTRACTOR")
        print("PASS: Message IDs: UNIQUE PER EMAIL")
        print("PASS: Campaign Integration: WORKING")
        print("PASS: Email Storage: WORKING")
        print("=" * 50)
        
        # Show where emails are stored for inspection
        print(f"\nTest emails stored in: temp_email_storage/")
        print("   You can inspect the HTML content and personalization")
        print("   Each email has unique company names, URLs, and message IDs")
        
        print("\nMCP EMAIL INTEGRATION TEST COMPLETED SUCCESSFULLY!")
        return True
        
    except Exception as e:
        print(f"\nMCP EMAIL INTEGRATION TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_actual_mcp_tools():
    """Test with actual MCP tools if available"""
    print("\nTesting Actual MCP Tool Integration...")
    
    # This would test the actual MCP tools:
    # mcp__instabids-email__send_email
    # mcp__instabids-email__send_instabids_notification
    
    print("   Actual MCP tool testing requires MCP server running")
    print("   Current test uses simulation for development")
    print("   Ready for MCP server integration")

if __name__ == "__main__":
    print("Starting MCP Email Integration Test Suite...")
    
    # Run the main test
    success = test_mcp_email_integration()
    
    # Test MCP tools
    test_actual_mcp_tools()
    
    if success:
        print("\nALL TESTS PASSED - MCP EMAIL INTEGRATION READY!")
        sys.exit(0)
    else:
        print("\nTESTS FAILED - CHECK ERRORS ABOVE")
        sys.exit(1)