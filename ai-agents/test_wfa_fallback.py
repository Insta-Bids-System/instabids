#!/usr/bin/env python3
"""
WFA Fallback Test - Shows form automation working without Claude
Tests the regular WFA agent with template-based form filling
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.wfa.agent import WebsiteFormAutomationAgent

def test_wfa_fallback():
    """Test WFA with template-based form filling (no Claude required)"""
    
    print("=" * 80)
    print("TESTING WFA FORM AUTOMATION (Template-Based)")
    print("=" * 80)
    print("\nThis tests form automation using templates (no Claude API needed)")
    
    # Initialize regular WFA agent
    wfa = WebsiteFormAutomationAgent()
    
    # Test bid card
    bid_card_data = {
        'id': 'kitchen-miami-fallback-test',
        'bid_document': {
            'all_extracted_data': {
                'project_type': 'kitchen_remodel',
                'location': {
                    'city': 'Miami Beach',
                    'state': 'FL', 
                    'zip_code': '33139',
                    'full_location': 'Miami Beach, FL'
                },
                'budget_min': 35000,
                'budget_max': 45000,
                'timeline': 'Start within 1 month',
                'urgency_level': 'standard',
                'project_description': 'Complete kitchen renovation including custom cabinets, quartz countertops, tile backsplash, and high-end stainless steel appliances. Open concept design preferred.'
            }
        }
    }
    
    # Test contractors
    test_contractors = [
        {
            'id': 'contractor-fallback-1',
            'company_name': 'Miami Kitchen Specialists',  
            'contact_name': 'Roberto Martinez',
            'email': 'roberto@miamikitchen.test',
            'website': 'https://httpbin.org/forms/post',  # Test form endpoint
            'service_types': ['kitchen_remodel'],
            'specialties': ['modern kitchens', 'custom cabinetry'],
            'years_in_business': 12
        },
        {
            'id': 'contractor-fallback-2',
            'company_name': 'Coastal Home Builders',
            'contact_name': 'Jennifer Chen', 
            'email': 'jen@coastal.test',
            'website': 'https://postman-echo.com/post',  # Another test endpoint
            'service_types': ['general_remodeling'],
            'specialties': ['coastal designs', 'hurricane-resistant'],
            'years_in_business': 8
        }
    ]
    
    print(f"\nProject: Kitchen Remodel in Miami Beach")
    print(f"Budget: ${bid_card_data['bid_document']['all_extracted_data']['budget_min']:,} - ${bid_card_data['bid_document']['all_extracted_data']['budget_max']:,}")
    print(f"Testing template-based form filling with {len(test_contractors)} contractors...\n")
    
    results = []
    
    for i, contractor in enumerate(test_contractors, 1):
        print(f"{'='*60}")
        print(f"CONTRACTOR {i}: {contractor['company_name']}")
        print(f"{'='*60}")
        print(f"Contact: {contractor['contact_name']}")
        print(f"Website: {contractor['website']}")
        print(f"Specialties: {', '.join(contractor['specialties'])}")
        
        print(f"\nUsing template-based form filling...")
        print("Steps:")
        print("1. Analyze website for contact forms") 
        print("2. Use template message with project details")
        print("3. Fill form fields automatically")
        print("4. Submit form")
        
        try:
            # Test website analysis
            print(f"\nAnalyzing website for forms...")
            analysis = wfa.analyze_website_for_form(contractor)
            
            if analysis['success'] and analysis['has_contact_form']:
                print(f"SUCCESS: Found {analysis['forms_found']} form(s)")
                
                # Test form filling  
                print(f"Filling form with project details...")
                result = wfa.fill_contact_form(contractor, bid_card_data)
                
                if result['success']:
                    print(f"SUCCESS: Form filled and submitted!")
                    print(f"   Form URL: {result['form_url']}")
                    print(f"   Fields Filled: {result['fields_filled']}")
                    
                    results.append({
                        'contractor': contractor['company_name'],
                        'success': True,
                        'form_url': result['form_url'],
                        'fields_filled': result['fields_filled']
                    })
                else:
                    print(f"FAILED: {result.get('error')}")
                    results.append({
                        'contractor': contractor['company_name'],
                        'success': False,
                        'error': result.get('error')
                    })
            else:
                print(f"FAILED: No contact form found")
                results.append({
                    'contractor': contractor['company_name'],
                    'success': False,
                    'error': 'No contact form found'
                })
                
        except Exception as e:
            print(f"ERROR: {e}")
            results.append({
                'contractor': contractor['company_name'],
                'success': False,
                'error': str(e)
            })
        
        print(f"\n" + "-" * 60)
    
    # Clean up
    wfa.stop_browser()
    
    # Summary
    print(f"\n{'='*80}")
    print("WFA TEMPLATE-BASED TEST RESULTS")
    print(f"{'='*80}")
    
    successful_forms = [r for r in results if r.get('success')]
    
    print(f"\nForms Successfully Filled: {len(successful_forms)}")
    print(f"Total Attempted: {len(test_contractors)}")
    
    if successful_forms:
        print(f"\nSuccessful Form Submissions:")
        for result in successful_forms:
            print(f"  - {result['contractor']}")
            print(f"    Form URL: {result['form_url']}")
            print(f"    Fields Filled: {result.get('fields_filled', 0)}")
        
        print(f"\nWFA Features Demonstrated:")
        print("- Automatic website form detection")
        print("- Template-based message generation")
        print("- Automatic form field filling")
        print("- Form submission with project details")
        print("- Professional message with bid card URL")
        
        return True
    else:
        print("\nNo forms were filled successfully")
        for result in results:
            if not result.get('success'):
                print(f"  - {result['contractor']}: {result.get('error')}")
        return False


def show_generated_message():
    """Show what message would be generated"""
    
    wfa = WebsiteFormAutomationAgent()
    
    bid_card_data = {
        'id': 'demo-kitchen-123',
        'bid_document': {
            'all_extracted_data': {
                'project_type': 'kitchen_remodel',
                'location': {
                    'city': 'Miami Beach',
                    'state': 'FL',
                    'full_location': 'Miami Beach, FL'
                },
                'budget_min': 35000,
                'budget_max': 45000,
                'timeline': 'Start within 1 month',
                'urgency_level': 'standard',
                'project_description': 'Complete kitchen renovation including custom cabinets, quartz countertops, and high-end appliances.'
            }
        }
    }
    
    contractor = {
        'company_name': 'Test Contractor Inc',
        'contact_name': 'John Smith'
    }
    
    print("\n" + "="*60)
    print("SAMPLE GENERATED MESSAGE")
    print("="*60)
    
    form_data = wfa._prepare_form_data(contractor, bid_card_data)
    
    print(f"Subject: Professional project inquiry")
    print(f"From: {form_data['name']} ({form_data['email']})")
    print(f"Phone: {form_data['phone']}")
    print(f"\nMessage Content:")
    print("-" * 40)
    print(form_data['message'])
    print("-" * 40)
    
    print(f"\nKey Features:")
    print("- Professional contact information")
    print("- Detailed project description")
    print("- Budget range included")
    print("- Timeline specified") 
    print("- Direct link to bid card")
    print("- InstaBids branding")


if __name__ == "__main__":
    print("WFA TEMPLATE-BASED FORM AUTOMATION TEST")
    print("This tests form automation without requiring Claude API")
    print()
    
    # Show sample message first
    show_generated_message()
    
    # Then test form filling
    success = test_wfa_fallback()
    
    if success:
        print(f"\nWFA TEMPLATE-BASED SUCCESS!")
        print("Form automation is working with professional templates.")
        print("Each contractor receives a detailed project inquiry.")
    else:
        print(f"\nWFA test encountered issues - check error messages above.")