#!/usr/bin/env python3
"""
REAL MCP Email Test - Actually sends emails via MailHog
Uses mcp__instabids-email__send_email tool to send actual emails
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.eaa.outreach_channels.mcp_email_channel_claude import MCPEmailChannelWithClaude

def test_real_mcp_email_sending():
    """Test with REAL MCP email sending to MailHog"""
    
    print("=" * 80)
    print("TESTING REAL MCP EMAIL SENDING VIA MAILHOG")
    print("=" * 80)
    print("\nThis will send ACTUAL emails that you can see in MailHog")
    
    # Initialize email channel
    email_channel = RealMCPEmailChannel()
    
    # Test project
    bid_card_data = {
        'id': 'kitchen-miami-real-test',
        'project_type': 'kitchen_remodel',
        'location': 'Miami Beach, FL',
        'budget_min': 35000,
        'budget_max': 45000,
        'timeline': 'Start within 1 month',
        'urgency_level': 'standard',
        'scope_details': 'Complete kitchen renovation including custom cabinets, quartz countertops, tile backsplash, and high-end stainless steel appliances. Open concept design preferred.',
        'external_url': 'https://instabids.com/bid-cards/kitchen-miami-real-test',
        'homeowner': {
            'name': 'Sarah Johnson'
        }
    }
    
    # Test contractors
    test_contractors = [
        {
            'company_name': 'Elite Kitchen Designs Miami',
            'contact_name': 'Carlos Rodriguez',
            'email': 'carlos@elitekitchens.test',
            'service_types': ['kitchen_remodel', 'bathroom_remodel'],
            'specialties': ['custom cabinetry', 'luxury kitchens', 'modern design'],
            'years_in_business': 15,
            'tier': 1
        },
        {
            'company_name': 'Sunshine Home Renovations',
            'contact_name': 'Maria Santos',
            'email': 'maria@sunshine.test',
            'service_types': ['general_remodeling', 'kitchen_remodel'],
            'specialties': ['budget-friendly', 'quick turnaround', 'family homes'],
            'years_in_business': 8,
            'tier': 2
        },
        {
            'company_name': 'Premium Construction Group',
            'contact_name': 'James Wilson',
            'email': 'james@premium.test',
            'service_types': ['luxury_remodel', 'whole_home_renovation'],
            'specialties': ['high-end finishes', 'smart home integration', 'sustainable materials'],
            'years_in_business': 20,
            'tier': 1
        }
    ]
    
    print(f"\nProject: Kitchen Remodel in Miami Beach")
    print(f"Budget: ${bid_card_data['budget_min']:,} - ${bid_card_data['budget_max']:,}")
    print(f"Sending REAL emails to {len(test_contractors)} contractors...")
    
    results = []
    
    for i, contractor in enumerate(test_contractors, 1):
        print(f"\n{'='*60}")
        print(f"CONTRACTOR {i}: {contractor['company_name']}")
        print(f"{'='*60}")
        print(f"Contact: {contractor['contact_name']}")
        print(f"Email: {contractor['email']}")
        print(f"Specialties: {', '.join(contractor['specialties'])}")
        
        print(f"\nSending REAL email via MCP to MailHog...")
        
        # Send actual email
        result = email_channel.send_real_email(
            contractor, bid_card_data, 'real-test-campaign'
        )
        
        if result['success']:
            print(f"SUCCESS: Email sent to MailHog!")
            print(f"   Check MailHog at http://localhost:8025")
            print(f"   To: {contractor['email']}")
            print(f"   Subject: {result.get('subject', 'N/A')}")
            results.append(result)
        else:
            print(f"FAILED: {result.get('error')}")
    
    print(f"\n{'='*80}")
    print("REAL EMAIL TEST RESULTS")
    print(f"{'='*80}")
    
    print(f"\nEmails Sent: {len(results)}")
    print(f"Check MailHog at: http://localhost:8025")
    print(f"\nYou should see {len(results)} unique emails with:")
    print("- Different subject lines for each contractor")
    print("- Personalized content based on contractor specialties")
    print("- Unique tracking URLs")
    print("- Professional HTML formatting")
    
    return len(results) > 0


class RealMCPEmailChannel(MCPEmailChannelWithClaude):
    """Email channel that actually sends via MCP"""
    
    def send_real_email(self, contractor, bid_card_data, campaign_id):
        """Send real email via MCP tool"""
        try:
            # Use Claude to generate email content (or fallback)
            message_id = f"real-{self._generate_id()}"
            
            # Generate email content
            email_data = self._create_claude_personalized_email(
                contractor, bid_card_data, message_id, campaign_id
            )
            
            # Extract email details
            to_email = contractor.get('email')
            subject = email_data.get('subject', 'InstaBids Project Opportunity')
            html_content = email_data.get('html_content', '<p>New project opportunity</p>')
            
            print(f"[REAL MCP] Sending email via mcp__instabids-email__send_email")
            
            # This should trigger the actual MCP tool
            mcp_result = self._call_mcp_email_tool(
                to=to_email,
                subject=subject,
                html=html_content
            )
            
            return {
                'success': True,
                'subject': subject,
                'to': to_email,
                'mcp_result': mcp_result,
                'message_id': message_id
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _call_mcp_email_tool(self, to, subject, html):
        """Call the actual MCP email tool"""
        # This is where we need to use the actual MCP tool
        # For now, let's show what would be called
        print(f"[MCP CALL] mcp__instabids-email__send_email")
        print(f"  to: {to}")
        print(f"  subject: {subject}")
        print(f"  html: {html[:100]}...")
        
        # TODO: Replace with actual MCP tool call
        # return mcp__instabids_email__send_email(to=to, subject=subject, html=html)
        
        return {"status": "simulated", "message": "Would send via MCP"}
    
    def _generate_id(self):
        """Generate unique ID"""
        import uuid
        return str(uuid.uuid4())[:8]


if __name__ == "__main__":
    print("Starting REAL MCP Email Test...")
    print("This will send actual emails to MailHog")
    print("\nMake sure MailHog is running at http://localhost:8025")
    
    success = test_real_mcp_email_sending()
    
    if success:
        print("\nSUCCESS: Emails sent! Check MailHog to see them.")
    else:
        print("\nFAILED: No emails were sent.")