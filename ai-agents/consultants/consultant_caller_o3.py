"""
O3 Consultant Caller - Enhanced Agent-to-Agent Communication

Provides building agents with direct access to OpenAI O3-powered consultants
for intelligent database analysis and recommendations.
"""

import asyncio
import json
import os
import subprocess
from typing import Any


class O3ConsultantCaller:
    """
    Enhanced interface for building agents to call O3-powered consultant agents
    
    Features:
    - OpenAI O3 database expert
    - Real Supabase schema integration
    - Intelligent migration generation
    - Performance optimization recommendations
    """

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.consultants_path = os.path.join(os.path.dirname(__file__))

    async def ask_database_expert(self, question: str, context: dict[str, Any] = None) -> dict[str, Any]:
        """
        Ask the O3 database expert any question about database design, optimization, or best practices
        
        Args:
            question: Natural language question about database
            context: Additional context like table names, performance issues, etc.
        
        Returns:
            O3-powered expert response with recommendation and implementation
        """
        consultation_data = {
            "action": "consult",
            "agent_id": self.agent_id,
            "data": {
                "request_type": "query",
                "description": question,
                "context": context or {},
                "urgency": "normal"
            }
        }

        return await self._call_o3_consultant(consultation_data)

    async def request_migration(self, change_description: str, context: dict[str, Any] = None) -> dict[str, Any]:
        """
        Request a database migration from the O3 expert
        
        Args:
            change_description: What you want to change/add
            context: Tables involved, requirements, etc.
        
        Returns:
            Migration SQL and impact analysis from O3
        """
        consultation_data = {
            "action": "consult",
            "agent_id": self.agent_id,
            "data": {
                "request_type": "change",
                "description": change_description,
                "context": context or {},
                "urgency": "normal"
            }
        }

        return await self._call_o3_consultant(consultation_data)

    async def optimize_performance(self, performance_issue: str, context: dict[str, Any] = None) -> dict[str, Any]:
        """
        Get O3 recommendations for database performance optimization
        
        Args:
            performance_issue: Description of the performance problem
            context: Slow queries, table names, response times, etc.
        
        Returns:
            O3 optimization recommendations
        """
        consultation_data = {
            "action": "consult",
            "agent_id": self.agent_id,
            "data": {
                "request_type": "optimize",
                "description": performance_issue,
                "context": context or {},
                "urgency": "blocking" if "slow" in performance_issue.lower() else "normal"
            }
        }

        return await self._call_o3_consultant(consultation_data)

    async def get_table_schema(self, table_name: str) -> dict[str, Any]:
        """Get real schema information for a specific table"""
        schema_data = {
            "action": "schema",
            "agent_id": self.agent_id,
            "data": {"table_name": table_name}
        }

        return await self._call_o3_consultant(schema_data)

    async def get_o3_table_analysis(self, table_name: str) -> dict[str, Any]:
        """Get OpenAI O3 intelligent analysis of a table"""
        analysis_data = {
            "action": "analyze",
            "agent_id": self.agent_id,
            "data": {"table_name": table_name}
        }

        return await self._call_o3_consultant(analysis_data)

    async def validate_schema_change(self, change_description: str, context: dict[str, Any] = None) -> dict[str, Any]:
        """
        Validate a proposed schema change before implementation
        
        Args:
            change_description: Proposed change to validate
            context: Tables, constraints, relationships to check
        
        Returns:
            O3 validation with warnings and recommendations
        """
        validation_data = {
            "action": "consult",
            "agent_id": self.agent_id,
            "data": {
                "request_type": "validate",
                "description": change_description,
                "context": context or {},
                "urgency": "normal"
            }
        }

        return await self._call_o3_consultant(validation_data)

    async def _call_o3_consultant(self, data: dict[str, Any]) -> dict[str, Any]:
        """Call the O3 database consultant agent"""
        try:
            # Convert data to JSON string
            input_json = json.dumps(data)

            # Path to O3 consultant agent
            consultant_script = os.path.join(self.consultants_path, "database_consultant_agent_o3.py")

            # Call the O3 consultant agent
            result = subprocess.run(
                ["python", consultant_script],
                input=input_json,
                text=True,
                capture_output=True,
                timeout=120  # Extended timeout for O3 processing
            )

            if result.returncode == 0:
                response = json.loads(result.stdout)
                return response
            else:
                return {
                    "status": "error",
                    "message": f"O3 Consultant failed: {result.stderr}",
                    "consultant": "O3 Database Expert"
                }

        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "message": "O3 Consultant timed out (complex analysis may take longer)",
                "consultant": "O3 Database Expert"
            }
        except json.JSONDecodeError as e:
            return {
                "status": "error",
                "message": f"Invalid JSON response from O3 consultant: {e}",
                "consultant": "O3 Database Expert"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error calling O3 consultant: {e!s}",
                "consultant": "O3 Database Expert"
            }


# Pre-built helper functions for common use cases
class DatabaseExpertHelpers:
    """Pre-built helper functions for common database consultation scenarios"""

    @staticmethod
    async def design_dashboard_queries(agent_id: str, dashboard_requirements: dict[str, Any]) -> dict[str, Any]:
        """Get O3 recommendations for dashboard query design"""
        caller = O3ConsultantCaller(agent_id)

        return await caller.ask_database_expert(
            "How should I structure my database queries for this dashboard to optimize performance and user experience?",
            context={
                "dashboard_type": dashboard_requirements.get("type", "admin"),
                "data_requirements": dashboard_requirements.get("data", []),
                "performance_targets": dashboard_requirements.get("performance", {}),
                "real_time_needs": dashboard_requirements.get("real_time", False)
            }
        )

    @staticmethod
    async def plan_new_feature_tables(agent_id: str, feature_description: str, requirements: dict[str, Any]) -> dict[str, Any]:
        """Get O3 recommendations for new feature database design"""
        caller = O3ConsultantCaller(agent_id)

        return await caller.request_migration(
            f"I need to implement {feature_description}. What database changes are needed?",
            context={
                "feature": feature_description,
                "requirements": requirements,
                "existing_integration": requirements.get("integrates_with", []),
                "data_volume": requirements.get("expected_volume", "unknown")
            }
        )

    @staticmethod
    async def troubleshoot_slow_queries(agent_id: str, performance_data: dict[str, Any]) -> dict[str, Any]:
        """Get O3 performance optimization recommendations"""
        caller = O3ConsultantCaller(agent_id)

        slow_queries = performance_data.get("slow_queries", [])
        query_times = performance_data.get("response_times", {})

        issue_description = f"Performance issues detected: {', '.join(slow_queries)} taking {query_times}"

        return await caller.optimize_performance(
            issue_description,
            context={
                "slow_operations": slow_queries,
                "current_performance": query_times,
                "target_performance": performance_data.get("target_times", {}),
                "affected_tables": performance_data.get("tables", [])
            }
        )


# Example usage for building agents
async def example_agent_usage():
    """Example showing how building agents can use the O3 consultant"""

    print("Testing O3 Database Consultant for Building Agents...")
    print("=" * 60)

    # Agent 1: Frontend dashboard optimization
    caller = O3ConsultantCaller("agent_1_frontend")

    dashboard_response = await caller.ask_database_expert(
        "I'm building a real-time bid tracking dashboard. How should I structure queries to show bid progress, contractor engagement, and homeowner notifications efficiently?",
        context={
            "component": "bid_tracking_dashboard",
            "tables": ["bid_cards", "contractors", "bid_card_views", "notifications"],
            "requirements": ["real-time updates", "sub-500ms response", "10+ concurrent users"]
        }
    )

    print("AGENT 1 - Dashboard Query Optimization:")
    print(f"Status: {dashboard_response['status']}")
    print(f"O3 Recommendation: {dashboard_response.get('recommendation', 'N/A')[:200]}...")

    # Agent 4: Contractor feature development
    caller = O3ConsultantCaller("agent_4_contractor_ux")

    feature_response = await caller.request_migration(
        "I need to add contractor portfolio management where contractors can upload project photos, descriptions, and client testimonials",
        context={
            "feature": "contractor_portfolio",
            "data_types": ["images", "descriptions", "testimonials", "project_metadata"],
            "relationships": ["contractors", "projects", "homeowners"],
            "storage_needs": "high-volume image storage"
        }
    )

    print("\nAGENT 4 - Portfolio Feature Migration:")
    print(f"Status: {feature_response['status']}")
    print(f"Migration SQL: {feature_response.get('implementation', 'N/A')[:200]}...")

    # Agent 2: Performance optimization
    caller = O3ConsultantCaller("agent_2_backend")

    performance_response = await caller.optimize_performance(
        "The contractor discovery process is taking 4+ seconds to find and rank contractors for bid cards",
        context={
            "slow_queries": ["contractor_search", "ranking_algorithm", "discovery_cache"],
            "current_performance": {"discovery": "4.2s", "ranking": "1.8s"},
            "target_performance": {"discovery": "800ms", "ranking": "300ms"},
            "tables": ["contractors", "contractor_discovery_cache", "potential_contractors"]
        }
    )

    print("\nAGENT 2 - Performance Optimization:")
    print(f"Status: {performance_response['status']}")
    print(f"O3 Optimization: {performance_response.get('recommendation', 'N/A')[:200]}...")

    # Helper function example
    print("\nHELPER FUNCTION - Dashboard Design:")
    helper_response = await DatabaseExpertHelpers.design_dashboard_queries(
        "agent_6_qa",
        {
            "type": "admin_monitoring",
            "data": ["system_health", "agent_status", "bid_card_metrics"],
            "performance": {"target_load_time": "300ms"},
            "real_time": True
        }
    )

    print(f"Helper Status: {helper_response['status']}")
    print(f"Helper Recommendation: {helper_response.get('recommendation', 'N/A')[:200]}...")


if __name__ == "__main__":
    asyncio.run(example_agent_usage())
