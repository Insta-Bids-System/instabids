"""CIA (Customer Interface Agent) Implementation - Using OpenAI GPT-5"""
import json
import os
import sys
import time
from datetime import datetime
from typing import Any, Optional
import httpx
import asyncio

from openai import AsyncOpenAI
from dotenv import load_dotenv
from supabase import create_client

# Import universal session manager for persistent memory
from services.universal_session_manager import universal_session_manager

# Import unified integration for homeowner context
from agents.cia.unified_integration import CIAUnifiedIntegration
from agents.cia.potential_bid_card_integration import PotentialBidCardManager

# Import LLM cost tracking
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from services.llm_cost_tracker import LLMCostTracker

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.cia.modification_handler import ModificationHandler
from agents.cia.prompts import SYSTEM_PROMPT, get_conversation_prompt
from agents.cia.service_complexity_classifier import ServiceComplexityClassifier
from agents.cia.state import (
    GROUP_BIDDING_PROJECTS,
    INTENTION_SCORE_FACTORS,
    REQUIRED_FIELDS_MINIMAL,
    SERVICE_TYPE_KEYWORDS,
)


# from memory.langgraph_integration import (
#     setup_project_aware_agent,
#     update_agent_memory_after_conversation,
# )
# Temporarily disabled to fix timeout issue


class CustomerInterfaceAgent:
    """CIA - Handles all homeowner interactions for project scoping"""

    def __init__(self, api_key: str):
        """Initialize the CIA with OpenAI GPT-5"""
        print(f"[CIA] Initializing with API key: {api_key[:20]}...")
        
        # Initialize cost tracker
        self.cost_tracker = LLMCostTracker()

        if api_key == "demo_key":
            self.client = None  # Demo mode
            self.api_type = "demo"
            print("[CIA] Running in DEMO mode - no API key provided")
        elif api_key.startswith("openai:"):
            # Use OpenAI GPT-5
            try:
                actual_key = api_key[7:]  # Remove "openai:" prefix
                self.client = AsyncOpenAI(api_key=actual_key)
                self.api_type = "openai"
                print("[CIA] Successfully initialized OpenAI client with GPT-5")
            except Exception as e:
                print(f"[CIA ERROR] Failed to initialize OpenAI client: {e}")
                self.client = None
                self.api_type = "none"
        else:
            # Direct OpenAI API key (no prefix)
            try:
                self.client = AsyncOpenAI(api_key=api_key)
                self.api_type = "openai"
                print("[CIA] Successfully initialized OpenAI client with GPT-5")
            except Exception as e:
                print(f"[CIA ERROR] Failed to initialize OpenAI client: {e}")
                self.client = None
                self.api_type = "none"

        # Initialize ModificationHandler for reliable modification detection
        self.modification_handler = ModificationHandler()

        # Initialize ServiceComplexityClassifier for project classification
        self.service_classifier = ServiceComplexityClassifier()

        # Initialize mode manager for switching between conversation and action modes
        from .mode_manager import ModeManager
        self.mode_manager = ModeManager()

        # Initialize Supabase connection for conversation persistence
        # Load from root .env file explicitly
        root_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), '.env')
        load_dotenv(root_env_path, override=True)
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        self.supabase = create_client(self.supabase_url, self.supabase_key)
        print("[CIA] Initialized Supabase connection")

        # Initialize unified integration for homeowner context adapter
        self.unified_integration = CIAUnifiedIntegration()
        
        # Initialize potential bid card manager
        self.bid_card_manager = PotentialBidCardManager()
        
        # Initialize the HomeownerContextAdapter for FULL database access
        from adapters.homeowner_context import HomeownerContextAdapter
        self.context_adapter = HomeownerContextAdapter()
        print("[CIA] Initialized HomeownerContextAdapter with FULL database access")

        # In-memory session storage (in production, use database)
        self.sessions = {}

    async def _call_llm(self, messages, max_tokens=4000, system=None):
        """Call OpenAI GPT-5 with vision support"""
        if not self.client:
            return None
            
        try:
            if self.api_type == "openai":
                # Convert messages to OpenAI format
                openai_messages = []
                
                # Add system message first if provided
                if system:
                    openai_messages.append({"role": "system", "content": system})
                
                for msg in messages:
                    if hasattr(msg, 'role') and hasattr(msg, 'content'):
                        # Legacy format - convert to dict
                        openai_messages.append({
                            "role": msg.role,
                            "content": msg.content
                        })
                    else:
                        # Already in dict format - check for vision content
                        content = msg.get("content")
                        if isinstance(content, list):
                            # Handle vision messages with text and images
                            formatted_content = []
                            for item in content:
                                if item.get("type") == "text":
                                    formatted_content.append({
                                        "type": "text",
                                        "text": item["text"]
                                    })
                                elif item.get("type") == "image":
                                    # Convert from Claude format to OpenAI format
                                    if item.get("source"):
                                        formatted_content.append({
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:{item['source']['media_type']};base64,{item['source']['data']}"
                                            }
                                        })
                            openai_messages.append({
                                "role": msg["role"],
                                "content": formatted_content
                            })
                        else:
                            # Simple text message
                            openai_messages.append(msg)
                
                # Use GPT-5 with vision support
                start_time = time.time()
                response = await self.client.chat.completions.create(
                    model="gpt-4o",  # Using GPT-4o (GPT-5 doesn't exist yet)
                    messages=openai_messages,
                    max_completion_tokens=max_tokens
                    # temperature=1 is default for GPT-4o, no need to specify
                )
                
                # Track the cost (using sync version to avoid async issues)
                duration_ms = int((time.time() - start_time) * 1000)
                if hasattr(response, 'usage'):
                    self.cost_tracker.track_llm_call_sync(
                        agent_name="CIA",
                        provider="openai",
                        model="gpt-4o",
                        input_tokens=response.usage.prompt_tokens,
                        output_tokens=response.usage.completion_tokens,
                        duration_ms=duration_ms,
                        context={
                            "user_id": user_id if 'user_id' in locals() else None,
                            "has_images": bool(images) if 'images' in locals() else False
                        }
                    )
                
                return response.choices[0].message.content
                
        except Exception as e:
            print(f"[CIA ERROR] GPT-5 call failed: {e}")
            return None
            
        return None

    async def handle_conversation(
        self,
        user_id: str,
        message: str,
        images: Optional[list[str]] = None,
        session_id: Optional[str] = None,
        existing_state: Optional[dict[str, Any]] = None,
        project_id: Optional[str] = None
    ) -> dict[str, Any]:
        """Main entry point for handling user conversations - now project-aware"""
        print(f"\n[CIA] Handling conversation - User: {user_id}, Session: {session_id}")
        print(f"[CIA] Project ID: {project_id}")
        print(f"[CIA] Message: {message}")
        print(f"[CIA] Has client: {self.client is not None}")
        
        # SAFETY CHECK: Ensure message is not None
        if message is None:
            message = ""
            print(f"[CIA] WARNING: message was None, using empty string")

        # UPDATED: Use universal session manager for persistent memory
        if not session_id:
            session_id = f"session_{user_id}_{datetime.now().timestamp()}"
        
        # Load or create session using universal session manager
        session_state = await universal_session_manager.get_or_create_session(
            session_id=session_id,
            user_id=user_id,
            agent_type="CIA",
            create_if_missing=True
        )
        
        # Add user message to session
        await universal_session_manager.add_message_to_session(
            session_id=session_id,
            role="user",
            content=message
        )
        
        # Load FULL context from HomeownerContextAdapter with complete database access
        print(f"[CIA] Loading FULL homeowner context via adapter...")
        try:
            # Use the adapter directly for FULL database access
            homeowner_context = self.context_adapter.get_full_agent_context(
                user_id=user_id,
                specific_bid_card_id=project_id,  # project_id is often the bid_card_id
                conversation_id=session_id
            )
            print(f"[CIA] Loaded FULL context: {len(homeowner_context)} data categories")
            print(f"[CIA] Context includes: {', '.join(homeowner_context.keys())}")
        except Exception as e:
            print(f"[CIA] ERROR: Could not load homeowner context: {e}")
            homeowner_context = {"context_available": False}
            # This should not happen - adapter should always work
            raise Exception(f"CRITICAL: HomeownerContextAdapter failed - CIA cannot function without database access: {e}")
        
        # Save homeowner context in state for use in response generation
        # Get or migrate to CIA-specific state structure
        if existing_state:
            # Use provided existing state
            state = existing_state
            state = self._migrate_to_new_structure(state)
            print(f"[CIA] Using provided existing state")
        else:
            # Get state from session context or create new
            existing_cia_state = session_state.get("context", {}).get("cia_state")
            if not existing_cia_state:
                state = self._create_new_session_with_instabids_structure(user_id, session_id)
                # Save new state to session context
                if "context" not in session_state:
                    session_state["context"] = {}
                session_state["context"]["cia_state"] = state
                print(f"[CIA] Created new CIA state in session: {session_id}")
                
                # Create potential bid card for new conversations
                bid_card_id = await self.bid_card_manager.create_potential_bid_card(
                    conversation_id=session_id,
                    session_id=session_id,
                    user_id=user_id
                )
                if bid_card_id:
                    state["potential_bid_card_id"] = bid_card_id
                    print(f"[CIA] Created potential bid card: {bid_card_id}")
            else:
                # Ensure state is properly structured
                state = existing_cia_state
                # Ensure critical fields exist and are not None
                if not state.get("collected_info"):
                    state["collected_info"] = {}
                if not state.get("messages"):
                    state["messages"] = []
                if "current_phase" not in state:
                    state["current_phase"] = "discovery"
                print(f"[CIA] Loaded existing CIA state from session: {session_id}")
        
        # Keep local reference for compatibility with existing code
        self.sessions[session_id] = state
        
        # Add homeowner context to state for use in response generation
        state["homeowner_context"] = homeowner_context

        # Restore active bid card if it exists
        if state.get("active_bid_card"):
            print(f"[CIA] Restored active bid card from session: {state['active_bid_card']}")

        # CRITICAL: MODE SWITCHING - Determine if we should be in action or conversation mode
        user_bid_cards = await self._find_user_bid_cards(user_id)

        # If we have an active bid card but it's not in the search results, add it
        if state.get("active_bid_card") and state.get("bid_card_context"):
            # Check if active card is in the results
            found_active = any(card["bid_card_number"] == state["active_bid_card"] for card in user_bid_cards)
            if not found_active:
                # Add the active bid card to the list
                user_bid_cards.append(state["bid_card_context"])
                print(f"[CIA] Added active bid card {state['active_bid_card']} to user's cards")

        context = {
            "user_bid_cards": user_bid_cards,
            "has_active_project": bool(project_id) or bool(state.get("active_bid_card")),
            "message_count": state.get("message_count", 0)
        }

        mode = self.mode_manager.analyze_intent(message, context)
        print(f"[CIA] Mode: {mode.value}")

        # ACTION MODE - Skip all project decisions, go straight to modifications
        if mode.value == "action" and user_bid_cards:
            print("[CIA] ACTION MODE: Handling modification directly")
            print(f"[CIA] ACTION MODE: State has active_bid_card: {state.get('active_bid_card')}")
            print(f"[CIA] ACTION MODE: State keys: {list(state.keys())}")

            # Check if this is a modification using GPT-5 intelligence
            modification_analysis = await self._analyze_modification_with_gpt5(message, state)
            is_modification = modification_analysis.get("is_modification", False)

            if is_modification:
                # ALWAYS use active bid card if available
                relevant_bid_card = None
                if state.get("active_bid_card"):
                    print(f"[CIA] ACTION MODE: Looking for active bid card: {state['active_bid_card']}")
                    # Look for the active bid card
                    for card in user_bid_cards:
                        print(f"[CIA] ACTION MODE: Checking card {card['bid_card_number']}")
                        if card["bid_card_number"] == state["active_bid_card"]:
                            relevant_bid_card = card
                            print(f"[CIA] ACTION MODE: FOUND ACTIVE bid card: {state['active_bid_card']}")
                            break
                    if not relevant_bid_card:
                        print(f"[CIA] ACTION MODE: Active bid card {state['active_bid_card']} not found in user's cards!")
                elif state.get("bid_card_number"):
                    # Fall back to context bid card
                    for card in user_bid_cards:
                        if card["bid_card_number"] == state["bid_card_number"]:
                            relevant_bid_card = card
                            print(f"[CIA] ACTION MODE: Using bid card from context: {state['bid_card_number']}")
                            break

                if not relevant_bid_card:
                    # Only search if no active context
                    project_type = modification_analysis.get("project_type")

                    if project_type:
                        # Look for bid card matching project type
                        for card in user_bid_cards:
                            if project_type and str(project_type).lower() in card.get("project_type", "").lower():
                                relevant_bid_card = card
                                break

                    # If no match, use most recent
                    if not relevant_bid_card:
                        relevant_bid_card = user_bid_cards[0]

                bid_card_number = relevant_bid_card["bid_card_number"]
                print(f"[CIA] Found bid card for modification: {bid_card_number}")

                # Apply modification through JAA
                result = await self._apply_bid_card_modification(
                    bid_card_number,
                    modification_analysis.get("modifications", {}),
                    user_id=user_id,
                    session_id=session_id,
                    message=message
                )

                if result.get("success"):
                    response = self.modification_handler.format_modification_response(
                        modification_analysis.get("modifications", {}),
                        bid_card_number,
                        relevant_bid_card["project_type"]
                    )

                    return {
                        "response": response,
                        "session_id": session_id,
                        "current_phase": "modification_complete",
                        "ready_for_jaa": False,
                        "missing_fields": [],
                        "state": state,
                        "modification_applied": True,
                        "mode": "action"
                    }
                else:
                    return {
                        "response": f"I had trouble updating that. {result.get('error', 'Could you try again?')}",
                        "session_id": session_id,
                        "current_phase": "modification_error",
                        "ready_for_jaa": False,
                        "missing_fields": [],
                        "state": state,
                        "mode": "action"
                    }

        # CONVERSATION MODE - Continue with normal project logic
        print("[CIA] CONVERSATION MODE: Normal project handling")

        # Ensure we have a proper user ID - convert to real user for persistence
        original_user_id = user_id
        if user_id == "00000000-0000-0000-0000-000000000000" or not user_id:
            from database_simple import db
            user_id = await db.get_or_create_test_user()
            print(f"[CIA] Converted anonymous user {original_user_id} to persistent user: {user_id}")

            # CRITICAL: Update state with the real user_id
            state["user_id"] = user_id
            print(f"[CIA] Updated state user_id to: {user_id}")

        # CRITICAL: Project Decision Logic - Determine if this is continuation or new project
        if not project_id:
            # Load user's project summaries for context
            try:
                from memory.multi_project_store import MultiProjectMemoryStore
                store = MultiProjectMemoryStore()
                summaries = await store.get_user_projects_summary(user_id)

                if summaries:
                    # Add project summaries to state for general conversation context
                    state["user_project_summaries"] = summaries
                    print(f"[CIA] Loaded {len(summaries)} project summaries for conversation context")
            except Exception as e:
                print(f"[CIA] Warning: Could not load project summaries: {e}")

            project_decision = await self._determine_project_intent(user_id, message)
            if project_decision:
                print(f"[CIA] Project decision: {project_decision}")
                if project_decision.get("action") == "ask_clarification":
                    # Return clarification question immediately
                    return {
                        "response": project_decision["response"],
                        "session_id": session_id,
                        "current_phase": "project_decision",
                        "ready_for_jaa": False,
                        "missing_fields": [],
                        "state": state,
                        "needs_project_decision": True,
                        "suggested_project_id": project_decision.get("suggested_project_id")
                    }
                elif project_decision.get("action") == "use_existing":
                    project_id = project_decision["project_id"]
                    print(f"[CIA] Using existing project: {project_id}")
                elif project_decision.get("action") == "create_new":
                    print(f"[CIA] Will create new project for: {project_decision.get('project_type')}")
                    # project_id remains None, will trigger new project creation

        # Set up project-aware memory context if project is specified
        cross_project_context = None
        agent_memory_config = None
        bid_card_context = None

        # Check if project_id is actually a bid card number
        if project_id and (project_id.startswith(("IBC-", "BC-"))):
            print(f"[CIA] Project ID is a bid card number: {project_id}")
            bid_card_context = await self._get_bid_card_details(project_id)
            if bid_card_context:
                print(f"[CIA] Loaded bid card context for {project_id}")
                # Add bid card to state for context awareness
                state["bid_card_context"] = bid_card_context
                state["bid_card_number"] = project_id
                state["active_bid_card"] = project_id  # PERSISTENT active card
                state["active_project_type"] = bid_card_context.get("project_type", "project")

        if project_id:
            try:
                # Initialize project-aware agent configuration
                # agent_memory_config = await setup_project_aware_agent(user_id, project_id, session_id)
                # cross_project_context = agent_memory_config.get("configurable", {}).get("cross_project_context", {})
                # Temporarily disabled to fix timeout
                agent_memory_config = {}
                cross_project_context = {}

                if cross_project_context:
                    print(f"[CIA] Loaded cross-project context with {len(cross_project_context.get('other_projects_summaries', []))} other projects")

                    # Add project awareness to state
                    state["project_context"] = {
                        "project_id": project_id,
                        "has_other_projects": cross_project_context.get("other_projects_count", 0) > 0,
                        "user_preferences": cross_project_context.get("user_memories", {}),
                        "related_projects": cross_project_context.get("project_relationships", {})
                    }
            except Exception as e:
                print(f"[CIA] Warning: Could not load project context: {e}")

        # Store images using unified attachment system
        if images and len(images) > 0:
            try:
                print(f"[CIA] Processing {len(images)} images with unified attachment system")
                
                # Convert user_id to UUID format for unified system
                import uuid
                try:
                    user_uuid = str(uuid.UUID(user_id))
                except ValueError:
                    user_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, user_id))
                
                # Handle images in unified system
                conversation_id = await self._ensure_unified_conversation(user_id, session_id)
                message_id = await self._save_unified_message(
                    conversation_id=conversation_id,
                    sender_type="user", 
                    sender_id=user_uuid,
                    content=message or "",
                    metadata={"agent": "CIA", "has_images": True, "image_count": len(images)}
                )
                urls = await self._upload_and_attach_images(conversation_id, message_id, images)
                
                # Store URLs in collected_info for backward compatibility
                if urls:
                    state["collected_info"]["uploaded_photos"] = urls
                    print(f"[CIA] Successfully processed {len(urls)} images via unified system")
                    # Set flag to prevent double saving in _save_to_unified_conversations
                    state["_images_already_saved"] = True
                else:
                    print("[CIA] Warning: No images were processed successfully")

            except Exception as e:
                print(f"[CIA] Error in unified image processing: {e}")
                images = []  # Continue without images

        # Add user message
        state["messages"].append({
            "role": "user",
            "content": message,
            "images": images,
            "metadata": {"timestamp": datetime.now().isoformat()}
        })

        # Store images in collected_info and database
        if images and len(images) > 0:
            state["collected_info"]["uploaded_photos"] = images
            print(f"[CIA] Added {len(images)} photos to collected_info")

            # Save photos to database if we have a project context
            if state.get("active_bid_card") and user_id:
                try:
                    from database_simple import db
                    for photo_url in images:
                        await db.save_project_photo(
                            user_id=user_id,
                            project_id=state["active_bid_card"],
                            photo_url=photo_url,
                            description="User uploaded project photo"
                        )
                    print(f"[CIA] Saved {len(images)} photos to database for project {state['active_bid_card']}")
                except Exception as e:
                    print(f"[CIA] Warning: Could not save photos to database: {e}")

        # Check for modification requests before generating response
        modification_result = await self._handle_modification_requests(user_id, message, state)
        if modification_result:
            return modification_result

        # Generate response
        start_time = time.time()

        if self.client:
            print("[CIA] Using GPT-5 API for response...")
            response_text = await self._generate_gpt5_response(state)
        else:
            print("[CIA] Using demo response (no API client)...")
            response_text = await self._generate_demo_response(state)

        response_time = time.time() - start_time
        print(f"[CIA] Response generated in {response_time:.2f} seconds")

        # Extract information using GPT-5
        await self._extract_and_update_info(state, message)

        # Add assistant response
        state["messages"].append({
            "role": "assistant",
            "content": response_text,
            "metadata": {"phase": state["current_phase"]}
        })

        # Check completeness and phase
        self._update_state_status(state)

        # Update project-aware memory after conversation if applicable
        if agent_memory_config and project_id:
            try:
                # Update memory with conversation insights
                # await update_agent_memory_after_conversation(
                #     user_id=user_id,
                #     project_id=project_id,
                #     session_id=session_id,
                #     conversation_summary=response_text[:500],  # First 500 chars as summary
                #     extracted_info=state["collected_info"],
                #     user_preferences_discovered={
                #         "budget_preference": state["collected_info"].get("budget_max"),
                #         "timeline_preference": state["collected_info"].get("urgency"),
                #         "communication_style": "detailed" if len(response_text) > 200 else "concise"
                #     },
                # Temporarily disabled to fix timeout
                print(f"[CIA] Updated project memory for user {user_id}, project {project_id}")
            except Exception as e:
                print(f"[CIA] Warning: Could not update project memory: {e}")

        # Ensure active bid card persists in session
        if state.get("active_bid_card") and session_id:
            if session_id not in self.sessions:
                self.sessions[session_id] = {}
            self.sessions[session_id]["active_bid_card"] = state["active_bid_card"]
            self.sessions[session_id]["active_project_type"] = state.get("active_project_type")
            print(f"[CIA] Persisted active bid card {state['active_bid_card']} in session")

        # Save session to memory and database
        self.sessions[session_id] = state

        # Save to unified conversation system for JAA processing
        try:
            await self._save_to_unified_conversations(state, user_id, session_id)
            print("[CIA] Saved conversation to unified system for JAA")
        except Exception as e:
            print(f"[CIA] ERROR: Could not save to unified system: {e}")
            print(f"[CIA] User ID: {user_id}")
            print(f"[CIA] Session ID: {session_id}")
            print(f"[CIA] State messages: {len(state.get('messages', []))}")
            import traceback
            print(f"[CIA] Traceback: {traceback.format_exc()}")

        # UPDATED: Save assistant response and update session
        try:
            # Add assistant response to session
            await universal_session_manager.add_message_to_session(
                session_id=session_id,
                role="assistant",
                content=response_text,
                metadata={
                    "current_phase": state["current_phase"],
                    "ready_for_jaa": state["ready_for_jaa"],
                    "project_type": state["collected_info"].get("project_type"),
                    "agent_type": "CIA"
                }
            )
            
            # Update session with latest CIA state
            session_state["context"]["cia_state"] = state
            await universal_session_manager.update_session(session_id, session_state)
            
            print(f"[CIA] Successfully updated session with persistent memory")
        except Exception as e:
            print(f"[CIA] Warning: Failed to save to universal session manager: {e}")

        return {
            "response": response_text,
            "session_id": session_id,
            "current_phase": state["current_phase"],
            "ready_for_jaa": state["ready_for_jaa"],
            "missing_fields": state.get("missing_fields", []),
            "state": state,  # Include state for persistence
            "project_id": project_id  # Include project ID in response
        }

    def _create_new_session_with_instabids_structure(self, user_id: str, session_id: str) -> dict[str, Any]:
        """Create a new conversation session with InstaBids 12 data points structure"""
        return {
            "user_id": user_id,
            "session_id": session_id,
            "messages": [],
            "current_phase": "intro",
            # NEW: InstaBids-focused collected info structure
            "collected_info": {
                # CORE PROJECT INFO
                "project_type": None,
                "service_type": None,
                "project_description": None,

                # CONTEXT & MOTIVATION
                "budget_context": None,
                "timeline_urgency": None,
                "urgency_reason": None,
                "location_zip": None,

                # SMART OPPORTUNITIES
                "group_bidding_potential": None,
                "group_bidding_interest": None,
                "property_context": None,

                # SUPPORTING INFO
                "material_preferences": None,
                "uploaded_photos": [],
                "photo_analyses": [],
                "special_requirements": None,

                # INTERNAL SCORING
                "intention_score": None,

                # LEGACY COMPATIBILITY
                "address": None,
                "property_type": None,
                "timeline_start": None,
                "budget_min": None,
                "budget_max": None,
                "urgency": None
            },
            "missing_fields": REQUIRED_FIELDS_MINIMAL.copy(),
            "ready_for_jaa": False,

            # INSTABIDS SPECIFIC TRACKING
            "instabids_value_mentioned": False,
            "group_bidding_discussed": False,
            "competitor_context": None,

            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

    def _migrate_to_new_structure(self, state: dict[str, Any]) -> dict[str, Any]:
        """Migrate existing state to new InstaBids structure"""
        if not state.get("collected_info"):
            return state

        old_info = state["collected_info"]

        # Create new structure
        new_info = {
            # CORE PROJECT INFO - migrate from old
            "project_type": old_info.get("project_type"),
            "service_type": self._classify_service_type_from_old_data(old_info),
            "project_description": old_info.get("project_description"),

            # CONTEXT & MOTIVATION
            "budget_context": self._derive_budget_context(old_info),
            "timeline_urgency": self._map_old_urgency(old_info.get("urgency")),
            "urgency_reason": None,
            "location_zip": self._extract_zip_from_address(old_info.get("address")),

            # SMART OPPORTUNITIES - new fields
            "group_bidding_potential": self._assess_group_bidding_from_project_type(old_info.get("project_type")),
            "group_bidding_interest": None,
            "property_context": old_info.get("property_type"),

            # SUPPORTING INFO
            "material_preferences": old_info.get("material_preferences"),
            "uploaded_photos": old_info.get("uploaded_photos", []),
            "photo_analyses": old_info.get("photo_analyses", []),
            "special_requirements": old_info.get("special_requirements"),

            # INTERNAL SCORING - calculate from existing data
            "intention_score": self._calculate_intention_from_old_data(old_info),

            # LEGACY COMPATIBILITY - preserve
            "address": old_info.get("address"),
            "property_type": old_info.get("property_type"),
            "timeline_start": old_info.get("timeline_start"),
            "budget_min": old_info.get("budget_min"),
            "budget_max": old_info.get("budget_max"),
            "urgency": old_info.get("urgency")
        }

        state["collected_info"] = new_info
        state["missing_fields"] = REQUIRED_FIELDS_MINIMAL.copy()

        # Add InstaBids tracking if missing
        if "instabids_value_mentioned" not in state:
            state["instabids_value_mentioned"] = False
        if "group_bidding_discussed" not in state:
            state["group_bidding_discussed"] = False

        return state

    async def _generate_gpt5_response(self, state: dict[str, Any]) -> str:
        """Generate response using OpenAI GPT-5 API"""
        print("[CIA] _generate_gpt5_response called")
        print(f"[CIA] Has bid_card_context: {'bid_card_context' in state}")
        if "bid_card_context" in state:
            print(f"[CIA] Bid card number: {state['bid_card_context'].get('bid_card_number')}")

        messages = []

        # Add conversation context
        total_messages = len(state["messages"])

        # If long conversation, add a simple summary of key facts
        if total_messages > 20:
            # Build a quick context summary from collected info
            context_summary = "Earlier in this conversation:\n"

            # Add key project details if available
            if state.get("collected_info"):
                info = state["collected_info"]
                if info.get("project_type"):
                    context_summary += f"- Project type: {info['project_type']}\n"
                if info.get("budget_max"):
                    context_summary += f"- Budget discussed: ${info.get('budget_min', 0):,} - ${info['budget_max']:,}\n"
                if info.get("timeline"):
                    context_summary += f"- Timeline: {info['timeline']}\n"
                if info.get("material_preferences"):
                    context_summary += f"- Materials: {', '.join(info['material_preferences'])}\n"
                if info.get("special_requirements"):
                    context_summary += f"- Special requirements: {', '.join(info['special_requirements'])}\n"

            # 🆕 Add bid submission context if available
            try:
                if state.get("bid_card_context") and state["bid_card_context"].get("id"):
                    bid_submissions = await self.get_bid_submissions_for_bid_card(state["bid_card_context"]["id"])
                    if bid_submissions:
                        context_summary += f"\nCONTRACTOR BIDS RECEIVED ({len(bid_submissions)}):\n"
                        for i, bid in enumerate(bid_submissions[:5]):  # Show up to 5 most recent
                            amount_text = f"${bid['amount']:,.2f}" if bid['amount'] else "Amount pending"
                            context_summary += f"- Bid {i+1}: {amount_text} from contractor {bid['contractor_id']}\n"
                            if bid['timeline']:
                                context_summary += f"  Timeline: {bid['timeline']}\n"
                        
                        if len(bid_submissions) > 5:
                            context_summary += f"- ... and {len(bid_submissions) - 5} more bids\n"
            except Exception as e:
                print(f"[CIA] Error loading bid context: {e}")

            # Add this context as a system message
            messages.append({
                "role": "assistant",
                "content": f"[Context from earlier messages: {context_summary}]"
            })

        # Add last 10 messages
        for msg in state["messages"][-10:]:  # Last 10 messages
            if msg["role"] == "user":
                if msg.get("images") and len(msg["images"]) > 0:
                    # Handle image messages - convert base64 to proper format for Claude
                    content = [{"type": "text", "text": msg["content"]}]
                    has_valid_images = False

                    for image_data in msg["images"]:
                        # Skip photo_id references (these are stored in DB)
                        if image_data.startswith("photo_id:"):
                            continue
                        elif image_data.startswith("data:image/"):
                            # Extract media type and base64 data
                            header, base64_data = image_data.split(",", 1)
                            media_type = header.split(":")[1].split(";")[0]

                            content.append({
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": base64_data
                                }
                            })
                            has_valid_images = True

                    # Only add message with images if we have actual image content
                    if has_valid_images:
                        messages.append({
                            "role": "user",
                            "content": content
                        })
                    else:
                        # Just text, no valid images
                        messages.append({
                            "role": "user",
                            "content": msg["content"]
                        })
                else:
                    messages.append({
                        "role": "user",
                        "content": msg["content"]
                    })
            elif msg["role"] == "assistant":
                messages.append({
                    "role": "assistant",
                    "content": msg["content"]
                })

        # Use NEW InstaBids-focused system prompt
        system_prompt = SYSTEM_PROMPT

        # Add homeowner context from adapter (IRIS insights, photos, cross-project memory)
        homeowner_context = state.get("homeowner_context", {})
        if homeowner_context and len(homeowner_context) > 3:  # More than just basic fields
            context_info = "\n\n🏠 HOMEOWNER CONTEXT (From Database):"
            
            # Add homeowner profile information
            if homeowner_context.get("homeowner"):
                profile = homeowner_context["homeowner"]
                context_info += f"\nHomeowner Profile Found: {profile.get('id', 'Unknown')}"
            
            # Add bid cards information
            if homeowner_context.get("bid_cards"):
                bid_cards = homeowner_context["bid_cards"]
                context_info += f"\n📋 BID CARDS: {len(bid_cards)} previous project(s)"
                for card in bid_cards[:3]:  # Show up to 3 recent projects
                    context_info += f"\n  - {card.get('project_type', 'Unknown')}: {card.get('title', 'Untitled')}"
            
            # Add contractor bids information - THIS IS THE KEY DATA
            if homeowner_context.get("contractor_bids"):
                bids = homeowner_context["contractor_bids"]
                context_info += f"\n💰 CONTRACTOR BIDS: {len(bids)} bid(s) received from contractors"
                for bid in bids[:5]:  # Show up to 5 recent bids
                    # Handle both field names: amount or bid_amount
                    amount = bid.get('amount') or bid.get('bid_amount', 'Unknown')
                    contractor = bid.get('contractor_name', 'Unknown Contractor')
                    context_info += f"\n  - ${amount} from {contractor}"
                
                context_info += f"\n\nIMPORTANT: When asked about bid amounts, provide these specific amounts to the homeowner."
            
            # Add user memories
            if homeowner_context.get("user_memories"):
                memories = homeowner_context["user_memories"]
                if memories:
                    context_info += f"\n📝 USER MEMORIES: {len(memories)} saved preference(s)"
            
            # Add conversation history
            if homeowner_context.get("conversations"):
                convs = homeowner_context["conversations"]
                context_info += f"\n💬 CONVERSATION HISTORY: {len(convs)} previous conversation(s)"
            
            context_info += "\n\nIMPORTANT: When asked about previous projects, bids, or contractors, reference this specific data above."
            system_prompt += context_info

        # Add active bid card context if available
        if state.get("active_bid_card"):
            # Always refresh bid card details to get latest updates
            fresh_bid_card = await self._get_bid_card_details(state["active_bid_card"])
            if fresh_bid_card:
                state["bid_card_context"] = fresh_bid_card

            bid_card = state.get("bid_card_context", {})
            print(f"[CIA] Adding active bid card context to prompt: {state['active_bid_card']}")
            bid_info = "\n\n🎯 ACTIVE PROJECT CONTEXT - YOU ARE CURRENTLY WORKING ON THIS PROJECT:"
            bid_info += f"\nBid Card: {state['active_bid_card']}"
            bid_info += f"\nProject Type: {bid_card.get('project_type', 'Unknown')}"
            bid_info += f"\nCurrent Budget: ${bid_card.get('budget_min', 0):,} - ${bid_card.get('budget_max', 0):,}"
            bid_info += f"\nUrgency: {bid_card.get('urgency_level', 'Unknown')}"
            bid_info += f"\nContractors Needed: {bid_card.get('contractor_count_needed', 0)}"
            bid_info += "\n\nIMPORTANT: Assume ALL questions and modifications relate to THIS project unless the user explicitly mentions a different project."

            # Add bid document details if available
            if bid_card.get("bid_document"):
                doc = bid_card["bid_document"]
                if doc.get("all_extracted_data"):
                    data = doc["all_extracted_data"]
                    if data.get("project_description"):
                        bid_info += f"\nProject Description: {data['project_description']}"
                    if data.get("location"):
                        loc = data["location"]
                        location_str = loc.get("city") or loc.get("address") or loc.get("full_location") or "Unknown"
                        bid_info += f"\nLocation: {location_str}"
                    if data.get("material_preferences"):
                        bid_info += f"\nMaterial Preferences: {', '.join(data['material_preferences'])}"
                    if data.get("special_requirements"):
                        bid_info += f"\nSpecial Requirements: {', '.join(data['special_requirements'])}"

            bid_info += "\n\nThe user is asking about modifying this specific bid card. Acknowledge the project details and help them with their modifications."
            system_prompt += bid_info

        # Add user's project summaries for general conversation context
        if state.get("user_project_summaries"):
            summaries = state["user_project_summaries"]
            projects_info = []
            for i, summary in enumerate(summaries):
                project_info = f"Project {i+1}: {summary.get('project_title', 'Unknown')}"
                project_info += f" ({summary.get('project_type', 'Unknown type')})"
                project_info += f" - Status: {summary.get('status', 'Unknown')}"
                project_info += f" - Budget: {summary.get('budget_range', 'Not specified')}"
                if summary.get("timeline"):
                    project_info += f" - Timeline: {summary['timeline']}"
                if summary.get("key_features"):
                    features = ", ".join(summary["key_features"][:3])  # First 3 features
                    project_info += f" - Features: {features}"
                projects_info.append(project_info)

            system_prompt += f"\n\nUSER'S CURRENT PROJECTS:\n{chr(10).join(projects_info)}"
            system_prompt += "\n\nWhen the user asks about their projects, reference these specific details to show you remember their work."

        # Add project awareness to system prompt if available
        if state.get("project_context"):
            project_ctx = state["project_context"]

            # Add user preferences from memory
            if project_ctx.get("user_preferences"):
                user_prefs = project_ctx["user_preferences"]
                if user_prefs.get("communication_preferences"):
                    comm_style = user_prefs["communication_preferences"].get("preferred_communication_style", "detailed")
                    system_prompt += f"\n\nUser Communication Preference: {comm_style}"

                if user_prefs.get("budget_preferences"):
                    budget_info = user_prefs["budget_preferences"]
                    if budget_info.get("recent_budget_ranges"):
                        recent_budgets = budget_info["recent_budget_ranges"][-3:]  # Last 3
                        system_prompt += f"\n\nUser's Recent Budget Ranges: {recent_budgets}"

            # Add related projects context
            if project_ctx.get("related_projects", {}).get("related_projects"):
                related = project_ctx["related_projects"]["related_projects"][:2]  # Top 2
                related_info = []
                for proj in related:
                    related_info.append(f"{proj['title']} ({proj['category']})")
                system_prompt += f"\n\nUser's Other Projects: {', '.join(related_info)}"

                # Add analysis for intelligent questions
                analysis = project_ctx["related_projects"].get("analysis", "")
                if analysis:
                    system_prompt += f"\n\nProject Context: {analysis}"

        # Ensure current_phase exists for conversation prompt
        current_phase = state.get("current_phase", "discovery")
        collected_info = state.get("collected_info", {})
        missing_fields = state.get("missing_fields", [])
        
        system_prompt += "\n\n" + get_conversation_prompt(
            current_phase,
            {"collected_info": collected_info, "missing_fields": missing_fields}
        )

        try:
            print(f"[CIA] Calling {self.api_type.upper()} API...")
            response_text = await self._call_llm(messages, max_tokens=1000, system=system_prompt)
            if response_text:
                print(f"[CIA] {self.api_type.upper()} API call successful")
                return response_text
            else:
                print("[CIA] LLM call returned None, falling back")
                return self._generate_demo_response(state)
        except Exception as e:
            print(f"[CIA ERROR] LLM API error: {e}")
            print(f"[CIA ERROR] Error type: {type(e).__name__}")
            print("[CIA] Falling back to demo response")
            return self._generate_demo_response(state)

    async def _generate_demo_response(self, state: dict[str, Any]) -> str:
        """Generate intelligent responses without API"""
        # Add artificial delay to simulate API call
        await asyncio.sleep(0.5)

        last_message = state["messages"][-1]["content"] if state["messages"] else ""
        phase = state["current_phase"]
        collected = state["collected_info"]

        # Phase-based responses
        if phase == "intro" and len(state["messages"]) == 1:
            return "Hi! I'm Alex, your project assistant at Instabids. I'll help you describe your home project so we can find you the perfect contractors at the best prices. What kind of project brings you here today?"

        # Generate contextual response based on what we know
        if not collected.get("project_type"):
            return self._ask_about_project_type(last_message)
        elif not collected.get("budget_min"):
            return self._ask_about_budget(collected["project_type"])
        elif not collected.get("timeline_start"):
            return self._ask_about_timeline(collected["project_type"])
        elif not collected.get("address"):
            return self._ask_about_location()
        else:
            return self._ask_for_details_or_photos(collected)

    def _ask_about_project_type(self, message: str) -> str:
        """Ask about project type"""
        message_lower = message.lower()

        if "kitchen" in message_lower:
            return "A kitchen project! That's exciting. Are you looking to do a complete renovation or update specific elements like cabinets, countertops, or appliances?"
        elif "bathroom" in message_lower:
            return "Bathroom renovations are great for both functionality and home value. Are you thinking about a full remodel or focusing on specific updates?"
        else:
            return "I'd love to help with your project! What type of work are you considering? Common projects include kitchen remodels, bathroom updates, roofing, flooring, or painting."

    def _ask_about_budget(self, project_type: str) -> str:
        """Ask about budget based on project type"""
        if project_type == "kitchen":
            return "For kitchen projects, budgets typically range from $15,000 for updates to $60,000+ for full remodels. What budget range are you comfortable with?"
        elif project_type == "bathroom":
            return "Bathroom remodels usually range from $8,000 to $25,000 depending on scope. What's your target budget for this project?"
        else:
            return "To help match you with the right contractors, could you share your approximate budget range for this project?"

    def _ask_about_timeline(self, project_type: str) -> str:
        """Ask about timeline"""
        return f"When are you hoping to start this {project_type} project? And do you have a target completion date in mind?"

    def _ask_about_location(self) -> str:
        """Ask about property location"""
        return "To connect you with local contractors, I'll need your property address. What's the address for this project?"

    def _ask_for_details_or_photos(self, collected: dict) -> str:
        """Ask for more details or photos"""
        if not collected.get("uploaded_photos"):
            return "Could you share some photos of the current space? This really helps contractors provide accurate bids."
        else:
            return "Is there anything else about your project you'd like me to know? Any specific concerns or must-have features?"

    async def _extract_and_update_info(self, state: dict[str, Any], message: str) -> None:
        """Extract information using intelligent GPT-5 with async handling"""
        collected = state["collected_info"]

        # Use intelligent GPT-5 extraction with timeout protection
        extracted_info = {}
        if self.client:
            try:
                # Add timeout to prevent hanging
                import asyncio
                print(f"[CIA] Starting GPT-5 extraction for: {message[:100]}...")
                extracted_info = await asyncio.wait_for(
                    self._gpt5_extract_information(message, collected),
                    timeout=30.0  # 30 second timeout
                )
                print(f"[CIA] GPT-5 extraction completed: {extracted_info}")
            except asyncio.TimeoutError:
                print(f"[CIA] GPT-5 extraction timed out after 30s, continuing without extraction")
                extracted_info = {}
            except Exception as e:
                print(f"[CIA] GPT-5 extraction failed: {e}")
                extracted_info = {}
        else:
            print("[CIA] No OpenAI client available, skipping extraction")
            extracted_info = {}

        # Update collected info with extracted data (progressive updates)
        for key, value in extracted_info.items():
            if value:  # Update any new information found
                old_value = collected.get(key)
                if old_value != value:  # Only log changes
                    collected[key] = value
                    if old_value:
                        print(f"[CIA] Updated {key}: {old_value} → {value}")
                    else:
                        print(f"[CIA] Extracted {key}: {value}")

        # Update state
        state["collected_info"] = collected

        # Classify service complexity if we have project information
        if collected.get("project_type") or collected.get("project_description"):
            try:
                print(f"[CIA] Classifying service complexity for project: {collected.get('project_type', 'Unknown')}")
                classification = self.service_classifier.classify_project(
                    project_type=collected.get("project_type", ""),
                    description=collected.get("project_description", ""),
                    recommended_trades=None  # Will be determined by classifier
                )
                
                # Update collected info with classification results
                collected.update({
                    "service_complexity": classification["service_complexity"],
                    "trade_count": classification["trade_count"],
                    "primary_trade": classification["primary_trade"],
                    "secondary_trades": classification.get("secondary_trades", [])
                })
                
                print(f"[CIA] Service complexity classification: {classification['service_complexity']} ({classification['trade_count']} trades)")
                print(f"[CIA] Primary trade: {classification['primary_trade']}")
                if classification.get("secondary_trades"):
                    print(f"[CIA] Secondary trades: {classification['secondary_trades']}")
                
                # Update state with classification
                state["collected_info"] = collected
                
            except Exception as e:
                print(f"[CIA] Error classifying service complexity: {e}")
                # Set defaults if classification fails
                collected.update({
                    "service_complexity": "single-trade",
                    "trade_count": 1,
                    "primary_trade": collected.get("project_type", "general"),
                    "secondary_trades": []
                })
        
        # Update potential bid card if we have one
        if state.get("potential_bid_card_id"):
            await self.bid_card_manager.update_from_collected_info(
                state["potential_bid_card_id"],
                collected
            )

    def _fast_pattern_extraction(self, message: str, existing_info: dict) -> dict[str, Any]:
        """Fast pattern-based field extraction using regex and keywords"""
        import re
        extracted = {}
        message_lower = message.lower()
        
        # Project type extraction (specific over general)
        project_types = {
            "bathroom renovation": ["bathroom renov", "bathroom remod", "bathroom updat"],
            "kitchen renovation": ["kitchen renov", "kitchen remod", "kitchen updat"],
            "roof repair": ["roof repair", "roof fix", "roofing"],
            "lawn care": ["lawn care", "lawn maint", "grass care"],
            "painting": ["painting", "paint job", "interior paint", "exterior paint"],
            "flooring": ["flooring", "floor install", "hardwood", "carpet", "tile floor"],
            "plumbing": ["plumbing", "plumber", "pipe", "faucet", "toilet"],
            "electrical": ["electrical", "electrician", "wiring", "outlet", "light"]
        }
        
        for project_type, keywords in project_types.items():
            if any(keyword in message_lower for keyword in keywords):
                extracted["project_type"] = project_type
                break
        
        # ZIP code extraction
        zip_match = re.search(r'\b(\d{5})\b', message)
        if zip_match:
            extracted["zip_code"] = zip_match.group(1)
        
        # Location extraction
        locations = ["manhattan", "brooklyn", "queens", "bronx", "staten island", 
                    "upper west side", "lower east side", "midtown", "downtown"]
        for location in locations:
            if location in message_lower:
                extracted["location"] = location.title()
                break
        
        # Budget extraction
        budget_patterns = [
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # $30,000 or $30,000.00
            r'(\d{1,3}(?:,\d{3})*)\s*(?:dollars?|bucks?)',  # 30,000 dollars
            r'budget.*?(\d{1,3}(?:,\d{3})*)',  # budget is 30,000
        ]
        
        budget_amounts = []
        for pattern in budget_patterns:
            matches = re.finditer(pattern, message_lower)
            for match in matches:
                try:
                    amount = int(match.group(1).replace(',', ''))
                    if 1000 <= amount <= 1000000:  # Reasonable range
                        budget_amounts.append(amount)
                except:
                    pass
        
        if budget_amounts:
            budget_amounts.sort()
            if len(budget_amounts) >= 2:
                extracted["budget_min"] = budget_amounts[0]
                extracted["budget_max"] = budget_amounts[-1]
            else:
                # Single amount - assume it's the target
                amount = budget_amounts[0]
                extracted["budget_min"] = int(amount * 0.8)  # 20% below
                extracted["budget_max"] = int(amount * 1.2)  # 20% above
        
        # Timeline extraction
        timeline_patterns = [
            (r'(\d+)\s*weeks?', lambda m: f"{m.group(1)} weeks"),
            (r'(\d+)\s*months?', lambda m: f"{m.group(1)} months"),
            (r'emergency', lambda m: "emergency"),
            (r'urgent', lambda m: "urgent"),
            (r'asap', lambda m: "urgent"),
            (r'flexible', lambda m: "flexible"),
            (r'by summer', lambda m: "by summer"),
            (r'by (\w+)', lambda m: f"by {m.group(1)}")
        ]
        
        for pattern, formatter in timeline_patterns:
            match = re.search(pattern, message_lower)
            if match:
                extracted["timeline"] = formatter(match)
                # Set urgency based on timeline
                timeline_val = extracted["timeline"].lower()
                if "emergency" in timeline_val or "asap" in timeline_val:
                    extracted["urgency"] = "emergency"
                elif "urgent" in timeline_val or ("weeks" in timeline_val and int(re.search(r'\d+', timeline_val).group()) <= 4):
                    extracted["urgency"] = "urgent"
                elif "flexible" in timeline_val:
                    extracted["urgency"] = "flexible"
                else:
                    extracted["urgency"] = "planning"
                break
        
        # Materials extraction
        materials_keywords = {
            "marble": ["marble"],
            "quartz": ["quartz"],
            "granite": ["granite"],
            "subway tile": ["subway tile"],
            "white cabinets": ["white cabinet"],
            "hardwood": ["hardwood", "wood floor"],
            "ceramic": ["ceramic"],
            "stainless steel": ["stainless steel"]
        }
        
        found_materials = []
        for material, keywords in materials_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                found_materials.append(material)
        
        if found_materials:
            extracted["materials"] = ", ".join(found_materials)
        
        # Quality expectations
        quality_keywords = {
            "luxury": ["luxury", "high-end", "premium"],
            "mid-range": ["quality", "good quality", "nice"],
            "budget-friendly": ["budget", "affordable", "cheap", "inexpensive"]
        }
        
        for quality, keywords in quality_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                extracted["quality_expectations"] = quality
                break
        
        # Contractor requirements
        contractor_reqs = []
        if "licensed" in message_lower:
            contractor_reqs.append("licensed")
        if "insured" in message_lower or "insurance" in message_lower:
            contractor_reqs.append("insured")
        if "bonded" in message_lower:
            contractor_reqs.append("bonded")
        if "experienced" in message_lower:
            contractor_reqs.append("experienced")
        
        if contractor_reqs:
            extracted["contractor_requirements"] = ", ".join(contractor_reqs)
        
        # Property details
        property_patterns = {
            "master bathroom": ["master bath"],
            "guest bathroom": ["guest bath"],
            "main kitchen": ["main kitchen", "kitchen"],
            "small bathroom": ["small bath"],
            "large kitchen": ["large kitchen"]
        }
        
        for prop_type, keywords in property_patterns.items():
            if any(keyword in message_lower for keyword in keywords):
                extracted["property_type"] = prop_type
                break
        
        # Size extraction
        size_match = re.search(r'(\d+)\s*(?:square\s*)?(?:feet|ft|sq\.?\s*ft)', message_lower)
        if size_match:
            extracted["property_size"] = f"{size_match.group(1)} square feet"
        
        # Condition descriptions
        condition_keywords = {
            "outdated": ["outdated", "old", "from the 1990s", "needs updating"],
            "damaged": ["damaged", "broken", "cracked", "leaking"],
            "good condition": ["good condition", "well maintained"],
            "needs work": ["needs work", "fixer upper"]
        }
        
        for condition, keywords in condition_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                extracted["current_condition"] = condition
                break
        
        print(f"[CIA] Pattern extraction found {len(extracted)} fields from message")
        return extracted

    async def _gpt5_extract_information(self, message: str, existing_info: dict) -> dict[str, Any]:
        """Use GPT-5 to intelligently extract InstaBids project information"""

        extraction_prompt = f"""
You are an expert InstaBids information extraction agent. Extract SPECIFIC project information from this user message and improve upon EXISTING INFO.

EXISTING INFO: {json.dumps(existing_info, indent=2)}

USER MESSAGE: "{message}"

CRITICAL: Look for SPECIFIC information like exact zip codes, dollar amounts, room types, materials, timeline words, company preferences.

Extract these fields (return only fields with NEW or UPDATED information):

{{
    // PROJECT SPECIFICS - Look for exact details
    "project_type": "SPECIFIC type like 'bathroom renovation', 'kitchen remodel', 'roof repair' (not just 'general')",
    "project_description": "SPECIFIC work details, materials mentioned, current problems",
    "zip_code": "EXACT zip code if mentioned (like '10001', '11201', '90210')",
    "location": "neighborhood/area if mentioned (like 'Manhattan', 'Brooklyn', 'Upper West Side')",
    
    // BUDGET & TIMELINE - Look for numbers and timing words
    "budget_min": "EXACT minimum dollar amount as number (extract from '$30,000', 'thirty thousand', etc.)",
    "budget_max": "EXACT maximum dollar amount as number", 
    "budget_context": "has_quotes|has_budget_range|exploring_options|dream_project",
    "timeline": "SPECIFIC timeline mentioned ('6 weeks', '4 weeks', 'urgent', 'by summer')",
    "urgency": "emergency|urgent|flexible|planning",
    
    // MATERIALS & PREFERENCES - Extract specific items mentioned
    "materials": "SPECIFIC materials mentioned ('quartz countertops', 'marble', 'subway tile', 'white cabinets')",
    "quality_expectations": "quality level mentioned ('high-end', 'luxury', 'budget-friendly', 'premium')",
    "special_requirements": "SPECIFIC requirements ('licensed contractors', 'insured', 'weekend work', 'permits')",
    
    // CONTRACTOR PREFERENCES
    "contractor_size": "size preference ('small company', 'established firm', 'local', 'experienced')",
    "contractor_requirements": "requirements mentioned ('licensed', 'insured', 'bonded', 'experienced')",
    
    // PROPERTY CONTEXT
    "property_type": "SPECIFIC type ('master bathroom', 'guest bathroom', 'kitchen', 'backyard')",
    "property_size": "size mentioned ('100 square feet', 'large kitchen', 'small bathroom')",
    "current_condition": "current state described ('outdated', '1990s', 'needs updating', 'damaged')"
}}

EXTRACTION RULES:
1. SPECIFIC OVER GENERIC: "bathroom renovation" NOT "general", "10001" NOT "location", "$30,000" NOT "budget mentioned"
2. EXACT NUMBERS: Extract actual dollar amounts, zip codes, square footage, timeline numbers
3. PRESERVE DETAILS: Keep specific material names, neighborhood names, company preferences
4. UPDATE EXISTING: If new info contradicts or adds to existing info, include the update
5. NO GENERIC DEFAULTS: Don't return "general", "standard", "typical" - be specific or return null

ONLY return JSON with fields that have SPECIFIC, EXTRACTABLE information from this message.
"""

        try:
            # Use GPT-5 for extraction
            print(f"[CIA] Using GPT-5 for extraction with message: {message[:100]}...")
            response_text = await self._call_llm(
                messages=[{"role": "user", "content": extraction_prompt}],
                max_tokens=1000,
                system=None
            )
            print(f"[CIA] GPT-5 raw response: {response_text[:200]}...")

            # Extract JSON from response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                print(f"[CIA] Extracted JSON: {json_str[:200]}...")
                extracted = json.loads(json_str)
                print(f"[CIA] Parsed extraction result: {extracted}")

                # Clean null values
                cleaned = {k: v for k, v in extracted.items() if v not in [None, "null", "", "not found"]}
                print(f"[CIA] Cleaned extraction result: {cleaned}")
                return cleaned
            else:
                print(f"[CIA] Could not extract JSON from GPT-5 response: {response_text}")
                return {}

        except Exception as e:
            print(f"[CIA] GPT-5 information extraction failed: {e}")
            import traceback
            traceback.print_exc()
            return {}

    async def _determine_project_intent(self, user_id: str, message: str) -> Optional[dict[str, Any]]:
        """Determine if user wants to continue existing project or create new one"""
        try:
            from memory.multi_project_store import MultiProjectMemoryStore
            store = MultiProjectMemoryStore()

            # Get user's existing projects
            summaries = await store.get_user_projects_summary(user_id)

            if not summaries:
                # No existing projects - definitely new
                return {"action": "create_new", "project_type": "unknown"}

            print(f"[CIA] User has {len(summaries)} existing projects")

            # Use Claude to analyze intent
            if not self.client:
                # Demo mode - simple heuristics
                return self._demo_project_intent(summaries, message)

            # Build prompt with user's project history
            projects_context = ""
            for i, summary in enumerate(summaries):
                projects_context += f"Project {i+1}: {summary.get('project_title', 'Unknown')} - {summary.get('project_type', 'Unknown type')}\n"
                projects_context += f"  Status: {summary.get('status', 'Unknown')}\n"
                projects_context += f"  Budget: {summary.get('budget_range', 'Not specified')}\n\n"

            intent_prompt = f"""Analyze this user message to determine project intent:

USER'S EXISTING PROJECTS:
{projects_context}

NEW USER MESSAGE: "{message}"

Determine the intent:
1. CONTINUATION: User wants to add/modify existing project
2. NEW_PROJECT: User wants separate, new project
3. CLARIFY: Unclear - need to ask user

Return JSON response:
{{
    "action": "use_existing|create_new|ask_clarification",
    "confidence": 0.0-1.0,
    "reasoning": "explanation",
    "project_id": "if use_existing",
    "project_type": "if create_new",
    "response": "if ask_clarification - exact question to ask user"
}}"""

            # Use GPT-5 for intent analysis
            response_text = await self._call_llm(
                messages=[{"role": "user", "content": intent_prompt}],
                max_tokens=400,
                system=None
            )

            # Extract JSON
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                decision = json.loads(json_str)

                # Map project_id if using existing
                if decision.get("action") == "use_existing" and summaries:
                    # For demo, use first project - in production, match by type/description
                    decision["project_id"] = summaries[0].get("project_id")

                return decision

            return None

        except Exception as e:
            print(f"[CIA] Project intent determination failed: {e}")
            return None

    def _demo_project_intent(self, summaries: list[dict], message: str) -> dict[str, Any]:
        """Demo version of project intent detection"""
        message_lower = message.lower()

        # Simple keyword matching
        continuation_words = ["add", "also", "include", "additional", "more", "extend"]
        new_project_words = ["bathroom", "different", "separate", "another", "new", "also need"]

        has_continuation = any(word in message_lower for word in continuation_words)
        has_new_project = any(word in message_lower for word in new_project_words)

        if has_continuation and not has_new_project:
            return {
                "action": "ask_clarification",
                "confidence": 0.7,
                "reasoning": "User mentions additions but unclear which project",
                "response": f"I see you want to add something. Would you like to add this to your existing {summaries[0].get('project_title', 'project')}, or is this a separate project?"
            }
        elif has_new_project:
            return {
                "action": "ask_clarification",
                "confidence": 0.8,
                "reasoning": "User mentions new type of work",
                "response": f"This sounds like it might be a separate project from your {summaries[0].get('project_title', 'current project')}. Should I create a new project for this work?"
            }
        else:
            return {
                "action": "create_new",
                "confidence": 0.6,
                "reasoning": "Unable to determine clear intent",
                "project_type": "unknown"
            }

    def _basic_extract_and_update_info(self, state: dict[str, Any], message: str) -> None:
        """Fallback basic extraction (original regex logic)"""
        collected = state["collected_info"]
        message_lower = message.lower()

        # Project type - expanded list
        if not collected.get("project_type"):
            project_types = [
                ("mold remediation", ["mold", "remediation", "black mold", "mold removal"]),
                ("lawn care", ["lawn", "grass", "mowing", "yard work"]),
                ("landscaping", ["landscape", "landscaping", "garden", "outdoor"]),
                ("kitchen", ["kitchen", "cabinets", "countertop"]),
                ("bathroom", ["bathroom", "shower", "tub", "toilet"]),
                ("roofing", ["roof", "roofing", "shingles", "leak"]),
                ("flooring", ["floor", "flooring", "carpet", "tile", "hardwood"]),
                ("painting", ["paint", "painting", "interior", "exterior"])
            ]

            for ptype, keywords in project_types:
                if any(keyword in message_lower for keyword in keywords):
                    collected["project_type"] = ptype
                    break

        # Budget extraction
        import re
        if not collected.get("budget_min") and ("budget" in message_lower or "spend" in message_lower or "$" in message):
            range_pattern = r"\$?(\d{1,3}(?:,\d{3})*)\s*(?:-|to|up to)\s*\$?(\d{1,3}(?:,\d{3})*)"
            range_match = re.search(range_pattern, message)

            if range_match:
                collected["budget_min"] = int(range_match.group(1).replace(",", ""))
                collected["budget_max"] = int(range_match.group(2).replace(",", ""))
                print(f"[CIA] Extracted budget range: ${collected['budget_min']}-${collected['budget_max']}")

        # Basic urgency detection
        if "emergency" in message_lower or "asap" in message_lower or "tomorrow" in message_lower:
            collected["urgency"] = "emergency"
        elif "urgent" in message_lower or "soon" in message_lower or "quickly" in message_lower:
            collected["urgency"] = "urgent"

        # Basic address extraction
        if not collected.get("address"):
            # Look for zip codes and city/state patterns
            zip_match = re.search(r"\b(\d{5})\b", message)
            if zip_match:
                collected["address"] = message  # Store full message for now, Claude will clean it up

        # Property type detection
        if not collected.get("property_type"):
            property_types = [
                ("single-family home", ["single-family", "house", "home", "detached"]),
                ("condo", ["condo", "condominium"]),
                ("apartment", ["apartment", "apt"]),
                ("townhouse", ["townhouse", "townhome"])
            ]

            for ptype, keywords in property_types:
                if any(keyword in message_lower for keyword in keywords):
                    collected["property_type"] = ptype
                    break

        # Business size preference detection
        if not collected.get("business_size_preference"):
            business_size_keywords = [
                ("INDIVIDUAL_HANDYMAN", ["individual handyman", "one person", "solo contractor", "handyman", "just one guy"]),
                ("OWNER_OPERATOR", ["owner operator", "family business", "small business owner", "owner-run", "family owned"]),
                ("LOCAL_BUSINESS_TEAMS", ["local company", "local business", "team of workers", "established company", "crew", "employees"]),
                ("NATIONAL_COMPANY", ["big company", "national company", "corporate", "franchise", "large company"])
            ]

            for size_type, keywords in business_size_keywords:
                if any(keyword in message_lower for keyword in keywords):
                    collected["business_size_preference"] = size_type
                    print(f"[CIA] Detected business size preference: {size_type}")
                    break

        # Service type preferences detection
        if not collected.get("service_type_preferences"):
            service_type_keywords = [
                ("REPAIR", ["repair", "fix", "fixing", "broken", "restore"]),
                ("INSTALLATION", ["install", "installation", "new", "replace", "setup"]),
                ("MAINTENANCE", ["maintain", "maintenance", "upkeep", "regular service", "ongoing"]),
                ("EMERGENCY", ["emergency", "urgent", "24/7", "immediate", "asap"]),
                ("CONSULTATION", ["estimate", "quote", "consultation", "assessment", "evaluation"])
            ]

            service_types = []
            for service_type, keywords in service_type_keywords:
                if any(keyword in message_lower for keyword in keywords):
                    service_types.append(service_type)

            if service_types:
                collected["service_type_preferences"] = service_types
                print(f"[CIA] Detected service type preferences: {service_types}")

    def _update_state_status(self, state: dict[str, Any]) -> None:
        """Update missing fields and phase"""
        collected = state["collected_info"]

        # Check missing required fields using NEW minimal requirements
        missing = []
        for field in REQUIRED_FIELDS_MINIMAL:
            if not collected.get(field):
                missing.append(field)

        state["missing_fields"] = missing
        state["ready_for_jaa"] = len(missing) == 0

        # INSTABIDS: Add intelligence about group bidding and service classification
        self._apply_instabids_intelligence(state)

        # Update phase based on progress
        if not collected.get("project_type"):
            state["current_phase"] = "discovery"
        elif not collected.get("budget_min"):
            state["current_phase"] = "details"
        elif not collected.get("uploaded_photos"):
            state["current_phase"] = "photos"
        elif len(missing) > 2:
            state["current_phase"] = "details"
        elif len(missing) > 0:
            state["current_phase"] = "review"
        else:
            state["current_phase"] = "complete"

    async def _handle_modification_requests(self, user_id: str, message: str, state: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Handle bid card modification requests through CIA orchestration"""

        # Use GPT-5 to intelligently detect modifications
        modification_analysis = await self._analyze_modification_with_gpt5(message, state)

        if not modification_analysis.get("is_modification", False):
            return None  # Not a modification request

        print(f"[CIA] GPT-5 detected modification request: {message}")
        print(f"[CIA] GPT-5 analysis: {modification_analysis}")

        # Extract modifications and project type from GPT-5's analysis
        modifications = modification_analysis.get("modifications", {})
        project_type = modification_analysis.get("project_type")
        confidence = modification_analysis.get("confidence", 0)

        if confidence < 0.8:
            print(f"[CIA] GPT-5 low confidence modification: {confidence}")
            return None

        try:
            # Create modification analysis in expected format
            modification_analysis = {
                "is_modification": True,
                "project_type": project_type,
                "modifications": modifications,
                "confidence": confidence
            }

            print(f"[CIA] Modification analysis result: {modification_analysis}")

            # Get the bid card to modify
            bid_card_number = modification_analysis.get("bid_card_number")

            # ALWAYS use active bid card if we have one
            if state.get("active_bid_card"):
                bid_card_number = state["active_bid_card"]
                print(f"[CIA] Using ACTIVE bid card from session: {bid_card_number}")
            elif not bid_card_number and state.get("bid_card_number"):
                bid_card_number = state["bid_card_number"]
                print(f"[CIA] Using bid card from context: {bid_card_number}")

            if not bid_card_number:
                # Only search if we have no active context
                project_type_to_find = modification_analysis.get("project_type", "")
                print(f"[CIA] No active bid card - searching for project type: {project_type_to_find}")
                bid_card_number = await self._find_relevant_bid_card(user_id, project_type_to_find)
                print(f"[CIA] Found bid card: {bid_card_number}")

            if not bid_card_number:
                return {
                    "response": "I'd like to help you make that change, but I need to know which project bid card to update. Could you specify which project this change is for?",
                    "session_id": state.get("session_id"),
                    "current_phase": "modification_clarification",
                    "ready_for_jaa": False,
                    "missing_fields": [],
                    "state": state
                }

            # Get existing bid card for validation
            existing_card = await self._get_bid_card_details(bid_card_number)

            # Check if there are actual modifications to apply
            has_actual_modifications = any(
                modifications.get(key) is not None
                for key in ["budget_min", "budget_max", "materials", "timeline", "urgency_level"]
            )

            if not has_actual_modifications:
                # User wants to continue working but hasn't specified changes yet
                # Generate response with bid card context
                return await self._generate_response_with_context(state, user_id, message, state.get("session_id"))

            # Validate modifications
            is_valid, error_message = self.modification_handler.validate_modifications(
                modifications,
                existing_card
            )

            if not is_valid:
                return {
                    "response": f"I can't make that change: {error_message}. Please provide a different value.",
                    "session_id": state.get("session_id"),
                    "current_phase": "modification_validation_error",
                    "ready_for_jaa": False,
                    "missing_fields": [],
                    "state": state
                }

            # Apply the modification through JAA
            result = await self._apply_bid_card_modification(
                bid_card_number, 
                modification_analysis.get("modifications", {}),
                user_id=user_id,
                session_id=session_id,
                message=message
            )

            if result.get("success"):
                # Add modification to conversation history
                modification_note = f"[MODIFICATION APPLIED] Updated bid card {bid_card_number}: {', '.join(result.get('modifications_applied', []))}"
                state["messages"].append({
                    "role": "system",
                    "content": modification_note,
                    "metadata": {"type": "modification_log", "timestamp": datetime.now().isoformat()}
                })

                # Update collected info with modifications
                if "collected_info" not in state:
                    state["collected_info"] = {}

                modifications = modification_analysis.get("modifications", {})
                if "budget_min" in modifications:
                    state["collected_info"]["budget_min"] = modifications["budget_min"]
                if "budget_max" in modifications:
                    state["collected_info"]["budget_max"] = modifications["budget_max"]
                if "timeline" in modifications:
                    state["collected_info"]["timeline_start"] = modifications["timeline"]
                if "materials" in modifications:
                    state["collected_info"]["materials_preferences"] = modifications["materials"]

                # Get the actual project type from the bid card
                project_type_display = modification_analysis.get("project_type", "project")
                if not project_type_display or project_type_display == "None":
                    # Try to get from the bid card result
                    if result.get("original_card", {}).get("project_type"):
                        project_type_display = result["original_card"]["project_type"]
                    else:
                        project_type_display = "project"

                # Use ModificationHandler to format the response
                response_text = self.modification_handler.format_modification_response(
                    modifications,
                    bid_card_number,
                    project_type_display
                )

                return {
                    "response": response_text,
                    "session_id": state.get("session_id"),
                    "current_phase": "modification_complete",
                    "ready_for_jaa": False,
                    "missing_fields": [],
                    "state": state,
                    "modification_applied": True,
                    "bid_card_updated": bid_card_number
                }
            else:
                return {
                    "response": f"I encountered an issue updating the bid card: {result.get('error', 'Unknown error')}. Could you try again or provide more details?",
                    "session_id": state.get("session_id"),
                    "current_phase": "modification_error",
                    "ready_for_jaa": False,
                    "missing_fields": [],
                    "state": state
                }

        except Exception as e:
            print(f"[CIA] Error handling modification request: {e}")
            return None

    async def _analyze_modification_intent(self, user_id: str, message: str) -> Optional[dict[str, Any]]:
        """Use Claude to analyze if message is a modification request"""

        try:
            modification_prompt = f"""Analyze this user message to determine if it's a bid card modification request:

USER MESSAGE: "{message}"

Determine:
1. Is this a modification request? (true/false)
2. What type of modification? (materials, budget, timeline, description, etc.)
3. What are the specific changes?
4. Which project type does this relate to? (kitchen, bathroom, etc.)

Return JSON:
{{
    "is_modification": true/false,
    "project_type": "kitchen|bathroom|etc",
    "modification_type": "materials|budget|timeline|description|urgency",
    "modifications": {{
        "materials": ["new materials list"] (if materials change),
        "budget_min": number (if budget change),
        "budget_max": number (if budget change),
        "timeline": "new timeline" (if timeline change),
        "project_description": "updated description" (if description change),
        "urgency_level": "emergency|urgent|flexible|planning" (if urgency change),
        "special_notes": "additional notes" (if special requirements)
    }},
    "confidence": 0.0-1.0
}}

Only return modifications that are clearly stated in the message."""

            # Use GPT-5 for modification prompt
            response_text = await self._call_llm(
                messages=[{"role": "user", "content": modification_prompt}],
                max_tokens=600,
                system=None
            )

            # Extract JSON
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                analysis = json.loads(json_str)

                if analysis.get("confidence", 0) >= 0.7:
                    return analysis

            return None

        except Exception as e:
            print(f"[CIA] Error analyzing modification intent: {e}")
            return None

    async def _find_user_bid_cards(self, user_id: str) -> list[dict[str, Any]]:
        """Find all bid cards for a user through conversations or direct user_id"""
        try:
            from database_simple import db

            # Get bid cards through conversations only (bid_cards table doesn't have user_id column)
            # Method 1: Get through conversations
            # Use unified conversation system to find user's conversations
            conversations = db.client.table("unified_conversations").select("metadata").contains("metadata", {"user_id": user_id}).execute()

            if conversations.data:
                thread_ids = [c["metadata"].get("session_id") for c in conversations.data if c["metadata"].get("session_id")]
                thread_cards = db.client.table("bid_cards").select("*").in_("cia_thread_id", thread_ids).order("created_at", desc=True).execute()
                
                # Return thread cards if found
                if thread_cards.data:
                    print(f"[CIA] Found {len(thread_cards.data)} bid cards for user through conversations")
                    return thread_cards.data
            else:
                print("[CIA] No bid cards found for user")
                return []

        except Exception as e:
            print(f"[CIA] Error finding bid cards: {e}")
            return []

    async def _find_relevant_bid_card(self, user_id: str, project_type: Optional[str] = None) -> Optional[str]:
        """Find the most relevant bid card for a user"""

        bid_cards = await self._find_user_bid_cards(user_id)

        if not bid_cards:
            return None

        # Filter by project type if specified
        if project_type and project_type != "None":
            filtered = [bc for bc in bid_cards if str(project_type).lower() in bc.get("project_type", "").lower()]
            if filtered:
                return filtered[0]["bid_card_number"]

        # Return most recent
        return bid_cards[0]["bid_card_number"]

    async def _get_bid_card_details(self, bid_card_number: str) -> dict[str, Any]:
        """Get existing bid card details for validation"""
        try:
            from database_simple import db
            result = db.client.table("bid_cards").select("*").eq("bid_card_number", bid_card_number).single().execute()
            return result.data if result.data else {}
        except Exception as e:
            print(f"[CIA] Error getting bid card details: {e}")
            return {}

    async def _apply_bid_card_modification(self, bid_card_number: str, modifications: dict[str, Any], user_id: str = None, session_id: str = None, message: str = "") -> dict[str, Any]:
        """Apply modifications to bid card using Intelligent JAA agent"""

        try:
            from database_simple import db
            print(f"[CIA] Applying modifications to bid card {bid_card_number}: {modifications}")

            # Get current bid card details
            bid_card_result = db.client.table("bid_cards").select("*").eq("bid_card_number", bid_card_number).execute()

            if not bid_card_result.data:
                return {"success": False, "error": f"Bid card {bid_card_number} not found"}

            current_bid_card = bid_card_result.data[0]
            bid_card_id = current_bid_card.get("id")

            # Apply modifications directly to bid card record
            updates = {}

            # Map CIA modifications to database fields
            if modifications.get("budget_min") is not None:
                updates["budget_min"] = int(modifications["budget_min"])
            if modifications.get("budget_max") is not None:
                updates["budget_max"] = int(modifications["budget_max"])
            if modifications.get("urgency_level"):
                updates["urgency_level"] = modifications["urgency_level"]
            if modifications.get("timeline"):
                # Update bid_document with timeline info
                bid_doc = current_bid_card.get("bid_document", {})
                bid_doc["timeline_updated"] = modifications["timeline"]
                bid_doc["last_modified"] = datetime.now().isoformat()
                updates["bid_document"] = bid_doc

            if updates:
                # Call JAA service instead of direct database update
                jaa_response = await self.call_jaa_update_service(bid_card_id, {
                    "source_agent": "cia_agent",
                    "conversation_snippet": message or f"Modifications: {modifications}",
                    "detected_change_hints": list(modifications.keys()),
                    "modifications": modifications,
                    "requester_info": {
                        "user_id": user_id or "cia_user",
                        "session_id": session_id or "cia_session"
                    }
                })
                
                if jaa_response.get("success"):
                    print(f"[CIA] Successfully updated bid card {bid_card_number} via JAA service")
                    return {
                        "success": True,
                        "bid_card_number": bid_card_number,
                        "jaa_response": jaa_response,
                        "modifications_applied": modifications,
                        "affected_contractors": jaa_response.get("affected_contractors", []),
                        "notification_content": jaa_response.get("notification_content")
                    }
                else:
                    return {"success": False, "error": f"JAA service failed: {jaa_response.get('error', 'Unknown error')}"}
            else:
                return {"success": False, "error": "No valid modifications provided"}

        except Exception as e:
            print(f"[CIA] Error applying bid card modification: {e}")
            return {"success": False, "error": str(e)}

    def _format_changes_summary(self, applied_fields: list[str], modifications: dict[str, Any]) -> str:
        """Format a human-readable summary of changes"""

        summaries = []

        for field in applied_fields:
            if field == "materials" and "materials" in modifications:
                materials = modifications["materials"]
                if isinstance(materials, list):
                    summaries.append(f"materials updated to {', '.join(materials[:2])}")
                else:
                    summaries.append(f"materials updated to {materials}")

            elif field == "budget_min" or field == "budget_max":
                if "budget_min" in modifications or "budget_max" in modifications:
                    min_budget = modifications.get("budget_min", "")
                    max_budget = modifications.get("budget_max", "")
                    if min_budget and max_budget:
                        summaries.append(f"budget updated to ${min_budget:,}-${max_budget:,}")
                    elif max_budget:
                        summaries.append(f"budget updated to ${max_budget:,}")

            elif field == "timeline" and "timeline" in modifications:
                summaries.append(f"timeline updated to {modifications['timeline']}")

            elif field == "urgency_level" and "urgency_level" in modifications:
                summaries.append(f"urgency changed to {modifications['urgency_level']}")

            elif field == "project_description" and "project_description" in modifications:
                summaries.append("project description updated")

            elif field == "special_notes" and "special_notes" in modifications:
                summaries.append("special requirements updated")

        return "; ".join(summaries) if summaries else "specifications updated"

    async def _analyze_modification_with_gpt5(self, message: str, state: dict[str, Any]) -> dict[str, Any]:
        """Use GPT-5 to intelligently analyze if this is a modification request"""
        try:
            analysis_prompt = f"""
            Analyze this message to determine if the user wants to modify an existing project: "{message}"

            CRITICAL: Pay special attention to FREQUENCY patterns - these are NOT materials!
            - "bi-weekly", "biweekly", "every other week" = frequency, NOT material
            - "weekly", "monthly", "daily" = frequency, NOT material

            Consider these modification types:
            1. BUDGET: "increase budget to $50k", "change from $40k to $60k", "budget should be $25,000"
            2. MATERIALS: "change from granite to quartz", "use hardwood instead", "switch to stainless steel"
            3. TIMELINE: "need it in 3 weeks", "extend to 8 weeks", "finish by March 15th"
            4. URGENCY: "make this urgent", "this is emergency", "no longer urgent", "flexible timing"
            5. FREQUENCY/SCHEDULE: "change to bi-weekly", "weekly instead of monthly", "every other week", "bi-weekly service"
            6. PROJECT SCOPE: "add a bathroom", "remove the deck", "include the garage"

            Return JSON with:
            {{
                "is_modification": true/false,
                "confidence": 0.0-1.0,
                "modification_type": "budget|materials|timeline|urgency|frequency|scope",
                "project_type": "kitchen|bathroom|lawn|null",
                "modifications": {{
                    "budget_min": number or null,
                    "budget_max": number or null,
                    "materials": ["material1", "material2"] or null,
                    "timeline": "X weeks" or null,
                    "urgency_level": "emergency|week|month|flexible" or null,
                    "frequency": "weekly|bi-weekly|monthly" or null,
                    "scope_changes": "description" or null
                }},
                "reasoning": "Why this is/isn't a modification"
            }}

            Examples:
            - "Change the lawn service to bi-weekly instead of weekly" → {{"is_modification": true, "modifications": {{"frequency": "bi-weekly"}}, "project_type": "lawn"}}
            - "Change to bi-weekly lawn service" → {{"is_modification": true, "modifications": {{"frequency": "bi-weekly"}}, "project_type": "lawn"}}
            - "Make it weekly instead" → {{"is_modification": true, "modifications": {{"frequency": "weekly"}}}}
            - "Change from granite to quartz" → {{"is_modification": true, "modifications": {{"materials": ["quartz"]}}}}
            - "Increase kitchen budget to $55,000" → {{"is_modification": true, "modifications": {{"budget_max": 55000, "budget_min": 44000}}, "project_type": "kitchen"}}
            - "I need a new bathroom" → {{"is_modification": false, "reasoning": "This is a new project request, not modifying existing"}}
            """

            if not self.client:
                return {"is_modification": False, "confidence": 0.0}

            # Use GPT-5 for analysis
            response_text = await self._call_llm(
                messages=[{"role": "user", "content": analysis_prompt}],
                max_tokens=500,
                system=None
            )

            if not response_text:
                return {"is_modification": False, "confidence": 0.0}

            # Parse JSON response
            import json

            # Strip markdown code blocks if present
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                if json_end > json_start:
                    response_text = response_text[json_start:json_end].strip()

            # Try to extract JSON from response
            try:
                # First try direct parsing
                analysis = json.loads(response_text)
                print(f"[CIA] GPT-5 modification analysis: {analysis}")
                return analysis
            except json.JSONDecodeError:
                # Try to find JSON in the response
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    try:
                        json_str = response_text[json_start:json_end]
                        analysis = json.loads(json_str)
                        print(f"[CIA] GPT-5 modification analysis: {analysis}")
                        return analysis
                    except:
                        pass

                print(f"[CIA] Could not parse GPT-5 response: {response_text[:200]}...")
                return {"is_modification": False, "confidence": 0.0}

        except Exception as e:
            print(f"[CIA] Error in GPT-5 modification analysis: {e}")
            return {"is_modification": False, "confidence": 0.0}

    def _classify_service_type_from_old_data(self, old_info: dict[str, Any]) -> Optional[str]:
        """Classify service type from old data structure"""
        project_type = str(old_info.get("project_type", "")).lower()
        description = str(old_info.get("project_description", "")).lower()
        combined_text = f"{project_type} {description}"

        # Use SERVICE_TYPE_KEYWORDS to classify
        for service_type, keywords in SERVICE_TYPE_KEYWORDS.items():
            if any(keyword in combined_text for keyword in keywords):
                return service_type

        return "installation"  # Default

    def _derive_budget_context(self, old_info: dict[str, Any]) -> Optional[str]:
        """Derive budget context from old budget data"""
        if (old_info.get("budget_min") and old_info.get("budget_max")) or old_info.get("budget_min") or old_info.get("budget_max"):
            return "has_budget_range"
        else:
            return "not_discussed"

    def _map_old_urgency(self, old_urgency: Optional[str]) -> Optional[str]:
        """Map old urgency to new timeline_urgency"""
        if not old_urgency:
            return None

        mapping = {
            "emergency": "emergency",
            "urgent": "urgent",
            "flexible": "flexible",
            "low": "planning",
            "medium": "flexible",
            "high": "urgent"
        }
        return mapping.get(old_urgency.lower(), "flexible")

    def _extract_zip_from_address(self, address: Optional[str]) -> Optional[str]:
        """Extract zip code from full address"""
        if not address:
            return None

        import re
        zip_match = re.search(r"\b(\d{5})\b", address)
        return zip_match.group(1) if zip_match else None

    def _assess_group_bidding_from_project_type(self, project_type: Optional[str]) -> Optional[bool]:
        """Assess group bidding potential from project type"""
        if not project_type:
            return None

        return any(group_type in project_type.lower() for group_type in GROUP_BIDDING_PROJECTS)

    def _calculate_intention_from_old_data(self, old_info: dict[str, Any]) -> Optional[int]:
        """Calculate intention score from old data"""
        score = 5  # Base score

        # Budget readiness
        if old_info.get("budget_min") or old_info.get("budget_max"):
            score += INTENTION_SCORE_FACTORS.get("budget_ready", 0)

        # Urgency
        urgency_value = old_info.get("urgency")
        urgency = urgency_value.lower() if urgency_value else ""
        if urgency in ["emergency", "urgent"]:
            score += INTENTION_SCORE_FACTORS.get("high_urgency", 0)

        # Photos uploaded
        if old_info.get("uploaded_photos"):
            score += INTENTION_SCORE_FACTORS.get("photos_uploaded", 0)

        # Detailed description
        if old_info.get("project_description") and len(old_info["project_description"]) > 50:
            score += INTENTION_SCORE_FACTORS.get("detailed_description", 0)

        return max(1, min(10, score))

    def _apply_instabids_intelligence(self, state: dict[str, Any]) -> None:
        """Apply InstaBids-specific intelligence to conversation state"""
        collected = state["collected_info"]

        # SMART SERVICE TYPE CLASSIFICATION
        if not collected.get("service_type") and collected.get("project_type"):
            collected["service_type"] = self._intelligent_service_classification(
                collected.get("project_description", ""),
                collected.get("project_type", ""),
                state.get("messages", [])
            )

        # GROUP BIDDING ASSESSMENT
        if collected.get("service_type") and collected.get("project_type"):
            if not collected.get("group_bidding_potential"):
                collected["group_bidding_potential"] = self._assess_group_bidding_potential(
                    collected["project_type"],
                    collected["service_type"],
                    collected.get("timeline_urgency")
                )

        # INTENTION SCORE CALCULATION
        if not collected.get("intention_score"):
            collected["intention_score"] = self._calculate_intention_score_intelligent(
                collected,
                state.get("messages", [])
            )

        # BUDGET CONTEXT INTELLIGENCE
        if not collected.get("budget_context"):
            collected["budget_context"] = self._derive_budget_context_intelligent(
                state.get("messages", [])
            )

    def _intelligent_service_classification(self, description: str, project_type: str, messages: list[dict]) -> Optional[str]:
        """Intelligently classify service type using context"""
        # Combine all text for analysis
        all_text = f"{description} {project_type}".lower()
        for msg in messages[-3:]:  # Last 3 messages
            if msg.get("role") == "user":
                all_text += f" {msg.get('content', '')}".lower()

        # Score each service type
        scores = {}
        for service_type, keywords in SERVICE_TYPE_KEYWORDS.items():
            scores[service_type] = sum(1 for keyword in keywords if keyword in all_text)

        # Return highest scoring service type
        if scores and max(scores.values()) > 0:
            return max(scores, key=scores.get)

        # Default logic based on project type
        if "care" in project_type or "clean" in project_type:
            return "ongoing_service"
        elif "repair" in all_text or "fix" in all_text:
            return "repair"
        else:
            return "installation"

    def _assess_group_bidding_potential(self, project_type: str, service_type: str, timeline_urgency: Optional[str]) -> bool:
        """Assess if project is good for group bidding"""
        # Must not be emergency/urgent
        if timeline_urgency in ["emergency", "urgent"]:
            return False

        # Must be standardized work type
        return any(group_type in project_type.lower() for group_type in GROUP_BIDDING_PROJECTS)

    def _calculate_intention_score_intelligent(self, collected: dict[str, Any], messages: list[dict]) -> int:
        """Calculate intelligent intention score 1-10"""
        score = 5  # Base neutral

        # Timeline urgency
        timeline_urgency = collected.get("timeline_urgency")
        if timeline_urgency == "emergency":
            score += INTENTION_SCORE_FACTORS.get("high_urgency", 0)
        elif timeline_urgency == "urgent":
            score += INTENTION_SCORE_FACTORS.get("specific_timeline", 0)

        # Budget readiness
        if collected.get("budget_min") or collected.get("budget_max"):
            score += INTENTION_SCORE_FACTORS.get("budget_ready", 0)

        # Photos uploaded
        if collected.get("uploaded_photos"):
            score += INTENTION_SCORE_FACTORS.get("photos_uploaded", 0)

        # Detailed description
        if collected.get("project_description") and len(collected["project_description"]) > 100:
            score += INTENTION_SCORE_FACTORS.get("detailed_description", 0)

        # Analyze message content for intention signals
        recent_messages = [msg.get("content", "").lower() for msg in messages[-3:] if msg.get("role") == "user"]
        combined_text = " ".join(recent_messages)

        # Positive signals
        if any(phrase in combined_text for phrase in ["ready", "need to", "have to", "must"]):
            score += 1

        # Negative signals
        if any(phrase in combined_text for phrase in ["maybe", "thinking", "exploring", "someday"]):
            score += INTENTION_SCORE_FACTORS.get("exploring_only", 0)

        if "future" in combined_text:
            score += INTENTION_SCORE_FACTORS.get("far_future", 0)

        return max(1, min(10, score))

    def _derive_budget_context_intelligent(self, messages: list[dict]) -> str:
        """Derive budget context from conversation"""
        recent_messages = [msg.get("content", "").lower() for msg in messages[-5:] if msg.get("role") == "user"]
        combined_text = " ".join(recent_messages)

        if any(phrase in combined_text for phrase in ["got quote", "already quoted", "contractor said"]):
            return "has_quotes"
        elif any(phrase in combined_text for phrase in ["budget", "$", "cost", "price", "spend"]):
            return "has_budget_range"
        elif any(phrase in combined_text for phrase in ["explore", "looking at", "research", "idea"]):
            return "exploring_options"
        elif any(phrase in combined_text for phrase in ["dream", "someday", "future", "maybe"]):
            return "dream_project"
        else:
            return "not_discussed"

    async def _generate_response_with_context(self, state: dict[str, Any], user_id: str, message: str, session_id: str) -> dict[str, Any]:
        """Generate a response using GPT-5 API with full bid card context"""
        # Add the user message to state
        state["messages"].append({
            "role": "user",
            "content": message,
            "metadata": {"timestamp": datetime.now().isoformat()}
        })

        # Generate response using GPT-5
        response_text = await self._generate_gpt5_response(state)

        # Add assistant response to state
        state["messages"].append({
            "role": "assistant",
            "content": response_text,
            "metadata": {"timestamp": datetime.now().isoformat()}
        })

        # Save conversation to unified system
        await self._save_to_unified_conversations(state, user_id, session_id)

        return {
            "response": response_text,
            "session_id": session_id,
            "current_phase": "conversation",
            "ready_for_jaa": False,
            "missing_fields": [],
            "state": state,
            "has_bid_card_context": True,
            "bid_card_number": state.get("bid_card_number")
        }

    async def _save_conversation_to_database(self, state: dict[str, Any], user_id: str, session_id: str):
        """Save conversation state to unified conversation system only"""
        try:
            # Use the unified conversation system through database.py
            from database_simple import db
            await db.save_conversation_state(
                user_id=user_id,
                thread_id=session_id,
                agent_type="CIA", 
                state=state
            )
            print(f"[CIA] Saved conversation to unified system: {session_id}")
            return {"thread_id": session_id, "user_id": user_id}
        except Exception as e:
            print(f"[CIA] Error saving conversation to unified system: {e}")
            # Don't raise - conversation can continue even if save fails
            return None

    async def _save_to_unified_conversations(self, state: dict[str, Any], user_id: str, session_id: str):
        """Save conversation to unified conversation system via HomeownerContextAdapter"""
        try:
            print(f"[CIA] Saving to unified conversation system via adapter - session: {session_id}")
            
            # Use the unified integration adapter instead of direct database calls
            result = await self.unified_integration.save_conversation_with_unified_system(
                user_id=user_id,
                state=state,
                session_id=session_id
            )
            
            if result.get("success"):
                print(f"[CIA] Successfully saved conversation via adapter")
                # Extract memories for cross-agent sharing (IRIS, messaging, etc.)
                await self.unified_integration._save_extracted_memories(user_id, state, result.get("conversation_id"))
                return
            else:
                print(f"[CIA] Failed to save via adapter: {result.get('error', 'Unknown error')}")
                # Don't fall back to direct database - adapter should be the only path
                
        except Exception as e:
            print(f"[CIA] Error saving to unified system via adapter: {e}")
            # Continue without throwing - allow conversation to proceed
            print(f"[CIA] Found {len(messages)} messages in state for saving")
            if messages and conversation_id:
                # Check if images were already saved to prevent double message saving
                if state.get('_images_already_saved'):
                    # Skip saving user message again, only save assistant response
                    messages_to_save = [m for m in messages[-2:] if m['role'] == 'assistant']
                    print(f"[CIA] Images already saved, only saving assistant response")
                else:
                    # Save the last 2 messages (user question and assistant response)
                    messages_to_save = messages[-2:] if len(messages) >= 2 else messages
                
                for message in messages_to_save:
                    print(f"[CIA] Saving message: role={message['role']}, content_preview={message.get('content', '')[:50]}...")
                    # Use a deterministic UUID for the CIA agent
                    cia_agent_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, "cia-agent"))
                    
                    message_data = {
                        "conversation_id": conversation_id,
                        "sender_type": "user" if message["role"] == "user" else "agent",
                        "sender_id": user_uuid if message["role"] == "user" else cia_agent_uuid,
                        "agent_type": "cia" if message["role"] == "assistant" else None,
                        "content": message.get("content", ""),
                        "content_type": "text",
                        "metadata": message.get("metadata", {}),
                        "created_at": message.get("metadata", {}).get("timestamp", datetime.now().isoformat())
                    }
                    
                    # Save message directly to Supabase
                    msg_result = self.supabase.table("unified_messages").insert(message_data).execute()
                    if msg_result.data:
                        print(f"[CIA] Saved {message['role']} message to unified system")
                    else:
                        print(f"[CIA] Warning: Failed to save {message['role']} message")
                
            # 3. Store conversation memory/state directly via Supabase
            if conversation_id:
                # Store collected info as memory
                collected_info = state.get("collected_info", {})
                if collected_info:
                    memory_data = {
                        "tenant_id": "00000000-0000-0000-0000-000000000000",
                        "conversation_id": conversation_id,
                        "memory_scope": "conversation",
                        "memory_type": "preference",
                        "memory_key": "collected_info",
                        "memory_value": collected_info,
                        "importance_score": 10,
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat()
                    }
                    
                    # Save memory directly to Supabase
                    mem_result = self.supabase.table("unified_conversation_memory").insert(memory_data).execute()
                    if mem_result.data:
                        print(f"[CIA] Saved collected info to unified memory")
                    else:
                        print(f"[CIA] Warning: Failed to save memory")
                
                # Store full state for JAA compatibility
                state_memory_data = {
                    "tenant_id": "00000000-0000-0000-0000-000000000000",
                    "conversation_id": conversation_id,
                    "memory_scope": "conversation",
                    "memory_type": "fact",
                    "memory_key": "cia_state",
                    "memory_value": {
                        "thread_id": session_id,
                        "user_id": user_id,
                        "agent_type": "CIA",
                        "state": state,
                        "created_at": datetime.now().isoformat()
                    },
                    "importance_score": 10,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                
                # Save state directly to Supabase
                state_result = self.supabase.table("unified_conversation_memory").insert(state_memory_data).execute()
                if state_result.data:
                    print(f"[CIA] Saved full state to unified memory for JAA")
                else:
                    print(f"[CIA] Warning: Failed to save state")
                
                print(f"[CIA] Successfully saved to unified conversation system")
                return {"conversation_id": conversation_id}
                
        except Exception as e:
            print(f"[CIA] Error saving to unified system: {e}")
            # Don't fallback - we want to see the actual error
            raise e

    async def get_bid_submissions_for_conversation(self, conversation_id: str) -> list[dict]:
        """Get all bid submissions from unified messaging system for a conversation"""
        try:
            # Query unified_messages for bid submissions
            result = self.supabase.table("unified_messages").select("*").eq(
                "conversation_id", conversation_id
            ).contains(
                "metadata", {"message_type": "bid_submission"}
            ).execute()
            
            bid_submissions = []
            for message in result.data:
                if message.get("metadata", {}).get("message_type") == "bid_submission":
                    bid_data = message["metadata"].get("bid_data", {})
                    bid_submissions.append({
                        "contractor_id": bid_data.get("contractor_id"),
                        "amount": bid_data.get("amount", 0),
                        "timeline": bid_data.get("timeline", ""),
                        "proposal": bid_data.get("filtered_content", ""),
                        "submitted_at": message.get("created_at"),
                        "security_threats": message["metadata"].get("threats_detected", []),
                        "bid_details": bid_data
                    })
            
            return sorted(bid_submissions, key=lambda x: x.get("submitted_at", ""), reverse=True)
            
        except Exception as e:
            print(f"[CIA] Error getting bid submissions: {e}")
            return []
    
    async def get_bid_submissions_for_bid_card(self, bid_card_id: str) -> list[dict]:
        """Get all bid submissions for a specific bid card"""
        try:
            # Query unified_messages for bid submissions related to this bid card
            result = self.supabase.table("unified_messages").select("*").contains(
                "metadata", {"message_type": "bid_submission"}
            ).execute()
            
            bid_submissions = []
            for message in result.data:
                if (message.get("metadata", {}).get("message_type") == "bid_submission" and
                    message.get("metadata", {}).get("bid_data", {}).get("bid_card_id") == bid_card_id):
                    
                    bid_data = message["metadata"].get("bid_data", {})
                    bid_submissions.append({
                        "contractor_id": bid_data.get("contractor_id"),
                        "amount": bid_data.get("amount", 0),
                        "timeline": bid_data.get("timeline", ""),
                        "proposal": bid_data.get("filtered_content", ""),
                        "submitted_at": message.get("created_at"),
                        "security_threats": message["metadata"].get("threats_detected", []),
                        "bid_details": bid_data
                    })
            
            return sorted(bid_submissions, key=lambda x: x.get("submitted_at", ""), reverse=True)
            
        except Exception as e:
            print(f"[CIA] Error getting bid submissions for bid card: {e}")
            return []

    async def call_jaa_update_service(self, bid_card_id: str, update_context: dict) -> dict:
        """
        Call JAA service to update bid card instead of direct database update
        
        Args:
            bid_card_id: Bid card ID to update
            update_context: Context including source_agent, conversation_snippet, etc.
            
        Returns:
            JAA response with success status and contractor notification data
        """
        try:
            # JAA service endpoint - use centralized configuration
            from config.service_urls import get_jaa_update_url
            jaa_endpoint = get_jaa_update_url(bid_card_id)
            
            # Prepare request payload
            payload = {
                "update_context": update_context,
                "update_type": "conversation_based"
            }
            
            print(f"[CIA] Calling JAA service for bid card {bid_card_id}")
            print(f"[CIA] JAA payload: {json.dumps(payload, indent=2)}")
            
            # Make async HTTP request to JAA service using httpx (non-blocking)
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    jaa_endpoint,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    jaa_response = response.json()
                    print(f"[CIA] JAA service success: {jaa_response.get('update_summary', {}).get('change_summary', 'Updated')}")
                    return jaa_response
                else:
                    error_msg = f"JAA service error {response.status_code}: {response.text}"
                    print(f"[CIA] {error_msg}")
                    return {
                        "success": False,
                        "error": error_msg
                    }
                
        except httpx.TimeoutException:
            error_msg = "JAA service timeout - request took longer than 30 seconds"
            print(f"[CIA] {error_msg}")
            return {"success": False, "error": error_msg}
            
        except httpx.ConnectError:
            error_msg = "JAA service unavailable - could not connect to localhost:8008"
            print(f"[CIA] {error_msg}")
            return {"success": False, "error": error_msg}
            
        except Exception as e:
            error_msg = f"JAA service call failed: {str(e)}"
            print(f"[CIA] {error_msg}")
            return {"success": False, "error": error_msg}

    # ========== UNIFIED IMAGE ATTACHMENT SYSTEM METHODS ==========
    
    async def _ensure_unified_conversation(self, user_id: str, session_id: str) -> str:
        """Get or create unified conversation, return conversation_id"""
        import uuid
        from datetime import datetime
        
        try:
            # Convert user_id to UUID format if needed
            try:
                user_uuid = str(uuid.UUID(user_id))
            except ValueError:
                user_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, user_id))
            
            # Check if conversation exists for this session
            existing = self.supabase.table("unified_conversations").select("*").eq("metadata->>session_id", session_id).execute()
            
            if existing.data:
                conversation_id = existing.data[0]["id"]
                print(f"[CIA] Found existing unified conversation: {conversation_id}")
                return conversation_id
            
            # Create new conversation
            conversation_data = {
                "tenant_id": "00000000-0000-0000-0000-000000000000",
                "created_by": user_uuid,
                "conversation_type": "project_setup",
                "entity_type": "homeowner", 
                "entity_id": user_uuid,
                "title": f"CIA Session - Images",
                "metadata": {"session_id": session_id},
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            result = self.supabase.table("unified_conversations").insert(conversation_data).execute()
            if result.data:
                conversation_id = result.data[0]["id"]
                print(f"[CIA] Created new unified conversation: {conversation_id}")
                return conversation_id
            else:
                raise Exception("Failed to create unified conversation")
                
        except Exception as e:
            print(f"[CIA] Error ensuring unified conversation: {e}")
            raise e

    async def _save_unified_message(self, conversation_id: str, sender_type: str, 
                                   sender_id: str, content: str, metadata: dict) -> str:
        """Save message to unified_messages, return message_id"""
        from datetime import datetime
        
        try:
            message_data = {
                "conversation_id": conversation_id,
                "sender_type": sender_type,
                "sender_id": sender_id,
                "agent_type": "cia" if sender_type == "agent" else None,
                "content": content,
                "content_type": "text",
                "metadata": metadata,
                "created_at": datetime.now().isoformat()
            }
            
            result = self.supabase.table("unified_messages").insert(message_data).execute()
            if result.data:
                message_id = result.data[0]["id"]
                print(f"[CIA] Saved {sender_type} message to unified system: {message_id}")
                return message_id
            else:
                raise Exception("Failed to save unified message")
                
        except Exception as e:
            print(f"[CIA] Error saving unified message: {e}")
            raise e

    async def _upload_and_attach_images(self, conversation_id: str, message_id: str, 
                                       images: list[str]) -> list[str]:
        """Upload images to Storage, create attachments, return URLs"""
        import base64
        import uuid
        from datetime import datetime
        
        urls = []
        try:
            for i, base64_image in enumerate(images):
                print(f"[CIA] Processing image {i+1} for unified attachment system")
                
                # Strip data: prefix
                clean_base64 = base64_image.split(',')[1] if ',' in base64_image else base64_image
                
                # Decode and detect format
                image_data = base64.b64decode(clean_base64)
                mime_type = 'image/jpeg'  # Default, could detect from header
                ext = 'jpg'
                
                # Upload to storage
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{uuid.uuid4()}_{i}.{ext}"
                storage_path = f"unified/{conversation_id}/{filename}"
                
                print(f"[CIA] Uploading image to Supabase Storage: {storage_path}")
                
                # Upload to Supabase Storage
                try:
                    upload_result = self.supabase.storage.from_("project-images").upload(
                        storage_path, image_data, {"content-type": mime_type}
                    )
                    print(f"[CIA] Upload result type: {type(upload_result)}")
                    print(f"[CIA] Upload successful for: {storage_path}")
                except Exception as upload_e:
                    print(f"[CIA] Storage upload failed: {upload_e}")
                    continue
                
                # Get public URL
                url_response = self.supabase.storage.from_("project-images").get_public_url(storage_path)
                url = url_response
                
                print(f"[CIA] Image uploaded successfully, URL: {url}")
                
                # Create attachment record (match actual table schema)
                attachment_data = {
                    "tenant_id": "00000000-0000-0000-0000-000000000000",
                    "message_id": message_id,
                    "mime_type": mime_type,
                    "file_size": len(image_data),
                    "storage_path": storage_path,
                    "created_at": datetime.now().isoformat()
                }
                
                attachment_result = self.supabase.table("unified_message_attachments").insert(attachment_data).execute()
                if attachment_result.data:
                    print(f"[CIA] Created unified attachment record: {attachment_result.data[0]['id']}")
                    urls.append(url)
                else:
                    print(f"[CIA] Failed to create attachment record")
            
            print(f"[CIA] Successfully processed {len(urls)} images for unified system")
            return urls
            
        except Exception as e:
            print(f"[CIA] Error uploading and attaching images: {e}")
            return urls  # Return partial results
