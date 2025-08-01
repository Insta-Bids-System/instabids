#!/usr/bin/env python3
"""
Direct form filling test - Tests your exact test site
"""

from playwright.sync_api import sync_playwright
import time
import os

def test_direct_form_fill():
    """Test direct form filling on your test site"""
    
    print("=" * 80)
    print("DIRECT FORM FILLING TEST")
    print("=" * 80)
    
    # Construct the correct file path
    test_site_path = os.path.abspath(r"C:\Users\Not John Or Justin\Documents\instabids\test-sites\lawn-care-contractor\index.html")
    test_site_url = f"file:///{test_site_path.replace(os.sep, '/')}"
    
    print(f"Test site path: {test_site_path}")
    print(f"Test site URL: {test_site_url}")
    
    # Check if file exists
    if not os.path.exists(test_site_path):
        print(f"ERROR: Test site file not found at: {test_site_path}")
        return False
    
    print("File exists, launching browser...")
    
    try:
        with sync_playwright() as p:
            # Launch browser (visible so you can see what happens)
            browser = p.chromium.launch(headless=False, slow_mo=1000)
            page = browser.new_page()
            
            print("Navigating to test site...")
            page.goto(test_site_url, wait_until="domcontentloaded")
            
            # Wait a moment for page to fully load
            time.sleep(2)
            
            print("Page loaded, checking for form...")
            
            # Check if the business form exists
            business_form = page.locator('#businessForm')
            if business_form.count() == 0:
                print("ERROR: Business form not found!")
                browser.close()
                return False
            
            print("Business form found! Filling fields...")
            
            # Clear any existing submissions first
            clear_btn = page.locator('.clear-btn')
            if clear_btn.count() > 0:
                print("Clearing existing submissions...")
                page.evaluate("clearSubmissions()")
                time.sleep(1)
            
            # Fill the form with InstaBids test data
            form_data = {
                'company_name': 'InstaBids Lead Generation',
                'contact_name': 'Sarah Johnson', 
                'email': 'projects@instabids.com',
                'phone': '(407) 555-0199',
                'website': 'https://instabids.com',
                'opportunity_type': 'lead_generation',
                'message': '''Hi! We specialize in connecting quality contractors with pre-qualified homeowners.

We have a lawn care project in Orlando, FL:
- Budget: $150-$250/month
- Timeline: Start immediately  
- Property: 0.5 acre residential
- Services needed: Weekly mowing, edging, trimming, leaf removal

The homeowner is pre-qualified and ready to start. We can provide verified leads for contractors in your service area.

This is a lead generation opportunity through our InstaBids platform. We handle the customer acquisition and provide you with qualified prospects.

Would you be interested in learning more about our contractor network?

Best regards,
Sarah Johnson
InstaBids Lead Generation
(407) 555-0199'''
            }
            
            print("Filling form fields:")
            
            # Fill each field
            page.fill('#companyName', form_data['company_name'])
            print(f"   Company Name: {form_data['company_name']}")
            
            page.fill('#contactName', form_data['contact_name'])
            print(f"   Contact Name: {form_data['contact_name']}")
            
            page.fill('#email', form_data['email'])
            print(f"   Email: {form_data['email']}")
            
            page.fill('#phone', form_data['phone'])
            print(f"   Phone: {form_data['phone']}")
            
            page.fill('#website', form_data['website'])
            print(f"   Website: {form_data['website']}")
            
            page.select_option('#opportunityType', form_data['opportunity_type'])
            print(f"   Opportunity Type: {form_data['opportunity_type']}")
            
            page.fill('#message', form_data['message'])
            print(f"   Message: {len(form_data['message'])} characters")
            
            print("\nForm filled! Submitting...")
            
            # Submit the form
            submit_btn = page.locator('#submitBtn')
            submit_btn.click()
            
            # Wait for submission to process
            time.sleep(3)
            
            # Check for success message
            success_message = page.locator('#successMessage')
            if success_message.is_visible():
                print("SUCCESS: Form submitted successfully!")
                print("   Success message is visible")
            else:
                print("WARNING: Success message not visible")
            
            # Check the submissions panel
            print("\nChecking submissions panel...")
            submissions = page.locator('.submission-item')
            submission_count = submissions.count()
            
            if submission_count > 0:
                print(f"VERIFIED: {submission_count} submission(s) found!")
                
                # Get the text of the first submission
                latest_submission = submissions.first
                submission_text = latest_submission.inner_text()
                
                print(f"\nLatest submission details:")
                print("-" * 50)
                print(submission_text)
                print("-" * 50)
                
                # Verify our data is in there
                if 'InstaBids' in submission_text and 'Sarah Johnson' in submission_text:
                    print("\nSUCCESS: Our InstaBids data is confirmed in the submission!")
                    result = True
                else:
                    print("\nWARNING: Could not verify our data in submission")
                    result = False
                    
            else:
                print("ERROR: No submissions found in panel")
                result = False
            
            print(f"\nTest complete! Browser will stay open for 10 seconds so you can verify...")
            time.sleep(10)
            
            browser.close()
            return result
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False


if __name__ == "__main__":
    print("DIRECT FORM FILLING TEST")
    print("This will fill your lawn-care-contractor test form with InstaBids data")
    print()
    
    success = test_direct_form_fill()
    
    if success:
        print("\nSUCCESS: Form submission verified!")
        print("Your test site form automation is working correctly.")
    else:
        print("\nFAILED: Form submission could not be verified.")
        print("Check the browser output above for details.")