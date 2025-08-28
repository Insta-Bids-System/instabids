"""
Test the bid card search fix
Tests that bid card search actually triggers when users ask for projects
"""

import asyncio
import logging
import requests
import json
import time
from datetime import datetime
from config.service_urls import get_backend_url

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_URL = f"{get_backend_url()}/api/coia/landing"

async def test_bid_card_search():
    """Test that bid card search mode triggers properly"""
    
    session_id = f"test-bid-search-{int(time.time())}"
    logger.info(f"Testing with session: {session_id}")
    
    # Test 1: Ask directly for projects after company is known
    logger.info("\n=== TEST 1: Direct project request ===")
    response1 = requests.post(API_URL, json={
        "message": "My company is TurfGrass Artificial Solutions",
        "session_id": session_id,
        "interface": "landing_page"
    }, timeout=30)
    
    if response1.status_code == 200:
        data1 = response1.json()
        logger.info(f"Response 1 mode: {data1.get('current_mode')}")
        logger.info(f"Company extracted: {data1.get('company_name')}")
    
    # Test 2: Now ask for projects - should trigger bid_card_search
    logger.info("\n=== TEST 2: Asking for projects ===")
    response2 = requests.post(API_URL, json={
        "message": "Show me available projects I can bid on",
        "session_id": session_id,
        "interface": "landing_page"
    }, timeout=30)
    
    if response2.status_code == 200:
        data2 = response2.json()
        mode = data2.get('current_mode')
        bid_cards = data2.get('bid_cards_attached', [])
        
        logger.info(f"Response 2 mode: {mode}")
        logger.info(f"Bid cards returned: {len(bid_cards)}")
        
        if mode == "bid_card_search":
            logger.info("SUCCESS: Bid card search mode triggered!")
        else:
            logger.error(f"FAILURE: Expected bid_card_search, got {mode}")
        
        if bid_cards:
            logger.info("SUCCESS: Bid cards returned!")
            for card in bid_cards[:3]:
                logger.info(f"  - {card.get('title')} in {card.get('location_city')}")
        else:
            logger.warning("No bid cards returned")
    
    # Test 3: Test with different phrasing
    logger.info("\n=== TEST 3: Alternative phrasing ===")
    session_id3 = f"test-alt-{int(time.time())}"
    
    response3 = requests.post(API_URL, json={
        "message": "I'm JM Holiday Lighting. What opportunities are available?",
        "session_id": session_id3,
        "interface": "landing_page"
    }, timeout=30)
    
    if response3.status_code == 200:
        data3 = response3.json()
        mode = data3.get('current_mode')
        logger.info(f"Response 3 mode: {mode}")
        
        if "opportunities" in data3.get('response', '').lower() or mode == "bid_card_search":
            logger.info("SUCCESS: System recognized opportunity request")
        else:
            logger.warning("System may not have recognized opportunity request")

if __name__ == "__main__":
    asyncio.run(test_bid_card_search())