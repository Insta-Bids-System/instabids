"""
CDA v2 - Intelligent Contractor Discovery Agent
Powered by Claude Opus 4 for nuanced matching decisions
"""
import json
import os
import sys
from datetime import datetime
from typing import Any, Optional

from dotenv import load_dotenv
from supabase import create_client


# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from agents.cda.intelligent_matcher import IntelligentContractorMatcher
from agents.cda.tier1_matcher_v2 import Tier1Matcher
from agents.cda.tier2_reengagement import Tier2Reengagement
from agents.cda.web_search_agent import WebSearchContractorAgent


class ContractorDiscoveryAgent:
    """CDA v2 - Uses Claude Opus 4 for intelligent contractor matching"""

    def __init__(self):
        """Initialize CDA with Opus 4 brain and data sources"""
        load_dotenv(override=True)
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        self.supabase = create_client(self.supabase_url, self.supabase_key)

        # Initialize components
        self.intelligent_matcher = IntelligentContractorMatcher(llm_provider="anthropic")  # Opus 4
        self.web_search = WebSearchContractorAgent(self.supabase)
        self.tier1_matcher = Tier1Matcher(self.supabase)
        self.tier2_reengagement = Tier2Reengagement(self.supabase)

        print("[CDA v2] Initialized with Claude Opus 4 intelligence")

    def discover_contractors(self, bid_card_id: str, contractors_needed: int = 5, radius_miles: int = 15) -> dict[str, Any]:
        """
        Main CDA function with intelligent matching and radius-based search

        Process:
        1. Load bid card data
        2. Use Opus 4 to deeply analyze what customer wants
        3. Search for contractors (3-tier system with radius filtering)
        4. Use Opus 4 to score each contractor
        5. Select best matches with explanations
        
        Args:
            bid_card_id: ID of the bid card to process
            contractors_needed: Number of contractors to select (default: 5)
            radius_miles: Search radius in miles for Tier 1 & 2 (default: 15)
        """
        try:
            print(f"[CDA v2] Starting intelligent contractor discovery for bid card: {bid_card_id} (radius: {radius_miles} miles)")

            # Step 1: Load bid card
            bid_card = self._load_bid_card(bid_card_id)
            if not bid_card:
                return {"success": False, "error": "Bid card not found"}

            print(f"[CDA v2] Loaded bid card - Project: {bid_card.get('project_type', 'Unknown')}")

            # Step 2: Opus 4 analyzes what customer really wants
            print("[CDA v2] Using Claude Opus 4 to analyze customer requirements...")
            bid_analysis = self.intelligent_matcher.analyze_bid_requirements(bid_card)

            print("[CDA v2] Opus 4 Analysis Complete:")
            print(f"  - Size Preference: {bid_analysis.get('contractor_size_preference', 'Unknown')}")
            print(f"  - Quality Focus: {bid_analysis.get('quality_vs_price_balance', 'Unknown')}")
            print(f"  - Trust Factors: {bid_analysis.get('trust_factors', 'Unknown')}")

            # Step 3: Gather contractors from all sources
            all_contractors = []

            # Tier 1: Internal database with radius search
            print(f"[CDA v2] Searching Tier 1: Internal contractor database within {radius_miles} miles...")
            tier1_results = self.tier1_matcher.find_matching_contractors(bid_card, radius_miles=radius_miles)
            if tier1_results["success"] and tier1_results["contractors"]:
                all_contractors.extend(tier1_results["contractors"])
                print(f"[CDA v2] Found {len(tier1_results['contractors'])} internal contractors within radius")
            else:
                print(f"[CDA v2] No internal contractors found within {radius_miles} miles")

            # Tier 2: Previous contacts with radius search
            print(f"[CDA v2] Searching Tier 2: Previous contractor contacts within {radius_miles} miles...")
            tier2_results = self.tier2_reengagement.find_reengagement_candidates(bid_card, radius_miles=radius_miles)
            if tier2_results and len(tier2_results) > 0:
                all_contractors.extend(tier2_results)
                print(f"[CDA v2] Found {len(tier2_results)} previous contacts within radius")
            else:
                print(f"[CDA v2] No previous contacts found within {radius_miles} miles")

            # Tier 3: Web search for new contractors with radius search
            if len(all_contractors) < contractors_needed * 2:  # Get extra for better selection
                print(f"[CDA v2] Searching Tier 3: Web search for new contractors within {radius_miles} miles...")
                web_results = self.web_search.discover_contractors_for_bid(
                    bid_card_id,
                    contractors_needed=contractors_needed * 2,
                    radius_miles=radius_miles
                )
                if web_results["success"] and web_results["contractors"]:
                    all_contractors.extend(web_results["contractors"])
                    print(f"[CDA v2] Found {len(web_results['contractors'])} new contractors via web search")

            # Remove duplicates
            unique_contractors = self._deduplicate_contractors(all_contractors)
            print(f"[CDA v2] Total unique contractors found: {len(unique_contractors)}")

            if not unique_contractors:
                return {
                    "success": False,
                    "error": "No contractors found",
                    "bid_analysis": bid_analysis
                }

            # Step 4: Use Opus 4 to intelligently score and select contractors
            print(f"[CDA v2] Using Claude Opus 4 to score {len(unique_contractors)} contractors...")
            selection_result = self.intelligent_matcher.rank_and_select_contractors(
                unique_contractors,
                bid_card,
                contractors_needed=contractors_needed
            )

            # Step 5: Get human-readable explanation
            explanation = self.intelligent_matcher.explain_selection(selection_result)

            # Step 6: Store the selected contractors with match data
            stored_contractors = self._store_matched_contractors(
                selection_result["selected_contractors"],
                bid_card_id,
                bid_analysis
            )

            # Return comprehensive results with radius info
            result = {
                "success": True,
                "bid_card_id": bid_card_id,
                "search_radius_miles": radius_miles,
                "bid_analysis": bid_analysis,
                "total_found": len(unique_contractors),
                "selected_count": len(selection_result["selected_contractors"]),
                "selected_contractors": selection_result["selected_contractors"],
                "explanation": explanation,
                "all_scores": selection_result["all_scores"],
                "stored_ids": stored_contractors,
                "tier_results": {
                    "tier1_internal": len(tier1_results.get("contractors", [])) if tier1_results.get("success") else 0,
                    "tier2_previous": len(tier2_results) if tier2_results else 0,
                    "tier3_web": len(web_results.get("contractors", [])) if 'web_results' in locals() and web_results.get("success") else 0
                }
            }

            print(f"[CDA v2] Discovery complete - Selected {len(selection_result['selected_contractors'])} contractors within {radius_miles} mile radius")
            print(f"[CDA v2] Explanation: {explanation}")

            return result

        except Exception as e:
            print(f"[CDA v2 ERROR] Discovery failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "bid_card_id": bid_card_id
            }

    def _load_bid_card(self, bid_card_id: str) -> Optional[dict[str, Any]]:
        """Load bid card from database or test data"""
        # Handle test bid cards
        if bid_card_id == "test-mom-and-pop-kitchen":
            return {
                "id": bid_card_id,
                "project_type": "kitchen remodel",
                "bid_document": {
                    "project_overview": {
                        "description": "We want to update our kitchen but keep the family feel. Looking for someone we can trust, not a big corporation. Our last contractor was terrible - took forever and overcharged us."
                    },
                    "budget_information": {
                        "budget_min": 8000,
                        "budget_max": 12000,
                        "notes": "We have some flexibility but want good value"
                    },
                    "timeline": {
                        "urgency_level": "month",
                        "notes": "Want it done right, not rushed"
                    }
                },
                "location": {
                    "city": "Coconut Creek",
                    "state": "FL",
                    "zip_code": "33442"
                },
                "contractor_count_needed": 5
            }

        # Load from database
        try:
            result = self.supabase.table("bid_cards").select("*").eq("id", bid_card_id).single().execute()
            return result.data if result.data else None
        except:
            return None

    def _deduplicate_contractors(self, contractors: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Remove duplicate contractors based on company name"""
        seen = set()
        unique = []

        for contractor in contractors:
            name = contractor.get("company_name", "").lower().strip()
            if name and name not in seen:
                seen.add(name)
                unique.append(contractor)

        return unique

    def _store_matched_contractors(self,
                                 contractors: list[dict[str, Any]],
                                 bid_card_id: str,
                                 bid_analysis: dict[str, Any]) -> list[str]:
        """Store selected contractors with intelligent match data"""
        stored_ids = []

        try:
            for contractor in contractors:
                # Prepare match record
                match_record = {
                    "bid_card_id": bid_card_id,
                    "contractor_id": contractor.get("id"),
                    "company_name": contractor.get("company_name"),
                    "match_score": contractor.get("match_score", 0),
                    "recommendation": contractor.get("recommendation", "unknown"),
                    "reasoning": contractor.get("reasoning", ""),
                    "key_strengths": json.dumps(contractor.get("key_strengths", [])),
                    "concerns": json.dumps(contractor.get("concerns", [])),
                    "bid_analysis": json.dumps(bid_analysis),
                    "created_at": datetime.now().isoformat()
                }

                # Store in contractor_bid_matches table (create if needed)
                result = self.supabase.table("contractor_bid_matches").insert(match_record).execute()

                if result.data:
                    stored_ids.append(result.data[0]["id"])
                    print(f"[CDA v2] Stored match: {contractor.get('company_name')} - Score: {contractor.get('match_score')}")

        except Exception as e:
            print(f"[CDA v2] Note: contractor_bid_matches table may not exist yet - {e}")
            # Continue anyway - main functionality still works

        return stored_ids


# Test the intelligent CDA
if __name__ == "__main__":
    print("TESTING INTELLIGENT CDA WITH CLAUDE OPUS 4")
    print("=" * 60)

    agent = ContractorDiscoveryAgent()

    # Test with mom & pop preference bid card with 15-mile radius
    result = agent.discover_contractors(
        bid_card_id="test-mom-and-pop-kitchen",
        contractors_needed=3,
        radius_miles=15
    )

    if result["success"]:
        print("\nSUCCESS - Intelligent Matching Results:")
        print(f"Total contractors found: {result['total_found']}")
        print(f"Selected: {result['selected_count']}")
        print(f"\nCustomer Explanation:\n{result['explanation']}")

        print("\nSelected Contractors:")
        for contractor in result["selected_contractors"]:
            print(f"\n{contractor.get('contractor_name', 'Unknown')}:")
            print(f"  Score: {contractor.get('match_score', 0)}")
            print(f"  Recommendation: {contractor.get('recommendation', 'Unknown')}")
            print(f"  Reasoning: {contractor.get('reasoning', 'No reasoning provided')}")
    else:
        print(f"\nERROR: {result.get('error', 'Unknown error')}")
