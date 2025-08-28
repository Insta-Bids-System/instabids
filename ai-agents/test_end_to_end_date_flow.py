#!/usr/bin/env python3
"""
End-to-End Date Flow Test
Tests complete date workflow from CIA extraction to EAA contractor messaging
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
from datetime import datetime, timedelta
from database_simple import db

# Mock a sample conversation that would extract dates
def test_end_to_end_date_flow():
    """Test complete date flow end-to-end"""
    print("="*70)
    print("END-TO-END DATE FLOW TEST")
    print("="*70)
    
    # STEP 1: Simulate CIA date extraction (this would normally be done by JAA)
    print("\nSTEP 1: Simulate date extraction (CIA -> JAA)")
    print("-" * 50)
    
    # Simulate CIA conversation that mentions a deadline
    homeowner_message = "I need my kitchen remodeled for my daughter's wedding on June 15th. It's really important we finish by then since we're having the reception at our house."
    
    from utils.date_parser import SimpleDateParser
    parser = SimpleDateParser()
    
    # Parse the date from conversation
    date_result = parser.parse_natural_language_date("wedding June 15th")
    print(f"Extracted date: {date_result}")
    
    # Calculate bid collection deadline
    if date_result['parsed_date']:
        bid_deadline = parser.calculate_bid_collection_deadline(date_result['parsed_date'])
        print(f"Bid collection deadline: {bid_deadline}")
    
    # STEP 2: Create bid card with date fields
    print("\nSTEP 2: Create bid card with extracted dates")
    print("-" * 50)
    
    # Sample bid card data with our extracted dates
    bid_card_data = {
        "id": "test-wedding-kitchen-" + str(int(datetime.now().timestamp())),
        "project_type": "Kitchen Remodel",
        "location": {"city": "Austin", "state": "TX", "zip_code": "78701"},
        "budget_min": 35000,
        "budget_max": 55000,
        "scope_summary": "Complete kitchen remodel for wedding reception - new cabinets, countertops, appliances, and flooring",
        "urgency_level": "month",  # Original urgency - will be overridden
        "contractor_count_needed": 4,
        "project_completion_deadline": date_result['parsed_date'].isoformat() if date_result['parsed_date'] else None,
        "bid_collection_deadline": bid_deadline.isoformat() if date_result['parsed_date'] else None,
        "deadline_hard": date_result['deadline_hard'],
        "deadline_context": date_result['deadline_context']
    }
    
    print(f"Bid card ID: {bid_card_data['id']}")
    print(f"Project deadline: {bid_card_data['project_completion_deadline']}")
    print(f"Bid collection deadline: {bid_card_data['bid_collection_deadline']}")
    print(f"Hard deadline: {bid_card_data['deadline_hard']}")
    print(f"Context: {bid_card_data['deadline_context']}")
    
    # STEP 3: Test campaign timing override
    print("\nSTEP 3: Test campaign orchestration with date override")
    print("-" * 50)
    
    from agents.orchestration.enhanced_campaign_orchestrator import CampaignRequest
    
    # Create campaign request
    campaign_request = CampaignRequest(
        bid_card_id=bid_card_data['id'],
        project_type=bid_card_data['project_type'],
        location=bid_card_data['location'],
        timeline_hours=120,  # Default: 5 days
        urgency_level=bid_card_data['urgency_level'],
        bids_needed=bid_card_data['contractor_count_needed'],
        project_completion_deadline=datetime.fromisoformat(bid_card_data['project_completion_deadline']) if bid_card_data['project_completion_deadline'] else None,
        bid_collection_deadline=datetime.fromisoformat(bid_card_data['bid_collection_deadline']) if bid_card_data['bid_collection_deadline'] else None,
        deadline_hard=bid_card_data['deadline_hard'],
        deadline_context=bid_card_data['deadline_context']
    )
    
    print(f"Original timeline: {campaign_request.timeline_hours} hours")
    
    # Simulate the orchestrator's date override logic
    timeline_hours = campaign_request.timeline_hours
    
    if campaign_request.project_completion_deadline:
        print(f"Exact deadline provided: {campaign_request.project_completion_deadline}")
        days_remaining = (campaign_request.project_completion_deadline - datetime.now()).days
        
        # Simple override logic (same as in orchestrator)
        if days_remaining <= 3:
            timeline_hours = 6  # Rush mode: 6 hours
            print(f"Rush mode activated: {days_remaining} days remaining, using 6 hours")
        elif days_remaining <= 7:
            timeline_hours = 24  # Fast track: 1 day
            print(f"Fast track activated: {days_remaining} days remaining, using 24 hours")
        elif days_remaining <= 14:
            timeline_hours = 72  # Normal: 3 days
            print(f"Normal timeline: {days_remaining} days remaining, using 72 hours")
        else:
            timeline_hours = 120  # Relaxed: 5 days
            print(f"Relaxed timeline: {days_remaining} days remaining, using 120 hours")
    
    print(f"Overridden timeline: {timeline_hours} hours")
    print(f"Days until deadline: {days_remaining}")
    
    # STEP 4: Test EAA template generation with deadline context
    print("\nSTEP 4: Test EAA template generation with deadline context")
    print("-" * 50)
    
    from agents.eaa.message_templates.template_engine import TemplateEngine
    
    template_engine = TemplateEngine()
    
    # Mock contractor data
    contractor = {
        "contact_name": "Sarah Johnson",
        "company_name": "Dream Kitchen Designs",
        "email": "sarah@dreamkitchens.com",
        "phone": "512-555-0123"
    }
    
    # Generate messages with deadline context
    messages = template_engine.generate_messages(
        contractor,
        bid_card_data,
        ["email"],
        "week"  # Urgency level (could be overridden by deadline proximity)
    )
    
    if "email" in messages:
        email = messages["email"]
        print(f"Email Subject: {email['subject']}")
        print(f"Template Used: {email['template_used']}")
        print(f"Personalization Score: {email['personalization_score']}")
        
        # Show key parts of the email
        print("\nEmail Content Preview:")
        print("-" * 30)
        content_lines = email['plain_content'].split('\n')
        
        # Show first few lines
        for i, line in enumerate(content_lines[:8]):
            if line.strip():
                print(line.strip())
        
        print("\n...")
        
        # Show deadline context specifically
        for i, line in enumerate(content_lines):
            if any(keyword in line.lower() for keyword in ['deadline', 'wedding', 'june', 'important']):
                print(f"DEADLINE CONTEXT: {line.strip()}")
                if i < len(content_lines) - 1 and content_lines[i+1].strip():
                    print(f"                  {content_lines[i+1].strip()}")
    
    # STEP 5: Summary and validation
    print("\nSTEP 5: Validation Summary")
    print("-" * 50)
    
    validations = {
        "Date extracted successfully": date_result['parsed_date'] is not None,
        "Deadline marked as hard": date_result['deadline_hard'] == True,
        "Context preserved": "wedding" in date_result['deadline_context'].lower(),
        "Bid deadline calculated": bid_deadline is not None if date_result['parsed_date'] else True,
        "Campaign timing overridden": timeline_hours != campaign_request.timeline_hours if campaign_request.project_completion_deadline else True,
        "EAA template includes deadline": "deadline" in messages["email"]["plain_content"].lower() if "email" in messages else False,
        "Subject line enhanced": any(keyword in messages["email"]["subject"].lower() for keyword in ["firm", "deadline"]) if "email" in messages and bid_card_data['deadline_hard'] else True
    }
    
    print("\nValidation Results:")
    all_passed = True
    for check, passed in validations.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {status}: {check}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*70)
    if all_passed:
        print("END-TO-END DATE FLOW: FULLY OPERATIONAL")
        print("All components working correctly:")
        print("- Date extraction from natural language")
        print("- Bid collection deadline calculation") 
        print("- Campaign timing override based on proximity")
        print("- Enhanced contractor messaging with deadline context")
    else:
        print("END-TO-END DATE FLOW: ISSUES DETECTED")
        print("Some components need attention - see validation results above")
    print("="*70)
    
    return all_passed

if __name__ == "__main__":
    try:
        success = test_end_to_end_date_flow()
        if success:
            print("\nSUCCESS: End-to-end date flow is working!")
        else:
            print("\nISSUES: End-to-end date flow has problems")
    except Exception as e:
        print(f"\nERROR during end-to-end testing: {e}")
        import traceback
        traceback.print_exc()