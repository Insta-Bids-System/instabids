"""
Visual test of bid cards in browser using Selenium
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

def test_bid_cards_visual():
    """Test bid cards display visually in browser"""
    
    # Setup Chrome driver
    driver = webdriver.Chrome()
    
    try:
        print("=" * 60)
        print("VISUAL BID CARDS TEST")
        print("=" * 60)
        
        # Navigate to test page
        url = "http://localhost:5173/test-bid-cards.html"
        print(f"Opening {url}")
        driver.get(url)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "message-input"))
        )
        
        # Find input and button
        input_field = driver.find_element(By.ID, "message-input")
        send_button = driver.find_element(By.XPATH, "//button[text()='Send']")
        
        # Clear and enter message
        input_field.clear()
        input_field.send_keys("I am a General Contractor looking for projects in Austin 78701")
        
        print("Sending message to COIA...")
        send_button.click()
        
        # Wait for response (up to 20 seconds)
        print("Waiting for response...")
        time.sleep(5)  # Initial wait
        
        # Check for bid cards
        bid_cards = driver.find_elements(By.CLASS_NAME, "bid-card")
        
        if bid_cards:
            print(f"SUCCESS! Found {len(bid_cards)} bid card elements")
            for i, card in enumerate(bid_cards, 1):
                title = card.find_element(By.TAG_NAME, "h3").text
                print(f"  Card {i}: {title}")
        else:
            print("NO BID CARDS FOUND - Checking for error messages...")
            
            # Check status
            status = driver.find_element(By.ID, "status")
            print(f"Status: {status.text}")
            
            # Check for assistant messages
            messages = driver.find_elements(By.CLASS_NAME, "assistant-message")
            if messages:
                print(f"Assistant response: {messages[-1].text[:200]}...")
        
        # Take screenshot
        driver.save_screenshot("bid_cards_test.png")
        print("Screenshot saved as bid_cards_test.png")
        
        # Check console for errors
        logs = driver.get_log('browser')
        errors = [log for log in logs if log['level'] == 'SEVERE']
        if errors:
            print("Browser errors found:")
            for error in errors:
                print(f"  {error['message']}")
        
        print()
        print("=" * 60)
        print("TEST COMPLETE - Check bid_cards_test.png for visual proof")
        print("=" * 60)
        
        # Keep browser open for manual inspection
        input("Press Enter to close browser...")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    test_bid_cards_visual()