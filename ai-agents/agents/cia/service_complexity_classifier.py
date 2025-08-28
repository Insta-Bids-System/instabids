"""
Service Complexity Classifier for CIA Agent
Classifies projects as single-trade, multi-trade, or complex-coordination
"""

from typing import Dict, List, Optional, Tuple
import re
import logging

logger = logging.getLogger(__name__)

class ServiceComplexityClassifier:
    """
    Classifies project complexity based on project type, description, and required trades
    """
    
    def __init__(self):
        # Single-trade project indicators
        self.single_trade_patterns = {
            "lawn_care": [
                "lawn", "grass", "mowing", "trimming", "edging", "fertilizer",
                "weed control", "lawn maintenance", "grass cutting"
            ],
            "roofing": [
                "roof", "shingle", "tile", "metal roof", "gutter", "downspout",
                "roof repair", "roof replacement", "roof installation"
            ],
            "turf_installation": [
                "artificial turf", "synthetic grass", "fake grass", "turf installation",
                "artificial lawn", "synthetic turf"
            ],
            "pool_service": [
                "pool cleaning", "pool maintenance", "pool service", "pool chemicals",
                "pool filter", "pool pump", "pool equipment"
            ],
            "window_cleaning": [
                "window cleaning", "window washing", "glass cleaning", "pressure washing",
                "exterior cleaning"
            ],
            "landscaping": [
                "landscaping", "garden", "plants", "irrigation", "sprinkler",
                "mulch", "tree service", "hedge trimming"
            ],
            "hvac": [
                "air conditioning", "hvac", "ac repair", "heating", "cooling",
                "duct cleaning", "ac installation"
            ],
            "electrical": [
                "electrical", "wiring", "outlet", "switch", "panel", "breaker",
                "electrical repair", "electrical installation"
            ],
            "plumbing": [
                "plumbing", "pipe", "faucet", "toilet", "sink", "drain",
                "water heater", "plumbing repair"
            ]
        }
        
        # Multi-trade project indicators
        self.multi_trade_patterns = {
            "kitchen_remodel": [
                "kitchen remodel", "kitchen renovation", "kitchen upgrade",
                "cabinet installation", "countertop", "backsplash"
            ],
            "bathroom_remodel": [
                "bathroom remodel", "bathroom renovation", "bathroom upgrade",
                "shower installation", "bathtub", "vanity"
            ],
            "home_addition": [
                "addition", "room addition", "home expansion", "new room"
            ],
            "general_renovation": [
                "renovation", "remodel", "upgrade", "makeover", "restoration"
            ]
        }
        
        # Complex coordination indicators
        self.complex_coordination_patterns = [
            "whole house", "complete renovation", "gut renovation",
            "new construction", "custom home", "major remodel",
            "structural work", "foundation", "load bearing"
        ]
    
    def classify_project(self, 
                        project_type: str, 
                        description: str = "", 
                        recommended_trades: List[str] = None) -> Dict[str, any]:
        """
        Classify project complexity
        
        Returns:
        {
            "service_complexity": "single-trade|multi-trade|complex-coordination",
            "trade_count": int,
            "primary_trade": str,
            "secondary_trades": List[str],
            "confidence_score": float,
            "reasoning": str
        }
        """
        
        if recommended_trades is None:
            recommended_trades = []
            
        project_text = f"{project_type} {description}".lower()
        
        # Check for complex coordination first
        for pattern in self.complex_coordination_patterns:
            if pattern in project_text:
                return self._create_classification(
                    "complex-coordination",
                    len(recommended_trades) if recommended_trades else 3,
                    self._extract_primary_trade(project_type, recommended_trades),
                    recommended_trades,
                    0.9,
                    f"Contains complex coordination indicator: '{pattern}'"
                )
        
        # Check trade count from recommended_trades
        trade_count = len(recommended_trades) if recommended_trades else 1
        
        if trade_count >= 3:
            return self._create_classification(
                "complex-coordination",
                trade_count,
                self._extract_primary_trade(project_type, recommended_trades),
                recommended_trades,
                0.85,
                f"Requires {trade_count} different trades"
            )
        
        # Check for single-trade patterns
        single_trade_match = self._match_single_trade_patterns(project_text)
        if single_trade_match:
            primary_trade, confidence = single_trade_match
            return self._create_classification(
                "single-trade",
                1,
                primary_trade,
                [],
                confidence,
                f"Matches single-trade pattern for {primary_trade}"
            )
        
        # Check for multi-trade patterns
        multi_trade_match = self._match_multi_trade_patterns(project_text)
        if multi_trade_match:
            primary_trade, confidence = multi_trade_match
            return self._create_classification(
                "multi-trade",
                trade_count if trade_count > 1 else 2,
                primary_trade,
                recommended_trades,
                confidence,
                f"Matches multi-trade pattern for {primary_trade}"
            )
        
        # Default classification based on trade count
        if trade_count == 1:
            return self._create_classification(
                "single-trade",
                1,
                self._extract_primary_trade(project_type, recommended_trades),
                [],
                0.6,
                "Single trade based on trade count"
            )
        elif trade_count == 2:
            return self._create_classification(
                "multi-trade",
                2,
                self._extract_primary_trade(project_type, recommended_trades),
                recommended_trades[1:] if len(recommended_trades) > 1 else [],
                0.7,
                "Multi-trade based on trade count"
            )
        else:
            return self._create_classification(
                "single-trade",  # Default to single-trade for unknown
                1,
                "general",
                [],
                0.5,
                "Default classification - insufficient information"
            )
    
    def _match_single_trade_patterns(self, project_text: str) -> Optional[Tuple[str, float]]:
        """Match against single-trade patterns"""
        best_match = None
        best_score = 0
        
        for trade, patterns in self.single_trade_patterns.items():
            for pattern in patterns:
                if pattern in project_text:
                    score = len(pattern) / len(project_text)  # Longer matches = higher confidence
                    if score > best_score:
                        best_score = score
                        best_match = trade
        
        if best_match and best_score > 0.1:
            return (best_match, min(0.9, best_score * 5))  # Scale to reasonable confidence
        
        return None
    
    def _match_multi_trade_patterns(self, project_text: str) -> Optional[Tuple[str, float]]:
        """Match against multi-trade patterns"""
        best_match = None
        best_score = 0
        
        for trade, patterns in self.multi_trade_patterns.items():
            for pattern in patterns:
                if pattern in project_text:
                    score = len(pattern) / len(project_text)
                    if score > best_score:
                        best_score = score
                        best_match = trade
        
        if best_match and best_score > 0.1:
            return (best_match, min(0.9, best_score * 5))
        
        return None
    
    def _extract_primary_trade(self, project_type: str, recommended_trades: List[str]) -> str:
        """Extract primary trade from project type or recommended trades"""
        if recommended_trades:
            return recommended_trades[0]
        
        # Extract from project_type
        project_lower = project_type.lower()
        
        # Common trade mappings
        trade_mappings = {
            "kitchen": "kitchen_contractor",
            "bathroom": "bathroom_contractor", 
            "lawn": "landscaping",
            "roof": "roofing",
            "turf": "landscaping",
            "pool": "pool_service",
            "window": "cleaning_service",
            "electrical": "electrical",
            "plumbing": "plumbing",
            "hvac": "hvac"
        }
        
        for keyword, trade in trade_mappings.items():
            if keyword in project_lower:
                return trade
        
        return "general_contractor"
    
    def _create_classification(self, 
                             service_complexity: str,
                             trade_count: int,
                             primary_trade: str,
                             secondary_trades: List[str],
                             confidence_score: float,
                             reasoning: str) -> Dict[str, any]:
        """Create classification result"""
        return {
            "service_complexity": service_complexity,
            "trade_count": trade_count,
            "primary_trade": primary_trade,
            "secondary_trades": secondary_trades,
            "confidence_score": confidence_score,
            "reasoning": reasoning
        }
    
    def is_group_bid_eligible(self, classification: Dict[str, any]) -> bool:
        """Determine if project is eligible for group bidding"""
        return (classification["service_complexity"] == "single-trade" and 
                classification["trade_count"] == 1)

# Global instance
service_classifier = ServiceComplexityClassifier()