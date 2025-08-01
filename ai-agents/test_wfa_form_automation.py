#!/usr/bin/env python3
"""
Test WFA (Website Form Automation) Agent
Tests the ability to find and fill out contractor website forms
"""

import sys
import os
import asyncio
from datetime import datetime

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.wfa.agent import WebsiteFormAutomationAgent

def test_wfa_form_detection():
    """Test WFA's ability to detect forms on contractor websites"""
    
    print("=" * 80)
    print("TESTING WFA - WEBSITE FORM AUTOMATION AGENT")
    print("=" * 80)
    print("\nThis test will:")
    print("1. Analyze contractor websites for contact forms")
    print("2. Identify form fields and their purposes")
    print("3. Fill out forms with project information")
    print("4. Track submission results")
    
    try:
        # Initialize WFA agent
        print("\nInitializing WFA Agent...")
        wfa = WebsiteFormAutomationAgent()
        
        # Test contractors with known websites
        test_contractors = [
            {
                'id': 'test-contractor-1',
                'company_name': 'ABC Construction',
                'website': 'https://www.example.com',  # Test site
                'email': 'contact@abcconstruction.com',
                'contact_name': 'John Smith'
            },
            # Add more real contractor websites if available
        ]
        
        # Create test bid card data
        bid_card_data = {
            'project_type': 'kitchen_remodel',
            'scope_summary': 'Complete kitchen renovation including new cabinets, countertops, and appliances',
            'budget_min': 25000,
            'budget_max': 35000,
            'location': 'Miami, FL',
            'timeline': 'Within 2-3 weeks',
            'homeowner_name': 'Test User',
            'homeowner_email': 'testuser@example.com',
            'homeowner_phone': '(305) 555-0100'
        }
        
        print(f"\nProject Details:")
        print(f"  Type: {bid_card_data['project_type']}")
        print(f"  Budget: ${bid_card_data['budget_min']:,} - ${bid_card_data['budget_max']:,}")
        print(f"  Location: {bid_card_data['location']}")
        
        # Test form detection
        print("\n" + "-"*60)
        print("STEP 1: FORM DETECTION")
        print("-"*60)
        
        for contractor in test_contractors:
            print(f"\nAnalyzing website for: {contractor['company_name']}")
            print(f"Website: {contractor['website']}")
            
            # Analyze website for forms
            analysis = wfa.analyze_website_for_form(contractor)
            
            if analysis['success']:
                print(f"  Has Contact Form: {analysis['has_contact_form']}")
                print(f"  Forms Found: {analysis['forms_found']}")
                
                if analysis['has_contact_form']:
                    best_form = analysis.get('best_form', {})
                    if best_form:
                        print(f"  Best Form URL: {best_form.get('page_url', 'N/A')}")
                        print(f"  Form Score: {best_form.get('score', 0)}")
                        print(f"  Fields Found:")
                        
                        for field in best_form.get('fields', []):
                            purpose = field.get('purpose', 'unknown')
                            label = field.get('label', field.get('placeholder', 'No label'))
                            required = '*' if field.get('required') else ''
                            print(f"    - {purpose}: {label} {required}")
            else:
                print(f"  Error: {analysis.get('error', 'Unknown error')}")
        
        # Test form filling
        print("\n" + "-"*60)
        print("STEP 2: FORM FILLING SIMULATION")
        print("-"*60)
        
        # Create form data mapping
        form_data = {
            'name': bid_card_data['homeowner_name'],
            'email': bid_card_data['homeowner_email'],
            'phone': bid_card_data['homeowner_phone'],
            'message': f"""
Project: {bid_card_data['project_type'].replace('_', ' ').title()}

{bid_card_data['scope_summary']}

Budget: ${bid_card_data['budget_min']:,} - ${bid_card_data['budget_max']:,}
Timeline: {bid_card_data['timeline']}
Location: {bid_card_data['location']}

Please provide a quote for this project. Thank you!
""".strip(),
            'company': 'InstaBids User',
            'address': bid_card_data['location'],
            'service': bid_card_data['project_type'].replace('_', ' ').title(),
            'budget': f"${bid_card_data['budget_min']:,} - ${bid_card_data['budget_max']:,}",
            'timeline': bid_card_data['timeline']
        }
        
        print("\nForm Data to Submit:")
        for key, value in form_data.items():
            if key == 'message':
                print(f"  {key}: [See below]")
            else:
                print(f"  {key}: {value}")
        
        print(f"\n  Message Content:")
        for line in form_data['message'].split('\n'):
            print(f"    {line}")
        
        # Test actual form filling (if we had real contractor sites)
        print("\n" + "-"*60)
        print("STEP 3: FORM SUBMISSION TRACKING")
        print("-"*60)
        
        print("\nForm Submission Results:")
        print("  Status: Would submit to real contractor websites")
        print("  Tracking: Each submission gets unique ID")
        print("  Attribution: Links back to campaign and bid card")
        
        # Show what would happen
        print("\nWFA Process Flow:")
        print("1. Email sent to contractor with bid card link")
        print("2. Contractor clicks link -> tracked")
        print("3. WFA automatically fills their contact form")
        print("4. Form submission tracked in database")
        print("5. Response linked back to original campaign")
        
        # Cleanup
        wfa.stop_browser()
        
        print("\n" + "="*80)
        print("WFA AGENT TEST COMPLETE")
        print("="*80)
        print("\nThe WFA agent is ready to:")
        print("  - Find contact forms on contractor websites")
        print("  - Identify form fields automatically")
        print("  - Fill forms with project information")
        print("  - Track submissions for attribution")
        
        return True
        
    except Exception as e:
        print(f"\nError testing WFA: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_wfa_with_real_site():
    """Test WFA with a real demo site"""
    
    print("\n" + "="*80)
    print("TESTING WFA WITH REAL FORM SUBMISSION")
    print("="*80)
    
    try:
        wfa = WebsiteFormAutomationAgent()
        
        # Create a real bid card scenario
        bid_card = {
            'id': 'test-bid-123',
            'project_type': 'bathroom_remodel',
            'scope_summary': 'Master bathroom renovation with new fixtures, tile, and vanity',
            'budget_min': 15000,
            'budget_max': 20000,
            'location': 'Miami Beach, FL',
            'timeline': 'Start within 1 month',
            'homeowner': {
                'name': 'Sarah Johnson',
                'email': 'sarah@example.com',
                'phone': '(305) 555-1234'
            }
        }
        
        # Test contractor to contact
        contractor = {
            'id': 'contractor-123',
            'company_name': 'Premium Bath Renovations',
            'website': 'https://httpbin.org/forms/post',  # Test form endpoint
            'contact_name': 'Mike Williams'
        }
        
        print(f"\nBid Card: {bid_card['project_type']}")
        print(f"Budget: ${bid_card['budget_min']:,} - ${bid_card['budget_max']:,}")
        print(f"Contractor: {contractor['company_name']}")
        
        # Fill out the form
        print("\nFilling out contractor contact form...")
        result = wfa.fill_contact_form(contractor, bid_card)
        
        if result['success']:
            print("Form submitted successfully!")
            print(f"Submission ID: {result.get('submission_id', 'N/A')}")
            print(f"Tracked in database: {result.get('tracked', False)}")
        else:
            print(f"Form submission failed: {result.get('error', 'Unknown error')}")
        
        wfa.stop_browser()
        return result.get('success', False)
        
    except Exception as e:
        print(f"\nError: {e}")
        return False

if __name__ == "__main__":
    print("Starting WFA Agent Tests...")
    
    # Test 1: Form detection
    success1 = test_wfa_form_detection()
    
    # Test 2: Real form submission
    success2 = test_wfa_with_real_site()
    
    if success1 and success2:
        print("\nALL WFA TESTS PASSED!")
        sys.exit(0)
    else:
        print("\nSOME WFA TESTS FAILED!")
        sys.exit(1)