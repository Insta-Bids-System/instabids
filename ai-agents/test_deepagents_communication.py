#!/usr/bin/env python3
"""Test DeepAgents sub-agent communication flow"""

import os
from deepagents import create_deep_agent
from langchain_core.tools import tool

# Set up OpenAI API key if not already set
if not os.getenv("OPENAI_API_KEY"):
    print("ERROR: Need OPENAI_API_KEY environment variable")
    exit(1)

# Create a simple tool for testing
@tool
def get_contractor_info(contractor_id: str) -> dict:
    """Get contractor information from database"""
    return {
        "id": contractor_id,
        "name": "Test Contractor LLC",
        "specialty": "Kitchen Remodeling", 
        "rating": 4.8,
        "typical_pricing": "$200/sqft"
    }

@tool  
def calculate_bid_pricing(project_type: str, sqft: int) -> dict:
    """Calculate pricing for a specific project"""
    base_rate = 200 if project_type == "kitchen" else 150
    total = base_rate * sqft
    return {
        "project_type": project_type,
        "sqft": sqft,
        "rate_per_sqft": base_rate,
        "total_estimate": total,
        "breakdown": f"{sqft} sqft × ${base_rate}/sqft = ${total:,}"
    }

# Define a specialized sub-agent
kitchen_specialist = {
    "name": "kitchen-specialist",
    "description": "Expert in kitchen remodeling bids and pricing",
    "prompt": """You are a kitchen remodeling specialist. You understand:
    - Cabinet pricing and layouts
    - Appliance packages and installation
    - Countertop materials and costs
    - Kitchen workflow and design principles
    
    When processing kitchen projects:
    1. Calculate accurate square footage pricing
    2. Consider complexity factors (islands, custom work)
    3. Provide detailed breakdown of costs
    4. Suggest timeline based on scope
    """,
    "tools": ["calculate_bid_pricing", "get_contractor_info"]
}

# Create the main agent with sub-agent
main_instructions = """You are a BSA (Bid Submission Agent) that helps contractors create professional bids.

Your process:
1. Understand the project requirements
2. Use specialized sub-agents when needed for expert analysis
3. Compile information into a professional proposal
4. Always be thorough and accurate

When you encounter kitchen projects, use the kitchen-specialist sub-agent for detailed analysis.
"""

def test_sub_agent_communication():
    print("Creating DeepAgents BSA with kitchen specialist sub-agent...")
    
    # Create the agent
    agent = create_deep_agent(
        tools=[get_contractor_info, calculate_bid_pricing],
        instructions=main_instructions,
        subagents=[kitchen_specialist]
    )
    
    print("Agent created successfully!")
    print("Agent type:", type(agent))
    
    # Test message - ask for a kitchen bid
    test_prompt = """
    I need help creating a bid for a kitchen remodel project.
    
    Project details:
    - Kitchen size: 200 sqft
    - Full remodel with new cabinets, countertops, appliances
    - Contractor ID: contractor-123
    
    Please:
    1. Use the kitchen specialist to analyze this project
    2. Get contractor information
    3. Calculate accurate pricing
    4. Create a professional bid proposal
    
    I want to see how the sub-agent handles the kitchen expertise.
    """
    
    print("\n" + "="*50)
    print("TESTING SUB-AGENT COMMUNICATION")
    print("="*50)
    print("Prompt:", test_prompt)
    print("\n" + "-"*30)
    print("AGENT RESPONSE:")
    print("-"*30)
    
    # Run the agent
    result = agent.invoke({
        "messages": [{"role": "user", "content": test_prompt}]
    })
    
    print("\nFinal Response:")
    print(result["messages"][-1].content)
    
    print("\n" + "="*50)
    print("ANALYZING COMMUNICATION FLOW")
    print("="*50)
    
    # Check the full message history to see sub-agent communication
    print(f"Total messages in conversation: {len(result['messages'])}")
    
    for i, msg in enumerate(result['messages']):
        print(f"\nMessage {i+1}:")
        print(f"  Role: {msg.role if hasattr(msg, 'role') else 'unknown'}")
        print(f"  Type: {type(msg).__name__}")
        if hasattr(msg, 'content'):
            preview = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
            print(f"  Content: {preview}")
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            print(f"  Tool Calls: {len(msg.tool_calls)}")
            for tc in msg.tool_calls:
                print(f"    - {tc.get('name', 'unknown')} with args: {tc.get('args', {})}")
    
    # Check if files were created/modified
    if "files" in result:
        print(f"\nFiles created/modified: {list(result['files'].keys())}")
    
    # Check todos
    if "todos" in result:
        print(f"\nTodos created: {len(result['todos'])}")
        for todo in result['todos']:
            print(f"  - {todo['content']} ({todo['status']})")
    
    return result

if __name__ == "__main__":
    try:
        result = test_sub_agent_communication()
        print("\n✅ Test completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()