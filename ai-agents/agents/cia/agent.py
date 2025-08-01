"""CIA (Customer Interface Agent) Implementation - Using Claude Opus 4"""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import anthropic
import json
import asyncio
import time
import sys
from supabase import create_client
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.cia.state import ConversationState, REQUIRED_FIELDS, PHASE_TRANSITIONS
from agents.cia.prompts import SYSTEM_PROMPT, get_conversation_prompt, IMAGE_ANALYSIS_PROMPT
from agents.cia.new_state import NewCollectedInfo, REQUIRED_FIELDS_MINIMAL, SERVICE_TYPE_KEYWORDS, GROUP_BIDDING_PROJECTS, INTENTION_SCORE_FACTORS
from agents.cia.new_prompts import SYSTEM_PROMPT as NEW_SYSTEM_PROMPT
from agents.cia.modification_handler import ModificationHandler
from memory.langgraph_integration import (
    setup_project_aware_agent,
    update_agent_memory_after_conversation
)


class CustomerInterfaceAgent:
    """CIA - Handles all homeowner interactions for project scoping"""
    
    def __init__(self, anthropic_api_key: str):
        """Initialize the CIA with Claude Opus 4"""
        print(f"[CIA] Initializing with API key: {anthropic_api_key[:20]}...")
        
        if anthropic_api_key == "demo_key":
            self.client = None  # Demo mode
            print("[CIA] Running in DEMO mode - no API key provided")
        else:
            try:
                self.client = anthropic.Anthropic(api_key=anthropic_api_key)
                print("[CIA] Successfully initialized Anthropic client")
            except Exception as e:
                print(f"[CIA ERROR] Failed to initialize Anthropic client: {e}")
                self.client = None
        
        # Initialize ModificationHandler for reliable modification detection
        self.modification_handler = ModificationHandler()
        
        # Initialize mode manager for switching between conversation and action modes
        from .mode_manager import ModeManager
        self.mode_manager = ModeManager()
        
        # Initialize Supabase connection for conversation persistence
        load_dotenv(override=True)
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        self.supabase = create_client(self.supabase_url, self.supabase_key)
        print("[CIA] Initialized Supabase connection")
        
        # In-memory session storage (in production, use database)
        self.sessions = {}
        
    async def handle_conversation(
        self, 
        user_id: str,
        message: str,
        images: Optional[List[str]] = None,
        session_id: Optional[str] = None,
        existing_state: Optional[Dict[str, Any]] = None,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Main entry point for handling user conversations - now project-aware"""
        print(f"\n[CIA] Handling conversation - User: {user_id}, Session: {session_id}")
        print(f"[CIA] Project ID: {project_id}")
        print(f"[CIA] Message: {message}")
        print(f"[CIA] Has client: {self.client is not None}")
        
        # Get or create session with NEW data structure
        if existing_state:
            # Restore from persisted state
            state = existing_state
            # Migrate to new structure if needed
            state = self._migrate_to_new_structure(state)
            self.sessions[session_id] = state
            print(f"[CIA] Restored session from database: {session_id}")
        elif not session_id or session_id not in self.sessions:
            # Create new session - preserve provided session_id if given
            if not session_id:
                session_id = f"session_{user_id}_{datetime.now().timestamp()}"
            self.sessions[session_id] = self._create_new_session_with_instabids_structure(user_id, session_id)
            print(f"[CIA] Created new session with InstaBids structure: {session_id}")
        
        state = self.sessions[session_id]
        
        # Restore active bid card if it exists
        if 'active_bid_card' in state and state['active_bid_card']:
            print(f"[CIA] Restored active bid card from session: {state['active_bid_card']}")
        
        # CRITICAL: MODE SWITCHING - Determine if we should be in action or conversation mode
        user_bid_cards = await self._find_user_bid_cards(user_id)
        
        # If we have an active bid card but it's not in the search results, add it
        if state.get('active_bid_card') and state.get('bid_card_context'):
            # Check if active card is in the results
            found_active = any(card['bid_card_number'] == state['active_bid_card'] for card in user_bid_cards)
            if not found_active:
                # Add the active bid card to the list
                user_bid_cards.append(state['bid_card_context'])
                print(f"[CIA] Added active bid card {state['active_bid_card']} to user's cards")
        
        context = {
            'user_bid_cards': user_bid_cards,
            'has_active_project': bool(project_id) or bool(state.get('active_bid_card')),
            'message_count': state.get('message_count', 0)
        }
        
        mode = self.mode_manager.analyze_intent(message, context)
        print(f"[CIA] Mode: {mode.value}")
        
        # ACTION MODE - Skip all project decisions, go straight to modifications
        if mode.value == "action" and user_bid_cards:
            print("[CIA] ACTION MODE: Handling modification directly")
            print(f"[CIA] ACTION MODE: State has active_bid_card: {state.get('active_bid_card')}")
            print(f"[CIA] ACTION MODE: State keys: {list(state.keys())}")
            
            # Check if this is a modification using Claude intelligence
            modification_analysis = await self._analyze_modification_with_claude(message, state)
            is_modification = modification_analysis.get('is_modification', False)
            
            if is_modification:
                # ALWAYS use active bid card if available
                relevant_bid_card = None
                if state.get('active_bid_card'):
                    print(f"[CIA] ACTION MODE: Looking for active bid card: {state['active_bid_card']}")
                    # Look for the active bid card
                    for card in user_bid_cards:
                        print(f"[CIA] ACTION MODE: Checking card {card['bid_card_number']}")
                        if card['bid_card_number'] == state['active_bid_card']:
                            relevant_bid_card = card
                            print(f"[CIA] ACTION MODE: FOUND ACTIVE bid card: {state['active_bid_card']}")
                            break
                    if not relevant_bid_card:
                        print(f"[CIA] ACTION MODE: Active bid card {state['active_bid_card']} not found in user's cards!")
                elif state.get('bid_card_number'):
                    # Fall back to context bid card
                    for card in user_bid_cards:
                        if card['bid_card_number'] == state['bid_card_number']:
                            relevant_bid_card = card
                            print(f"[CIA] ACTION MODE: Using bid card from context: {state['bid_card_number']}")
                            break
                
                if not relevant_bid_card:
                    # Only search if no active context
                    project_type = modification_analysis.get('project_type')
                    
                    if project_type:
                        # Look for bid card matching project type
                        for card in user_bid_cards:
                            if project_type.lower() in card.get('project_type', '').lower():
                                relevant_bid_card = card
                                break
                    
                    # If no match, use most recent
                    if not relevant_bid_card:
                        relevant_bid_card = user_bid_cards[0]
                
                bid_card_number = relevant_bid_card['bid_card_number']
                print(f"[CIA] Found bid card for modification: {bid_card_number}")
                
                # Apply modification through JAA
                result = await self._apply_bid_card_modification(
                    bid_card_number,
                    modification_analysis.get('modifications', {})
                )
                
                if result.get('success'):
                    response = self.modification_handler.format_modification_response(
                        modification_analysis.get('modifications', {}),
                        bid_card_number,
                        relevant_bid_card['project_type']
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
        
        # CRITICAL: Project Decision Logic - Determine if this is continuation or new project
        if not project_id and user_id != "00000000-0000-0000-0000-000000000000":
            # Load user's project summaries for context
            try:
                from memory.multi_project_store import MultiProjectMemoryStore
                store = MultiProjectMemoryStore()
                summaries = await store.get_user_projects_summary(user_id)
                
                if summaries:
                    # Add project summaries to state for general conversation context
                    state['user_project_summaries'] = summaries
                    print(f"[CIA] Loaded {len(summaries)} project summaries for conversation context")
            except Exception as e:
                print(f"[CIA] Warning: Could not load project summaries: {e}")
            
            project_decision = await self._determine_project_intent(user_id, message)
            if project_decision:
                print(f"[CIA] Project decision: {project_decision}")
                if project_decision.get('action') == 'ask_clarification':
                    # Return clarification question immediately
                    return {
                        "response": project_decision['response'],
                        "session_id": session_id,
                        "current_phase": "project_decision",
                        "ready_for_jaa": False,
                        "missing_fields": [],
                        "state": state,
                        "needs_project_decision": True,
                        "suggested_project_id": project_decision.get('suggested_project_id')
                    }
                elif project_decision.get('action') == 'use_existing':
                    project_id = project_decision['project_id']
                    print(f"[CIA] Using existing project: {project_id}")
                elif project_decision.get('action') == 'create_new':
                    print(f"[CIA] Will create new project for: {project_decision.get('project_type')}")
                    # project_id remains None, will trigger new project creation
        
        # Set up project-aware memory context if project is specified
        cross_project_context = None
        agent_memory_config = None
        bid_card_context = None
        
        # Check if project_id is actually a bid card number
        if project_id and (project_id.startswith('IBC-') or project_id.startswith('BC-')):
            print(f"[CIA] Project ID is a bid card number: {project_id}")
            bid_card_context = await self._get_bid_card_details(project_id)
            if bid_card_context:
                print(f"[CIA] Loaded bid card context for {project_id}")
                # Add bid card to state for context awareness
                state['bid_card_context'] = bid_card_context
                state['bid_card_number'] = project_id
                state['active_bid_card'] = project_id  # PERSISTENT active card
                state['active_project_type'] = bid_card_context.get('project_type', 'project')
        
        if project_id and user_id != "00000000-0000-0000-0000-000000000000":
            try:
                # Initialize project-aware agent configuration
                agent_memory_config = await setup_project_aware_agent(user_id, project_id, session_id)
                cross_project_context = agent_memory_config.get('configurable', {}).get('cross_project_context', {})
                
                if cross_project_context:
                    print(f"[CIA] Loaded cross-project context with {len(cross_project_context.get('other_projects_summaries', []))} other projects")
                    
                    # Add project awareness to state
                    state['project_context'] = {
                        'project_id': project_id,
                        'has_other_projects': cross_project_context.get('other_projects_count', 0) > 0,
                        'user_preferences': cross_project_context.get('user_memories', {}),
                        'related_projects': cross_project_context.get('project_relationships', {})
                    }
            except Exception as e:
                print(f"[CIA] Warning: Could not load project context: {e}")
        
        # Upload images to storage first to avoid token limits
        if images and len(images) > 0:
            try:
                # Check if bucket exists
                try:
                    buckets = self.supabase.storage.list_buckets()
                    bucket_names = [b['name'] for b in buckets] if buckets else []
                    if 'project-images' not in bucket_names:
                        self.supabase.storage.create_bucket('project-images', {'public': True})
                except:
                    pass  # Bucket might already exist
                
                # Upload each image
                image_urls = []
                for idx, base64_image in enumerate(images):
                    try:
                        # Generate unique filename
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        file_name = f"{user_id}/{timestamp}_{idx}.jpg"
                        
                        # Decode and upload
                        import base64
                        image_data = base64.b64decode(base64_image)
                        
                        # Upload to storage
                        self.supabase.storage.from_('project-images').upload(
                            file_name, 
                            image_data,
                            {"content-type": "image/jpeg"}
                        )
                        
                        # Get public URL
                        url = self.supabase.storage.from_('project-images').get_public_url(file_name)
                        image_urls.append(url)
                        print(f"[CIA] Uploaded image {idx + 1} to: {url}")
                        
                    except Exception as e:
                        print(f"[CIA] Error uploading image {idx + 1}: {e}")
                        # For RLS errors, use local storage fallback
                        if "row-level security" in str(e) or "Unauthorized" in str(e):
                            print(f"[CIA] Storage RLS issue - using local storage fallback")
                            try:
                                # Use local file system
                                from pathlib import Path
                                import uuid
                                
                                # Create uploads directory
                                uploads_dir = Path(__file__).parent.parent.parent / 'static' / 'uploads' / user_id
                                uploads_dir.mkdir(parents=True, exist_ok=True)
                                
                                # Save image locally
                                filename = f"{timestamp}_{idx}_{uuid.uuid4().hex[:8]}.jpg"
                                file_path = uploads_dir / filename
                                
                                with open(file_path, 'wb') as f:
                                    f.write(image_data)
                                
                                # Create local URL
                                local_url = f"http://localhost:8008/static/uploads/{user_id}/{filename}"
                                image_urls.append(local_url)
                                print(f"[CIA] Saved to local storage: {local_url}")
                                
                            except Exception as local_e:
                                print(f"[CIA] Local storage also failed: {local_e}")
                                # Last resort - truncate base64 to avoid token limit
                                print(f"[CIA] WARNING: Keeping truncated base64")
                                image_urls.append(base64_image[:1000] + "...[truncated]")
                        continue
                
                # Replace base64 with URLs
                if image_urls:
                    images = image_urls
                    print(f"[CIA] Successfully uploaded {len(image_urls)} images to storage")
                else:
                    print(f"[CIA] Warning: Failed to upload images, continuing without them")
                    images = []
                    
            except Exception as e:
                print(f"[CIA] Error in image upload process: {e}")
                images = []  # Continue without images
        
        # Add user message
        state["messages"].append({
            "role": "user",
            "content": message,
            "images": images,
            "metadata": {"timestamp": datetime.now().isoformat()}
        })
        
        # Store images in collected_info
        if images and len(images) > 0:
            state['collected_info']['uploaded_photos'] = images
            print(f"[CIA] Added {len(images)} photos to collected_info")
        
        # Check for modification requests before generating response
        modification_result = await self._handle_modification_requests(user_id, message, state)
        if modification_result:
            return modification_result
        
        # Generate response
        start_time = time.time()
        
        if self.client:
            print("[CIA] Using Claude API for response...")
            response_text = await self._generate_claude_response(state)
        else:
            print("[CIA] Using demo response (no API client)...")
            response_text = self._generate_demo_response(state)
        
        response_time = time.time() - start_time
        print(f"[CIA] Response generated in {response_time:.2f} seconds")
        
        # Extract information using Claude Opus 4
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
        if agent_memory_config and project_id and user_id != "00000000-0000-0000-0000-000000000000":
            try:
                # Update memory with conversation insights
                await update_agent_memory_after_conversation(
                    user_id=user_id,
                    project_id=project_id,
                    session_id=session_id,
                    conversation_summary=response_text[:500],  # First 500 chars as summary
                    extracted_info=state["collected_info"],
                    user_preferences_discovered={
                        "budget_preference": state["collected_info"].get("budget_max"),
                        "timeline_preference": state["collected_info"].get("urgency"),
                        "communication_style": "detailed" if len(response_text) > 200 else "concise"
                    },
                    project_relationships={
                        "mentioned_other_projects": any(phrase in message.lower() for phrase in ["other project", "also need", "in addition to"]),
                        "project_type": state["collected_info"].get("project_type")
                    }
                )
                print(f"[CIA] Updated project memory for user {user_id}, project {project_id}")
            except Exception as e:
                print(f"[CIA] Warning: Could not update project memory: {e}")
        
        # Ensure active bid card persists in session
        if state.get('active_bid_card') and session_id:
            if session_id not in self.sessions:
                self.sessions[session_id] = {}
            self.sessions[session_id]['active_bid_card'] = state['active_bid_card']
            self.sessions[session_id]['active_project_type'] = state.get('active_project_type')
            print(f"[CIA] Persisted active bid card {state['active_bid_card']} in session")
        
        # Save session to memory and database
        self.sessions[session_id] = state
        
        # Save to database for JAA processing
        try:
            await self._save_conversation_to_database(state, user_id, session_id)
            print(f"[CIA] Saved conversation to database for JAA")
        except Exception as e:
            print(f"[CIA] Warning: Could not save to database: {e}")
        
        return {
            "response": response_text,
            "session_id": session_id,
            "current_phase": state["current_phase"],
            "ready_for_jaa": state["ready_for_jaa"],
            "missing_fields": state.get("missing_fields", []),
            "state": state,  # Include state for persistence
            "project_id": project_id  # Include project ID in response
        }
    
    def _create_new_session_with_instabids_structure(self, user_id: str, session_id: str) -> Dict[str, Any]:
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
    
    def _migrate_to_new_structure(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate existing state to new InstaBids structure"""
        if not state.get('collected_info'):
            return state
            
        old_info = state['collected_info']
        
        # Create new structure
        new_info = {
            # CORE PROJECT INFO - migrate from old
            "project_type": old_info.get('project_type'),
            "service_type": self._classify_service_type_from_old_data(old_info),
            "project_description": old_info.get('project_description'),
            
            # CONTEXT & MOTIVATION
            "budget_context": self._derive_budget_context(old_info),
            "timeline_urgency": self._map_old_urgency(old_info.get('urgency')),
            "urgency_reason": None,
            "location_zip": self._extract_zip_from_address(old_info.get('address')),
            
            # SMART OPPORTUNITIES - new fields
            "group_bidding_potential": self._assess_group_bidding_from_project_type(old_info.get('project_type')),
            "group_bidding_interest": None,
            "property_context": old_info.get('property_type'),
            
            # SUPPORTING INFO
            "material_preferences": old_info.get('material_preferences'),
            "uploaded_photos": old_info.get('uploaded_photos', []),
            "photo_analyses": old_info.get('photo_analyses', []),
            "special_requirements": old_info.get('special_requirements'),
            
            # INTERNAL SCORING - calculate from existing data
            "intention_score": self._calculate_intention_from_old_data(old_info),
            
            # LEGACY COMPATIBILITY - preserve
            "address": old_info.get('address'),
            "property_type": old_info.get('property_type'),
            "timeline_start": old_info.get('timeline_start'),
            "budget_min": old_info.get('budget_min'),
            "budget_max": old_info.get('budget_max'),
            "urgency": old_info.get('urgency')
        }
        
        state['collected_info'] = new_info
        state['missing_fields'] = REQUIRED_FIELDS_MINIMAL.copy()
        
        # Add InstaBids tracking if missing
        if 'instabids_value_mentioned' not in state:
            state['instabids_value_mentioned'] = False
        if 'group_bidding_discussed' not in state:
            state['group_bidding_discussed'] = False
            
        return state
    
    async def _generate_claude_response(self, state: Dict[str, Any]) -> str:
        """Generate response using Claude Opus 4 API"""
        print(f"[CIA] _generate_claude_response called")
        print(f"[CIA] Has bid_card_context: {'bid_card_context' in state}")
        if 'bid_card_context' in state:
            print(f"[CIA] Bid card number: {state['bid_card_context'].get('bid_card_number')}")
        
        messages = []
        
        # Add conversation context
        total_messages = len(state["messages"])
        
        # If long conversation, add a simple summary of key facts
        if total_messages > 20:
            # Build a quick context summary from collected info
            context_summary = "Earlier in this conversation:\n"
            
            # Add key project details if available
            if state.get('collected_info'):
                info = state['collected_info']
                if info.get('project_type'):
                    context_summary += f"- Project type: {info['project_type']}\n"
                if info.get('budget_max'):
                    context_summary += f"- Budget discussed: ${info.get('budget_min', 0):,} - ${info['budget_max']:,}\n"
                if info.get('timeline'):
                    context_summary += f"- Timeline: {info['timeline']}\n"
                if info.get('material_preferences'):
                    context_summary += f"- Materials: {', '.join(info['material_preferences'])}\n"
                if info.get('special_requirements'):
                    context_summary += f"- Special requirements: {', '.join(info['special_requirements'])}\n"
            
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
                    
                    for image_data in msg["images"]:
                        if image_data.startswith("data:image/"):
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
                    
                    messages.append({
                        "role": "user",
                        "content": content
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
        system_prompt = NEW_SYSTEM_PROMPT
        
        # Add active bid card context if available
        if state.get('active_bid_card'):
            # Always refresh bid card details to get latest updates
            fresh_bid_card = await self._get_bid_card_details(state['active_bid_card'])
            if fresh_bid_card:
                state['bid_card_context'] = fresh_bid_card
            
            bid_card = state.get('bid_card_context', {})
            print(f"[CIA] Adding active bid card context to prompt: {state['active_bid_card']}")
            bid_info = f"\n\n🎯 ACTIVE PROJECT CONTEXT - YOU ARE CURRENTLY WORKING ON THIS PROJECT:"
            bid_info += f"\nBid Card: {state['active_bid_card']}"
            bid_info += f"\nProject Type: {bid_card.get('project_type', 'Unknown')}"
            bid_info += f"\nCurrent Budget: ${bid_card.get('budget_min', 0):,} - ${bid_card.get('budget_max', 0):,}"
            bid_info += f"\nUrgency: {bid_card.get('urgency_level', 'Unknown')}"
            bid_info += f"\nContractors Needed: {bid_card.get('contractor_count_needed', 0)}"
            bid_info += f"\n\nIMPORTANT: Assume ALL questions and modifications relate to THIS project unless the user explicitly mentions a different project."
            
            # Add bid document details if available
            if bid_card.get('bid_document'):
                doc = bid_card['bid_document']
                if doc.get('all_extracted_data'):
                    data = doc['all_extracted_data']
                    if data.get('project_description'):
                        bid_info += f"\nProject Description: {data['project_description']}"
                    if data.get('location'):
                        loc = data['location']
                        location_str = loc.get('city') or loc.get('address') or loc.get('full_location') or 'Unknown'
                        bid_info += f"\nLocation: {location_str}"
                    if data.get('material_preferences'):
                        bid_info += f"\nMaterial Preferences: {', '.join(data['material_preferences'])}"
                    if data.get('special_requirements'):
                        bid_info += f"\nSpecial Requirements: {', '.join(data['special_requirements'])}"
            
            bid_info += f"\n\nThe user is asking about modifying this specific bid card. Acknowledge the project details and help them with their modifications."
            system_prompt += bid_info
        
        # Add user's project summaries for general conversation context
        if state.get('user_project_summaries'):
            summaries = state['user_project_summaries']
            projects_info = []
            for i, summary in enumerate(summaries):
                project_info = f"Project {i+1}: {summary.get('project_title', 'Unknown')}"
                project_info += f" ({summary.get('project_type', 'Unknown type')})"
                project_info += f" - Status: {summary.get('status', 'Unknown')}"
                project_info += f" - Budget: {summary.get('budget_range', 'Not specified')}"
                if summary.get('timeline'):
                    project_info += f" - Timeline: {summary['timeline']}"
                if summary.get('key_features'):
                    features = ', '.join(summary['key_features'][:3])  # First 3 features
                    project_info += f" - Features: {features}"
                projects_info.append(project_info)
            
            system_prompt += f"\n\nUSER'S CURRENT PROJECTS:\n{chr(10).join(projects_info)}"
            system_prompt += "\n\nWhen the user asks about their projects, reference these specific details to show you remember their work."
        
        # Add project awareness to system prompt if available
        if state.get('project_context'):
            project_ctx = state['project_context']
            
            # Add user preferences from memory
            if project_ctx.get('user_preferences'):
                user_prefs = project_ctx['user_preferences']
                if user_prefs.get('communication_preferences'):
                    comm_style = user_prefs['communication_preferences'].get('preferred_communication_style', 'detailed')
                    system_prompt += f"\n\nUser Communication Preference: {comm_style}"
                
                if user_prefs.get('budget_preferences'):
                    budget_info = user_prefs['budget_preferences']
                    if budget_info.get('recent_budget_ranges'):
                        recent_budgets = budget_info['recent_budget_ranges'][-3:]  # Last 3
                        system_prompt += f"\n\nUser's Recent Budget Ranges: {recent_budgets}"
            
            # Add related projects context
            if project_ctx.get('related_projects', {}).get('related_projects'):
                related = project_ctx['related_projects']['related_projects'][:2]  # Top 2
                related_info = []
                for proj in related:
                    related_info.append(f"{proj['title']} ({proj['category']})")
                system_prompt += f"\n\nUser's Other Projects: {', '.join(related_info)}"
                
                # Add analysis for intelligent questions
                analysis = project_ctx['related_projects'].get('analysis', '')
                if analysis:
                    system_prompt += f"\n\nProject Context: {analysis}"
        
        system_prompt += "\n\n" + get_conversation_prompt(
            state["current_phase"],
            {"collected_info": state["collected_info"], "missing_fields": state.get("missing_fields", [])}
        )
        
        try:
            print("[CIA] Calling Claude API...")
            response = self.client.messages.create(
                model="claude-opus-4-20250514",  # Updated to Claude Opus 4
                max_tokens=1000,
                temperature=0.7,
                system=system_prompt,
                messages=messages
            )
            print("[CIA] Claude API call successful")
            return response.content[0].text
        except Exception as e:
            print(f"[CIA ERROR] Claude API error: {e}")
            print(f"[CIA ERROR] Error type: {type(e).__name__}")
            print("[CIA] Falling back to demo response")
            return self._generate_demo_response(state)
    
    def _generate_demo_response(self, state: Dict[str, Any]) -> str:
        """Generate intelligent responses without API"""
        # Add artificial delay to simulate API call
        time.sleep(0.5)
        
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
    
    def _ask_for_details_or_photos(self, collected: Dict) -> str:
        """Ask for more details or photos"""
        if not collected.get("uploaded_photos"):
            return "Could you share some photos of the current space? This really helps contractors provide accurate bids."
        else:
            return "Is there anything else about your project you'd like me to know? Any specific concerns or must-have features?"
    
    async def _extract_and_update_info(self, state: Dict[str, Any], message: str) -> None:
        """Extract information using Claude Opus 4 intelligence"""
        collected = state["collected_info"]
        
        # Use Claude Opus 4 for intelligent information extraction
        if self.client:
            try:
                extracted_info = await self._claude_extract_information(message, collected)
                
                # Update collected info with extracted data
                for key, value in extracted_info.items():
                    if value and not collected.get(key):  # Only update if we don't have it yet
                        collected[key] = value
                        print(f"[CIA] Extracted {key}: {value}")
                
            except Exception as e:
                print(f"[CIA] Claude extraction failed: {e}, falling back to basic extraction")
                self._basic_extract_and_update_info(state, message)
        else:
            # Fallback to basic extraction
            self._basic_extract_and_update_info(state, message)
        
        # Update state
        state["collected_info"] = collected

    async def _claude_extract_information(self, message: str, existing_info: Dict) -> Dict[str, Any]:
        """Use Claude Opus 4 to intelligently extract InstaBids project information"""
        
        extraction_prompt = f"""
You are an expert InstaBids information extraction agent. Extract project information from this user message using the NEW InstaBids 12 data points structure.

EXISTING INFO: {json.dumps(existing_info, indent=2)}

USER MESSAGE: "{message}"

Extract the following InstaBids-focused information (return "null" if not found):

{{
    // CORE PROJECT INFO (1-3)
    "project_type": "high-level category (lawn care, roofing, kitchen remodel, etc.)",
    "service_type": "installation|repair|ongoing_service|handyman|appliance_repair|labor_only",
    "project_description": "detailed work needed and current situation",
    
    // CONTEXT & MOTIVATION (4-6) 
    "budget_context": "has_quotes|has_budget_range|exploring_options|dream_project|not_discussed",
    "timeline_urgency": "emergency|urgent|flexible|planning",
    "urgency_reason": "WHY timeline exists (HOA deadline, damage, selling house, etc.)",
    "location_zip": "zip code only (not full address unless offered)",
    
    // SMART OPPORTUNITIES (7-8)
    "group_bidding_potential": true/false,
    "group_bidding_interest": "user's interest in group pricing if mentioned",
    "property_context": "only if relevant (large property, access issues, etc.)",
    
    // SUPPORTING INFO (9-11)
    "material_preferences": "only if mentioned naturally",
    "special_requirements": "permits, HOA, access constraints, timing restrictions",
    
    // INTERNAL SCORING (12)
    "intention_score": 1-10,
    
    // LEGACY COMPATIBILITY
    "budget_min": "minimum budget as number if specific amount mentioned",
    "budget_max": "maximum budget as number if specific amount mentioned",
    "address": "full address if provided (prefer zip only)",
    "property_type": "house, condo, apartment, etc."
}}

SERVICE TYPE CLASSIFICATION:
- INSTALLATION: "new", "install", "replace", "remodel", "renovation", "build", "putting in"
- REPAIR: "repair", "fix", "broken", "damaged", "not working", "problem", "crack", "leak"
- ONGOING_SERVICE: "weekly", "monthly", "regular", "maintenance", "cleaning", "service", "every"
- HANDYMAN: "small job", "quick fix", "help with", "handyman", "odd job", "minor", "simple"
- APPLIANCE_REPAIR: "washer", "dryer", "dishwasher", "refrigerator", "oven", "microwave", "ac unit"
- LABOR_ONLY: "labor only", "just need someone", "help moving", "need muscle", "no materials"

GROUP BIDDING ASSESSMENT:
- Consider: Is this standardized work? Could neighbors benefit? Is timeline flexible?
- Good candidates: roofing, lawn care, driveway, fence, exterior painting, pressure washing
- NOT good: emergency repairs, custom work, interior personal spaces

INTENTION SCORE (1-10):
- High (8-10): Specific timeline, has budget, uploaded photos, mentions urgency
- Medium (5-7): General timeline, exploring pricing, has some details
- Low (1-4): "someday", "maybe", "just looking", no timeline

BUDGET CONTEXT INTELLIGENCE:
- Don't force budget discussion - understand their context
- "Got quotes" = has_quotes, "Rough idea" = exploring_options
- "Have range in mind" = has_budget_range, "Dream project" = dream_project

ONLY extract information clearly stated or strongly implied. Focus on understanding intent and motivation.
Return valid JSON only.
"""

        try:
            response = self.client.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=1000,
                temperature=0.1,
                messages=[{"role": "user", "content": extraction_prompt}]
            )
            
            response_text = response.content[0].text
            
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                extracted = json.loads(json_str)
                
                # Clean null values
                return {k: v for k, v in extracted.items() if v not in [None, "null", "", "not found"]}
            else:
                print(f"[CIA] Could not extract JSON from Claude response")
                return {}
                
        except Exception as e:
            print(f"[CIA] Claude information extraction failed: {e}")
            return {}
    
    async def _determine_project_intent(self, user_id: str, message: str) -> Optional[Dict[str, Any]]:
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

            response = self.client.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=400,
                temperature=0.1,
                messages=[{"role": "user", "content": intent_prompt}]
            )
            
            response_text = response.content[0].text
            
            # Extract JSON
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                decision = json.loads(json_str)
                
                # Map project_id if using existing
                if decision.get('action') == 'use_existing' and summaries:
                    # For demo, use first project - in production, match by type/description
                    decision['project_id'] = summaries[0].get('project_id')
                
                return decision
            
            return None
            
        except Exception as e:
            print(f"[CIA] Project intent determination failed: {e}")
            return None
    
    def _demo_project_intent(self, summaries: List[Dict], message: str) -> Dict[str, Any]:
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

    def _basic_extract_and_update_info(self, state: Dict[str, Any], message: str) -> None:
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
        if not collected.get("budget_min") and ('budget' in message_lower or 'spend' in message_lower or '$' in message):
            range_pattern = r'\$?(\d{1,3}(?:,\d{3})*)\s*(?:-|to|up to)\s*\$?(\d{1,3}(?:,\d{3})*)'
            range_match = re.search(range_pattern, message)
            
            if range_match:
                collected["budget_min"] = int(range_match.group(1).replace(',', ''))
                collected["budget_max"] = int(range_match.group(2).replace(',', ''))
                print(f"[CIA] Extracted budget range: ${collected['budget_min']}-${collected['budget_max']}")
        
        # Basic urgency detection
        if "emergency" in message_lower or "asap" in message_lower or "tomorrow" in message_lower:
            collected["urgency"] = "emergency"
        elif "urgent" in message_lower or "soon" in message_lower or "quickly" in message_lower:
            collected["urgency"] = "urgent"
        
        # Basic address extraction
        if not collected.get("address"):
            # Look for zip codes and city/state patterns
            zip_match = re.search(r'\b(\d{5})\b', message)
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
    
    def _update_state_status(self, state: Dict[str, Any]) -> None:
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
    
    async def _handle_modification_requests(self, user_id: str, message: str, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle bid card modification requests through CIA orchestration"""
        
        # Use Claude Opus 4 to intelligently detect modifications
        modification_analysis = await self._analyze_modification_with_claude(message, state)
        
        if not modification_analysis.get('is_modification', False):
            return None  # Not a modification request
        
        print(f"[CIA] Claude detected modification request: {message}")
        print(f"[CIA] Claude analysis: {modification_analysis}")
        
        # Extract modifications and project type from Claude's analysis
        modifications = modification_analysis.get('modifications', {})
        project_type = modification_analysis.get('project_type')
        confidence = modification_analysis.get('confidence', 0)
        
        if confidence < 0.8:
            print(f"[CIA] Claude low confidence modification: {confidence}")
            return None
        
        try:
            # Create modification analysis in expected format
            modification_analysis = {
                'is_modification': True,
                'project_type': project_type,
                'modifications': modifications,
                'confidence': confidence
            }
            
            print(f"[CIA] Modification analysis result: {modification_analysis}")
            
            # Get the bid card to modify
            bid_card_number = modification_analysis.get('bid_card_number')
            
            # ALWAYS use active bid card if we have one
            if state.get('active_bid_card'):
                bid_card_number = state['active_bid_card']
                print(f"[CIA] Using ACTIVE bid card from session: {bid_card_number}")
            elif not bid_card_number and state.get('bid_card_number'):
                bid_card_number = state['bid_card_number']
                print(f"[CIA] Using bid card from context: {bid_card_number}")
            
            if not bid_card_number:
                # Only search if we have no active context
                project_type_to_find = modification_analysis.get('project_type', '')
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
                for key in ['budget_min', 'budget_max', 'materials', 'timeline', 'urgency_level']
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
            result = await self._apply_bid_card_modification(bid_card_number, modification_analysis.get('modifications', {}))
            
            if result.get('success'):
                # Add modification to conversation history
                modification_note = f"[MODIFICATION APPLIED] Updated bid card {bid_card_number}: {', '.join(result.get('modifications_applied', []))}"
                state["messages"].append({
                    "role": "system",
                    "content": modification_note,
                    "metadata": {"type": "modification_log", "timestamp": datetime.now().isoformat()}
                })
                
                # Update collected info with modifications
                if 'collected_info' not in state:
                    state['collected_info'] = {}
                    
                modifications = modification_analysis.get('modifications', {})
                if 'budget_min' in modifications:
                    state['collected_info']['budget_min'] = modifications['budget_min']
                if 'budget_max' in modifications:
                    state['collected_info']['budget_max'] = modifications['budget_max']
                if 'timeline' in modifications:
                    state['collected_info']['timeline_start'] = modifications['timeline']
                if 'materials' in modifications:
                    state['collected_info']['materials_preferences'] = modifications['materials']
                
                # Get the actual project type from the bid card
                project_type_display = modification_analysis.get('project_type', 'project')
                if not project_type_display or project_type_display == 'None':
                    # Try to get from the bid card result
                    if result.get('original_card', {}).get('project_type'):
                        project_type_display = result['original_card']['project_type']
                    else:
                        project_type_display = 'project'
                
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
    
    async def _analyze_modification_intent(self, user_id: str, message: str) -> Optional[Dict[str, Any]]:
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

            response = self.client.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=600,
                temperature=0.1,
                messages=[{"role": "user", "content": modification_prompt}]
            )
            
            response_text = response.content[0].text
            
            # Extract JSON
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                analysis = json.loads(json_str)
                
                if analysis.get('confidence', 0) >= 0.7:
                    return analysis
                    
            return None
            
        except Exception as e:
            print(f"[CIA] Error analyzing modification intent: {e}")
            return None
    
    async def _find_user_bid_cards(self, user_id: str) -> List[Dict[str, Any]]:
        """Find all bid cards for a user through conversations or direct user_id"""
        try:
            from database_simple import db
            
            # Get bid cards through conversations only (bid_cards table doesn't have user_id column)
            # Method 1: Get through conversations
            conversations = db.client.table('agent_conversations').select('thread_id').eq('user_id', user_id).execute()
            
            if conversations.data:
                thread_ids = [c['thread_id'] for c in conversations.data]
                thread_cards = db.client.table('bid_cards').select('*').in_('cia_thread_id', thread_ids).order('created_at', desc=True).execute()
            else:
                thread_cards = {'data': []}
            
            # Return thread cards if found
            if thread_cards.data:
                print(f"[CIA] Found {len(thread_cards.data)} bid cards for user through conversations")
                return thread_cards.data
            else:
                print(f"[CIA] No bid cards found for user")
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
        if project_type and project_type != 'None':
            filtered = [bc for bc in bid_cards if project_type.lower() in bc.get('project_type', '').lower()]
            if filtered:
                return filtered[0]['bid_card_number']
        
        # Return most recent
        return bid_cards[0]['bid_card_number']
    
    async def _get_bid_card_details(self, bid_card_number: str) -> Dict[str, Any]:
        """Get existing bid card details for validation"""
        try:
            from database_simple import db
            result = db.client.table('bid_cards').select('*').eq('bid_card_number', bid_card_number).single().execute()
            return result.data if result.data else {}
        except Exception as e:
            print(f"[CIA] Error getting bid card details: {e}")
            return {}
    
    async def _apply_bid_card_modification(self, bid_card_number: str, modifications: Dict[str, Any]) -> Dict[str, Any]:
        """Apply modifications to bid card using Intelligent JAA agent"""
        
        try:
            from database_simple import db
            print(f"[CIA] Applying modifications to bid card {bid_card_number}: {modifications}")
            
            # Get current bid card details
            bid_card_result = db.client.table('bid_cards').select('*').eq('bid_card_number', bid_card_number).execute()
            
            if not bid_card_result.data:
                return {'success': False, 'error': f'Bid card {bid_card_number} not found'}
            
            current_bid_card = bid_card_result.data[0]
            
            # Apply modifications directly to bid card record
            updates = {}
            
            # Map CIA modifications to database fields
            if modifications.get('budget_min') is not None:
                updates['budget_min'] = int(modifications['budget_min'])
            if modifications.get('budget_max') is not None:
                updates['budget_max'] = int(modifications['budget_max'])
            if modifications.get('urgency_level'):
                updates['urgency_level'] = modifications['urgency_level']
            if modifications.get('timeline'):
                # Update bid_document with timeline info
                bid_doc = current_bid_card.get('bid_document', {})
                bid_doc['timeline_updated'] = modifications['timeline']
                bid_doc['last_modified'] = datetime.now().isoformat()
                updates['bid_document'] = bid_doc
            
            if updates:
                # Update the bid card in database
                update_result = db.client.table('bid_cards').update(updates).eq('bid_card_number', bid_card_number).execute()
                
                if update_result.data:
                    print(f"[CIA] Successfully updated bid card {bid_card_number}")
                    return {
                        'success': True, 
                        'bid_card_number': bid_card_number,
                        'modifications_applied': updates,
                        'updated_bid_card': update_result.data[0]
                    }
                else:
                    return {'success': False, 'error': 'Database update failed'}
            else:
                return {'success': False, 'error': 'No valid modifications provided'}
                
        except Exception as e:
            print(f"[CIA] Error applying bid card modification: {e}")
            return {'success': False, 'error': str(e)}
    
    def _format_changes_summary(self, applied_fields: List[str], modifications: Dict[str, Any]) -> str:
        """Format a human-readable summary of changes"""
        
        summaries = []
        
        for field in applied_fields:
            if field == 'materials' and 'materials' in modifications:
                materials = modifications['materials']
                if isinstance(materials, list):
                    summaries.append(f"materials updated to {', '.join(materials[:2])}")
                else:
                    summaries.append(f"materials updated to {materials}")
                    
            elif field == 'budget_min' or field == 'budget_max':
                if 'budget_min' in modifications or 'budget_max' in modifications:
                    min_budget = modifications.get('budget_min', '')
                    max_budget = modifications.get('budget_max', '')
                    if min_budget and max_budget:
                        summaries.append(f"budget updated to ${min_budget:,}-${max_budget:,}")
                    elif max_budget:
                        summaries.append(f"budget updated to ${max_budget:,}")
                        
            elif field == 'timeline' and 'timeline' in modifications:
                summaries.append(f"timeline updated to {modifications['timeline']}")
                
            elif field == 'urgency_level' and 'urgency_level' in modifications:
                summaries.append(f"urgency changed to {modifications['urgency_level']}")
                
            elif field == 'project_description' and 'project_description' in modifications:
                summaries.append("project description updated")
                
            elif field == 'special_notes' and 'special_notes' in modifications:
                summaries.append("special requirements updated")
        
        return '; '.join(summaries) if summaries else "specifications updated"
    
    async def _analyze_modification_with_claude(self, message: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Use Claude Opus 4 to intelligently analyze if this is a modification request"""
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
            
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                temperature=0.1,
                messages=[{
                    "role": "user", 
                    "content": analysis_prompt
                }]
            )
            
            # Parse Claude's JSON response
            import json
            response_text = response.content[0].text
            
            # Strip markdown code blocks if present
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                if json_end > json_start:
                    response_text = response_text[json_start:json_end].strip()
            
            # Try to extract JSON from response
            try:
                # First try direct parsing
                analysis = json.loads(response_text)
                print(f"[CIA] Claude modification analysis: {analysis}")
                return analysis
            except json.JSONDecodeError:
                # Try to find JSON in the response
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    try:
                        json_str = response_text[json_start:json_end]
                        analysis = json.loads(json_str)
                        print(f"[CIA] Claude modification analysis: {analysis}")
                        return analysis
                    except:
                        pass
                
                print(f"[CIA] Could not parse Claude response: {response_text[:200]}...")
                return {"is_modification": False, "confidence": 0.0}
                
        except Exception as e:
            print(f"[CIA] Error in Claude modification analysis: {e}")
            return {"is_modification": False, "confidence": 0.0}
    
    def _classify_service_type_from_old_data(self, old_info: Dict[str, Any]) -> Optional[str]:
        """Classify service type from old data structure"""
        project_type = old_info.get('project_type', '').lower()
        description = old_info.get('project_description', '').lower()
        combined_text = f"{project_type} {description}"
        
        # Use SERVICE_TYPE_KEYWORDS to classify
        for service_type, keywords in SERVICE_TYPE_KEYWORDS.items():
            if any(keyword in combined_text for keyword in keywords):
                return service_type
                
        return "installation"  # Default
    
    def _derive_budget_context(self, old_info: Dict[str, Any]) -> Optional[str]:
        """Derive budget context from old budget data"""
        if old_info.get('budget_min') and old_info.get('budget_max'):
            return "has_budget_range"
        elif old_info.get('budget_min') or old_info.get('budget_max'):
            return "has_budget_range"
        else:
            return "not_discussed"
    
    def _map_old_urgency(self, old_urgency: Optional[str]) -> Optional[str]:
        """Map old urgency to new timeline_urgency"""
        if not old_urgency:
            return None
            
        mapping = {
            'emergency': 'emergency',
            'urgent': 'urgent',
            'flexible': 'flexible',
            'low': 'planning',
            'medium': 'flexible',
            'high': 'urgent'
        }
        return mapping.get(old_urgency.lower(), 'flexible')
    
    def _extract_zip_from_address(self, address: Optional[str]) -> Optional[str]:
        """Extract zip code from full address"""
        if not address:
            return None
            
        import re
        zip_match = re.search(r'\b(\d{5})\b', address)
        return zip_match.group(1) if zip_match else None
    
    def _assess_group_bidding_from_project_type(self, project_type: Optional[str]) -> Optional[bool]:
        """Assess group bidding potential from project type"""
        if not project_type:
            return None
            
        return any(group_type in project_type.lower() for group_type in GROUP_BIDDING_PROJECTS)
    
    def _calculate_intention_from_old_data(self, old_info: Dict[str, Any]) -> Optional[int]:
        """Calculate intention score from old data"""
        score = 5  # Base score
        
        # Budget readiness
        if old_info.get('budget_min') or old_info.get('budget_max'):
            score += INTENTION_SCORE_FACTORS.get('budget_ready', 0)
        
        # Urgency
        urgency_value = old_info.get('urgency')
        urgency = urgency_value.lower() if urgency_value else ''
        if urgency in ['emergency', 'urgent']:
            score += INTENTION_SCORE_FACTORS.get('high_urgency', 0)
        
        # Photos uploaded
        if old_info.get('uploaded_photos'):
            score += INTENTION_SCORE_FACTORS.get('photos_uploaded', 0)
        
        # Detailed description
        if old_info.get('project_description') and len(old_info['project_description']) > 50:
            score += INTENTION_SCORE_FACTORS.get('detailed_description', 0)
        
        return max(1, min(10, score))
    
    def _apply_instabids_intelligence(self, state: Dict[str, Any]) -> None:
        """Apply InstaBids-specific intelligence to conversation state"""
        collected = state['collected_info']
        
        # SMART SERVICE TYPE CLASSIFICATION
        if not collected.get('service_type') and collected.get('project_type'):
            collected['service_type'] = self._intelligent_service_classification(
                collected.get('project_description', ''),
                collected.get('project_type', ''),
                state.get('messages', [])
            )
        
        # GROUP BIDDING ASSESSMENT
        if collected.get('service_type') and collected.get('project_type'):
            if not collected.get('group_bidding_potential'):
                collected['group_bidding_potential'] = self._assess_group_bidding_potential(
                    collected['project_type'],
                    collected['service_type'],
                    collected.get('timeline_urgency')
                )
        
        # INTENTION SCORE CALCULATION
        if not collected.get('intention_score'):
            collected['intention_score'] = self._calculate_intention_score_intelligent(
                collected,
                state.get('messages', [])
            )
        
        # BUDGET CONTEXT INTELLIGENCE
        if not collected.get('budget_context'):
            collected['budget_context'] = self._derive_budget_context_intelligent(
                state.get('messages', [])
            )
    
    def _intelligent_service_classification(self, description: str, project_type: str, messages: List[Dict]) -> Optional[str]:
        """Intelligently classify service type using context"""
        # Combine all text for analysis
        all_text = f"{description} {project_type}".lower()
        for msg in messages[-3:]:  # Last 3 messages
            if msg.get('role') == 'user':
                all_text += f" {msg.get('content', '')}".lower()
        
        # Score each service type
        scores = {}
        for service_type, keywords in SERVICE_TYPE_KEYWORDS.items():
            scores[service_type] = sum(1 for keyword in keywords if keyword in all_text)
        
        # Return highest scoring service type
        if scores and max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        # Default logic based on project type
        if 'care' in project_type or 'clean' in project_type:
            return 'ongoing_service'
        elif 'repair' in all_text or 'fix' in all_text:
            return 'repair'
        else:
            return 'installation'
    
    def _assess_group_bidding_potential(self, project_type: str, service_type: str, timeline_urgency: Optional[str]) -> bool:
        """Assess if project is good for group bidding"""
        # Must not be emergency/urgent
        if timeline_urgency in ['emergency', 'urgent']:
            return False
        
        # Must be standardized work type
        return any(group_type in project_type.lower() for group_type in GROUP_BIDDING_PROJECTS)
    
    def _calculate_intention_score_intelligent(self, collected: Dict[str, Any], messages: List[Dict]) -> int:
        """Calculate intelligent intention score 1-10"""
        score = 5  # Base neutral
        
        # Timeline urgency
        timeline_urgency = collected.get('timeline_urgency')
        if timeline_urgency == 'emergency':
            score += INTENTION_SCORE_FACTORS.get('high_urgency', 0)
        elif timeline_urgency == 'urgent':
            score += INTENTION_SCORE_FACTORS.get('specific_timeline', 0)
        
        # Budget readiness
        if collected.get('budget_min') or collected.get('budget_max'):
            score += INTENTION_SCORE_FACTORS.get('budget_ready', 0)
        
        # Photos uploaded
        if collected.get('uploaded_photos'):
            score += INTENTION_SCORE_FACTORS.get('photos_uploaded', 0)
        
        # Detailed description
        if collected.get('project_description') and len(collected['project_description']) > 100:
            score += INTENTION_SCORE_FACTORS.get('detailed_description', 0)
        
        # Analyze message content for intention signals
        recent_messages = [msg.get('content', '').lower() for msg in messages[-3:] if msg.get('role') == 'user']
        combined_text = ' '.join(recent_messages)
        
        # Positive signals
        if any(phrase in combined_text for phrase in ['ready', 'need to', 'have to', 'must']):
            score += 1
        
        # Negative signals
        if any(phrase in combined_text for phrase in ['maybe', 'thinking', 'exploring', 'someday']):
            score += INTENTION_SCORE_FACTORS.get('exploring_only', 0)
        
        if 'future' in combined_text:
            score += INTENTION_SCORE_FACTORS.get('far_future', 0)
        
        return max(1, min(10, score))
    
    def _derive_budget_context_intelligent(self, messages: List[Dict]) -> str:
        """Derive budget context from conversation"""
        recent_messages = [msg.get('content', '').lower() for msg in messages[-5:] if msg.get('role') == 'user']
        combined_text = ' '.join(recent_messages)
        
        if any(phrase in combined_text for phrase in ['got quote', 'already quoted', 'contractor said']):
            return 'has_quotes'
        elif any(phrase in combined_text for phrase in ['budget', '$', 'cost', 'price', 'spend']):
            return 'has_budget_range'
        elif any(phrase in combined_text for phrase in ['explore', 'looking at', 'research', 'idea']):
            return 'exploring_options'
        elif any(phrase in combined_text for phrase in ['dream', 'someday', 'future', 'maybe']):
            return 'dream_project'
        else:
            return 'not_discussed'
    
    async def _generate_response_with_context(self, state: Dict[str, Any], user_id: str, message: str, session_id: str) -> Dict[str, Any]:
        """Generate a response using Claude API with full bid card context"""
        # Add the user message to state
        state["messages"].append({
            "role": "user",
            "content": message,
            "metadata": {"timestamp": datetime.now().isoformat()}
        })
        
        # Generate response using Claude
        response_text = await self._generate_claude_response(state)
        
        # Add assistant response to state
        state["messages"].append({
            "role": "assistant",
            "content": response_text,
            "metadata": {"timestamp": datetime.now().isoformat()}
        })
        
        # Save conversation
        await self._save_conversation_to_database(state, user_id, session_id)
        
        return {
            "response": response_text,
            "session_id": session_id,
            "current_phase": "conversation",
            "ready_for_jaa": False,
            "missing_fields": [],
            "state": state,
            "has_bid_card_context": True,
            "bid_card_number": state.get('bid_card_number')
        }
    
    async def _save_conversation_to_database(self, state: Dict[str, Any], user_id: str, session_id: str):
        """Save conversation state to database for JAA processing"""
        try:
            conversation_data = {
                'thread_id': session_id,
                'user_id': user_id,
                'agent_type': 'CIA',
                'state': json.dumps(state),
                'created_at': datetime.now().isoformat()
            }
            
            # Check if conversation already exists
            existing = self.supabase.table('agent_conversations').select("*").eq('thread_id', session_id).execute()
            
            if existing.data:
                # Update existing conversation
                result = self.supabase.table('agent_conversations').update(conversation_data).eq('thread_id', session_id).execute()
                print(f"[CIA] Updated existing conversation in database: {session_id}")
            else:
                # Insert new conversation
                result = self.supabase.table('agent_conversations').insert(conversation_data).execute()
                print(f"[CIA] Inserted new conversation to database: {session_id}")
                
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"[CIA] Error saving conversation to database: {e}")
            raise e