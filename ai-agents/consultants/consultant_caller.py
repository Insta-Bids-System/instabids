"""
Consultant Caller - Agent-to-Agent Communication System

This module allows building agents to call consultant agents internally
using the Task tool for agent-to-agent communication.
"""

import json
from typing import Any


class ConsultantCaller:
    """
    Interface for building agents to call consultant agents
    """

    @staticmethod
    async def call_database_consultant(
        agent_id: str,
        request_type: str,  # 'query', 'change', 'validate', 'optimize'
        description: str,
        context: dict[str, Any] = None,
        urgency: str = "normal"
    ) -> dict[str, Any]:
        """
        Call the Database Schema Consultant
        
        Args:
            agent_id: Which agent is making the request (Agent_1, Agent_2, etc.)
            request_type: Type of consultation needed
            description: What you need help with
            context: Additional context for the request
            urgency: 'blocking', 'normal', 'async'
            
        Returns:
            Dict with recommendation, implementation, impacts, etc.
        """

        # Prepare the consultation request
        consultation_request = {
            "agent_id": agent_id,
            "request_type": request_type,
            "description": description,
            "context": context or {},
            "urgency": urgency
        }

        # Format as prompt for Task tool
        prompt = f"""
You are the Database Schema Consultant for InstaBids.

CONSULTATION REQUEST:
- Requesting Agent: {agent_id}
- Request Type: {request_type}
- Description: {description}
- Context: {json.dumps(context or {}, indent=2)}
- Urgency: {urgency}

INSTRUCTIONS:
1. Load the database consultant from consultants/database_consultant.py
2. Initialize it with current schema knowledge
3. Process this consultation request
4. Return a JSON response with:
   - recommendation: Your expert advice
   - implementation: SQL/migration code if applicable
   - impacts: List of what this change affects
   - warnings: Any concerns or risks
   - alternatives: Other options to consider

RESPOND WITH ONLY THE JSON RESULT.
"""

        # Call the database consultant agent using Task tool
        # Note: This would be implemented by the calling agent using:
        # result = await task_tool.invoke({
        #     "description": "Database consultation",
        #     "prompt": prompt,
        #     "subagent_type": "database-consultant"
        # })

        return {
            "prompt": prompt,
            "consultation_request": consultation_request
        }


# Example usage functions for building agents
async def ask_database_consultant_about_tables(agent_id: str) -> dict[str, Any]:
    """Example: Get list of all tables"""
    return await ConsultantCaller.call_database_consultant(
        agent_id=agent_id,
        request_type="query",
        description="list all tables in the database",
        context={}
    )


async def ask_database_consultant_for_new_table(
    agent_id: str,
    table_name: str,
    purpose: str,
    fields: list
) -> dict[str, Any]:
    """Example: Request new table creation"""
    return await ConsultantCaller.call_database_consultant(
        agent_id=agent_id,
        request_type="change",
        description=f"I need to create a new table called {table_name}",
        context={
            "add_table": True,
            "table_name": table_name,
            "purpose": purpose,
            "fields": fields
        }
    )


async def ask_database_consultant_about_relationships(agent_id: str) -> dict[str, Any]:
    """Example: Query table relationships"""
    return await ConsultantCaller.call_database_consultant(
        agent_id=agent_id,
        request_type="query",
        description="show me all table relationships and foreign keys",
        context={}
    )


async def ask_database_consultant_for_table_schema(
    agent_id: str,
    table_name: str
) -> dict[str, Any]:
    """Example: Get specific table schema"""
    return await ConsultantCaller.call_database_consultant(
        agent_id=agent_id,
        request_type="query",
        description=f"show me the {table_name} table schema with all columns",
        context={"table_name": table_name}
    )


# Direct usage example for testing
if __name__ == "__main__":
    import asyncio

    async def test_consultant_caller():
        print("Testing Consultant Caller Interface")
        print("=" * 40)

        # Example 1: Query all tables
        result1 = await ask_database_consultant_about_tables("Agent_4")
        print("\\nExample 1 - Query all tables:")
        print("Prompt length:", len(result1["prompt"]))
        print("Request type:", result1["consultation_request"]["request_type"])

        # Example 2: Request new table
        result2 = await ask_database_consultant_for_new_table(
            agent_id="Agent_4",
            table_name="contractor_reviews",
            purpose="Track reviews and ratings for contractors",
            fields=[
                {"name": "contractor_id", "type": "uuid", "nullable": False},
                {"name": "homeowner_id", "type": "uuid", "nullable": False},
                {"name": "project_id", "type": "uuid", "nullable": False},
                {"name": "rating", "type": "integer", "nullable": False},
                {"name": "review_text", "type": "text", "nullable": True},
                {"name": "would_recommend", "type": "boolean", "nullable": False}
            ]
        )
        print("\\nExample 2 - Request new table:")
        print("Table name:", result2["consultation_request"]["context"]["table_name"])
        print("Fields count:", len(result2["consultation_request"]["context"]["fields"]))

        # Example 3: Query relationships
        result3 = await ask_database_consultant_about_relationships("Agent_6")
        print("\\nExample 3 - Query relationships:")
        print("Description:", result3["consultation_request"]["description"])

        print("\\nConsultant Caller testing complete!")

    asyncio.run(test_consultant_caller())
