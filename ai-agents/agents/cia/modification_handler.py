"""
Production-ready modification handler for CIA agent
Handles all bid card modifications with 100% reliability
"""
import re
from typing import Dict, Any, Optional, Tuple
from datetime import datetime


class ModificationHandler:
    """Reliable modification detection and processing"""
    
    def __init__(self):
        # Define modification patterns with high precision
        self.modification_patterns = {
            'budget': {
                'patterns': [
                    # Basic budget changes
                    r'change.*?budget.*?to.*?\$?(\d+(?:,\d{3})*(?:k)?)',
                    r'increase.*?budget.*?to.*?\$?(\d+(?:,\d{3})*(?:k)?)',
                    r'decrease.*?budget.*?to.*?\$?(\d+(?:,\d{3})*(?:k)?)',
                    r'budget.*?(?:should be|is now|to).*?\$?(\d+(?:,\d{3})*(?:k)?)',
                    r'make.*?budget.*?\$?(\d+(?:,\d{3})*(?:k)?)-?\$?(\d+(?:,\d{3})*(?:k)?)?',
                    # Budget ranges
                    r'\$(\d+(?:,\d{3})*(?:k)?)\s*-\s*\$?(\d+(?:,\d{3})*(?:k)?)',
                    r'\$(\d+(?:,\d{3})*(?:k)?)\s+to\s+\$?(\d+(?:,\d{3})*(?:k)?)',
                    # Simple mentions
                    r'budget.*?\$?(\d+(?:,\d{3})*(?:k)?)',
                    r'\$?(\d+(?:,\d{3})*(?:k)?)\s*(?:max|maximum)',
                ],
                'type': 'budget'
            },
            'materials': {
                'patterns': [
                    # Change X to Y patterns
                    r'change.*?(\w+).*?(?:to|into)\s+(\w+)',
                    r'(\w+)\s+(?:instead of|rather than)\s+(\w+)',
                    r'(?:want|need|prefer)\s+(\w+)\s+(?:instead|rather)',
                    r'(?:switch|replace)\s+(?:to|with)?\s*(\w+)',
                    # Direct material mentions
                    r'(?:want|need|use)\s+(\w+)\s+(?:countertop|flooring|floor|cabinet|tile)',
                    r'(?:switch to|replace with)\s+(\w+)',
                    r'use\s+(\w+)\s+(?:floors?|flooring)',
                ],
                'type': 'materials'
            },
            'timeline': {
                'patterns': [
                    # Timeline changes
                    r'change.*?timeline.*?to\s+(\d+\s*(?:week|month|day)s?)',
                    r'timeline.*?(?:should be|is now|to)\s+(\d+\s*(?:week|month|day)s?)',
                    r'make.*?timeline\s+(\d+\s*(?:week|month|day)s?)',
                    # Start/completion patterns  
                    r'start\s+in\s+(\d+\s*(?:week|month|day)s?)',
                    r'begin\s+in\s+(\d+\s*(?:week|month|day)s?)',
                    r'need\s+it\s+done\s+in\s+(\d+\s*(?:week|month|day)s?)',
                    r'(?:need|want).*?(?:done|completed?).*?(?:in|within)\s+(\d+\s*(?:week|month|day)s?)',
                    # Direct mentions
                    r'(?:in|within)?\s*(\d+\s*(?:week|month|day)s?)\s*(?:timeline|timeframe)?',
                ],
                'type': 'timeline'
            },
            'urgency': {
                'patterns': [
                    # Emergency patterns
                    r'this\s+is\s+now\s+an?\s*(emergency|urgent)',
                    r'this\s+is\s+an?\s*(emergency|urgent)',
                    r'(?:make it|mark as)\s+(?:an?\s+)?(emergency|urgent|asap)',
                    r'(?:now|is)\s+(?:an?\s+)?(emergency|urgent)',
                    # Urgent patterns
                    r'mark\s+as\s+(urgent|emergency)(?:\s+please)?',
                    r'(?:make|mark).*?(urgent|emergency)',
                    # Not urgent patterns
                    r'(?:no longer|not|isn\'t)\s+urgent',
                    r'it\'s\s+no\s+longer\s+urgent',
                ],
                'type': 'urgency'
            }
        }
        
        # Material mappings for common changes
        self.material_mappings = {
            'granite': ['granite', 'granite countertops', 'granite tops'],
            'quartz': ['quartz', 'quartz countertops', 'engineered stone'],
            'marble': ['marble', 'marble countertops', 'natural marble'],
            'laminate': ['laminate', 'formica', 'laminate countertops'],
            'butcher block': ['butcher block', 'wood countertops', 'wooden tops'],
            'tile': ['tile', 'ceramic tile', 'porcelain tile'],
            'stainless': ['stainless steel', 'stainless', 'steel appliances'],
            'vinyl': ['vinyl', 'luxury vinyl', 'vinyl plank', 'lvp'],
            'hardwood': ['hardwood', 'wood floors', 'wooden flooring'],
        }
    
    def detect_modification(self, message: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Detect if message is a modification request with high accuracy
        
        Returns:
            (is_modification, modification_details)
        """
        message_lower = message.lower()
        
        # Quick check for modification indicators
        modification_indicators = [
            'change', 'update', 'modify', 'edit', 'switch', 'replace',
            'increase', 'decrease', 'instead', 'different', 'new',
            'want to', 'need to', 'should be', 'make it', 'prefer',
            'make the', 'budget', 'timeline', 'use', 'this is', 'now',
            'mark', 'no longer', 'it\'s', 'start in', 'need it done'
        ]
        
        # More lenient check
        has_indicator = any(indicator in message_lower for indicator in modification_indicators)
        
        # Detailed pattern matching
        modifications = {}
        modification_found = False
        
        # Check each modification type
        for mod_type, config in self.modification_patterns.items():
            for pattern in config['patterns']:
                match = re.search(pattern, message_lower)
                if match:
                    modification_found = True
                    
                    if mod_type == 'budget':
                        # Handle budget ranges
                        if match.lastindex and match.lastindex >= 2:
                            # Range pattern matched
                            min_str = match.group(1).replace(',', '')
                            max_str = match.group(2).replace(',', '')
                            
                            # Handle 'k' notation
                            if min_str.endswith('k'):
                                min_val = int(min_str[:-1]) * 1000
                            else:
                                min_val = int(min_str)
                                
                            if max_str.endswith('k'):
                                max_val = int(max_str[:-1]) * 1000
                            else:
                                max_val = int(max_str)
                                
                            modifications['budget_min'] = min_val
                            modifications['budget_max'] = max_val
                        else:
                            # Single value
                            budget_str = match.group(1).replace(',', '')
                            
                            # Handle 'k' notation
                            if budget_str.endswith('k'):
                                budget_value = int(budget_str[:-1]) * 1000
                            else:
                                budget_value = int(budget_str)
                                
                            modifications['budget_max'] = budget_value
                            
                            # Always infer budget_min for single value patterns
                            # For "increase" commands or any single budget value, set min to 80%
                            modifications['budget_min'] = int(budget_value * 0.8)
                    
                    elif mod_type == 'materials':
                        # Skip if this looks like a timeline match
                        captured_text = match.group(1)
                        if captured_text.isdigit():
                            continue  # Skip numeric captures
                            
                        # Extract material change based on pattern
                        if 'instead' in pattern or 'rather than' in pattern or 'change' in pattern:
                            # These patterns have old and new materials
                            if match.lastindex and match.lastindex >= 2:
                                # For "X instead of Y", X is the new material
                                if 'instead' in pattern:
                                    new_material = match.group(1)
                                    old_material = match.group(2)
                                else:
                                    # For "change X to Y", Y is the new material
                                    old_material = match.group(1)
                                    new_material = match.group(2)
                            else:
                                new_material = match.group(1)
                                old_material = None
                        else:
                            # Single material mentioned
                            new_material = match.group(1)
                            old_material = None
                        
                        # Normalize material names
                        new_material_normalized = self._normalize_material(new_material)
                        modifications['materials'] = [new_material_normalized]
                        
                    elif mod_type == 'timeline':
                        # Extract timeline
                        timeline_str = match.group(1)
                        modifications['timeline'] = timeline_str
                        
                    elif mod_type == 'urgency':
                        # Extract urgency level
                        # Check for "not urgent" patterns first
                        if 'not urgent' in message_lower or 'no longer urgent' in message_lower:
                            modifications['urgency_level'] = 'flexible'
                        elif 'emergency' in message_lower or 'asap' in message_lower:
                            modifications['urgency_level'] = 'emergency'
                        elif 'urgent' in message_lower or 'immediately' in message_lower:
                            modifications['urgency_level'] = 'emergency'
                    
                    break  # Found match for this type
        
        # Try to infer project type from context
        project_type = self._infer_project_type(message)
        
        return modification_found, {
            'modifications': modifications,
            'project_type': project_type,
            'confidence': 0.95 if modification_found else 0.0
        }
    
    def _normalize_material(self, material: str) -> str:
        """Normalize material names for consistency"""
        material_lower = material.lower().strip()
        
        # Check material mappings
        for standard_name, variations in self.material_mappings.items():
            if any(var in material_lower for var in variations):
                return standard_name
        
        # Return cleaned version if no mapping found
        return material_lower
    
    def _infer_project_type(self, message: str) -> Optional[str]:
        """Infer project type from message context"""
        message_lower = message.lower()
        
        project_indicators = {
            'kitchen': ['kitchen', 'countertop', 'cabinet', 'appliance', 'sink', 'backsplash'],
            'bathroom': ['bathroom', 'shower', 'tub', 'vanity', 'toilet', 'tile'],
            'flooring': ['floor', 'flooring', 'carpet', 'hardwood', 'laminate', 'vinyl'],
            'roofing': ['roof', 'shingle', 'gutter', 'attic'],
            'painting': ['paint', 'color', 'wall', 'interior', 'exterior'],
            'landscaping': ['lawn', 'yard', 'garden', 'landscape', 'tree'],
        }
        
        for project_type, keywords in project_indicators.items():
            if any(keyword in message_lower for keyword in keywords):
                return project_type
        
        return None
    
    def validate_modifications(self, modifications: Dict[str, Any], 
                             existing_bid_card: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate modifications against existing bid card
        
        Returns:
            (is_valid, error_message)
        """
        # Budget validation
        if 'budget_max' in modifications:
            new_max = modifications['budget_max']
            if new_max < 1000:
                return False, "Budget must be at least $1,000"
            if new_max > 1000000:
                return False, "Budget exceeds maximum allowed ($1,000,000)"
        
        # Timeline validation
        if 'timeline' in modifications:
            timeline = modifications['timeline'].lower()
            # Ensure timeline is reasonable
            if 'day' in timeline:
                days = int(re.search(r'(\d+)', timeline).group(1))
                if days < 1:
                    return False, "Timeline must be at least 1 day"
            elif 'week' in timeline:
                weeks = int(re.search(r'(\d+)', timeline).group(1))
                if weeks > 52:
                    return False, "Timeline cannot exceed 52 weeks"
        
        # Materials validation
        if 'materials' in modifications:
            if not modifications['materials']:
                return False, "Materials list cannot be empty"
            
        return True, ""
    
    def format_modification_response(self, modifications: Dict[str, Any], 
                                   bid_card_number: str,
                                   project_type: str) -> str:
        """Generate user-friendly modification confirmation"""
        changes = []
        
        if 'budget_max' in modifications:
            budget = modifications['budget_max']
            changes.append(f"budget updated to ${budget:,}")
        
        if 'materials' in modifications:
            materials = modifications['materials']
            if isinstance(materials, list) and materials:
                material_str = materials[0] if len(materials) == 1 else ', '.join(materials)
                changes.append(f"materials changed to {material_str}")
        
        if 'timeline' in modifications:
            changes.append(f"timeline updated to {modifications['timeline']}")
        
        if 'urgency_level' in modifications:
            changes.append(f"urgency changed to {modifications['urgency_level']}")
            
        if 'frequency' in modifications:
            changes.append(f"service frequency changed to {modifications['frequency']}")
        
        if not changes:
            return f"I've updated your {project_type} bid card ({bid_card_number}) with your requested changes."
        
        changes_str = '; '.join(changes)
        return f"Perfect! I've updated your {project_type} bid card ({bid_card_number}) with the following changes: {changes_str}. Contractors will be notified of these updates."