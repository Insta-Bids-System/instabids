"""
Bid Card Search Node for COIA LangGraph System
Integrates existing bid card API with COIA agents
"""
import logging
from datetime import datetime
from typing import Any

from langchain_core.messages import AIMessage

from .unified_state import UnifiedCoIAState


logger = logging.getLogger(__name__)


async def bid_card_search_node(state: UnifiedCoIAState) -> dict[str, Any]:
    """
    Search and display bid cards based on contractor profile and preferences
    Leverages existing bid card API system with memory persistence
    """

    logger.info("=== BID CARD SEARCH NODE ACTIVATED ===")

    # Extract search criteria from state with memory enhancement
    user_message = state["messages"][-1].content if state["messages"] else ""
    contractor_profile = state.get("contractor_profile", {})

    # Load additional data from persistent memory if contractor_id is available
    contractor_id = state.get("contractor_id")
    if contractor_id:
        logger.info(f"Using contractor ID from memory: {contractor_id}")
        # Enhance profile with stored memory data
        if state.get("research_findings"):
            research_data = state["research_findings"]
            if isinstance(research_data, dict):
                # Add research data to profile for better search
                contractor_profile.update({
                    "company_name": research_data.get("company_name"),
                    "service_areas": research_data.get("service_areas", []),
                    "specializations": research_data.get("services", [])
                })

    logger.info(f"Enhanced contractor profile for search: {list(contractor_profile.keys())}")

    # Parse search intent from message
    search_criteria = _extract_search_criteria(user_message, contractor_profile)

    # Call existing bid card search API
    bid_cards = await search_bid_cards(search_criteria)

    # Format response with bid cards
    response = _format_bid_card_response(bid_cards, search_criteria, contractor_profile)

    # Attach bid cards to state for frontend display
    bid_cards_attached = [_format_for_attachment(card) for card in bid_cards[:5]]

    # Update state
    return {
        "messages": [AIMessage(content=response)],
        "current_mode": "bid_card_search",
        "bid_cards_attached": bid_cards_attached,
        "tool_results": {
            "bid_card_search": {
                "total_found": len(bid_cards),
                "displayed": len(bid_cards_attached),
                "search_criteria": search_criteria
            }
        },
        "last_updated": datetime.utcnow().isoformat()
    }


def _extract_search_criteria(message: str, profile: dict[str, Any]) -> dict[str, Any]:
    """Extract search criteria from message and contractor profile with memory enhancement"""

    criteria = {}
    message_lower = message.lower()

    # Location-based search with memory enhancement
    if "near me" in message_lower or "in my area" in message_lower:
        # Use profile service areas from memory
        if profile.get("service_areas"):
            criteria["location_city"] = profile["service_areas"][0]
            logger.info(f"Using service area from memory: {profile['service_areas'][0]}")
        elif profile.get("city"):
            criteria["location_city"] = profile["city"]
        # Also add service radius if available
        if profile.get("service_radius_miles"):
            criteria["radius_miles"] = profile["service_radius_miles"]

    # Use contractor's preferred project types from memory
    if profile.get("preferred_project_types"):
        criteria["project_types"] = profile["preferred_project_types"]
        logger.info(f"Using preferred project types from memory: {profile['preferred_project_types']}")

    # Use contractor's minimum project size for budget filtering
    if profile.get("minimum_project_size"):
        criteria["budget_min"] = profile["minimum_project_size"]
        logger.info(f"Using minimum project size from memory: ${profile['minimum_project_size']}")

    # Budget extraction with profile override
    budget_keywords = {
        "under 1000": {"budget_max": 1000},
        "under 5000": {"budget_max": 5000},
        "under 10000": {"budget_max": 10000},
        "over 10000": {"budget_min": 10000},
        "budget": {}  # Will extract from profile
    }

    for keyword, budget in budget_keywords.items():
        if keyword in message_lower:
            criteria.update(budget)
            break

    # Project type extraction
    project_types = {
        "kitchen": ["kitchen remodel", "kitchen renovation"],
        "bathroom": ["bathroom remodel", "bathroom renovation"],
        "lawn": ["lawn care", "landscaping", "yard work"],
        "roofing": ["roof repair", "roof replacement"],
        "plumbing": ["plumbing", "pipe repair"],
        "electrical": ["electrical", "wiring"],
        "painting": ["interior painting", "exterior painting"],
        "flooring": ["flooring", "carpet", "hardwood"],
        "hvac": ["hvac", "heating", "cooling", "air conditioning"]
    }

    for key, types in project_types.items():
        if key in message_lower:
            criteria["project_types"] = types
            break

    # Use contractor specialties if no specific type mentioned
    if "project_types" not in criteria and profile.get("specialties"):
        criteria["project_types"] = profile["specialties"]

    # Timeline extraction
    if "urgent" in message_lower or "emergency" in message_lower:
        criteria["urgency_level"] = "emergency"
    elif "soon" in message_lower or "this week" in message_lower:
        criteria["urgency_level"] = "urgent"
    elif "flexible" in message_lower:
        criteria["urgency_level"] = "flexible"

    # Group bidding preference
    if "group" in message_lower or "save money" in message_lower:
        criteria["group_buying_eligible"] = True

    # Status filter - focus on active bid cards
    criteria["status"] = ["active", "collecting_bids", "generated"]

    logger.info(f"Extracted search criteria: {criteria}")
    return criteria


async def search_bid_cards(criteria: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Call the existing bid card search API
    This would integrate with routers/bid_card_api.py
    """

    try:
        # Import the actual search function from bid card API
        from routers.bid_card_api import search_bid_cards_handler

        # Prepare search request
        search_request = {
            "filters": criteria,
            "sort_by": "created_at",
            "sort_order": "desc",
            "limit": 20,
            "offset": 0
        }

        # Call the search handler
        results = await search_bid_cards_handler(search_request)

        if results and "bid_cards" in results:
            return results["bid_cards"]
        else:
            logger.warning("No bid cards found with criteria")
            return []

    except ImportError:
        # Fallback to mock data if API not available
        logger.warning("Bid card API not available, using mock data")
        return _get_mock_bid_cards(criteria)
    except Exception as e:
        logger.error(f"Error searching bid cards: {e}")
        return []


def _format_bid_card_response(bid_cards: list[dict[str, Any]], criteria: dict[str, Any], contractor_profile: dict[str, Any] = None) -> str:
    """Format bid cards into conversational response with personalization"""

    contractor_name = ""
    if contractor_profile and contractor_profile.get("company_name"):
        contractor_name = f", {contractor_profile['company_name']},"

    if not bid_cards:
        personalized_message = f"I couldn't find any active projects matching your criteria right now{contractor_name}. "

        # Add personalized suggestions based on profile
        if contractor_profile:
            if contractor_profile.get("service_areas"):
                personalized_message += f"I searched in your service area of {contractor_profile['service_areas'][0]}. "
            if contractor_profile.get("preferred_project_types"):
                types = ", ".join(contractor_profile["preferred_project_types"])
                personalized_message += f"I looked for your preferred project types: {types}. "

        return (
            personalized_message +
            "Would you like me to:\n"
            "1. Broaden the search parameters?\n"
            "2. Set up an alert for when matching projects become available?\n"
            "3. Help you create your own bid request?"
        )

    # Build response with personalization
    response_parts = []

    # Personalized header
    count = len(bid_cards)
    greeting = ""
    if contractor_name:
        greeting = contractor_name + " "

    if count == 1:
        response_parts.append(f"Great news{contractor_name}! I found 1 project that matches your expertise:")
    else:
        response_parts.append(f"Great news{contractor_name}! I found {count} projects that match your expertise:")

    # Display top 5 bid cards
    for i, card in enumerate(bid_cards[:5], 1):
        card_text = _format_single_bid_card(card, i)
        response_parts.append(card_text)

    # Footer with actions
    response_parts.append("\n**What would you like to do?**")
    response_parts.append("• Type 'more' to see additional projects")
    response_parts.append("• Type 'details [number]' to see full project details")
    response_parts.append("• Type 'bid [number]' to submit a bid")
    response_parts.append("• Type 'filter' to refine your search")

    # Add group bidding suggestion if applicable
    if any(card.get("group_buying_eligible") for card in bid_cards[:5]):
        response_parts.append("\n💡 **Tip**: Some of these projects are eligible for group bidding (15-25% savings)!")

    return "\n\n".join(response_parts)


def _format_single_bid_card(card: dict[str, Any], index: int) -> str:
    """Format a single bid card for display"""

    parts = [f"**{index}. {card.get('title', 'Untitled Project')}**"]

    # Location
    city = card.get("location_city", "Unknown")
    state = card.get("location_state", "")
    location = f"{city}, {state}" if state else city
    parts.append(f"📍 Location: {location}")

    # Budget
    budget_min = card.get("budget_min", 0)
    budget_max = card.get("budget_max", 0)
    if budget_max:
        parts.append(f"💰 Budget: ${budget_min:,} - ${budget_max:,}")
    elif budget_min:
        parts.append(f"💰 Budget: ${budget_min:,}+")

    # Timeline
    timeline = card.get("timeline", {})
    if timeline.get("start_date"):
        parts.append(f"📅 Start: {timeline['start_date']}")

    # Urgency
    urgency = card.get("urgency_level")
    if urgency == "emergency":
        parts.append("🚨 **EMERGENCY - Immediate response needed**")
    elif urgency == "urgent":
        parts.append("⚡ **URGENT - Quick turnaround required**")

    # Bid status
    bids_received = card.get("bids_received_count", 0)
    contractor_count = card.get("contractor_count_needed", 4)
    if bids_received < contractor_count:
        parts.append(f"🎯 Bids: {bids_received}/{contractor_count} (Still accepting bids)")
    else:
        parts.append(f"✅ Bids: {contractor_count}/{contractor_count} (Target met)")

    # Group buying
    if card.get("group_buying_eligible"):
        parts.append("👥 **Group Bidding Available** - Potential 15-25% savings")

    # Brief description
    if card.get("description"):
        desc = card["description"][:150]
        if len(card["description"]) > 150:
            desc += "..."
        parts.append(f"📝 {desc}")

    return "\n".join(parts)


def _format_for_attachment(card: dict[str, Any]) -> dict[str, Any]:
    """Format bid card for attachment to message (frontend display)"""

    return {
        "id": card.get("id"),
        "bid_card_number": card.get("bid_card_number"),
        "title": card.get("title", "Untitled Project"),
        "description": card.get("description", ""),
        "project_type": card.get("project_type"),
        "location_city": card.get("location_city"),
        "location_state": card.get("location_state"),
        "budget_min": card.get("budget_min"),
        "budget_max": card.get("budget_max"),
        "timeline": card.get("timeline", {}),
        "urgency_level": card.get("urgency_level"),
        "bids_received_count": card.get("bids_received_count", 0),
        "contractor_count_needed": card.get("contractor_count_needed", 4),
        "group_buying_eligible": card.get("group_buying_eligible", False),
        "status": card.get("status"),
        "created_at": card.get("created_at")
    }


def _get_mock_bid_cards(criteria: dict[str, Any]) -> list[dict[str, Any]]:
    """Return mock bid cards for testing"""

    mock_cards = [
        {
            "id": "mock-001",
            "bid_card_number": "BC-MOCK-001",
            "title": "Kitchen Remodel - Modern Update",
            "description": "Complete kitchen renovation including new cabinets, countertops, and appliances. Looking for experienced contractor with modern design expertise.",
            "project_type": "kitchen_remodel",
            "location_city": "Dallas",
            "location_state": "TX",
            "budget_min": 15000,
            "budget_max": 25000,
            "timeline": {"start_date": "2025-02-15", "duration": "4-6 weeks"},
            "urgency_level": "standard",
            "bids_received_count": 2,
            "contractor_count_needed": 4,
            "group_buying_eligible": True,
            "status": "collecting_bids",
            "created_at": "2025-01-30T10:00:00Z"
        },
        {
            "id": "mock-002",
            "bid_card_number": "BC-MOCK-002",
            "title": "Emergency Plumbing Repair",
            "description": "Urgent pipe burst repair needed. Water damage in basement. Need immediate response.",
            "project_type": "plumbing",
            "location_city": "Fort Worth",
            "location_state": "TX",
            "budget_min": 500,
            "budget_max": 2000,
            "timeline": {"start_date": "ASAP", "duration": "1-2 days"},
            "urgency_level": "emergency",
            "bids_received_count": 1,
            "contractor_count_needed": 3,
            "group_buying_eligible": False,
            "status": "collecting_bids",
            "created_at": "2025-01-30T14:30:00Z"
        },
        {
            "id": "mock-003",
            "bid_card_number": "BC-MOCK-003",
            "title": "Lawn Care Service - Monthly",
            "description": "Looking for reliable lawn care service. Weekly mowing, edging, and seasonal treatments.",
            "project_type": "lawn_care",
            "location_city": "Arlington",
            "location_state": "TX",
            "budget_min": 150,
            "budget_max": 200,
            "timeline": {"start_date": "2025-02-01", "duration": "Ongoing monthly"},
            "urgency_level": "flexible",
            "bids_received_count": 3,
            "contractor_count_needed": 4,
            "group_buying_eligible": True,
            "status": "collecting_bids",
            "created_at": "2025-01-29T09:00:00Z"
        }
    ]

    # Filter based on criteria
    filtered = mock_cards

    if criteria.get("project_types"):
        project_types = criteria["project_types"]
        filtered = [c for c in filtered if any(pt in c["project_type"] for pt in project_types)]

    if criteria.get("urgency_level"):
        filtered = [c for c in filtered if c["urgency_level"] == criteria["urgency_level"]]

    if criteria.get("budget_max"):
        filtered = [c for c in filtered if c["budget_min"] <= criteria["budget_max"]]

    return filtered
