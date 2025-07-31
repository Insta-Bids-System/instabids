"""
Live WFA Demo: Actually fill contractor form with rich preview link
"""
import asyncio
import sys
import os
from playwright.async_api import async_playwright

async def run_live_wfa_demo():
    """Run live WFA demonstration with actual form filling"""
    print("LIVE WFA DEMONSTRATION")
    print("=" * 50)
    print("This will open a browser and show:")
    print("1. Contractor website form")
    print("2. WFA filling the form with rich preview link")
    print("3. How the rich preview displays")
    print()
    
    # Prepare form data
    bid_card_id = "d57cd6cd-f424-460e-9c15-7a08c09507f3"
    rich_preview_url = f"http://localhost:8000/api/bid-cards/{bid_card_id}/preview"
    
    form_data = {
        "company_name": "Instabids",
        "contact_name": "Sales Team",
        "email": "partnerships@instabids.com", 
        "phone": "(555) 123-BIDS",
        "website": "https://instabids.com",
        "opportunity_type": "lead_generation",
        "message": f"""STOP PAYING FOR LEADS!

We're Instabids - the AI-powered platform DESTROYING Angie's List and Google's lead monopoly.

✅ FREE qualified projects in your area
✅ Direct homeowner communication  
✅ Only pay when you WIN the job

HERE'S A REAL PROJECT YOU CAN BID ON RIGHT NOW:
{rich_preview_url}

This is a lawn project ($200-$400) in your area.

CLICK THE LINK ABOVE - It shows a beautiful visual preview with project details, budget, timeline, and location!

Ready to cut your customer acquisition costs by 90%?

Reply to get early access to Instabids Pro."""
    }
    
    async with async_playwright() as p:
        print("Opening browser...")
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        page = await browser.new_page()
        
        try:
            # Step 1: Navigate to contractor website
            contractor_url = "file:///C:/Users/Not John Or Justin/Documents/instabids/test-sites/lawn-care-contractor/index.html"
            print(f"Navigating to: {contractor_url}")
            await page.goto(contractor_url)
            await page.wait_for_timeout(2000)
            
            print("✅ Contractor website loaded - Green Lawn Pro")
            print()
            
            # Step 2: Fill out the form as Instabids
            print("🤖 WFA Bot now filling out the form...")
            
            # Fill company name
            print(f"Filling company name: {form_data['company_name']}")
            await page.fill('#companyName', form_data['company_name'])
            await page.wait_for_timeout(500)
            
            # Fill contact name
            print(f"Filling contact name: {form_data['contact_name']}")
            await page.fill('#contactName', form_data['contact_name'])
            await page.wait_for_timeout(500)
            
            # Fill email
            print(f"Filling email: {form_data['email']}")
            await page.fill('#email', form_data['email'])
            await page.wait_for_timeout(500)
            
            # Fill phone
            print(f"Filling phone: {form_data['phone']}")
            await page.fill('#phone', form_data['phone'])
            await page.wait_for_timeout(500)
            
            # Fill website
            print(f"Filling website: {form_data['website']}")
            await page.fill('#website', form_data['website'])
            await page.wait_for_timeout(500)
            
            # Select opportunity type
            print(f"Selecting opportunity type: {form_data['opportunity_type']}")
            await page.select_option('#opportunityType', form_data['opportunity_type'])
            await page.wait_for_timeout(500)
            
            # Fill message with rich preview link
            print("Filling message with RICH PREVIEW LINK...")
            await page.fill('#message', form_data['message'])
            await page.wait_for_timeout(1000)
            
            print("✅ Form filled with rich preview link!")
            print(f"Rich Preview URL in message: {rich_preview_url}")
            print()
            
            # Step 3: Highlight the rich preview link
            print("Highlighting the rich preview link in the message...")
            await page.evaluate("""
                const messageField = document.getElementById('message');
                const linkStart = messageField.value.indexOf('http://localhost:8000/api/bid-cards/');
                if (linkStart !== -1) {
                    messageField.focus();
                    messageField.setSelectionRange(linkStart, linkStart + 77);
                }
            """)
            await page.wait_for_timeout(3000)
            
            # Step 4: Open rich preview in new tab
            print("Opening rich preview in new tab to show what contractors see...")
            preview_page = await browser.new_page()
            await preview_page.goto(rich_preview_url)
            await preview_page.wait_for_timeout(2000)
            
            print("✅ Rich preview opened!")
            print()
            print("NOW YOU CAN SEE:")
            print("1. LEFT TAB: Contractor form filled by WFA")
            print("   - Instabids company info")
            print("   - Rich preview link in message")
            print("2. RIGHT TAB: Rich visual bid card preview")
            print("   - Beautiful design with project details")
            print("   - This is what 'pops up' when link is shared!")
            print()
            
            # Wait for user to see both tabs
            print("Press Enter to continue or Ctrl+C to exit...")
            input()
            
            # Step 5: Submit the form (optional)
            print("Submitting form? (y/n): ", end="")
            submit = input().lower().strip()
            
            if submit == 'y':
                await page.click('#businessForm button[type="submit"]')
                print("✅ Form submitted!")
                print("Contractor would now receive this outreach with rich preview link")
                await page.wait_for_timeout(2000)
            
        except Exception as e:
            print(f"Error during demo: {e}")
        
        finally:
            print("Demo complete. Closing browser in 5 seconds...")
            await page.wait_for_timeout(5000)
            await browser.close()

def main():
    """Run the live demo"""
    print("Starting live WFA demonstration...")
    print("This will show the complete flow of:")
    print("- WFA filling contractor forms")
    print("- Rich preview links in action")
    print("- How bid cards 'pop up' visually")
    print()
    
    try:
        asyncio.run(run_live_wfa_demo())
        
        print("\n" + "=" * 50)
        print("LIVE DEMO COMPLETE!")
        print("=" * 50)
        print("What you just saw:")
        print("✅ WFA bot filling contractor form with Instabids info")
        print("✅ Rich preview URL included in outreach message")
        print("✅ Visual bid card preview opening in new tab")
        print("✅ Professional design that 'pops up' as requested")
        print()
        print("This demonstrates the complete solution:")
        print("- No more plain links")
        print("- Rich visual previews everywhere")  
        print("- Bid cards 'pop up' when shared")
        print("- Higher contractor engagement expected")
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"Demo failed: {e}")
        print("Make sure Playwright is installed: pip install playwright")
        print("Then run: playwright install chromium")

if __name__ == "__main__":
    main()