#!/usr/bin/env python3
"""
Debug COIA endpoint to see what's happening
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "deepagents-system" / "src"))
sys.path.insert(0, str(Path(__file__).parent))

# Load environment
from dotenv import load_dotenv
root_env = Path(__file__).parent.parent / '.env'
if root_env.exists():
    load_dotenv(root_env, override=True)

# Set OpenAI key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

async def test_landing_endpoint():
    """Test the landing endpoint directly"""
    from routers.coia_landing_api import landing_page_conversation
    from routers.coia_landing_api import ChatRequest
    
    request = ChatRequest(
        message="I am Justin from JM Holiday Lighting in Fort Lauderdale. We specialize in holiday and outdoor lighting installations.",
        session_id="test-session-debug-001",
        contractor_lead_id="test-debug-001",
        user_id="test-user-debug-001"
    )
    
    print("\n=== TESTING LANDING ENDPOINT DIRECTLY ===")
    print(f"Request: {request.message}")
    
    try:
        result = await landing_page_conversation(request)
        print(f"\nSuccess: {result.success}")
        print(f"Company Name: {result.company_name}")
        print(f"\nResponse:")
        print("-" * 60)
        print(result.response)
        print("-" * 60)
        
        # Check for real data
        if result.response and any(x in result.response for x in ['Phone:', 'Email:', 'Website:', '(561)']):
            print("\n✅ SUCCESS: Real DeepAgents data detected!")
        else:
            print("\n⚠️ WARNING: Template response detected")
            
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_landing_endpoint())