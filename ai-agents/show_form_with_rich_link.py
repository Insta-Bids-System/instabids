"""
Show contractor form filling with rich preview link
"""
import webbrowser
import time
import requests

def show_contractor_form_filling():
    """Demonstrate form filling with rich preview"""
    print("INSTABIDS WFA CONTRACTOR OUTREACH DEMO")
    print("=" * 50)
    
    # Data that WFA would fill
    company_data = {
        "company_name": "Instabids",
        "contact_name": "Sales Team", 
        "email": "partnerships@instabids.com",
        "phone": "(555) 123-BIDS",
        "website": "https://instabids.com",
        "opportunity_type": "lead_generation"
    }
    
    # Rich preview URL
    bid_card_id = "d57cd6cd-f424-460e-9c15-7a08c09507f3"
    rich_preview_url = f"http://localhost:8000/api/bid-cards/{bid_card_id}/preview"
    
    # Sales message with rich preview link
    sales_message = f"""STOP PAYING FOR LEADS! 

We're Instabids - the AI-powered platform DESTROYING Angie's List and Google's lead monopoly.

No more $50-200 per lead
No more competing with 10+ contractors  
No more fake leads

FREE qualified projects in your area
Direct homeowner communication
Only pay when you WIN the job

HERE'S A REAL PROJECT YOU CAN BID ON RIGHT NOW:
{rich_preview_url}

This is a lawn project ($200-$400) - see the full details above.

CLICK THE LINK ABOVE - It shows a beautiful visual preview with project details, budget, timeline, and location. This is exactly what you'll see when shared in emails, SMS, and social media!

Ready to cut your customer acquisition costs by 90%? 

Reply to get early access to Instabids Pro."""
    
    print("STEP 1: WFA fills Green Lawn Pro's business form with:")
    print(f"Company: {company_data['company_name']}")
    print(f"Contact: {company_data['contact_name']}")
    print(f"Email: {company_data['email']}")
    print(f"Phone: {company_data['phone']}")
    print()
    
    print("STEP 2: Message includes rich preview link:")
    print(f"Rich Preview URL: {rich_preview_url}")
    print()
    
    print("STEP 3: Testing rich preview...")
    try:
        response = requests.get(rich_preview_url)
        if response.status_code == 200:
            print("SUCCESS: Rich preview is working!")
            print("When contractors click this link, they see:")
            print("- Visual bid card with project details")
            print("- Budget: $200 - $400")
            print("- Timeline: Within 1 week") 
            print("- Professional Instabids branding")
            print()
        else:
            print(f"ERROR: Preview not working - {response.status_code}")
    except Exception as e:
        print(f"ERROR: Could not test preview - {e}")
    
    print("STEP 4: Opening rich preview in browser...")
    print(f"Opening: {rich_preview_url}")
    print()
    print("This is what contractors see when they receive our outreach!")
    print("The bid card 'pops up' visually as requested.")
    
    # Open the rich preview in browser
    try:
        webbrowser.open(rich_preview_url)
        print("Browser opened with rich preview!")
    except Exception as e:
        print(f"Could not open browser: {e}")
    
    print()
    print("WHAT YOU SHOULD SEE IN THE BROWSER:")
    print("- Beautiful gradient header with project icon")
    print("- Project title: 'Lawn'")
    print("- Budget highlight: '$200 - $400'")
    print("- Timeline: 'Within 1 week'")
    print("- Professional design with call-to-action")
    print("- This is the visual preview that 'pops up'!")
    
    return rich_preview_url

def show_contractor_website():
    """Also open the contractor website to show the complete flow"""
    print("\nSTEP 5: Opening contractor website...")
    
    # Create the contractor website path
    contractor_site = "C:\\Users\\Not John Or Justin\\Documents\\instabids\\test-sites\\lawn-care-contractor\\index.html"
    
    try:
        webbrowser.open(f"file:///{contractor_site}")
        print("Contractor website opened!")
        print()
        print("WHAT YOU SHOULD SEE:")
        print("- Green Lawn Pro website") 
        print("- Business opportunity form")
        print("- This is where WFA would fill Instabids info")
        print("- The message field would contain the rich preview link")
    except Exception as e:
        print(f"Could not open contractor site: {e}")

def main():
    """Run the demonstration"""
    rich_preview_url = show_contractor_form_filling()
    show_contractor_website()
    
    print("\n" + "=" * 50)
    print("DEMONSTRATION COMPLETE!")
    print("=" * 50)
    print("You should now see TWO browser tabs:")
    print()
    print("1. RICH PREVIEW TAB:")
    print("   - Beautiful visual bid card")
    print("   - This is what 'pops up' when link is shared")
    print("   - Professional design with project details")
    print()
    print("2. CONTRACTOR WEBSITE TAB:")
    print("   - Green Lawn Pro business form")
    print("   - This is where WFA fills our outreach")
    print("   - Message field would contain the rich preview link")
    print()
    print("THE FLOW:")
    print("1. WFA fills contractor form with rich preview link")
    print("2. Contractor receives form submission")
    print("3. Contractor clicks link and sees visual bid card") 
    print("4. Bid card 'pops up' beautifully as requested!")
    print()
    print(f"Rich Preview URL: {rich_preview_url}")

if __name__ == "__main__":
    main()