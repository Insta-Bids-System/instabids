"""
Categorization Tool Handler - Connects OpenAI tool calls to database
Used by CIA and IRIS agents for intelligent project categorization
"""

import json
import logging
from typing import Dict, Any, Optional
from .project_types import (
    PROJECT_TYPE_MAPPING,
    get_project_scope,
    get_required_capabilities
)

logger = logging.getLogger(__name__)

# OpenAI Tool Definition
CATEGORIZATION_TOOL = {
    "type": "function",
    "function": {
        "name": "categorize_project",
        "description": "Categorize home improvement project - MUST pick service category and exact project type from predefined lists",
        "parameters": {
            "type": "object",
            "properties": {
                "service_category": {
                    "type": "string",
                    "enum": [
                        "Installation", "Repair", "Replacement", "Renovation", 
                        "Maintenance", "Ongoing", "Emergency", "Labor Only",
                        "Consultation", "Events", "Rentals", 
                        "Lifestyle & Wellness", "Professional/Digital", "AI Solutions"
                    ],
                    "description": "The primary type of service being requested"
                },
                "project_scope": {
                    "type": "string", 
                    "enum": ["single_trade", "multi_trade", "full_renovation"],
                    "description": "The complexity/scope level of the project"
                },
                "required_capabilities": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of specific trades, skills, or capabilities needed"
                },
                "normalized_project_type": {
                    "type": "string",
                    "enum": [
                        "ac_rental", "access_control_system_installation", "access_control_system_repair", "access_control_system_replacement", "accessibility_assessment",
                        "aging_in_place_modifications", "ai_security", "air_duct_cleaning", "air_quality_improvement", "allergy_reduction_improvements",
                        "annual_roof_inspection", "antenna_installation", "antenna_repair", "antenna_replacement", "appliance_installation",
                        "appliance_maintenance", "appliance_repair", "appliance_replacement", "architectural_consultation", "attic_renovation",
                        "audio_visual", "automated_systems", "automation", "awning_installation", "awning_repair",
                        "awning_replacement", "backup_battery_system_installation", "backup_battery_system_repair", "backup_battery_system_replacement", "basement_renovation",
                        "bathroom_fixture_installation", "bathroom_fixture_repair", "bathroom_fixture_replacement", "bathroom_renovation", "biweekly_pool_service",
                        "burst_pipe", "business_automation", "business_security_system", "cabinet_installation", "cabinet_repair",
                        "cabinet_replacement", "camera_system_installation", "camera_system_repair", "camera_system_replacement", "carbon_monoxide_detector_installation",
                        "carbon_monoxide_detector_repair", "carbon_monoxide_detector_replacement", "caulking_maintenance", "central_vacuum_installation", "central_vacuum_repair",
                        "central_vacuum_replacement", "chimney_cleaning", "cleanup", "closet_system_installation", "closet_system_repair",
                        "closet_system_replacement", "code_consultation", "color_consultation", "commercial_av_system", "commercial_cleaning",
                        "conference_room_setup", "construction_cleanup", "construction_equipment_rental", "contractor_consultation", "consultation",
                        "countertop_installation", "countertop_repair", "countertop_replacement", "data_cabling_installation", "data_cabling_repair",
                        "data_cabling_replacement", "data_center_setup", "deck_installation", "deck_renovation", "deck_repair",
                        "deck_replacement", "deck_staining", "demolition", "design_consultation", "digital_signage",
                        "door_installation", "door_repair", "door_replacement", "drainage_system_installation", "drainage_system_repair",
                        "drainage_system_replacement", "driveway_gate_operator_installation", "driveway_gate_operator_repair", "driveway_gate_operator_replacement", "driveway_installation",
                        "driveway_renovation", "driveway_repair", "driveway_replacement", "driveway_sealing", "drywall_installation",
                        "drywall_repair", "drywall_replacement", "dumpster_rental", "electrical_panel_installation", "electrical_panel_repair",
                        "electrical_panel_replacement", "electrical_repair", "elevator_or_lift_installation", "elevator_or_lift_repair", "elevator_or_lift_replacement",
                        "emergency_board_up", "emergency_chimney_repair", "emergency_electrical", "emergency_foundation", "emergency_garage_door",
                        "emergency_generator", "emergency_glass_repair", "emergency_hvac", "emergency_locksmith", "emergency_pest_control",
                        "emergency_plumbing", "emergency_roofing", "emergency_septic", "emergency_structural_repair", "emergency_tree_removal",
                        "emergency_water_heater", "emergency_well_pump", "energy_audit", "engineering_consultation", "equipment_rental",
                        "ergonomic_home_office", "estimate", "estate_sale_prep", "ev_charger_installation", "ev_charger_repair",
                        "ev_charger_replacement", "event_landscaping", "event_lighting", "excavation", "exterior_renovation",
                        "fence_installation", "fence_repair", "fence_replacement", "fence_staining", "fertilizer_application",
                        "filter_replacement", "fire_damage", "fire_pit_installation", "fire_pit_repair", "fire_pit_replacement",
                        "fire_sprinkler_installation", "fire_sprinkler_repair", "fire_sprinkler_replacement", "fireplace_installation", "fireplace_repair",
                        "fireplace_replacement", "flood_damage", "flooring_installation", "flooring_repair", "flooring_replacement",
                        "foundation_repair", "fountain_maintenance", "furniture_assembly", "garage_conversion", "garage_door_installation",
                        "garage_door_maintenance", "garage_door_repair", "garage_door_replacement", "gas_leak", "gazebo_installation",
                        "gazebo_repair", "gazebo_replacement", "general_labor", "generator_installation", "generator_maintenance",
                        "generator_repair", "generator_rental", "generator_replacement", "glass_shower_enclosure_installation", "glass_shower_enclosure_repair",
                        "glass_shower_enclosure_replacement", "greenhouse_installation", "greenhouse_repair", "greenhouse_replacement", "grounds_maintenance",
                        "grout_maintenance", "gutter_cleaning", "hauling", "heater_rental", "holiday_decoration_install",
                        "holiday_decoration_maintenance", "holiday_lighting_installation", "holiday_lighting_repair", "holiday_lighting_replacement", "home_addition",
                        "home_audio_installation", "home_audio_repair", "home_audio_replacement", "home_gym", "home_inspection",
                        "home_network_installation", "home_network_repair", "home_network_replacement", "home_office", "home_theater_installation",
                        "home_theater_repair", "home_theater_replacement", "home_theater_setup", "home_watch_service", "hot_tub",
                        "hot_tub_installation", "hot_tub_repair", "hot_tub_replacement", "hvac_installation", "hvac_maintenance",
                        "hvac_repair", "hvac_replacement", "indoor_garden", "insulation_installation", "insulation_repair",
                        "insulation_replacement", "intelligent_lighting", "intercom_system_installation", "intercom_system_repair", "intercom_system_replacement",
                        "interior_design_consultation", "interior_lighting_installation", "interior_lighting_repair", "interior_lighting_replacement", "inventory_system_setup",
                        "irrigation_maintenance_contract", "irrigation_system_installation", "irrigation_system_repair", "irrigation_system_replacement", "janitorial_services",
                        "kitchen_fixture_installation", "kitchen_fixture_repair", "kitchen_fixture_replacement", "kitchen_renovation", "labor_only_cabinet_install",
                        "labor_only_concrete", "labor_only_countertop", "labor_only_deck", "labor_only_drywall", "labor_only_electrical",
                        "labor_only_fence", "labor_only_flooring", "labor_only_framing", "labor_only_insulation", "labor_only_landscaping",
                        "labor_only_masonry", "labor_only_painting", "labor_only_plumbing", "labor_only_roofing", "labor_only_siding",
                        "labor_only_tile", "landscape_design_consultation", "landscaping_renovation", "landscaping_service", "lawn_maintenance",
                        "lift_rental", "lightning_protection_system_installation", "lightning_protection_system_repair", "lightning_protection_system_replacement", "meditation_space",
                        "mold_remediation", "monthly_cleaning_service", "monthly_pest_control", "move_out_cleaning", "moving_assistance",
                        "moving_equipment_rental", "mulch_installation", "network_infrastructure", "networking", "open_house_staging",
                        "outdoor_event", "outdoor_kitchen_installation", "outdoor_kitchen_repair", "outdoor_kitchen_replacement", "outdoor_lighting_installation",
                        "outdoor_lighting_repair", "outdoor_lighting_replacement", "paint_touch_ups", "parking_lot_maintenance", "party_equipment_rental",
                        "party_setup", "party_tent_setup", "patio_installation", "patio_renovation", "patio_repair",
                        "patio_replacement", "pergola_installation", "pergola_repair", "pergola_replacement", "permit_consultation",
                        "pest_control_maintenance", "pet_friendly_renovations", "planning", "playground_installation", "playground_repair",
                        "playground_replacement", "plumbing_repair", "pond_maintenance", "pool_design_consultation", "pool_installation",
                        "pool_maintenance", "pool_repair", "pool_replacement", "porch_renovation", "portable_restroom_rental",
                        "portable_storage_rental", "portable_toilet_rental", "pos_system_installation", "power_outage", "predictive_maintenance",
                        "pressure_washing", "project_assessment", "projector_installation", "projector_repair", "projector_replacement",
                        "property_maintenance", "quarterly_hvac_service", "radon_system_installation", "radon_system_repair", "radon_system_replacement",
                        "railing_installation", "railing_repair", "railing_replacement", "retaining_wall_installation", "retaining_wall_repair",
                        "retaining_wall_replacement", "roof_maintenance", "roof_renovation", "roof_repair", "roof_replacement",
                        "satellite_dish_installation", "satellite_dish_repair", "satellite_dish_replacement", "sauna", "sauna_installation",
                        "sauna_repair", "sauna_replacement", "scaffold_rental", "seasonal_gutter_cleaning", "security_assessment",
                        "security_cameras", "security_monitoring", "security_system_installation", "security_system_repair", "security_system_replacement",
                        "septic_maintenance", "sewer_backup_cleanup", "shed_installation", "shed_repair", "shed_replacement",
                        "skylight_installation", "skylight_repair", "skylight_replacement", "smart_home", "smart_home_ai",
                        "smart_home_system_installation", "smart_home_system_repair", "smart_home_system_replacement", "smart_home_wellness", "smart_lock_installation",
                        "smart_lock_repair", "smart_lock_replacement", "smoke_detector_installation", "smoke_detector_repair", "smoke_detector_replacement",
                        "snow_removal", "snow_removal_contract", "solar_panel_cleaning", "solar_panel_installation", "solar_panel_repair",
                        "solar_panel_replacement", "solar_tube_installation", "solar_tube_repair", "solar_tube_replacement", "soundproofing_installation",
                        "soundproofing_project", "soundproofing_repair", "soundproofing_replacement", "spa_installation", "sprinkler_winterization",
                        "staging", "steam_room_installation", "steam_shower_installation", "steam_shower_repair", "steam_shower_replacement",
                        "storm_damage", "storm_shutter_installation", "storm_shutter_repair", "storm_shutter_replacement", "studio_setup",
                        "sump_pump_installation", "sump_pump_repair", "sump_pump_replacement", "sunroom_renovation", "temporary_fencing",
                        "temporary_installation", "tent_rental", "tool_rental", "tree_trimming", "trim_molding_installation",
                        "trim_molding_repair", "trim_molding_replacement", "turf_installation", "turf_repair", "turf_replacement",
                        "ventilation_fan_installation", "ventilation_fan_repair", "ventilation_fan_replacement", "video_doorbell_installation", "video_doorbell_repair",
                        "video_doorbell_replacement", "voice_control", "walkway_installation", "walkway_repair", "walkway_replacement",
                        "water_filtration_installation", "water_filtration_repair", "water_filtration_replacement", "water_heater_flush", "water_heater_installation",
                        "water_heater_repair", "water_heater_replacement", "water_quality_system", "water_softener_installation", "water_softener_repair",
                        "water_softener_replacement", "waterproofing_system_installation", "waterproofing_system_repair", "waterproofing_system_replacement", "wedding_setup",
                        "weed_control", "weekly_lawn_care", "weekly_trash_service", "wellness_room", "whole_home_renovation",
                        "window_cleaning", "window_installation", "window_repair", "window_replacement", "window_treatment_installation",
                        "window_treatment_repair", "window_treatment_replacement", "wine_cellar_construction", "wine_cellar_installation", "wine_cellar_repair",
                        "wine_cellar_replacement", "yoga_studio", "zen_garden"
                    ],
                    "description": "MUST pick from the pre-defined project types - no custom types allowed"
                },
                "confidence_score": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "description": "Confidence level in the categorization (0.0 to 1.0)"
                },
                "reasoning": {
                    "type": "string",
                    "description": "Brief explanation of categorization decision"
                }
            },
            "required": ["service_category", "normalized_project_type", "project_scope", "confidence_score"]
        }
    }
}

async def handle_categorize_project_tool(
    bid_card_id: str,
    project_data: Dict[str, Any],
    tool_call_args: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Handle categorize_project tool call from OpenAI
    
    Args:
        bid_card_id: ID of bid card being categorized
        project_data: Original project info (title, description, etc.)
        tool_call_args: Arguments from OpenAI function call
        
    Returns:
        Result dictionary with success status and message
    """
    try:
        logger.info(f"Processing categorization tool call for bid card {bid_card_id}")
        
        # Extract tool call results
        service_category = tool_call_args.get("service_category")
        confidence = tool_call_args.get("confidence_score", 0)
        
        # If no bid_card_id, just return the categorization without database update
        if not bid_card_id:
            logger.warning("No bid_card_id provided - returning categorization without database update")
            return {
                "success": True,
                "service_category": service_category,
                "confidence": confidence,
                "project_scope": tool_call_args.get("project_scope"),
                "normalized_project_type": tool_call_args.get("normalized_project_type"),
                "message": f"Tagged: {service_category}, {tool_call_args.get('project_scope', 'single_trade')} ({confidence:.2f} confidence)",
                "no_database_update": True
            }
        
        # Validate confidence threshold
        if confidence < 0.7:
            return {
                "success": False,
                "confidence_too_low": True,
                "confidence": confidence,
                "message": f"Confidence too low ({confidence:.2f}) - ask clarifying question instead"
            }
        
        # Enhance with pre-built intelligence
        enhanced_data = enhance_categorization_with_prebuilt(
            project_data, tool_call_args
        )
        
        # Save to database if confidence is high enough
        await upsert_bid_card_categorization(bid_card_id, enhanced_data)
        
        logger.info(f"Successfully categorized bid card {bid_card_id}: {service_category}, {enhanced_data['project_scope']}")
        
        return {
            "success": True,
            "confidence": confidence,
            "categorization": enhanced_data,
            "message": f"Tagged: {service_category}, {enhanced_data['project_scope']} ({confidence:.2f} confidence)"
        }
        
    except Exception as e:
        logger.error(f"Error handling categorization tool call: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Categorization failed due to system error"
        }

def enhance_categorization_with_prebuilt(
    project_data: Dict[str, Any], 
    tool_call_args: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Enhance OpenAI categorization with pre-built intelligence
    
    Args:
        project_data: Original project information
        tool_call_args: OpenAI tool call arguments
        
    Returns:
        Enhanced categorization data
    """
    service_category = tool_call_args["service_category"]
    user_input = f"{project_data.get('title', '')} {project_data.get('description', '')}"
    
    # LLM must provide normalized_project_type from enum - no fallback needed
    
    # Use pre-built scope rules if not provided or if we can improve it
    project_type = tool_call_args["normalized_project_type"]
    prebuilt_scope = get_project_scope(project_type)
    if "project_scope" not in tool_call_args or prebuilt_scope != "single_trade":
        tool_call_args["project_scope"] = prebuilt_scope
    
    # Use pre-built capabilities if not provided or enhance existing ones
    prebuilt_capabilities = get_required_capabilities(project_type)
    existing_capabilities = tool_call_args.get("required_capabilities", [])
    
    # Merge capabilities (prebuilt + LLM-suggested)
    all_capabilities = list(set(prebuilt_capabilities + existing_capabilities))
    tool_call_args["required_capabilities"] = all_capabilities
    
    return tool_call_args

async def upsert_bid_card_categorization(
    bid_card_id: str, 
    categorization_data: Dict[str, Any]
) -> None:
    """
    Update bid card with categorization data
    
    Args:
        bid_card_id: Bid card to update
        categorization_data: Categorization fields to save
    """
    from database_simple import db
    
    # Prepare update data
    update_data = {
        "service_category": categorization_data["service_category"].lower(),
        "project_scope": categorization_data["project_scope"],
        "required_capabilities": categorization_data.get("required_capabilities", []),
        "updated_at": "now()"
    }
    
    # Add normalized project type if available
    if "normalized_project_type" in categorization_data:
        update_data["project_type"] = categorization_data["normalized_project_type"]
    
    # Update bid card
    try:
        result = db.client.table("bid_cards").update(update_data).eq("id", bid_card_id).execute()
        
        if not result.data:
            # Try potential_bid_cards table if bid_cards update failed
            potential_result = db.client.table("potential_bid_cards").update(update_data).eq("id", bid_card_id).execute()
            
            if not potential_result.data:
                logger.warning(f"No bid card or potential bid card found with ID {bid_card_id}")
            else:
                logger.info(f"Updated potential bid card {bid_card_id} with categorization")
        else:
            logger.info(f"Updated bid card {bid_card_id} with categorization")
            
    except Exception as e:
        logger.error(f"Database error updating categorization for {bid_card_id}: {e}")
        raise

def create_categorization_prompt_context(project_data: Dict[str, Any]) -> str:
    """
    Create context for LLM prompt that includes pre-built knowledge
    
    Args:
        project_data: Project information to categorize
        
    Returns:
        Formatted context string for LLM
    """
    context = f"""
Project to categorize:
- Project Type: {project_data.get('project_type', 'Not specified')}
- Title: {project_data.get('title', 'Not specified')}
- Description: {project_data.get('description', 'Not specified')}

Available service categories: {', '.join(PROJECT_TYPE_MAPPING.keys())}

Remember:
- Use confidence_score < 0.7 to ask clarifying questions
- MUST pick from the predefined project type enum - no custom types allowed
- Consider scope based on number of trades involved
"""
    
    return context