#!/usr/bin/env python3
"""
Better JAA Extractor - Updated with InstaBids 12 data points and fixed budget extraction
"""
import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional


class BetterJAAExtractor:
    """Extract all the meaningful data points from CIA conversations - UPDATED"""
    
    def extract_bid_card_data(self, conversation_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract all meaningful data from CIA conversation - INCLUDING INSTABIDS 12 POINTS
        """
        # Get messages and collected_info
        state = conversation_json.get('state', {})
        collected_info = state.get('collected_info', {})
        messages = state.get('messages', [])
        
        # Combine all user messages for analysis
        user_messages = []
        for msg in messages:
            if msg.get('role') == 'user':
                user_messages.append(msg.get('content', ''))
        
        full_conversation = ' '.join(user_messages)
        print(f"\nAnalyzing conversation: {full_conversation[:200]}...")
        
        # Extract all data points INCLUDING InstaBids 12
        bid_card = {
            # CORE IDENTIFICATION (1-3)
            'project_type': self._extract_project_type(full_conversation, collected_info),
            'service_type': self._extract_service_type(full_conversation, collected_info),
            'project_description': self._extract_detailed_description(full_conversation, collected_info),
            
            # BUDGET & TIMELINE (4-6)
            'budget_min': self._extract_real_budget_min(full_conversation, collected_info),
            'budget_max': self._extract_real_budget_max(full_conversation, collected_info),
            'budget_context': self._extract_budget_context(full_conversation, collected_info),
            'urgency_level': self._extract_urgency(full_conversation),
            'timeline_urgency': self._extract_timeline_urgency(full_conversation, collected_info),
            'urgency_reason': self._extract_urgency_reason(full_conversation),
            
            # LOCATION & PROPERTY (7-9)
            'location': self._extract_location(full_conversation, collected_info),
            'location_zip': self._extract_zip_code(full_conversation, collected_info),
            'property_details': self._extract_property_details(full_conversation, collected_info),
            'property_context': collected_info.get('property_context'),
            
            # PREFERENCES & REQUIREMENTS (10-11)
            'materials_preferences': self._extract_materials(full_conversation),
            'material_preferences': self._extract_materials(full_conversation),  # Duplicate for compatibility
            'special_requirements': self._extract_special_requirements(full_conversation, collected_info),
            'homeowner_preferences': self._extract_preferences(full_conversation),
            'concerns_issues': self._extract_concerns(full_conversation),
            
            # IMAGES (Keep existing)
            'images': collected_info.get('uploaded_photos', []),
            'image_analysis': collected_info.get('photo_analyses', []),
            
            # INSTABIDS SPECIFIC (12)
            'group_bidding_potential': self._extract_group_bidding_potential(full_conversation, collected_info),
            'intention_score': self._calculate_intention_score(full_conversation, collected_info),
            
            # CONTRACTOR REQUIREMENTS
            'contractor_requirements': self._extract_contractor_requirements(full_conversation, collected_info)
        }
        
        return bid_card
    
    def _extract_project_type(self, conversation: str, collected_info: Dict) -> str:
        """Extract project type from conversation"""
        # First check collected_info
        if collected_info.get('project_type'):
            return collected_info['project_type']
            
        text = conversation.lower()
        
        # Common project types
        project_types = {
            'lawn': ['lawn', 'grass', 'mowing', 'yard', 'landscaping'],
            'roofing': ['roof', 'shingles', 'leak', 'gutter'],
            'kitchen': ['kitchen', 'cabinets', 'countertop', 'appliances'],
            'bathroom': ['bathroom', 'toilet', 'shower', 'tub', 'vanity'],
            'flooring': ['floor', 'carpet', 'tile', 'hardwood', 'vinyl'],
            'painting': ['paint', 'wall', 'ceiling', 'interior', 'exterior'],
            'plumbing': ['plumb', 'pipe', 'water', 'drain', 'faucet'],
            'electrical': ['electric', 'outlet', 'wiring', 'light', 'switch'],
            'hvac': ['hvac', 'air condition', 'heating', 'ac', 'furnace'],
            'windows': ['window', 'door', 'glass'],
            'pool': ['pool', 'spa', 'hot tub'],
            'cleaning': ['clean', 'maid', 'housekeeping']
        }
        
        for project_type, keywords in project_types.items():
            if any(keyword in text for keyword in keywords):
                return project_type
        
        return 'general'
    
    def _extract_service_type(self, conversation: str, collected_info: Dict) -> str:
        """Extract InstaBids service type classification"""
        # Check collected_info first
        if collected_info.get('service_type'):
            return collected_info['service_type']
            
        text = conversation.lower()
        
        # Service type indicators
        service_types = {
            'installation': ['install', 'new', 'add', 'build', 'construct', 'replace'],
            'repair': ['repair', 'fix', 'broken', 'damaged', 'not working', 'leak', 'problem'],
            'ongoing_service': ['weekly', 'monthly', 'regular', 'maintenance', 'service', 'every'],
            'handyman': ['small job', 'quick fix', 'handyman', 'odd job', 'minor'],
            'appliance_repair': ['appliance', 'washer', 'dryer', 'refrigerator', 'dishwasher'],
            'labor_only': ['labor', 'help', 'assist', 'move', 'haul']
        }
        
        for service_type, keywords in service_types.items():
            if any(keyword in text for keyword in keywords):
                return service_type
        
        return 'installation'  # Default
    
    def _extract_real_budget_min(self, conversation: str, collected_info: Dict) -> int:
        """FIXED: Extract actual budget from conversation text"""
        # First check collected_info
        if collected_info.get('budget_min'):
            return int(collected_info['budget_min'])
            
        text = conversation.lower()
        
        # Updated patterns to handle single values better
        budget_patterns = [
            # Range patterns
            r'budget.*?\$?(\d{1,3}(?:,\d{3})*|\d+)\s*(?:-|to)\s*\$?(\d{1,3}(?:,\d{3})*|\d+)',
            r'\$?(\d{1,3}(?:,\d{3})*|\d+)\s*(?:-|to)\s*\$?(\d{1,3}(?:,\d{3})*|\d+).*?budget',
            # Single value patterns - FIXED
            r'budget.*?(?:around|about|approximately)?\s*\$?(\d{1,3}(?:,\d{3})*|\d+)',
            r'(?:around|about|approximately)\s*\$?(\d{1,3}(?:,\d{3})*|\d+).*?budget',
            r'\$?(\d{1,3}(?:,\d{3})*|\d+)\s*(?:budget|for.*?(?:work|job|project))'
        ]
        
        for pattern in budget_patterns:
            match = re.search(pattern, text)
            if match:
                # Remove commas and convert to int
                if len(match.groups()) >= 2 and match.group(2):  # Range pattern
                    return int(match.group(1).replace(',', ''))
                else:  # Single number
                    return int(match.group(1).replace(',', ''))
        
        return 5000  # Default
    
    def _extract_real_budget_max(self, conversation: str, collected_info: Dict) -> int:
        """FIXED: Extract actual budget max from conversation"""
        # First check collected_info
        if collected_info.get('budget_max'):
            return int(collected_info['budget_max'])
            
        text = conversation.lower()
        
        # Range patterns first
        range_patterns = [
            r'budget.*?\$?(\d{1,3}(?:,\d{3})*|\d+)\s*(?:-|to)\s*\$?(\d{1,3}(?:,\d{3})*|\d+)',
            r'\$?(\d{1,3}(?:,\d{3})*|\d+)\s*(?:-|to)\s*\$?(\d{1,3}(?:,\d{3})*|\d+).*?budget'
        ]
        
        for pattern in range_patterns:
            match = re.search(pattern, text)
            if match and len(match.groups()) >= 2 and match.group(2):
                return int(match.group(2).replace(',', ''))
        
        # Single value patterns - use same as min
        single_patterns = [
            r'budget.*?(?:around|about|approximately)?\s*\$?(\d{1,3}(?:,\d{3})*|\d+)',
            r'(?:around|about|approximately)\s*\$?(\d{1,3}(?:,\d{3})*|\d+).*?budget',
            r'\$?(\d{1,3}(?:,\d{3})*|\d+)\s*(?:budget|for.*?(?:work|job|project))'
        ]
        
        for pattern in single_patterns:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1).replace(',', ''))
        
        # If we found a min, use min * 1.2 as max
        min_budget = self._extract_real_budget_min(conversation, collected_info)
        if min_budget > 5000:  # Not default
            return int(min_budget * 1.2)
        
        return 15000  # Default
    
    def _extract_budget_context(self, conversation: str, collected_info: Dict) -> str:
        """Extract InstaBids budget context"""
        if collected_info.get('budget_context'):
            return collected_info['budget_context']
            
        text = conversation.lower()
        
        if any(phrase in text for phrase in ['budget', 'cost', 'price', 'spend', 'afford', '$']):
            if any(phrase in text for phrase in ['around', 'about', 'approximately']):
                return 'has_budget_range'
            elif any(phrase in text for phrase in ['max', 'maximum', 'up to', 'no more than']):
                return 'has_max_budget'
            else:
                return 'has_budget'
        
        return 'not_discussed'
    
    def _extract_timeline_urgency(self, conversation: str, collected_info: Dict) -> str:
        """Extract InstaBids timeline urgency"""
        if collected_info.get('timeline_urgency'):
            return collected_info['timeline_urgency']
            
        text = conversation.lower()
        
        if any(phrase in text for phrase in ['emergency', 'asap', 'immediately', 'urgent', 'right away']):
            return 'emergency'
        elif any(phrase in text for phrase in ['this week', 'soon', 'quickly', 'fast']):
            return 'urgent'
        elif any(phrase in text for phrase in ['flexible', 'no rush', 'whenever', 'planning']):
            return 'flexible'
        else:
            return 'planning'
    
    def _extract_urgency_reason(self, conversation: str) -> str:
        """Extract reason for urgency"""
        text = conversation.lower()
        
        if 'leak' in text:
            return 'Active leak or water damage'
        elif 'broken' in text or 'not working' in text:
            return 'System/component failure'
        elif 'event' in text or 'party' in text or 'guests' in text:
            return 'Upcoming event deadline'
        elif 'selling' in text or 'listing' in text:
            return 'Preparing property for sale'
        
        return None
    
    def _extract_zip_code(self, conversation: str, collected_info: Dict) -> str:
        """Extract zip code"""
        if collected_info.get('location_zip'):
            return collected_info['location_zip']
            
        zip_match = re.search(r'\b(\d{5})\b', conversation)
        return zip_match.group(1) if zip_match else None
    
    def _extract_group_bidding_potential(self, conversation: str, collected_info: Dict) -> bool:
        """Determine if project suitable for group bidding"""
        if collected_info.get('group_bidding_potential') is not None:
            return collected_info['group_bidding_potential']
            
        # Projects good for group bidding
        group_friendly = ['lawn', 'roofing', 'painting', 'cleaning', 'pool']
        project_type = self._extract_project_type(conversation, collected_info)
        
        return project_type in group_friendly
    
    def _calculate_intention_score(self, conversation: str, collected_info: Dict) -> int:
        """Calculate InstaBids intention score (1-10)"""
        if collected_info.get('intention_score'):
            return collected_info['intention_score']
            
        score = 5  # Base score
        
        # Positive indicators
        if self._extract_real_budget_min(conversation, collected_info) > 5000:  # Has real budget
            score += 2
        if self._extract_timeline_urgency(conversation, collected_info) in ['emergency', 'urgent']:
            score += 2
        if any(phrase in conversation.lower() for phrase in ['need', 'want', 'looking for', 'ready']):
            score += 1
            
        # Negative indicators
        if any(phrase in conversation.lower() for phrase in ['just curious', 'wondering', 'might', 'maybe']):
            score -= 2
        if self._extract_timeline_urgency(conversation, collected_info) == 'flexible':
            score -= 1
            
        return max(1, min(10, score))
    
    def _extract_urgency(self, conversation: str) -> str:
        """Extract urgency for database (emergency/week/month/flexible)"""
        text = conversation.lower()
        
        if any(word in text for word in ['asap', 'immediately', 'urgent', 'emergency', 'right away']):
            return 'emergency'
        elif any(word in text for word in ['this week', 'next week', 'within a week', 'soon']):
            return 'week' 
        elif any(word in text for word in ['month', 'next month', 'within a month']):
            return 'month'
        elif any(word in text for word in ['no rush', 'whenever', 'flexible', 'planning']):
            return 'flexible'
        
        return 'flexible'  # Default
    
    def _extract_location(self, conversation: str, collected_info: Dict) -> Dict[str, Any]:
        """Extract detailed location information"""
        # Start with collected_info address
        address = collected_info.get('address', '')
        
        # Parse zip code
        zip_match = re.search(r'\b(\d{5})\b', conversation or address)
        zip_code = zip_match.group(1) if zip_match else None
        
        # Extract city and state from conversation
        city = None
        state = None
        
        # Common patterns
        location_match = re.search(r'in\s+([A-Z][a-z]+),?\s+([A-Z][a-z]+)', conversation)
        if location_match:
            city = location_match.group(1)
            state = location_match.group(2)
        
        return {
            'address': address,
            'zip_code': zip_code,
            'city': city,
            'state': state,
            'full_location': f"{city}, {state} {zip_code}" if city and state and zip_code else address
        }
    
    def _extract_detailed_description(self, conversation: str, collected_info: Dict) -> str:
        """Extract detailed project description"""
        if collected_info.get('project_description'):
            return collected_info['project_description']
            
        # Look for descriptive phrases
        descriptions = []
        
        # Find sentences with project keywords
        sentences = conversation.split('.')
        for sentence in sentences:
            if any(word in sentence.lower() for word in ['need', 'want', 'looking', 'require', 'problem', 'issue']):
                descriptions.append(sentence.strip())
        
        return ' '.join(descriptions) if descriptions else 'Project details to be discussed'
    
    def _extract_property_details(self, conversation: str, collected_info: Dict) -> Dict[str, Any]:
        """Extract property type, size, access info"""
        details = {}
        
        # Property type
        if 'house' in conversation.lower():
            details['type'] = 'house'
        elif 'condo' in conversation.lower():
            details['type'] = 'condo'
        elif 'apartment' in conversation.lower():
            details['type'] = 'apartment'
        elif 'commercial' in conversation.lower():
            details['type'] = 'commercial'
        else:
            details['type'] = 'residential'
        
        # Size indicators
        size_match = re.search(r'(\d+)\s*(?:sq|square)\s*(?:ft|feet)', conversation.lower())
        if size_match:
            details['size'] = f"{size_match.group(1)} sq ft"
        
        # Story/floor info
        if '2 story' in conversation.lower() or 'two story' in conversation.lower():
            details['stories'] = 2
        elif '1 story' in conversation.lower() or 'single story' in conversation.lower():
            details['stories'] = 1
        
        return details
    
    def _extract_materials(self, conversation: str) -> List[str]:
        """Extract material preferences"""
        materials = []
        text = conversation.lower()
        
        # Common materials
        material_keywords = [
            'wood', 'vinyl', 'tile', 'carpet', 'hardwood', 'laminate',
            'granite', 'marble', 'quartz', 'concrete', 'asphalt',
            'shingle', 'metal', 'copper', 'pvc', 'ceramic'
        ]
        
        for material in material_keywords:
            if material in text:
                materials.append(material)
        
        return materials
    
    def _extract_special_requirements(self, conversation: str, collected_info: Dict) -> List[str]:
        """Extract any special requirements"""
        requirements = []
        text = conversation.lower()
        
        # Common requirements
        if 'permit' in text:
            requirements.append('Permits required')
        if 'hoa' in text:
            requirements.append('HOA approval needed')
        if 'insurance' in text:
            requirements.append('Insurance claim')
        if 'eco' in text or 'green' in text:
            requirements.append('Eco-friendly materials')
        if 'pet' in text:
            requirements.append('Pet-friendly')
        
        return requirements
    
    def _extract_preferences(self, conversation: str) -> Dict[str, Any]:
        """Extract homeowner preferences"""
        prefs = {}
        text = conversation.lower()
        
        # Communication preferences
        if 'text' in text or 'sms' in text:
            prefs['communication'] = 'text'
        elif 'email' in text:
            prefs['communication'] = 'email'
        elif 'call' in text or 'phone' in text:
            prefs['communication'] = 'phone'
        
        # Contractor preferences
        if 'licensed' in text:
            prefs['contractor_type'] = 'licensed_only'
        if 'local' in text:
            prefs['contractor_location'] = 'local_preferred'
        
        return prefs
    
    def _extract_concerns(self, conversation: str) -> List[str]:
        """Extract homeowner concerns"""
        concerns = []
        text = conversation.lower()
        
        concern_keywords = {
            'damage': 'Property damage',
            'leak': 'Water leak',
            'mold': 'Mold concerns',
            'safety': 'Safety issues',
            'code': 'Building code compliance',
            'noise': 'Noise concerns',
            'mess': 'Cleanliness during work',
            'cost': 'Cost concerns'
        }
        
        for keyword, concern in concern_keywords.items():
            if keyword in text:
                concerns.append(concern)
        
        return concerns
    
    def _extract_contractor_requirements(self, conversation: str, collected_info: Dict) -> Dict[str, Any]:
        """Extract contractor requirements"""
        requirements = {
            'contractor_count': 4,  # Default
            'specialties_required': [],
            'licenses_required': [],
            'equipment_needed': []
        }
        
        # Adjust contractor count based on project size
        budget_max = self._extract_real_budget_max(conversation, collected_info)
        if budget_max > 50000:
            requirements['contractor_count'] = 6
        elif budget_max > 25000:
            requirements['contractor_count'] = 5
        elif budget_max < 5000:
            requirements['contractor_count'] = 3
        
        # Specialties based on project type
        project_type = self._extract_project_type(conversation, collected_info)
        specialty_map = {
            'roofing': ['roofing', 'gutter installation'],
            'plumbing': ['plumbing', 'pipe fitting'],
            'electrical': ['electrical', 'wiring'],
            'hvac': ['hvac', 'refrigeration'],
            'pool': ['pool maintenance', 'pool construction']
        }
        
        requirements['specialties_required'] = specialty_map.get(project_type, [])
        
        # License requirements
        if project_type in ['electrical', 'plumbing', 'hvac']:
            requirements['licenses_required'] = [f"{project_type}_license"]
        
        return requirements