"""
Database Consultant Agent - Specialized Agent for Task Tool

This agent can be invoked by building agents via the Task tool
to provide database schema consultation and expertise.
"""

import asyncio
import json
import os
import sys
from typing import Any


# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from database_consultant import ConsultationRequest, DatabaseSchemaConsultant


class DatabaseConsultantAgent:
    """
    Specialized consultant agent that can be called via Task tool
    """

    def __init__(self):
        self.consultant = DatabaseSchemaConsultant()
        self.initialized = False

    async def initialize_if_needed(self):
        """Initialize consultant if not already done"""
        if not self.initialized:
            await self.consultant.initialize()
            self.initialized = True

    async def handle_consultation(self, prompt: str) -> str:
        """
        Handle consultation request from building agent
        
        Expected prompt format should contain:
        - Requesting Agent
        - Request Type
        - Description
        - Context
        - Urgency
        """
        await self.initialize_if_needed()

        try:
            # Parse the consultation request from the prompt
            request_data = self._parse_consultation_request(prompt)

            # Create consultation request object
            consultation_request = ConsultationRequest(
                agent_id=request_data.get("agent_id", "unknown"),
                request_type=request_data.get("request_type", "query"),
                description=request_data.get("description", ""),
                context=request_data.get("context", {}),
                urgency=request_data.get("urgency", "normal")
            )

            # Get consultation response
            response = await self.consultant.consult(consultation_request)

            # Format response as JSON
            result = {
                "recommendation": response.recommendation,
                "implementation": response.implementation,
                "impacts": response.impacts or [],
                "warnings": response.warnings or [],
                "alternatives": response.alternatives or [],
                "estimated_time": response.estimated_time,
                "consultant_info": {
                    "tables_in_knowledge_base": len(self.consultant.schema_cache),
                    "relationships_tracked": len(self.consultant.relationships_cache),
                    "last_scan": self.consultant.last_scan
                }
            }

            return json.dumps(result, indent=2, default=str)

        except Exception as e:
            error_result = {
                "error": f"Database Consultant Error: {e!s}",
                "recommendation": "Unable to process consultation request",
                "warnings": [str(e)]
            }
            return json.dumps(error_result, indent=2)

    def _parse_consultation_request(self, prompt: str) -> dict[str, Any]:
        """
        Parse consultation request from prompt text
        """
        request_data = {}

        lines = prompt.split("\n")
        current_section = None
        context_lines = []

        for line in lines:
            line = line.strip()

            if line.startswith("- Requesting Agent:"):
                request_data["agent_id"] = line.split(":", 1)[1].strip()
            elif line.startswith("- Request Type:"):
                request_data["request_type"] = line.split(":", 1)[1].strip()
            elif line.startswith("- Description:"):
                request_data["description"] = line.split(":", 1)[1].strip()
            elif line.startswith("- Urgency:"):
                request_data["urgency"] = line.split(":", 1)[1].strip()
            elif line.startswith("- Context:"):
                current_section = "context"
                context_start = line.split(":", 1)[1].strip()
                if context_start:
                    context_lines.append(context_start)
            elif current_section == "context" and line:
                context_lines.append(line)

        # Parse context JSON if present
        if context_lines:
            try:
                context_text = "\n".join(context_lines)
                request_data["context"] = json.loads(context_text)
            except:
                request_data["context"] = {"raw_context": "\n".join(context_lines)}
        else:
            request_data["context"] = {}

        return request_data


# Main function for when this agent is called via Task tool
async def main():
    """
    Main entry point when called as a specialized agent
    """
    # Check if we have input from stdin (when called via Task tool)
    if sys.stdin.isatty():
        # Running directly, use test prompt
        test_prompt = """
You are the Database Schema Consultant for InstaBids.

CONSULTATION REQUEST:
- Requesting Agent: Agent_4
- Request Type: query
- Description: list all tables in the database
- Context: {}
- Urgency: normal

INSTRUCTIONS:
1. Load the database consultant from consultants/database_consultant.py
2. Initialize it with current schema knowledge
3. Process this consultation request
4. Return a JSON response

RESPOND WITH ONLY THE JSON RESULT.
"""
        print("Running in test mode with sample prompt")
        prompt = test_prompt
    else:
        # Read prompt from stdin (when called via Task tool)
        prompt = sys.stdin.read()

    # Create and run the consultant agent
    agent = DatabaseConsultantAgent()
    result = await agent.handle_consultation(prompt)

    # Output the result
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
