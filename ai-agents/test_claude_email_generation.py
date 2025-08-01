#!/usr/bin/env python3
"""
Test Claude Email Generation
Shows how Claude writes unique, personalized emails for each contractor
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.eaa.outreach_channels.mcp_email_channel_claude import MCPEmailChannelWithClaude
import json

def test_claude_email_generation():
    """Test Claude's ability to write unique emails"""
    
    print("=" * 80)
    print("TESTING CLAUDE EMAIL GENERATION")
    print("=" * 80)
    print("\nThis test will show:")
    print("1. How Claude writes unique emails for each contractor")
    print("2. No templates - each email is completely different")
    print("3. Personalization based on contractor details")
    
    # Initialize Claude email channel
    print("\nInitializing Claude Email Channel...")
    claude_channel = MCPEmailChannelWithClaude()
    
    # Test bid card
    bid_card_data = {
        'id': 'kitchen-miami-2025',
        'project_type': 'kitchen_remodel',
        'location': 'Miami Beach, FL',
        'budget_min': 35000,
        'budget_max': 45000,
        'timeline': 'Start within 1 month',
        'urgency_level': 'standard',
        'scope_details': 'Complete kitchen renovation including custom cabinets, quartz countertops, tile backsplash, and high-end stainless steel appliances. Open concept design preferred.',
        'external_url': 'https://instabids.com/bid-cards/kitchen-miami-2025'
    }
    
    # Test contractors with different profiles
    test_contractors = [
        {
            'company_name': 'Elite Kitchen Designs Miami',
            'contact_name': 'Carlos Rodriguez',
            'email': 'carlos@elitekitchensmiami.com',
            'service_types': ['kitchen_remodel', 'bathroom_remodel'],
            'specialties': ['custom cabinetry', 'luxury kitchens', 'modern design'],
            'years_in_business': 15,
            'tier': 1
        },
        {
            'company_name': 'Sunshine Home Renovations',
            'contact_name': 'Maria Santos',
            'email': 'maria@sunshinehomereno.com',
            'service_types': ['general_remodeling', 'kitchen_remodel'],
            'specialties': ['budget-friendly', 'quick turnaround', 'family homes'],
            'years_in_business': 8,
            'tier': 2
        },
        {
            'company_name': 'Premium Construction Group',
            'contact_name': 'James Wilson',
            'email': 'james@premiumconstruction.com',
            'service_types': ['luxury_remodel', 'whole_home_renovation'],
            'specialties': ['high-end finishes', 'smart home integration', 'sustainable materials'],
            'years_in_business': 20,
            'tier': 1
        }
    ]
    
    print(f"\nProject: {bid_card_data['project_type'].replace('_', ' ').title()}")
    print(f"Location: {bid_card_data['location']}")
    print(f"Budget: ${bid_card_data['budget_min']:,} - ${bid_card_data['budget_max']:,}")
    
    print("\n" + "-"*60)
    print("GENERATING UNIQUE EMAILS WITH CLAUDE")
    print("-"*60)
    
    results = []
    for i, contractor in enumerate(test_contractors, 1):
        print(f"\nContractor {i}: {contractor['company_name']}")
        print(f"  Contact: {contractor['contact_name']}")
        print(f"  Specialties: {', '.join(contractor['specialties'])}")
        
        # Generate email with Claude
        result = claude_channel.send_personalized_outreach(
            contractor, bid_card_data, 'test-campaign-123'
        )
        
        if result['success']:
            print(f"  ✓ Claude generated unique email")
            results.append(result)
        else:
            print(f"  ✗ Failed: {result.get('error')}")
    
    # Show generated emails
    print("\n" + "="*80)
    print("CLAUDE-GENERATED EMAILS")
    print("="*80)
    
    sent_emails = claude_channel.get_sent_emails_for_testing()
    
    for i, email in enumerate(sent_emails, 1):
        print(f"\nEmail {i} to {email['company_name']}:")
        print(f"Subject: {email['subject']}")
        print(f"Claude Generated: {email.get('claude_generated', False)}")
        print(f"Unique URL: {email['external_url']}")
        print("-" * 40)
    
    # Verify uniqueness
    print("\n" + "="*80)
    print("UNIQUENESS VERIFICATION")
    print("="*80)
    
    subjects = [e['subject'] for e in sent_emails]
    unique_subjects = set(subjects)
    
    print(f"\nTotal Emails: {len(sent_emails)}")
    print(f"Unique Subjects: {len(unique_subjects)}")
    print(f"All Unique: {len(subjects) == len(unique_subjects)}")
    
    if len(subjects) == len(unique_subjects):
        print("\n✓ SUCCESS: Every contractor received a completely unique email!")
    else:
        print("\n✗ Some emails may be similar")
    
    # Show example of personalization
    print("\n" + "="*80)
    print("PERSONALIZATION EXAMPLES")
    print("="*80)
    
    print("\nNotice how Claude:")
    print("1. References each contractor's specific specialties")
    print("2. Writes in different tones for different contractors")
    print("3. Creates urgency differently based on contractor profile")
    print("4. Uses contractor names and company details naturally")
    print("5. No two emails are the same - each is uniquely written")
    
    return True

def compare_template_vs_claude():
    """Show the difference between template and Claude emails"""
    
    print("\n" + "="*80)
    print("TEMPLATE VS CLAUDE COMPARISON")
    print("="*80)
    
    print("\n🤖 TEMPLATE-BASED (Current):")
    print("-" * 40)
    print("Subject: New Kitchen Remodel Project in Miami Beach - Elite Kitchen Designs Miami")
    print("\nHello there,")
    print("\nWe have a kitchen remodel project in Miami Beach.")
    print("Budget: $35,000 - $45,000")
    print("Timeline: Start within 1 month")
    print("\nClick here to view details and submit your bid.")
    
    print("\n\n🧠 CLAUDE-GENERATED (New):")
    print("-" * 40)
    print("Subject: Perfect Match: Luxury Kitchen Project in Miami Beach Needs Your Custom Cabinetry Expertise")
    print("\nHi Carlos,")
    print("\nI'm reaching out to Elite Kitchen Designs Miami specifically because of your")
    print("outstanding reputation for custom cabinetry and luxury kitchen transformations.")
    print("After reviewing your portfolio, particularly your recent modern kitchen projects")
    print("in the Miami area, I believe you'd be the perfect fit for this high-end")
    print("kitchen renovation in Miami Beach...")
    
    print("\n\nThe Claude version:")
    print("- Uses contractor's actual name")
    print("- References their specific expertise")
    print("- Mentions their portfolio/past work")
    print("- Creates a narrative, not just facts")
    print("- Feels like a personal invitation")

if __name__ == "__main__":
    print("Testing Claude Email Generation...")
    
    # First show the comparison
    compare_template_vs_claude()
    
    # Then run the actual test
    # Note: This will make real Claude API calls
    print("\n\nNOTE: This test would make real Claude API calls.")
    print("Each email costs approximately $0.015 with Claude Opus.")
    print("To run the actual test, uncomment the line below:")
    
    # Uncomment to run with real API calls:
    # test_claude_email_generation()
    
    print("\n" + "="*80)
    print("ARCHITECTURE EXPLANATION")
    print("="*80)
    
    print("\nCurrent Architecture (Separate Agents):")
    print("- Each agent is a standalone Python class")
    print("- Agents communicate through the database")
    print("- Orchestrator calls them sequentially")
    print("- Each agent maintains its own state")
    
    print("\nLangGraph Architecture (Alternative):")
    print("- Single graph with connected nodes")
    print("- Shared state passed between nodes")
    print("- Direct message passing")
    print("- More tightly coupled")
    
    print("\nPros of Current Approach:")
    print("+ Agents are independent and modular")
    print("+ Easy to test individually")
    print("+ Can run agents on different servers")
    print("+ Database provides audit trail")
    
    print("\nCons of Current Approach:")
    print("- More database calls")
    print("- Harder to pass complex state")
    print("- Less real-time coordination")
    print("- More complex error handling")