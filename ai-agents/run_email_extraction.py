#!/usr/bin/env python3
"""
Run Email Extraction on Contractors Missing Emails
Uses Playwright to scrape contractor websites for contact emails
"""

from agents.email_extraction.agent import EmailExtractionAgent
import json
from datetime import datetime


def run_email_extraction_batch():
    """Run email extraction on contractors needing emails"""
    print("EMAIL EXTRACTION CAMPAIGN")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize agent
    agent = EmailExtractionAgent()
    
    # Get current status
    status = agent.get_extraction_status()
    print("CURRENT STATUS:")
    print(f"  Total Contractors: {status.get('total_contractors', 0)}")
    print(f"  With Emails: {status.get('with_emails', 0)} ({status.get('email_coverage', 0):.1f}%)")
    print(f"  Needing Extraction: {status.get('needing_extraction', 0)}")
    print()
    
    if status.get('needing_extraction', 0) == 0:
        print("No contractors need email extraction!")
        return
    
    # Process in batches to avoid timeouts
    batch_size = 5
    total_to_process = min(25, status.get('needing_extraction', 0))  # Process up to 25
    batches = (total_to_process + batch_size - 1) // batch_size  # Ceiling division
    
    print(f"EXTRACTION PLAN:")
    print(f"  Processing: {total_to_process} contractors")
    print(f"  Batch Size: {batch_size}")
    print(f"  Total Batches: {batches}")
    print()
    
    all_results = {
        'total_processed': 0,
        'emails_found': 0,
        'emails_updated': 0,
        'contractors': []
    }
    
    # Process each batch
    for batch_num in range(batches):
        print(f"\nBATCH {batch_num + 1}/{batches}")
        print("-" * 30)
        
        # Run extraction for this batch
        result = agent.extract_emails_from_contractors(limit=batch_size)
        
        if result.get('success'):
            # Update totals
            all_results['total_processed'] += result.get('total_processed', 0)
            all_results['emails_found'] += result.get('emails_found', 0)
            all_results['emails_updated'] += result.get('emails_updated', 0)
            
            # Show batch results
            print(f"Processed: {result.get('total_processed', 0)}")
            print(f"Emails Found: {result.get('emails_found', 0)}")
            print(f"Database Updated: {result.get('emails_updated', 0)}")
            
            # Show contractor details
            for contractor in result.get('contractors', []):
                if contractor.get('primary_email'):
                    print(f"  ✓ {contractor['company_name']}: {contractor['primary_email']}")
                else:
                    print(f"  ✗ {contractor['company_name']}: No email found")
                
                all_results['contractors'].append(contractor)
        else:
            print(f"Batch failed: {result.get('error', 'Unknown error')}")
        
        # Don't process more if we've reached our target
        if all_results['total_processed'] >= total_to_process:
            break
    
    # Final summary
    print("\n" + "=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)
    print(f"Total Contractors Processed: {all_results['total_processed']}")
    print(f"Emails Successfully Found: {all_results['emails_found']}")
    print(f"Database Records Updated: {all_results['emails_updated']}")
    print(f"Success Rate: {(all_results['emails_found'] / all_results['total_processed'] * 100):.1f}%" if all_results['total_processed'] > 0 else "0%")
    
    # Get updated status
    print("\nUPDATED DATABASE STATUS:")
    new_status = agent.get_extraction_status()
    print(f"  Total Contractors: {new_status.get('total_contractors', 0)}")
    print(f"  With Emails: {new_status.get('with_emails', 0)} ({new_status.get('email_coverage', 0):.1f}%)")
    print(f"  Still Needing Extraction: {new_status.get('needing_extraction', 0)}")
    
    # Save results to file
    results_file = f"email_extraction_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults saved to: {results_file}")
    
    return all_results


if __name__ == "__main__":
    print("Starting Email Extraction Agent...")
    print("This will visit contractor websites and extract email addresses")
    print("Using headless browser automation (Playwright)")
    print()
    
    results = run_email_extraction_batch()
    
    print("\nEmail extraction campaign complete!")