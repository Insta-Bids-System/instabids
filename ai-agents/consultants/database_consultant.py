"""
InstaBids Database Schema Consultant Agent

Expert agent that maintains complete knowledge of all Supabase tables,
relationships, and can suggest optimal database changes.

Usage:
- Building agents can call this consultant for database advice
- Consultant has full schema knowledge and migration capabilities
- Can create migrations, analyze impacts, suggest optimizations
"""

import datetime
import json
import os
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class TableSchema:
    """Complete table schema information"""
    name: str
    columns: dict[str, Any]
    primary_key: list[str]
    foreign_keys: list[dict[str, str]]
    indexes: list[dict[str, Any]]
    constraints: list[dict[str, Any]]
    row_count: Optional[int] = None
    created_at: Optional[str] = None


@dataclass
class ConsultationRequest:
    """Request for database consultation"""
    agent_id: str
    request_type: str  # 'query', 'change', 'validate', 'optimize'
    description: str
    context: dict[str, Any]
    urgency: str = "normal"  # 'blocking', 'normal', 'async'


@dataclass
class ConsultationResponse:
    """Response from database consultant"""
    recommendation: str
    implementation: Optional[str] = None  # SQL/migration code
    impacts: list[str] = None
    alternatives: list[str] = None
    warnings: list[str] = None
    estimated_time: Optional[str] = None


class DatabaseSchemaConsultant:
    """
    Database Schema Expert Agent
    
    Maintains complete knowledge of InstaBids database schema
    and provides expert consultation for database changes.
    """

    def __init__(self, knowledge_base_path: str = None):
        self.knowledge_base_path = knowledge_base_path or "consultants/knowledge/database"
        self.schema_cache = {}
        self.relationships_cache = {}
        self.last_scan = None

    async def initialize(self):
        """Initialize consultant with current database state"""
        print("Database Consultant: Initializing with current schema...")

        # Scan all tables and build complete knowledge base
        await self.scan_database()
        await self.analyze_relationships()
        await self.save_knowledge_base()

        print(f"Database Consultant: Initialized with {len(self.schema_cache)} tables")

    async def scan_database(self):
        """Scan all tables in Supabase database"""
        # This would use mcp__supabase__ tools to get schema
        # For now, we'll build from known tables structure
        print("Scanning all database tables...")

        # Get all tables
        tables = await self._get_all_tables()

        for table_name in tables:
            schema = await self._get_table_schema(table_name)
            self.schema_cache[table_name] = schema

        self.last_scan = datetime.datetime.now().isoformat()

    async def _get_all_tables(self) -> list[str]:
        """Get list of all tables in database"""
        # Known tables from the comprehensive analysis
        return [
            # Bid Card Ecosystem (15 tables)
            "bid_cards", "bid_card_distributions", "bid_card_engagement_events",
            "bid_card_views", "bids", "outreach_campaigns", "contractor_outreach_attempts",
            "campaign_check_ins", "campaign_contractors", "contractor_responses",
            "response_events", "manual_followup_tasks", "notifications",
            "followup_attempts", "followup_logs",

            # Contractor Discovery & Management (8 tables)
            "contractors", "contractor_leads", "potential_contractors",
            "potential_contractors_backup", "contractor_discovery_cache",
            "contractor_engagement_summary", "discovery_runs", "email_tracking_events",

            # Homeowner & Project Management (10 tables)
            "homeowners", "projects", "project_contexts", "project_summaries",
            "project_photos", "user_memories", "agent_conversations", "messages",
            "profiles", "reviews",

            # Inspiration & Design System (6 tables)
            "inspiration_boards", "inspiration_conversations", "inspiration_images",
            "generated_dream_spaces", "vision_compositions", "photo_storage",

            # Business & Operations (2 tables)
            "payments", "message_templates",

            # New Bid Card System Tables (5 tables)
            "contractor_bids", "bid_card_messages", "bid_milestones",
            "bid_card_images", "bid_card_documents", "message_attachments",
            "group_bids"
        ]

    async def _get_table_schema(self, table_name: str) -> TableSchema:
        """Get detailed schema for a specific table"""
        # This would use Supabase MCP to get actual schema
        # For now, we'll create example schemas for key tables

        schemas = {
            "bid_cards": TableSchema(
                name="bid_cards",
                columns={
                    "id": {"type": "uuid", "nullable": False, "default": "gen_random_uuid()"},
                    "title": {"type": "varchar(255)", "nullable": True},
                    "description": {"type": "text", "nullable": True},
                    "budget_min": {"type": "decimal(10,2)", "nullable": True},
                    "budget_max": {"type": "decimal(10,2)", "nullable": True},
                    "project_type": {"type": "varchar(100)", "nullable": True},
                    "status": {"type": "varchar(20)", "nullable": False, "default": "'draft'"},
                    "homeowner_id": {"type": "uuid", "nullable": False},
                    "created_at": {"type": "timestamp", "nullable": False, "default": "NOW()"},
                    "updated_at": {"type": "timestamp", "nullable": False, "default": "NOW()"}
                },
                primary_key=["id"],
                foreign_keys=[
                    {"column": "homeowner_id", "references": "homeowners.id"}
                ],
                indexes=[
                    {"name": "idx_bid_cards_status", "columns": ["status"]},
                    {"name": "idx_bid_cards_homeowner", "columns": ["homeowner_id"]},
                    {"name": "idx_bid_cards_created", "columns": ["created_at"]}
                ],
                constraints=[
                    {"type": "check", "name": "valid_budget", "condition": "budget_min <= budget_max"},
                    {"type": "check", "name": "valid_status", "condition": "status IN ('draft', 'active', 'collecting_bids', 'bids_complete', 'closed')"}
                ]
            ),
            "contractors": TableSchema(
                name="contractors",
                columns={
                    "id": {"type": "uuid", "nullable": False, "default": "gen_random_uuid()"},
                    "business_name": {"type": "varchar(255)", "nullable": False},
                    "contact_name": {"type": "varchar(255)", "nullable": False},
                    "email": {"type": "varchar(255)", "nullable": False},
                    "phone": {"type": "varchar(50)", "nullable": True},
                    "website": {"type": "varchar(255)", "nullable": True},
                    "specialty": {"type": "varchar(100)", "nullable": True},
                    "location_city": {"type": "varchar(100)", "nullable": True},
                    "location_state": {"type": "varchar(50)", "nullable": True},
                    "verified": {"type": "boolean", "nullable": False, "default": "false"},
                    "created_at": {"type": "timestamp", "nullable": False, "default": "NOW()"}
                },
                primary_key=["id"],
                foreign_keys=[],
                indexes=[
                    {"name": "idx_contractors_email", "columns": ["email"], "unique": True},
                    {"name": "idx_contractors_specialty", "columns": ["specialty"]},
                    {"name": "idx_contractors_location", "columns": ["location_city", "location_state"]}
                ],
                constraints=[
                    {"type": "unique", "name": "unique_contractor_email", "columns": ["email"]}
                ]
            )
        }

        return schemas.get(table_name, TableSchema(
            name=table_name,
            columns={"id": {"type": "uuid", "nullable": False}},
            primary_key=["id"],
            foreign_keys=[],
            indexes=[],
            constraints=[]
        ))

    async def analyze_relationships(self):
        """Analyze all foreign key relationships"""
        print("Analyzing table relationships...")

        relationships = {}

        for table_name, schema in self.schema_cache.items():
            for fk in schema.foreign_keys:
                rel_key = f"{table_name}.{fk['column']}"
                relationships[rel_key] = {
                    "from_table": table_name,
                    "from_column": fk["column"],
                    "to_table": fk["references"].split(".")[0],
                    "to_column": fk["references"].split(".")[1],
                    "relationship_type": "many_to_one"
                }

        self.relationships_cache = relationships

    async def save_knowledge_base(self):
        """Save complete knowledge base to files"""
        print("Saving knowledge base...")

        # Save schema snapshot
        schema_data = {
            "last_updated": self.last_scan,
            "table_count": len(self.schema_cache),
            "tables": {name: {
                "name": schema.name,
                "columns": schema.columns,
                "primary_key": schema.primary_key,
                "foreign_keys": schema.foreign_keys,
                "indexes": schema.indexes,
                "constraints": schema.constraints
            } for name, schema in self.schema_cache.items()}
        }

        await self._save_json("schema_current.json", schema_data)

        # Save relationships
        relationships_data = {
            "last_updated": self.last_scan,
            "relationship_count": len(self.relationships_cache),
            "relationships": self.relationships_cache
        }

        await self._save_json("relationships.json", relationships_data)

    async def _save_json(self, filename: str, data: dict):
        """Save data to JSON file"""
        filepath = os.path.join(self.knowledge_base_path, filename)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)

    async def consult(self, request: ConsultationRequest) -> ConsultationResponse:
        """Main consultation method"""
        print(f"Database Consultant: Received {request.request_type} request from {request.agent_id}")

        if request.request_type == "query":
            return await self._handle_query(request)
        elif request.request_type == "change":
            return await self._handle_change_request(request)
        elif request.request_type == "validate":
            return await self._handle_validation(request)
        elif request.request_type == "optimize":
            return await self._handle_optimization(request)
        else:
            return ConsultationResponse(
                recommendation="Unknown request type",
                warnings=["Request type not recognized"]
            )

    async def _handle_query(self, request: ConsultationRequest) -> ConsultationResponse:
        """Handle information queries"""
        description = request.description.lower()

        if "tables" in description and "list" in description:
            table_list = list(self.schema_cache.keys())
            return ConsultationResponse(
                recommendation=f"Found {len(table_list)} tables in database",
                implementation="\n".join(f"- {table}" for table in sorted(table_list))
            )

        if "relationships" in description:
            rel_count = len(self.relationships_cache)
            return ConsultationResponse(
                recommendation=f"Found {rel_count} foreign key relationships",
                implementation=json.dumps(self.relationships_cache, indent=2)
            )

        # Table-specific queries
        for table_name in self.schema_cache:
            if table_name in description:
                schema = self.schema_cache[table_name]
                return ConsultationResponse(
                    recommendation=f"Schema information for {table_name}",
                    implementation=json.dumps({
                        "columns": schema.columns,
                        "primary_key": schema.primary_key,
                        "foreign_keys": schema.foreign_keys,
                        "indexes": schema.indexes
                    }, indent=2)
                )

        return ConsultationResponse(
            recommendation="Query not understood. Try asking about 'tables list', 'relationships', or specific table names."
        )

    async def _handle_change_request(self, request: ConsultationRequest) -> ConsultationResponse:
        """Handle requests to modify database schema"""
        context = request.context

        if "add_table" in context:
            return await self._suggest_new_table(context)
        elif "add_column" in context:
            return await self._suggest_new_column(context)
        elif "modify_table" in context:
            return await self._suggest_table_modification(context)

        return ConsultationResponse(
            recommendation="Change request needs more specific context",
            alternatives=[
                "Specify 'add_table' with table definition",
                "Specify 'add_column' with table and column details",
                "Specify 'modify_table' with changes needed"
            ]
        )

    async def _suggest_new_table(self, context: dict[str, Any]) -> ConsultationResponse:
        """Suggest schema for new table"""
        table_name = context.get("table_name", "new_table")
        purpose = context.get("purpose", "")
        fields = context.get("fields", [])

        # Analyze purpose and suggest optimal schema
        columns = []
        columns.append("id UUID PRIMARY KEY DEFAULT gen_random_uuid()")

        for field in fields:
            field_name = field.get("name", "")
            field_type = field.get("type", "text")
            nullable = field.get("nullable", True)

            null_clause = "" if nullable else " NOT NULL"
            columns.append(f"{field_name} {field_type.upper()}{null_clause}")

        # Always add timestamps
        columns.append("created_at TIMESTAMP NOT NULL DEFAULT NOW()")
        columns.append("updated_at TIMESTAMP NOT NULL DEFAULT NOW()")

        migration_sql = f"""
-- Migration: Add {table_name} table
CREATE TABLE {table_name} (
  {',\\n  '.join(columns)}
);

-- Add indexes
CREATE INDEX idx_{table_name}_created ON {table_name}(created_at);
"""

        return ConsultationResponse(
            recommendation=f"Suggested schema for {table_name} table",
            implementation=migration_sql,
            impacts=[
                f"New table {table_name} will be created",
                "Consider adding foreign key relationships if needed",
                "Add appropriate indexes for query performance"
            ]
        )

    async def _handle_validation(self, request: ConsultationRequest) -> ConsultationResponse:
        """Validate proposed database changes"""
        return ConsultationResponse(
            recommendation="Validation logic to be implemented",
            warnings=["Validation feature under development"]
        )

    async def _handle_optimization(self, request: ConsultationRequest) -> ConsultationResponse:
        """Suggest database optimizations"""
        return ConsultationResponse(
            recommendation="Optimization analysis to be implemented",
            alternatives=["Add missing indexes", "Normalize relationships", "Partition large tables"]
        )

    def get_table_info(self, table_name: str) -> Optional[TableSchema]:
        """Get information about a specific table"""
        return self.schema_cache.get(table_name)

    def get_related_tables(self, table_name: str) -> list[str]:
        """Get list of tables related to given table"""
        related = []

        for rel_key, rel_info in self.relationships_cache.items():
            if rel_info["from_table"] == table_name:
                related.append(rel_info["to_table"])
            elif rel_info["to_table"] == table_name:
                related.append(rel_info["from_table"])

        return list(set(related))


# Example usage functions for testing
async def test_database_consultant():
    """Test the database consultant"""
    consultant = DatabaseSchemaConsultant()
    await consultant.initialize()

    # Test queries
    requests = [
        ConsultationRequest(
            agent_id="test_agent",
            request_type="query",
            description="list all tables",
            context={}
        ),
        ConsultationRequest(
            agent_id="test_agent",
            request_type="query",
            description="show me bid_cards table schema",
            context={}
        ),
        ConsultationRequest(
            agent_id="test_agent",
            request_type="change",
            description="add contractor certifications table",
            context={
                "add_table": True,
                "table_name": "contractor_certifications",
                "purpose": "track contractor licenses and certifications",
                "fields": [
                    {"name": "contractor_id", "type": "uuid", "nullable": False},
                    {"name": "certification_type", "type": "varchar(100)", "nullable": False},
                    {"name": "issuer", "type": "varchar(255)", "nullable": False},
                    {"name": "issue_date", "type": "date", "nullable": True},
                    {"name": "expiry_date", "type": "date", "nullable": True},
                    {"name": "document_url", "type": "text", "nullable": True}
                ]
            }
        )
    ]

    for request in requests:
        response = await consultant.consult(request)
        print(f"\\n--- {request.request_type.upper()} ---")
        print(f"Request: {request.description}")
        print(f"Response: {response.recommendation}")
        if response.implementation:
            print(f"Implementation:\\n{response.implementation}")
        if response.impacts:
            print(f"Impacts: {', '.join(response.impacts)}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_database_consultant())
