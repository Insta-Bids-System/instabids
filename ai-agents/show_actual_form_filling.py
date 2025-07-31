"""
Show actual form filling with bid card link in message
"""
import asyncio
from playwright.async_api import async_playwright
import webbrowser
import time

async def show_form_filling_with_bid_card_link():
    """Actually fill the form and show the bid card link in the message"""
    print("ACTUAL FORM FILLING DEMONSTRATION")
    print("=" * 50)
    print("Opening browser to show:")
    print("1. Real contractor website") 
    print("2. WFA filling the form")
    print("3. Bid card link visible in message field")
    print("4. What happens when you click the link")
    print()
    
    # Form data with rich preview link
    bid_card_id = "d57cd6cd-f424-460e-9c15-7a08c09507f3"
    rich_preview_url = f"http://localhost:8000/api/bid-cards/{bid_card_id}/preview"
    
    sales_message = f"""STOP PAYING FOR LEADS!

We're Instabids - the AI-powered platform destroying Angie's List.

No more $50-200 per lead
No more competing with 10+ contractors
No more fake leads

FREE qualified projects in your area
Direct homeowner communication
Only pay when you WIN the job

HERE'S A REAL PROJECT YOU CAN BID ON RIGHT NOW:
{rich_preview_url}

This is a lawn project ($200-$400) in your area - see the full details by clicking the link above.

Ready to cut your customer acquisition costs by 90%?

Reply to get early access to Instabids Pro."""

    async with async_playwright() as p:
        print("Opening browser...")
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page()
        
        try:
            # Navigate to contractor website
            contractor_url = "file:///C:/Users/Not John Or Justin/Documents/instabids/test-sites/lawn-care-contractor/index.html"
            print(f"Loading contractor website: Green Lawn Pro")
            await page.goto(contractor_url)
            await page.wait_for_load_state('networkidle')
            
            print("SUCCESS: Contractor website loaded")
            print()
            
            # Fill the form step by step
            print("FILLING FORM AS INSTABIDS:")
            
            print("- Company Name: Instabids")
            await page.fill('#companyName', 'Instabids')
            await page.wait_for_timeout(800)
            
            print("- Contact: Sales Team")
            await page.fill('#contactName', 'Sales Team')
            await page.wait_for_timeout(800)
            
            print("- Email: partnerships@instabids.com")
            await page.fill('#email', 'partnerships@instabids.com')
            await page.wait_for_timeout(800)
            
            print("- Phone: (555) 123-BIDS")
            await page.fill('#phone', '(555) 123-BIDS')
            await page.wait_for_timeout(800)
            
            print("- Website: https://instabids.com")
            await page.fill('#website', 'https://instabids.com')
            await page.wait_for_timeout(800)
            
            print("- Opportunity Type: Lead Generation")
            await page.select_option('#opportunityType', 'lead_generation')
            await page.wait_for_timeout(800)
            
            print("- Message with BID CARD LINK:")
            await page.fill('#message', sales_message)
            await page.wait_for_timeout(1000)
            
            print()
            print("FORM FILLED! Now you can see:")
            print("1. All Instabids information in the form fields")
            print("2. The message contains the rich preview URL:")
            print(f"   {rich_preview_url}")
            print("3. This is what the contractor will receive")
            print()
            
            # Highlight the URL in the message field
            print("Highlighting the bid card link in the message...")
            await page.evaluate(f"""
                const messageField = document.getElementById('message');
                const linkStart = messageField.value.indexOf('{rich_preview_url}');
                if (linkStart !== -1) {{
                    messageField.focus();
                    messageField.setSelectionRange(linkStart, linkStart + {len(rich_preview_url)});
                    messageField.style.backgroundColor = '#ffeb3b';
                }}
            """)
            
            print("BID CARD LINK IS NOW HIGHLIGHTED IN YELLOW!")
            print()
            print("Press Enter to open the bid card link in a new tab...")
            input()
            
            # Open the bid card link in a new tab
            print("Opening bid card preview in new tab...")
            preview_page = await browser.new_page()
            await preview_page.goto(rich_preview_url)
            await preview_page.wait_for_load_state('networkidle')
            
            print()
            print("NOW YOU CAN SEE BOTH:")
            print("LEFT TAB: Contractor form with bid card link in message")
            print("RIGHT TAB: What the bid card link shows when clicked")
            print()
            print("This demonstrates:")
            print("- WFA fills contractor forms with our info")
            print("- Message includes rich preview link")
            print("- Link shows visual bid card instead of plain URL")
            print("- Contractors see professional project details")
            print()
            
            print("Press Enter to submit the form (optional)...")
            submit_choice = input()
            
            if submit_choice.strip() == "":
                print("Submitting form...")
                await page.click('button[type="submit"]')
                print("FORM SUBMITTED!")
                print("Contractor would now receive this business opportunity")
                print("with the rich bid card link embedded in the message!")
                await page.wait_for_timeout(2000)
            
            print()
            print("Press Enter to close browser...")
            input()
            
        except Exception as e:
            print(f"Error: {e}")
            print("Make sure the server is running on localhost:8000")
        
        finally:
            await browser.close()

def main():
    """Run the demonstration"""
    print("This will show you EXACTLY what you requested:")
    print("1. Real contractor website form")
    print("2. WFA filling it with Instabids info")
    print("3. Bid card link visible in the message field")
    print("4. What happens when the link is clicked")
    print()
    print("Starting in 3 seconds...")
    time.sleep(3)
    
    try:
        asyncio.run(show_form_filling_with_bid_card_link())
        
        print()
        print("DEMONSTRATION COMPLETE!")
        print("You just saw:")
        print("- Real contractor form being filled")
        print("- Bid card link embedded in message")
        print("- Visual preview when link is clicked")
        print("- This is the complete WFA workflow!")
        
    except KeyboardInterrupt:
        print("Demonstration stopped by user")
    except Exception as e:
        print(f"Error running demo: {e}")
        print("Make sure Playwright is installed:")
        print("pip install playwright")
        print("playwright install chromium")

if __name__ == "__main__":
    main()