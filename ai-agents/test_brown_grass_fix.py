"""
Leonardo test to fix brown grass issue - target ALL grass areas
"""

import asyncio
import os
import aiohttp
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Improved prompts targeting brown grass specifically
TEST_CONFIGS = [
    {
        "name": "Replace ALL grass - green AND brown",
        "init_strength": 0.20,
        "guidance_scale": 8,
        "prompt": "Replace ALL lawn areas with artificial turf - both green grass AND brown dead patches. Complete lawn transformation to uniform emerald synthetic grass. Soccer goal stays in exact position. Remove all brown dead spots and make entire yard perfect green turf.",
        "negative_prompt": "brown grass, dead patches, keep brown areas, partial coverage"
    },
    {
        "name": "Target brown dead areas specifically", 
        "init_strength": 0.25,
        "guidance_scale": 7,
        "prompt": "Transform entire lawn to artificial turf. The brown patchy dead areas must become green turf. All grass surface - green healthy and brown dying areas - becomes uniform synthetic grass. Perfect emerald artificial turf covering complete yard.",
        "negative_prompt": "brown patches remaining, dead grass left behind, incomplete replacement"
    },
    {
        "name": "Complete surface renovation",
        "init_strength": 0.22,
        "guidance_scale": 8,
        "prompt": "Professional artificial turf installation removing ALL existing grass. Green areas and brown dead patches all become uniform synthetic turf. Complete yard renovation with perfect artificial grass. Soccer goal preserved in exact location.",
        "negative_prompt": "natural grass remaining, brown spots, uneven turf, partial installation"
    }
]

async def upload_and_transform(config_num, config):
    """Upload image and run transformation"""
    LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY")
    backyard_path = r"C:\Users\Not John Or Justin\Documents\instabids\test-images\YOUR_ACTUAL_BACKYARD.jpg"
    
    headers = {"Authorization": f"Bearer {LEONARDO_API_KEY}", "Content-Type": "application/json"}
    
    try:
        async with aiohttp.ClientSession() as session: