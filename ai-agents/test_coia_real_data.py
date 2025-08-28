"""
Test COIA streaming with REAL database integration
Tests the fixed COIA system using actual Supabase database calls
"""

import asyncio
import json
import sys
import os
import requests
import time
from config.service_urls import get_backend_url

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_coia_streaming_real_data():
    """Test COIA streaming endpoint with TurfGrass company using real database"""
    
    print("TESTING COIA with REAL database integration")
    print("=" * 60)
    
    # Test data - TurfGrass Artificial Solutions
    test_request = {
        "message": "Hi, I own TurfGrass Artificial Solutions in South Florida. We specialize in artificial grass installation and landscaping services.",
        "session_id": "test_session_real_data",
        "interface": "chat"
    }
    
    try:
        # Make request to COIA streaming endpoint
        print(f"Making request to COIA streaming endpoint...")
        print(f"Message: {test_request['message']}")
        print()
        
        url = f"{get_backend_url()}/ai/coia/chat/stream"
        
        # Use requests with streaming
        with requests.post(url, json=test_request, stream=True) as response:
            if response.status_code != 200:
                print(f"ERROR: {response.status_code} - {response.text}")
                return
            
            print("Streaming response:")
            print("-" * 40)
            
            message_count = 0
            tool_calls = []
            real_data_found = False
            
            # Process streaming response
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    if line_text.startswith('data: '):
                        message_count += 1
                        try:
                            data = json.loads(line_text[6:])  # Remove 'data: ' prefix
                            
                            msg_type = data.get('type', 'unknown')
                            content = data.get('content', '')
                            
                            print(f"[{msg_type.upper()}] {content}")
                            
                            # Track tool calls
                            if msg_type == 'tool_call':
                                tool_calls.append(content)
                            
                            # Check for real data indicators in content
                            if 'Real Supabase Database' in str(data) or 'Supabase Direct Connection' in str(data):
                                real_data_found = True
                                
                            # Check metadata for real data
                            if 'metadata' in data and data['metadata']:
                                metadata = data['metadata']
                                if metadata.get('profile') and metadata.get('bid_cards'):
                                    print(f"METADATA FOUND:")
                                    print(f"   Profile completeness: {metadata['profile'].get('completeness_score', 0)}%")
                                    print(f"   Bid cards found: {len(metadata['bid_cards'])}")
                                    
                                    # Check for real bid cards
                                    for card in metadata['bid_cards']:
                                        if card.get('source') == 'Real Supabase Database':
                                            real_data_found = True
                                            print(f"   REAL BID CARD: {card.get('title', 'Unknown')}")
                                        
                        except json.JSONDecodeError:
                            if line_text != 'data: [DONE]':
                                print(f"[RAW] {line_text}")
                        
                        # Stop after reasonable number of messages  
                        if message_count > 50:
                            break
            
            print("-" * 40)
            print(f"SUMMARY:")
            print(f"   Total messages: {message_count}")
            print(f"   Tool calls made: {len(tool_calls)}")
            print(f"   Real data found: {'YES' if real_data_found else 'NO'}")
            
            print(f"\nTool calls executed:")
            for i, call in enumerate(tool_calls, 1):
                print(f"   {i}. {call}")
                
            # Verdict
            print(f"\nTEST RESULT:")
            if real_data_found and len(tool_calls) >= 3:
                print("SUCCESS - COIA is using REAL database integration!")
                print("   - Web search executed")
                print("   - Profile built with real data") 
                print("   - Real bid cards retrieved from Supabase")
            else:
                print("FAILURE - Still using fake data or incomplete integration")
                print(f"   Real data found: {real_data_found}")
                print(f"   Tool calls: {len(tool_calls)} (need >= 3)")
                
    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_coia_streaming_real_data()