"""
Direct test of GPT-4o contact filtering without database dependencies
"""

import asyncio
import os
from openai import AsyncOpenAI
from pathlib import Path

# Load API key from .env file
env_path = Path(__file__).parent / '.env'
openai_key = None

if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if line.startswith('OPENAI_API_KEY='):
                openai_key = line.split('=', 1)[1].strip()
                break

if not openai_key:
    print("ERROR: No OpenAI API key found")
    exit(1)

client = AsyncOpenAI(api_key=openai_key)

async def test_gpt4o_filtering():
    """Test if GPT-4o can detect and filter contact information"""
    
    test_message = """I can do this project for $5000. 
Call me at 555-123-4567 or email me at contractor@email.com
I'm available to start next week."""

    prompt = """You are a security filter for a contractor bidding platform.
Analyze this message and:
1. Detect any contact information (phone, email, addresses)
2. Return a filtered version with contact info replaced with [CONTACT REMOVED]
3. List what was detected

Message: """ + test_message

    try:
        print("Testing GPT-4o contact detection...")
        print("-" * 40)
        print("Original message:")
        print(test_message)
        print("-" * 40)
        
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a security filter."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        
        result = response.choices[0].message.content
        print("GPT-4o Response:")
        print(result)
        
        # Check if it detected the contact info
        if "555-123-4567" in result or "contractor@email.com" in result:
            print("\n[FAILURE] GPT-4o did not filter contact information!")
            return False
        elif "[CONTACT REMOVED]" in result or "removed" in result.lower():
            print("\n[SUCCESS] GPT-4o correctly detected and filtered contact info!")
            return True
        else:
            print("\n[UNCLEAR] Check the response manually")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] API call failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_gpt4o_filtering())
    print("\n" + "=" * 60)
    if success:
        print("BASIC GPT-4o FILTERING WORKS")
    else:
        print("GPT-4o FILTERING FAILED")