"""
Intelligent Job Assessment Agent - LangGraph + Claude Opus 4 Implementation
Replaces regex-based extraction with real AI intelligence
"""
import json
import os
import sys
from datetime import datetime
from typing import Annotated, Any

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from supabase import create_client


# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from typing_extensions import TypedDict

from database_simple import SupabaseDB
from bid_card_utils import create_bid_card_with_defaults


class IntelligentJAAState(TypedDict):
    """State for the Intelligent JAA Agent"""
    messages: Annotated[list[BaseMessage], add_messages]
    conversation_data: dict[str, Any]
    extracted_data: dict[str, Any]
    bid_card_data: dict[str, Any]
    thread_id: str
    stage: str  # 'analysis', 'extraction', 'validation', 'generation'
    errors: list[str]

class JobAssessmentAgent:
    """
    Intelligent Job Assessment Agent using Claude Opus 4 + LangGraph
    Replaces simple regex patterns with real AI understanding
    """

    def __init__(self):
        """Initialize Intelligent JAA with Claude Opus 4 and LangGraph"""
        load_dotenv(override=True)

        # Initialize Anthropic client
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        self.llm = ChatAnthropic(
            model="claude-opus-4-20250514",  # Claude Opus 4 - most powerful model for complex reasoning
            api_key=self.anthropic_key,
            temperature=0.1,
            max_tokens=4000
        )

        # Initialize Supabase
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        self.supabase = create_client(self.supabase_url, self.supabase_key)
        self.db = SupabaseDB()

        # Build the LangGraph workflow
        self.workflow = self._build_workflow()

        print("[INTELLIGENT JAA] Initialized with Claude Opus 4 + LangGraph")

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for intelligent bid card generation"""

        workflow = StateGraph(IntelligentJAAState)

        # Add nodes
        workflow.add_node("analyze_conversation", self._analyze_conversation)
        workflow.add_node("extract_project_data", self._extract_project_data)
        workflow.add_node("validate_extraction", self._validate_extraction)
        workflow.add_node("generate_bid_card", self._generate_bid_card)

        # Add edges
        workflow.add_edge(START, "analyze_conversation")
        workflow.add_edge("analyze_conversation", "extract_project_data")
        workflow.add_edge("extract_project_data", "validate_extraction")
        workflow.add_edge("validate_extraction", "generate_bid_card")
        workflow.add_edge("generate_bid_card", END)

        return workflow.compile()

    def process_conversation(self, thread_id: str) -> dict[str, Any]:
        """
        Main entry point: Process CIA conversation with full AI intelligence

        Args:
            thread_id: The conversation thread ID from CIA

        Returns:
            Dict with success status and bid card data
        """
        print(f"\n[INTELLIGENT JAA] Processing conversation: {thread_id}")

        try:
            # Step 1: Load conversation from database
            print("[INTELLIGENT JAA] Loading conversation from database...")
            result = self.supabase.table("agent_conversations").select("*").eq("thread_id", thread_id).execute()

            if not result.data or len(result.data) == 0:
                return {
                    "success": False,
                    "error": f"No conversation found for thread_id: {thread_id}"
                }

            conversation_data = result.data[0]

            # Parse state if it's JSON string
            state = conversation_data.get("state", {})
            if isinstance(state, str):
                state = json.loads(state)
                conversation_data["state"] = state

            print(f"[INTELLIGENT JAA] Loaded conversation with {len(state.get('messages', []))} messages")

            # Step 2: Initialize state and run LangGraph workflow
            initial_state = {
                "messages": [],
                "conversation_data": conversation_data,
                "extracted_data": {},
                "bid_card_data": {},
                "thread_id": thread_id,
                "stage": "analysis",
                "errors": []
            }

            # Run the intelligent workflow
            final_state = self.workflow.invoke(initial_state)

            if final_state["errors"]:
                return {
                    "success": False,
                    "error": f'Processing errors: {"; ".join(final_state["errors"])}'
                }

            # Step 3: Save to database using new utility
            print("[INTELLIGENT JAA] Creating bid card with fixed database schema...")
            
            # Prepare project data for the new utility
            project_data = {
                "project_type": final_state["bid_card_data"].get("project_type", "general_renovation"),
                "title": final_state["bid_card_data"].get("title", "New Project"),
                "description": final_state["bid_card_data"].get("description", ""),
                "urgency_level": final_state["bid_card_data"].get("urgency_level", "week"),
                "complexity_score": final_state["bid_card_data"].get("complexity_score", 3),
                "contractor_count_needed": final_state["bid_card_data"].get("contractor_count_needed", 3),
                "budget_min": final_state["bid_card_data"].get("budget_min"),
                "budget_max": final_state["bid_card_data"].get("budget_max"),
                "requirements": final_state["bid_card_data"].get("requirements", []),
                "location_city": final_state["bid_card_data"].get("location_city"),
                "location_state": final_state["bid_card_data"].get("location_state"),
                "location_zip": final_state["bid_card_data"].get("location_zip"),
                "cia_thread_id": thread_id[-20:],  # Truncate to fit VARCHAR(20)
                "timeline_start": final_state["bid_card_data"].get("timeline_start"),
                "timeline_end": final_state["bid_card_data"].get("timeline_end")
            }
            
            # Create bid card using the new utility
            create_result = create_bid_card_with_defaults(project_data)
            
            if create_result["success"]:
                bid_card_data = create_result["bid_card"]
                bid_card_number = create_result["bid_card_number"]
                
                # Update the bid_document with AI analysis
                bid_document = {
                    "bid_card_number": bid_card_number,
                    "full_cia_thread_id": thread_id,
                    "all_extracted_data": final_state["extracted_data"],
                    "ai_analysis": final_state["bid_card_data"],
                    "generated_at": datetime.now().isoformat(),
                    "extraction_method": "IntelligentJAA_ClaudeOpus4",
                    "instabids_version": "3.0"
                }
                
                # Update the bid_document field
                update_result = self.supabase.table("bid_cards").update({
                    "bid_document": bid_document
                }).eq("id", bid_card_data["id"]).execute()
                
                print(f"[INTELLIGENT JAA] SUCCESS: Created bid card {bid_card_number}")
                print(f"[INTELLIGENT JAA] Project: {final_state['bid_card_data'].get('project_type')}")
                print(f"[INTELLIGENT JAA] Budget: ${final_state['bid_card_data'].get('budget_min')}-${final_state['bid_card_data'].get('budget_max')}")
                
                return {
                    "success": True,
                    "bid_card_number": bid_card_number,
                    "bid_card_data": final_state["bid_card_data"],
                    "cia_thread_id": thread_id,
                    "database_id": bid_card_data["id"]
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to create bid card: {create_result['error']}"
                }

        except Exception as e:
            print(f"[INTELLIGENT JAA ERROR] {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }

    def _analyze_conversation(self, state: IntelligentJAAState) -> IntelligentJAAState:
        """Step 1: Analyze conversation with AI to understand project scope"""
        print("[INTELLIGENT JAA] Stage 1: Analyzing conversation with Claude Opus 4...")

        # Extract conversation messages
        conversation_state = state["conversation_data"].get("state", {})
        messages = conversation_state.get("messages", [])
        collected_info = conversation_state.get("collected_info", {})

        # Combine all user messages
        user_messages = []
        for msg in messages:
            if msg.get("role") == "user":
                user_messages.append(msg.get("content", ""))

        full_conversation = "\n".join(user_messages)

        # Create analysis prompt
        analysis_prompt = f"""
You are an expert project analyst for InstaBids, a contractor marketplace.

Analyze this homeowner conversation and provide a detailed understanding of their project:

CONVERSATION:
{full_conversation}

COLLECTED INFO FROM CIA:
{json.dumps(collected_info, indent=2)}

Please analyze and provide:

1. PROJECT UNDERSTANDING:
   - What type of project is this?
   - What is the homeowner's primary goal?
   - What specific work needs to be done?

2. URGENCY & TIMELINE:
   - How urgent is this project?
   - When do they want to start?
   - Any time constraints or deadlines?

3. BUDGET ANALYSIS:
   - What budget range did they mention?
   - Do they seem price-sensitive or quality-focused?
   - Are there any budget constraints?

4. COMPLEXITY ASSESSMENT:
   - Is this a simple or complex project?
   - What challenges might contractors face?
   - Any special requirements or permits needed?

5. HOMEOWNER PROFILE:
   - How serious are they about proceeding?
   - Do they seem well-informed about the project?
   - Any specific preferences or concerns?

Provide your analysis in clear, structured format.
"""

        try:
            response = self.llm.invoke([
                SystemMessage(content="You are an expert project analyst for InstaBids contractor marketplace."),
                HumanMessage(content=analysis_prompt)
            ])

            # Store analysis
            state["extracted_data"]["ai_analysis"] = response.content
            state["stage"] = "extraction"

            print("[INTELLIGENT JAA] Conversation analysis complete")
            return state

        except Exception as e:
            state["errors"].append(f"Analysis failed: {e!s}")
            return state

    def _extract_project_data(self, state: IntelligentJAAState) -> IntelligentJAAState:
        """Step 2: Extract structured data points using AI intelligence"""
        print("[INTELLIGENT JAA] Stage 2: Extracting structured data with AI...")

        # Get conversation data
        conversation_state = state["conversation_data"].get("state", {})
        messages = conversation_state.get("messages", [])
        collected_info = conversation_state.get("collected_info", {})

        user_messages = []
        for msg in messages:
            if msg.get("role") == "user":
                user_messages.append(msg.get("content", ""))

        full_conversation = "\n".join(user_messages)

        # Create extraction prompt
        extraction_prompt = f"""
You are a data extraction specialist for InstaBids contractor marketplace.

Extract structured data from this homeowner conversation:

CONVERSATION:
{full_conversation}

COLLECTED INFO:
{json.dumps(collected_info, indent=2)}

PREVIOUS ANALYSIS:
{state["extracted_data"].get('ai_analysis', 'No previous analysis')}

Extract the following data points in JSON format:

{{
  "project_type": "kitchen|bathroom|roofing|flooring|plumbing|electrical|hvac|painting|landscaping|general",
  "service_type": "installation|repair|maintenance|renovation|new_construction",
  "project_description": "Detailed description of work needed",
  "budget_min": integer (minimum budget in dollars),
  "budget_max": integer (maximum budget in dollars),
  "budget_confidence": "high|medium|low",
  "urgency_level": "emergency|urgent|flexible",
  "timeline_start": "when they want to start",
  "timeline_duration": "expected project duration",
  "location": {{
    "address": "full address if provided",
    "city": "city name",
    "state": "state name",
    "zip_code": "zip code",
    "property_type": "house|condo|apartment|commercial"
  }},
  "materials_specified": ["list of materials mentioned"],
  "special_requirements": ["list of special needs"],
  "homeowner_info": {{
    "name": "homeowner name if provided",
    "email": "email if provided",
    "phone": "phone if provided",
    "communication_preference": "email|phone|text"
  }},
  "contractor_requirements": {{
    "count_needed": integer (3-6 contractors),
    "specialties_required": ["list of required specialties"],
    "license_requirements": ["list of required licenses"]
  }},
  "complexity_factors": ["list of complexity factors"],
  "quality_expectations": "basic|standard|premium",
  "intention_score": integer (1-10, how serious are they)
}}

IMPORTANT:
- Only extract data that is clearly mentioned or strongly implied
- Use null for unknown values
- Be conservative with budget estimates
- Consider urgency carefully based on language used
- Assess intention score based on specificity and commitment level

Return ONLY the JSON, no additional text.
"""

        try:
            response = self.llm.invoke([
                SystemMessage(content="You are a data extraction specialist. Return only valid JSON."),
                HumanMessage(content=extraction_prompt)
            ])

            # Clean the response - remove markdown code blocks if present
            response_content = response.content.strip()
            if response_content.startswith("```json"):
                response_content = response_content[7:]  # Remove ```json
            if response_content.endswith("```"):
                response_content = response_content[:-3]  # Remove ```
            response_content = response_content.strip()

            # Parse the JSON response
            extracted_data = json.loads(response_content)
            state["extracted_data"].update(extracted_data)
            state["stage"] = "validation"

            print("[INTELLIGENT JAA] Data extraction complete")
            return state

        except json.JSONDecodeError as e:
            state["errors"].append(f"JSON parsing failed: {e!s}")
            return state
        except Exception as e:
            state["errors"].append(f"Extraction failed: {e!s}")
            return state

    def _validate_extraction(self, state: IntelligentJAAState) -> IntelligentJAAState:
        """Step 3: Validate extracted data and fill in missing pieces"""
        print("[INTELLIGENT JAA] Stage 3: Validating and enriching data...")

        # Basic validation and defaults
        extracted = state["extracted_data"]

        # Ensure required fields have sensible defaults
        if not extracted.get("project_type"):
            extracted["project_type"] = "general"

        if not extracted.get("budget_min") or extracted["budget_min"] < 100:
            extracted["budget_min"] = 5000

        if not extracted.get("budget_max") or extracted["budget_max"] < extracted["budget_min"]:
            extracted["budget_max"] = max(extracted["budget_min"] * 2, 15000)

        if not extracted.get("urgency_level"):
            extracted["urgency_level"] = "flexible"

        if not extracted.get("contractor_requirements"):
            extracted["contractor_requirements"] = {
                "count_needed": 4,
                "specialties_required": [],
                "license_requirements": []
            }

        # Calculate complexity score
        complexity_score = self._calculate_complexity_score(extracted)
        extracted["complexity_score"] = complexity_score

        state["stage"] = "generation"
        print("[INTELLIGENT JAA] Data validation complete")
        return state

    def _generate_bid_card(self, state: IntelligentJAAState) -> IntelligentJAAState:
        """Step 4: Generate final bid card with all InstaBids-specific data"""
        print("[INTELLIGENT JAA] Stage 4: Generating professional bid card...")

        extracted = state["extracted_data"]

        # Generate final bid card data
        bid_card_data = {
            # Core project info
            "project_type": extracted.get("project_type", "general"),
            "service_type": extracted.get("service_type", "installation"),
            "project_description": extracted.get("project_description", "Project details to be discussed"),

            # Budget and timeline
            "budget_min": extracted.get("budget_min", 5000),
            "budget_max": extracted.get("budget_max", 15000),
            "budget_confidence": extracted.get("budget_confidence", "medium"),
            "urgency_level": extracted.get("urgency_level", "flexible"),
            "timeline_start": extracted.get("timeline_start"),
            "timeline_duration": extracted.get("timeline_duration"),

            # Location
            "location": extracted.get("location", {}),

            # Requirements
            "materials_specified": extracted.get("materials_specified", []),
            "special_requirements": extracted.get("special_requirements", []),

            # Contractor needs
            "contractor_count_needed": extracted.get("contractor_requirements", {}).get("count_needed", 4),
            "specialties_required": extracted.get("contractor_requirements", {}).get("specialties_required", []),
            "license_requirements": extracted.get("contractor_requirements", {}).get("license_requirements", []),

            # InstaBids metrics
            "complexity_score": extracted.get("complexity_score", 5),
            "intention_score": extracted.get("intention_score", 7),
            "quality_expectations": extracted.get("quality_expectations", "standard"),

            # Homeowner info
            "homeowner_info": extracted.get("homeowner_info", {}),

            # AI generated insights
            "ai_insights": {
                "project_analysis": state["extracted_data"].get("ai_analysis"),
                "complexity_factors": extracted.get("complexity_factors", []),
                "generated_by": "IntelligentJAA_ClaudeOpus4",
                "generated_at": datetime.now().isoformat()
            }
        }

        state["bid_card_data"] = bid_card_data
        print("[INTELLIGENT JAA] Bid card generation complete")
        return state

    def _calculate_complexity_score(self, extracted_data: dict[str, Any]) -> int:
        """Calculate project complexity score (1-10) using AI-extracted data"""
        score = 5  # Base score

        # Budget impact
        budget_max = extracted_data.get("budget_max", 0)
        if budget_max > 100000:
            score += 4
        elif budget_max > 50000:
            score += 3
        elif budget_max > 25000:
            score += 2
        elif budget_max > 10000:
            score += 1
        elif budget_max < 2000:
            score -= 2

        # Urgency impact
        urgency = extracted_data.get("urgency_level", "flexible")
        if urgency == "emergency":
            score += 3
        elif urgency == "urgent":
            score += 2

        # Special requirements
        special_reqs = extracted_data.get("special_requirements", [])
        score += len(special_reqs)

        # Complexity factors
        complexity_factors = extracted_data.get("complexity_factors", [])
        score += len(complexity_factors) * 0.5

        # License requirements indicate complexity
        license_reqs = extracted_data.get("contractor_requirements", {}).get("license_requirements", [])
        score += len(license_reqs)

        return max(1, min(10, int(score)))

    def _generate_bid_card_number(self) -> str:
        """Generate unique bid card number"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"IBC-{timestamp}"  # Intelligent Bid Card prefix


# Test the intelligent agent
if __name__ == "__main__":

    def test_intelligent_jaa():
        """Test the intelligent JAA with a real conversation"""
        jaa = JobAssessmentAgent()

        # Use a real thread ID from your testing
        test_thread_id = "session_1727644456_test_bathroom_renovation"

        result = jaa.process_conversation(test_thread_id)

        if result.get("success"):
            print("\nINTELLIGENT JAA Test Passed!")
            print(f"Created bid card: {result['bid_card_number']}")
            print(f"Project type: {result['bid_card_data']['project_type']}")
            print(f"Budget: ${result['bid_card_data']['budget_min']}-${result['bid_card_data']['budget_max']}")
        else:
            print(f"\nINTELLIGENT JAA Test Failed: {result.get('error')}")

    test_intelligent_jaa()
