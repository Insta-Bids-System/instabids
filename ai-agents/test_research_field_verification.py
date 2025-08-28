"""
Test to verify that research mode fills all 40-50 contractor fields properly
"""
import requests
import json
from config.service_urls import get_backend_url

def test_research_field_population():
    payload = {
        'message': 'Hi, I am Justin with JM Holiday Lighting. We specialize in professional Christmas light installation in Fort Lauderdale.',
        'session_id': 'test-research-fields',
        'contractor_lead_id': 'test-lead-123'
    }

    print("Testing research field population for JM Holiday Lighting...")
    response = requests.post(f'{get_backend_url()}/api/coia/landing', json=payload, timeout=45)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return

    data = response.json()

    print('\n=== CONTRACTOR PROFILE DATA ===')
    if 'contractor_profile' in data:
        profile = data['contractor_profile']
        print(f'Profile fields filled: {len(profile)} fields')
        for key, value in profile.items():
            if value:  # Only show non-empty fields
                print(f'  {key}: {value}')
    else:
        print('No contractor profile found')

    print('\n=== RESEARCH FINDINGS ===')
    if 'research_findings' in data and data['research_findings']:
        findings = data['research_findings']
        print(f'Research status: {findings.get("status", "unknown")}')
        if 'raw_data' in findings:
            raw = findings['raw_data']
            if 'auto_generated_profile' in raw:
                auto_profile = raw['auto_generated_profile']
                print(f'Auto-profile completeness: {auto_profile.get("completeness_score", 0)}%')
                print('Auto-profile fields:')
                for key, value in auto_profile.items():
                    if value and key != 'profile_insights':
                        print(f'  {key}: {value}')
                        
                # Check specific expected fields
                expected_fields = [
                    'business_name', 'phone', 'address', 'website', 
                    'google_rating', 'verified_business', 'completeness_score'
                ]
                found_fields = sum(1 for field in expected_fields if auto_profile.get(field))
                print(f'\nExpected fields found: {found_fields}/{len(expected_fields)}')
                
                if auto_profile.get('profile_insights'):
                    print('\nProfile insights:')
                    for insight in auto_profile['profile_insights']:
                        print(f'  - {insight}')
    else:
        print('No research findings')

    print('\n=== GOOGLE DATA VERIFICATION ===')
    if 'research_findings' in data and data['research_findings'].get('raw_data'):
        raw = data['research_findings']['raw_data']
        if 'google_business' in raw:
            google_data = raw['google_business']
            print('Google Business data:')
            for key, value in google_data.items():
                if value:
                    print(f'  {key}: {value}')
        else:
            print('No Google business data found')

if __name__ == "__main__":
    test_research_field_population()