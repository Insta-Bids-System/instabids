"""
CIA Image Integration Module
Connects uploaded images to CIA agent for analysis and context
"""

import base64
import httpx
import json
import asyncio
from typing import List, Dict, Optional
from openai import AsyncOpenAI
import os
import logging

logger = logging.getLogger(__name__)

class CIAImageIntegration:
    """Handles image integration for CIA agent"""
    
    def __init__(self):
        self.image_cache = {}
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    async def prepare_images_for_vision(self, image_urls: List[str]) -> List[Dict]:
        """
        Convert image URLs to format needed for LLM vision
        URLs from Supabase Storage can be passed directly to Claude/GPT-4
        """
        vision_messages = []
        
        for url in image_urls:
            if not url:
                continue
                
            # For Supabase Storage URLs, we can pass them directly
            if "supabase.co/storage" in url:
                vision_messages.append({
                    "type": "image",
                    "source": {
                        "type": "url",
                        "url": url
                    }
                })
                logger.info(f"Added Supabase Storage image for vision: {url[:60]}...")
            else:
                # For other URLs, we might need to fetch and encode
                # But for now, pass URL directly
                vision_messages.append({
                    "type": "image",
                    "source": {
                        "type": "url",
                        "url": url
                    }
                })
                
        return vision_messages
    
    async def analyze_images_with_context(self, image_urls: List[str], project_context: Dict) -> Dict:
        """
        Analyze images with project context using GPT-4o Vision
        Returns structured analysis for bid card fields
        """
        analysis_result = {
            "detected_issues": [],
            "estimated_square_footage": None,
            "material_conditions": [],
            "recommended_trades": [],
            "project_scope": [],
            "safety_concerns": [],
            "budget_indicators": [],
            "confidence": 0.0
        }
        
        if not image_urls:
            return analysis_result
            
        try:
            logger.info(f"Analyzing {len(image_urls)} images for bid card extraction")
            
            # Build prompt for image analysis
            analysis_prompt = f"""
            Analyze these property images for a home improvement project.
            
            Project context:
            - Property area: {project_context.get('property_area', 'Unknown')}
            - User notes: {project_context.get('user_notes', 'No notes provided')}
            
            Please identify:
            1. Visible issues or damage
            2. Estimated square footage of area shown
            3. Material conditions (e.g., wood rot, concrete cracks)
            4. Recommended contractor trades needed
            5. Project scope elements
            6. Any safety concerns
            7. Budget indicators based on visible condition
            
            Respond with JSON in this format:
            {{
                "detected_issues": ["issue1", "issue2"],
                "estimated_square_footage": 500,
                "material_conditions": ["condition1", "condition2"],
                "recommended_trades": ["plumbing", "electrical"],
                "project_scope": ["scope1", "scope2"],
                "safety_concerns": ["concern1"],
                "budget_indicators": ["high-end", "custom work"],
                "confidence": 0.8
            }}
            """
            
            # Prepare content with images
            content = [{"type": "text", "text": analysis_prompt}]
            
            # Add each image
            for i, image_url in enumerate(image_urls):
                # Ensure proper format for OpenAI Vision
                if not image_url.startswith("data:") and not image_url.startswith("http"):
                    image_url = f"data:image/jpeg;base64,{image_url}"
                
                content.append({
                    "type": "image_url",
                    "image_url": {"url": image_url}
                })
                logger.info(f"Added image {i+1} for analysis")
            
            # Call OpenAI Vision API
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing property images for home improvement projects. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content
            logger.info(f"Image analysis completed: {len(analysis_text)} characters")
            
            # Parse JSON response
            try:
                json_start = analysis_text.find('{')
                json_end = analysis_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_text = analysis_text[json_start:json_end]
                    analysis_result = json.loads(json_text)
                else:
                    logger.warning("No JSON found in analysis response")
                    analysis_result["detected_issues"] = ["Analysis completed but format unclear"]
                    analysis_result["confidence"] = 0.3
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON from image analysis")
                analysis_result["detected_issues"] = [analysis_text[:200]]
                analysis_result["confidence"] = 0.3
                
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            analysis_result["detected_issues"] = [f"Analysis failed: {str(e)}"]
            analysis_result["confidence"] = 0.0
        
        return analysis_result
    
    def extract_bid_card_fields_from_images(self, image_analysis: Dict) -> Dict:
        """
        Extract potential bid card fields from image analysis
        """
        bid_card_updates = {}
        
        # Map analysis to bid card fields
        if image_analysis.get("estimated_square_footage"):
            bid_card_updates["square_footage"] = image_analysis["estimated_square_footage"]
            
        if image_analysis.get("recommended_trades"):
            trades = image_analysis["recommended_trades"]
            if trades:
                bid_card_updates["primary_trade"] = trades[0]
                if len(trades) > 1:
                    bid_card_updates["secondary_trades"] = trades[1:]
                    
        if image_analysis.get("detected_issues"):
            scope_notes = "Issues identified from photos: " + ", ".join(image_analysis["detected_issues"])
            bid_card_updates["user_scope_notes"] = scope_notes
            
        if image_analysis.get("safety_concerns"):
            bid_card_updates["urgency_level"] = "urgent" if image_analysis["safety_concerns"] else "standard"
            
        # Estimate complexity based on analysis
        if len(image_analysis.get("detected_issues", [])) > 3:
            bid_card_updates["project_complexity"] = "high"
        elif len(image_analysis.get("detected_issues", [])) > 1:
            bid_card_updates["project_complexity"] = "medium"
        else:
            bid_card_updates["project_complexity"] = "low"
            
        return bid_card_updates
    
    async def update_conversation_with_images(self, conversation_state: Dict, image_data: Dict) -> Dict:
        """
        Update conversation state with image information
        """
        if "uploaded_images" not in conversation_state:
            conversation_state["uploaded_images"] = []
            
        # Add new image data
        conversation_state["uploaded_images"].append({
            "url": image_data.get("url"),
            "description": image_data.get("description"),
            "analysis": image_data.get("analysis"),
            "uploaded_at": image_data.get("uploaded_at")
        })
        
        # Update context for CIA
        if "image_context" not in conversation_state:
            conversation_state["image_context"] = {
                "total_images": 0,
                "analyzed_images": 0,
                "pending_analysis": []
            }
            
        conversation_state["image_context"]["total_images"] = len(conversation_state["uploaded_images"])
        
        # Mark for analysis
        if image_data.get("url") and not image_data.get("analysis"):
            conversation_state["image_context"]["pending_analysis"].append(image_data.get("url"))
            
        return conversation_state
    
    def build_image_context_prompt(self, conversation_state: Dict) -> str:
        """
        Build context prompt about uploaded images for CIA
        """
        if not conversation_state.get("uploaded_images"):
            return ""
            
        image_count = len(conversation_state["uploaded_images"])
        analyzed_count = sum(1 for img in conversation_state["uploaded_images"] if img.get("analysis"))
        
        context = f"\n[Image Context: User has uploaded {image_count} image(s)"
        
        if analyzed_count > 0:
            context += f", {analyzed_count} analyzed"
            
        # Add descriptions if available
        descriptions = [img.get("description") for img in conversation_state["uploaded_images"] if img.get("description")]
        if descriptions:
            context += f". Images show: {', '.join(descriptions[:3])}"
            
        context += "]\n"
        
        return context
    
    async def prepare_message_with_images(self, message: str, image_urls: List[str]) -> List[Dict]:
        """
        Prepare a message with embedded images for vision-enabled LLM
        """
        content = [
            {"type": "text", "text": message}
        ]
        
        # Add images to the message
        for url in image_urls:
            if url and "supabase.co/storage" in url:
                content.append({
                    "type": "image",
                    "source": {
                        "type": "url", 
                        "url": url
                    }
                })
                
        return content
    
    async def update_potential_bid_card_with_images(
        self, 
        potential_bid_card_id: str, 
        image_urls: List[str], 
        analysis_results: Dict
    ) -> bool:
        """
        Update a potential bid card with image URLs and analysis results
        
        Args:
            potential_bid_card_id: ID of the potential bid card
            image_urls: List of Supabase Storage URLs
            analysis_results: Results from image analysis
            
        Returns:
            Success status
        """
        try:
            from database_simple import db
            
            # Update potential bid card with image data
            update_data = {
                "photo_ids": json.dumps(image_urls),  # Store as JSON array
                "image_analysis": json.dumps(analysis_results),
                "updated_at": "now()"
            }
            
            # If analysis extracted fields, update them too
            if analysis_results.get("recommended_trades"):
                trades = analysis_results["recommended_trades"]
                if trades:
                    update_data["project_type"] = trades[0]  # Use first trade as project type
            
            if analysis_results.get("detected_issues"):
                issues_text = "Issues identified from photos: " + ", ".join(analysis_results["detected_issues"])
                update_data["description"] = issues_text
            
            if analysis_results.get("estimated_square_footage"):
                update_data["square_footage"] = analysis_results["estimated_square_footage"]
            
            result = db.client.table("potential_bid_cards").update(update_data).eq("id", potential_bid_card_id).execute()
            
            if result.data:
                logger.info(f"Updated potential bid card {potential_bid_card_id} with {len(image_urls)} images")
                return True
            else:
                logger.error(f"Failed to update potential bid card {potential_bid_card_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update potential bid card with images: {e}")
            return False
    
    def format_image_context_for_conversation(self, analysis_results: Dict) -> str:
        """
        Format image analysis results for inclusion in conversation context
        
        Args:
            analysis_results: Results from image analysis
            
        Returns:
            Formatted string for conversation context
        """
        try:
            if not analysis_results or not analysis_results.get("detected_issues"):
                return "Images uploaded - analysis in progress."
            
            context_parts = []
            
            if analysis_results.get("recommended_trades"):
                trades = analysis_results["recommended_trades"]
                if trades:
                    context_parts.append(f"Project type: {trades[0]}")
            
            if analysis_results.get("detected_issues"):
                issues = analysis_results["detected_issues"][:3]  # Limit to 3 issues
                context_parts.append(f"Issues found: {', '.join(issues)}")
            
            if analysis_results.get("estimated_square_footage"):
                sq_ft = analysis_results["estimated_square_footage"]
                context_parts.append(f"Estimated area: {sq_ft} sq ft")
            
            if analysis_results.get("safety_concerns"):
                context_parts.append("Safety concerns noted")
            
            confidence = analysis_results.get("confidence", 0.0)
            if confidence > 0.7:
                context_parts.append("(High confidence)")
            elif confidence > 0.4:
                context_parts.append("(Moderate confidence)")
            else:
                context_parts.append("(Low confidence)")
            
            return " | ".join(context_parts)
            
        except Exception as e:
            logger.error(f"Failed to format image context: {e}")
            return "Images uploaded - processing."

# Global instance for use in routes
cia_image_integration = CIAImageIntegration()