#!/usr/bin/env python3
"""
Test WFA form submission to exact test site
Tests actual form filling on the lawn-care-contractor test site
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.wfa.agent import WebsiteFormAutomationAgent
from playwright.sync_api import sync_playwright
import time

def test_exact_form_submission():
    """Test form submission to your exact test site"""
    
    print("=" * 80)
    print("TESTING EXACT FORM SUBMISSION")
    print("=" * 80)
    print("Testing your actual test site: lawn-care-contractor/index.html")
    
    # Path to your test site
    test_site_path = r"C:\Users\Not John Or Justin\Documents\instabids\test-sites\lawn-care-contractor\index.html"
    test_site_url = f"file:///{test_site_path}"
    
    print(f"Test site URL: {test_site_url}")
    
    # Test contractor data
    contractor = {
        'id': 'test-contractor-wfa',
        'company_name': 'InstaBids Lead Generation',
        'contact_name': 'Sarah Johnson',
        'email': 'projects@instabids.com',
        'website': test_site_url,  # Your exact test site
        'phone': '(407) 555-0199'
    }
    
    # Bid card data
    bid_card_data = {
        'id': 'lawn-care-test-123',
        'bid_document': {
            'all_extracted_data': {
                'project_type': 'lawn_care',
                'location': {
                    'city': 'Orlando',
                    'state': 'FL',
                    'full_location': 'Orlando, FL'
                },
                'budget_min': 150,
                'budget_max': 250,
                'timeline': 'Start immediately',
                'urgency_level': 'urgent',
                'project_description': 'Weekly lawn mowing and maintenance service needed for 0.5 acre residential property. Includes edging, trimming, and leaf removal. Property has irrigation system. Looking for reliable service provider.'
            }
        }
    }
    
    print(f"\nContractor: {contractor['company_name']}")
    print(f"Contact: {contractor['contact_name']}")
    print(f"Website: {contractor['website']}")
    
    print(f"\nProject: Lawn Care Service")
    print(f"Location: Orlando, FL")
    print(f"Budget: ${bid_card_data['bid_document']['all_extracted_data']['budget_min']}-${bid_card_data['bid_document']['all_extracted_data']['budget_max']}/month")
    
    print(f"\nTesting form submission...")
    
    # Method 1: Try with WFA agent
    try:
        print("\n--- Method 1: Using WFA Agent ---")
        wfa = WebsiteFormAutomationAgent()
        
        result = wfa.fill_contact_form(contractor, bid_card_data)
        
        if result['success']:
            print(f"SUCCESS: WFA filled form!")
            print(f"   Form URL: {result['form_url']}")
            print(f"   Fields filled: {result.get('fields_filled', 'unknown')}")
        else:
            print(f"FAILED: {result.get('error')}")
        
        wfa.stop_browser()
        
    except Exception as e:
        print(f"WFA Error: {e}")
    
    # Method 2: Direct Playwright test
    try:
        print(f"\n--- Method 2: Direct Playwright Test ---")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)  # Visible browser
            page = browser.new_page()
            
            print(f"Navigating to: {test_site_url}")
            page.goto(test_site_url, wait_until="networkidle")
            
            print("Page loaded, looking for form...")
            
            # Check if form exists
            form = page.locator('#businessForm')
            if form.count() > 0:
                print("Found business form!")
                
                # Fill the form fields
                print("Filling form fields...")
                
                # Company Name
                page.fill('#companyName', contractor['company_name'])
                print(f"   Company: {contractor['company_name']}")
                
                # Contact Name  
                page.fill('#contactName', contractor['contact_name'])
                print(f"   Contact: {contractor['contact_name']}")
                
                # Email
                page.fill('#email', contractor['email'])
                print(f"   Email: {contractor['email']}")
                
                # Phone
                page.fill('#phone', contractor['phone'])
                print(f"   Phone: {contractor['phone']}")
                
                # Website
                page.fill('#website', 'https://instabids.com')
                print(f"   Website: https://instabids.com")
                
                # Opportunity Type
                page.select_option('#opportunityType', 'lead_generation')
                print(f"   Type: Lead Generation")
                
                # Message
                message = f"""Hi! We have a {bid_card_data['bid_document']['all_extracted_data']['project_type']} project in {bid_card_data['bid_document']['all_extracted_data']['location']['full_location']}.

Project Details:
- Budget: ${bid_card_data['bid_document']['all_extracted_data']['budget_min']}-${bid_card_data['bid_document']['all_extracted_data']['budget_max']}/month
- Timeline: {bid_card_data['bid_document']['all_extracted_data']['timeline']}
- Description: {bid_card_data['bid_document']['all_extracted_data']['project_description']}

The homeowner is pre-qualified and ready to start. This is a lead generation opportunity through InstaBids platform.

View full project details: https://instabids.com/bid-cards/{bid_card_data['id']}

Best regards,
{contractor['contact_name']}
InstaBids Lead Generation"""
                
                page.fill('#message', message)
                print(f"   Message: {len(message)} characters")
                
                # Submit the form
                print("\nSubmitting form...")
                page.click('#submitBtn')
                
                # Wait for submission to complete
                time.sleep(2)
                
                # Check for success message
                success_msg = page.locator('#successMessage')
                if success_msg.is_visible():
                    print("SUCCESS: Form submitted successfully!")
                    print("   Success message is visible")
                else:
                    print("UNCLEAR: No success message visible")
                
                # Check submissions panel
                time.sleep(1)
                submissions = page.locator('.submission-item')
                submission_count = submissions.count()
                
                if submission_count > 0:
                    print(f"VERIFIED: {submission_count} submission(s) found in submissions panel!")
                    
                    # Get the latest submission details
                    latest = submissions.first
                    submission_text = latest.inner_text()
                    print(f"Latest submission preview:")
                    print(f"   {submission_text[:200]}...")
                else:
                    print("WARNING: No submissions found in panel")
                
                # Let user see the result
                print(f"\nForm is now submitted! Check the page visually.")
                print("Press Enter to close browser...")
                input()
                
            else:
                print("ERROR: Could not find business form on page")
            
            browser.close()
            
    except Exception as e:
        print(f"Playwright Error: {e}")
    
    print(f"\n{'='*80}")
    print("FORM SUBMISSION TEST COMPLETE")
    print(f"{'='*80}")
    
    print(f"\nTo verify the submission:")
    print(f"1. Open the test site in your browser: {test_site_url}")
    print(f"2. Scroll down to 'Form Submissions (For Testing)' panel")
    print(f"3. You should see the submission with InstaBids data")
    
    return True


if __name__ == "__main__":
    print("EXACT FORM SUBMISSION TEST")
    print("This will test your actual lawn-care-contractor test site")
    print()
    
    test_exact_form_submission()