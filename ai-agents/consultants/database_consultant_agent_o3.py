"""
Database Consultant Agent - O3 Powered
Agent interface that building agents can call via Task tool for database expertise
"""

import asyncio
import json
import os
import sys
from typing import Any


# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from consultants.database_consultant_o3 import ConsultationRequest, O3DatabaseConsultant


class DatabaseConsultantAgent:
    """
    Agent interface for the O3 Database Consultant
    
    Building agents can call this via the Task tool to get database expertise
    """

    def __init__(self):
        self.consultant = None
        self.initialized = False

    async def initialize(self):
        """Initialize the consultant if not already done"""
        if not self.initialized:
            print("Database Consultant Agent: Initializing O3 consultant...")
            self.consultant = O3DatabaseConsultant()
            await self.consultant.initialize_with_real_database()
            self.initialized = True
            print("Database Consultant Agent: Ready for consultations")

    async def handle_consultation(self, agent_id: str, request_data: dict[str, Any]) -> dict[str, Any]:
        """
        Handle consultation request from building agents
        
        Args:
            agent_id: ID of the requesting agent (e.g., "agent_1_frontend")
            request_data: Dictionary containing:
                - request_type: 'query', 'change', 'validate', 'optimize'
                - description: Natural language description of the request
                - context: Additional context data
                - urgency: 'blocking', 'normal', 'async'
        
        Returns:
            Dictionary with consultation response
        """
        await self.initialize()

        # Create consultation request
        request = ConsultationRequest(
            agent_id=agent_id,
            request_type=request_data.get("request_type", "query"),
            description=request_data.get("description", ""),
            context=request_data.get("context", {}),
            urgency=request_data.get("urgency", "normal")
        )

        # Get O3 consultation
        response = await self.consultant.consult_with_o3(request)

        # Return structured response
        return {
            "status": "success",
            "recommendation": response.recommendation,
            "implementation": response.implementation,
            "impacts": response.impacts or [],
            "alternatives": response.alternatives or [],
            "warnings": response.warnings or [],
            "estimated_time": response.estimated_time,
            "consultant": "O3 Database Expert",
            "timestamp": "2025-08-02T12:00:00Z"
        }

    async def quick_schema_lookup(self, table_name: str) -> dict[str, Any]:
        """Quick lookup for table schema information"""
        await self.initialize()

        if table_name not in self.consultant.schema_cache:
            return {
                "status": "error",
                "message": f"Table '{table_name}' not found in schema cache",
                "available_tables": list(self.consultant.schema_cache.keys())
            }

        schema = self.consultant.schema_cache[table_name]
        return {
            "status": "success",
            "table_name": table_name,
            "schema": schema,
            "related_tables": self.consultant.relationships_cache
        }

    async def get_o3_table_analysis(self, table_name: str) -> dict[str, Any]:
        """Get O3-powered analysis of a specific table"""
        await self.initialize()

        analysis = await self.consultant.get_table_analysis(table_name)

        return {
            "status": "success",
            "table_name": table_name,
            "o3_analysis": analysis,
            "consultant": "OpenAI O3",
            "timestamp": "2025-08-02T12:00:00Z"
        }


# Main function for Task tool integration
async def main():
    """
    Main function that can be called by building agents via Task tool
    
    Expected input format:
    {
        "action": "consult|schema|analyze",
        "agent_id": "agent_X_name",
        "data": {...}
    }
    """
    # Parse command line arguments or stdin
    import sys

    if len(sys.argv) > 1:
        # Command line argument
        input_data = json.loads(sys.argv[1])
    else:
        # Read from stdin
        input_data = json.loads(sys.stdin.read())

    agent = DatabaseConsultantAgent()

    action = input_data.get("action", "consult")
    agent_id = input_data.get("agent_id", "unknown_agent")
    data = input_data.get("data", {})

    try:
        if action == "consult":
            result = await agent.handle_consultation(agent_id, data)
        elif action == "schema":
            table_name = data.get("table_name", "")
            result = await agent.quick_schema_lookup(table_name)
        elif action == "analyze":
            table_name = data.get("table_name", "")
            result = await agent.get_o3_table_analysis(table_name)
        else:
            result = {
                "status": "error",
                "message": f"Unknown action: {action}",
                "available_actions": ["consult", "schema", "analyze"]
            }

        # Output result as JSON
        print(json.dumps(result, indent=2))

    except Exception as e:
        error_result = {
            "status": "error",
            "message": str(e),
            "action": action,
            "agent_id": agent_id
        }
        print(json.dumps(error_result, indent=2))


# Test function
async def test_agent_interface():
    """Test the agent interface"""
    print("Testing Database Consultant Agent Interface...")

    agent = DatabaseConsultantAgent()

    # Test consultation
    test_consultation = {
        "request_type": "query",
        "description": "I need to understand how bid cards connect to contractors",
        "context": {"tables": ["bid_cards", "contractors"]},
        "urgency": "normal"
    }

    print("\n" + "="*60)
    print("TEST: Database Consultation")
    print("="*60)

    result = await agent.handle_consultation("agent_test", test_consultation)
    print(f"Status: {result['status']}")
    print(f"Recommendation: {result['recommendation']}")

    if result.get("implementation"):
        print(f"Implementation: {result['implementation']}")

    # Test schema lookup
    print("\n" + "="*60)
    print("TEST: Schema Lookup")
    print("="*60)

    schema_result = await agent.quick_schema_lookup("bid_cards")
    print(f"Status: {schema_result['status']}")
    print(f"Table: {schema_result.get('table_name', 'N/A')}")

    # Test O3 analysis
    print("\n" + "="*60)
    print("TEST: O3 Table Analysis")
    print("="*60)

    analysis_result = await agent.get_o3_table_analysis("contractors")
    print(f"Status: {analysis_result['status']}")
    print(f"O3 Analysis: {analysis_result.get('o3_analysis', 'N/A')[:200]}...")

    print("\n" + "="*60)
    print("AGENT INTERFACE TEST COMPLETE")
    print("="*60)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run test
        asyncio.run(test_agent_interface())
    else:
        # Run main function for Task tool integration
        asyncio.run(main())
