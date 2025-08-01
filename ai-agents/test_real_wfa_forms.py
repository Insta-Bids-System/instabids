#!/usr/bin/env python3
"""
REAL WFA Test - Actually fills website forms with unique contractor data
This will use the WFA agent to fill actual website contact forms
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.wfa.claude_enhanced_agent import ClaudeEnhancedWFA

def test_real_wfa_form_filling():
    """Test WFA with real websites and bid cards"""
    
    print("=" * 80)
    print("TESTING REAL WFA FORM AUTOMATION")
    print("=" * 80)
    print("\nThis will use Claude to understand website forms and fill them automatically")
    
    # Initialize WFA agent
    wfa = ClaudeEnhancedWFA()
    
    # Real bid card data
    bid_card_data = {
        'id': 'kitchen-miami-wfa-test',
        'project_type': 'kitchen_remodel',
        'location': 'Miami Beach, FL',
        'budget_min': 35000,
        'budget_max': 45000,
        'timeline': 'Start within 1 month',
        'urgency_level': 'standard',
        'scope_details': 'Complete kitchen renovation including custom cabinets, quartz countertops, tile backsplash, and high-end stainless steel appliances. Open concept design preferred.',
        'external_url': 'https://instabids.com/bid-cards/kitchen-miami-wfa-test',
        'homeowner': {
            'name': 'Sarah Johnson'
        }
    }
    
    # Test contractors with different websites
    test_contractors = [
        {
            'id': 'contractor-wfa-1',
            'company_name': 'Miami Kitchen Pros',
            'contact_name': 'Roberto Martinez',
            'email': 'roberto@miamikitchen.test',
            'website': 'https://httpbin.org/forms/post',  # Simple test form
            'service_types': ['kitchen_remodel'],
            'specialties': ['modern kitchens', 'custom cabinetry'],
            'years_in_business': 12
        },
        {
            'id': 'contractor-wfa-2', 
            'company_name': 'Coastal Construction',
            'contact_name': 'Jennifer Chen',
            'email': 'jen@coastal.test',
            'website': 'https://postman-echo.com/post',  # Another test endpoint
            'service_types': ['general_remodeling'],
            'specialties': ['coastal designs', 'hurricane-resistant'],
            'years_in_business': 8
        }
    ]
    
    print(f"\nProject: {bid_card_data['project_type'].replace('_', ' ').title()}")
    print(f"Location: {bid_card_data['location']}")
    print(f"Budget: ${bid_card_data['budget_min']:,} - ${bid_card_data['budget_max']:,}")
    print(f"Testing form automation with {len(test_contractors)} contractors...\n")
    
    results = []
    
    for i, contractor in enumerate(test_contractors, 1):
        print(f"{'='*60}")
        print(f"CONTRACTOR {i}: {contractor['company_name']}")
        print(f"{'='*60}")
        print(f"Contact: {contractor['contact_name']}")
        print(f"Website: {contractor['website']}")
        print(f"Specialties: {', '.join(contractor['specialties'])}")
        
        print(f"\nClaude analyzing website form...")
        print("Steps:")
        print("1. Navigate to contractor website")
        print("2. Claude analyzes HTML to understand form fields")
        print("3. Claude creates personalized content for each field")
        print("4. Fill form automatically with project details")
        print("5. Submit form")
        
        try:
            # Use the Claude-enhanced WFA to fill the form
            result = wfa.fill_contact_form(contractor, bid_card_data)
            
            if result['success']:
                print(f"\nSUCCESS: Form filled and submitted!")
                print(f"   Submission ID: {result['submission_id']}")
                print(f"   Website: {result['website']}")
                print(f"   Claude Analysis: {result.get('claude_analyzed', False)}")
                print(f"   Fields Filled: {result.get('fields_filled', 0)}")
                
                results.append({
                    'contractor': contractor['company_name'],
                    'success': True,
                    'submission_id': result['submission_id'],
                    'website': result['website']
                })
            else:
                print(f"\nFAILED: {result.get('error')}")
                results.append({
                    'contractor': contractor['company_name'],
                    'success': False,
                    'error': result.get('error')
                })
                
        except Exception as e:
            print(f"\nERROR: {e}")
            results.append({
                'contractor': contractor['company_name'],
                'success': False,
                'error': str(e)
            })
        
        print(f"\n" + "-" * 60)
    
    # Clean up browser
    wfa.stop_browser()
    
    # Summary
    print(f"\n{'='*80}")
    print("WFA FORM AUTOMATION TEST RESULTS")
    print(f"{'='*80}")
    
    successful_forms = [r for r in results if r.get('success')]
    
    print(f"\nForms Successfully Filled: {len(successful_forms)}")
    print(f"Total Attempted: {len(test_contractors)}")
    
    if successful_forms:
        print(f"\nSuccessful Form Submissions:")
        for result in successful_forms:
            print(f"  - {result['contractor']}")
            print(f"    Website: {result['website']}")
            print(f"    Submission ID: {result['submission_id']}")
        
        print(f"\nClaude WFA Features Demonstrated:")
        print("- Intelligent form field understanding")
        print("- Personalized content generation for each contractor")
        print("- Automatic form filling and submission")
        print("- Unique project details for each submission")
        
        return True
    else:
        print("\nNo forms were filled successfully")
        for result in results:
            if not result.get('success'):
                print(f"  - {result['contractor']}: {result.get('error')}")
        return False


def test_simple_form_understanding():
    """Test just the Claude form understanding part"""
    
    print("\n" + "="*60)
    print("TESTING CLAUDE FORM UNDERSTANDING")
    print("="*60)
    
    wfa = ClaudeEnhancedWFA()
    
    # Sample HTML form
    sample_html = """
    <form action="/contact" method="post">
        <div>
            <label for="name">Your Name</label>
            <input type="text" id="name" name="name" required>
        </div>
        <div>
            <label for="email">Email Address</label>
            <input type="email" id="email" name="email" required>
        </div>
        <div>
            <label for="phone">Phone Number</label>
            <input type="tel" id="phone" name="phone">
        </div>
        <div>
            <label for="company">Company Name</label>
            <input type="text" id="company" name="company">
        </div>
        <div>
            <label for="message">Project Details</label>
            <textarea id="message" name="message" rows="5" required></textarea>
        </div>
        <button type="submit">Send Message</button>
    </form>
    """
    
    print("Sample form HTML provided to Claude...")
    print("Testing Claude's ability to understand form structure...")
    
    # Mock page object for testing
    class MockPage:
        def content(self):
            return sample_html
    
    mock_page = MockPage()
    
    try:
        # Test Claude's form analysis
        analysis = wfa.analyze_form_with_claude(mock_page, sample_html)
        
        print(f"\nClaude's Form Analysis:")
        print(f"Has Contact Form: {analysis.get('form_analysis', {}).get('has_contact_form', False)}")
        print(f"Form Purpose: {analysis.get('form_analysis', {}).get('form_purpose', 'Unknown')}")
        
        fields = analysis.get('form_analysis', {}).get('fields', [])
        print(f"Fields Identified: {len(fields)}")
        
        for field in fields:
            print(f"  - {field.get('purpose', 'unknown')}: {field.get('selector', 'no selector')}")
        
        # Test strategy creation
        bid_card = {
            'project_type': 'kitchen_remodel',
            'location': 'Miami Beach, FL',
            'budget_min': 35000,
            'budget_max': 45000,
            'timeline': 'Start within 1 month',
            'scope_details': 'Complete kitchen renovation'
        }
        
        print(f"\nTesting strategy creation...")
        strategy = wfa.create_form_filling_strategy(analysis, bid_card)
        
        print(f"Strategy Created: {bool(strategy.get('field_values'))}")
        if strategy.get('field_values'):
            print("Field Values Generated:")
            for field, value in strategy['field_values'].items():
                print(f"  - {field}: {value[:50]}{'...' if len(str(value)) > 50 else ''}")
        
        return True
        
    except Exception as e:
        print(f"Claude form understanding failed: {e}")
        return False


if __name__ == "__main__":
    print("REAL WFA FORM AUTOMATION TEST")
    print("This will test Claude's ability to understand and fill website forms")
    print()
    
    # First test Claude's form understanding
    understanding_success = test_simple_form_understanding()
    
    if understanding_success:
        print(f"\n{'='*80}")
        # Then test real form filling (if form understanding works)
        success = test_real_wfa_form_filling()
        
        if success:
            print(f"\nWFA FORM AUTOMATION SUCCESS!")
            print("Claude successfully:")
            print("- Analyzed website forms")
            print("- Generated personalized content")
            print("- Filled forms automatically")
            print("- Submitted forms with project details")
        else:
            print(f"\nWFA form filling failed")
    else:
        print(f"\nClaude form understanding failed - skipping form filling test")