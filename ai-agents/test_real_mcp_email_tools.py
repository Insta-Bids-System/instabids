#!/usr/bin/env python3
"""
Test REAL MCP Email Tools Integration
Tests the actual MCP tools: mcp__instabids-email__send_email
"""

import asyncio
from datetime import datetime

async def test_real_mcp_email_tool():
    """Test the actual MCP email tool with personalized contractor outreach"""
    
    print("=" * 70)
    print("TESTING REAL MCP EMAIL TOOLS")
    print("=" * 70)
    
    # Test contractor data
    test_contractor = {
        'company_name': 'Green Lawn Masters',
        'contact_name': 'Mike Johnson',
        'email': 'mike@greenlawnmasters.com'
    }
    
    # Test bid card data
    bid_card = {
        'project_type': 'lawn_care',
        'location': 'Miami, FL',
        'budget_min': 150,
        'budget_max': 250,
        'scope_summary': 'Weekly lawn maintenance including mowing, edging, and trimming',
        'timeline': 'Start within 1 week'
    }
    
    # Create personalized email content
    subject = f"New {bid_card['project_type'].title()} Project - {bid_card['location']} (${bid_card['budget_min']}-${bid_card['budget_max']})"
    
    # Plain text body
    plain_body = f"""
Hello {test_contractor['contact_name']} at {test_contractor['company_name']},

We have a new {bid_card['project_type']} project in {bid_card['location']} that matches your expertise.

Project Details:
- Type: {bid_card['project_type'].title()}
- Location: {bid_card['location']}
- Budget: ${bid_card['budget_min']}-${bid_card['budget_max']}/month
- Timeline: {bid_card['timeline']}
- Scope: {bid_card['scope_summary']}

This is a qualified lead from a verified homeowner ready to move forward.

View Project & Submit Bid:
https://instabids.com/bid-cards/test-project?contractor={test_contractor['company_name'].replace(' ', '_')}

Best regards,
InstaBids Team
"""

    # HTML body with personalization
    html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; margin: 20px;">
    <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
        <h2 style="color: #22c55e;">New Project Opportunity - InstaBids</h2>
        
        <p>Hello {test_contractor['contact_name']} at <strong>{test_contractor['company_name']}</strong>,</p>
        
        <p>We have a new {bid_card['project_type']} project in {bid_card['location']} that matches your expertise.</p>
        
        <div style="background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3>Project Details:</h3>
            <ul>
                <li><strong>Type:</strong> {bid_card['project_type'].title()}</li>
                <li><strong>Location:</strong> {bid_card['location']}</li>
                <li><strong>Budget:</strong> ${bid_card['budget_min']}-${bid_card['budget_max']}/month</li>
                <li><strong>Timeline:</strong> {bid_card['timeline']}</li>
                <li><strong>Scope:</strong> {bid_card['scope_summary']}</li>
            </ul>
        </div>
        
        <p style="text-align: center;">
            <a href="https://instabids.com/bid-cards/test-project?contractor={test_contractor['company_name'].replace(' ', '_')}" 
               style="background: #22c55e; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block;">
                View Project & Submit Bid
            </a>
        </p>
        
        <hr style="margin: 30px 0; border: 1px solid #e5e7eb;">
        
        <p style="font-size: 14px; color: #6b7280;">
            This email was sent to {test_contractor['email']} because you're registered as a contractor in our network.
        </p>
    </div>
</body>
</html>
"""

    print(f"\nSending personalized email to: {test_contractor['company_name']}")
    print(f"To: {test_contractor['email']}")
    print(f"Subject: {subject}")
    
    # Here we would call the actual MCP tool
    # Since I can't directly invoke MCP tools from Python, I'll show what the call would look like
    print("\nMCP Tool Call Structure:")
    print("Tool: mcp__instabids-email__send_email")
    print("Parameters:")
    print(f"  to: {test_contractor['email']}")
    print(f"  subject: {subject}")
    print(f"  body: [Plain text version]")
    print(f"  html: [HTML version with {test_contractor['company_name']} personalization]")
    print(f"  from: noreply@instabids.com")
    
    print("\nThe MCP tool would send this email via the configured SMTP server (MailHog)")
    print("Each contractor gets unique personalization in:")
    print(f"  - Company name: {test_contractor['company_name']}")
    print(f"  - Contact greeting: {test_contractor['contact_name']}")
    print(f"  - Tracking URL: Includes contractor name")
    
    return True

async def test_mcp_notification_tool():
    """Test the MCP notification tool"""
    
    print("\n" + "=" * 70)
    print("TESTING MCP NOTIFICATION TOOL")
    print("=" * 70)
    
    notification_data = {
        'project_name': 'Lawn Care Project',
        'contractor_name': 'Green Lawn Masters',
        'homeowner_name': 'John Smith',
        'project_details': 'Weekly lawn maintenance for residential property',
        'bid_amount': '$150-$250/month',
        'connection_fee': '$49'
    }
    
    print("\nMCP Notification Tool Call:")
    print("Tool: mcp__instabids-email__send_instabids_notification")
    print("Parameters:")
    print("  to: mike@greenlawnmasters.com")
    print("  type: new_bid")
    print("  data:", notification_data)
    
    print("\nThis would send a pre-formatted InstaBids notification email")
    print("with the contractor-specific data filled into the template")
    
    return True

async def main():
    """Main test execution"""
    print("Testing Real MCP Email Tools Integration...")
    print("Note: Actual MCP tools need to be called from Claude, not Python")
    print("This test shows the structure and personalization that would be sent")
    
    # Test email tool
    await test_real_mcp_email_tool()
    
    # Test notification tool
    await test_mcp_notification_tool()
    
    print("\n" + "=" * 70)
    print("MCP EMAIL TOOL TEST COMPLETE")
    print("=" * 70)
    print("\nTo actually send emails:")
    print("1. The MCP email server must be running")
    print("2. Claude needs to call the MCP tools directly")
    print("3. Each email will be personalized per contractor")
    print("4. Emails will be delivered via configured SMTP (MailHog)")

if __name__ == "__main__":
    asyncio.run(main())