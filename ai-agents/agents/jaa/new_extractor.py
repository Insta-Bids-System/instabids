"""
NEW JAA Extractor - Updated for InstaBids 12 Data Points System
"""
import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional


class NewJAAExtractor:
    """Extract InstaBids-focused data from CIA conversations"""
    
    def extract_bid_card_data(self, conversation_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract all 12 InstaBids data points from CIA conversation
        """
        # Get messages and collected_info from new state structure
        state = conversation_json.get('state', {})
        collected_info = state.get('collected_info', {})
        messages = state.get('messages', [])
        
        # Combine user messages for fallback extraction
        user_messages = []
        for msg in messages:
            if msg.get('role') == 'user':
                user_messages.append(msg.get('content', ''))
        
        full_conversation = ' '.join(user_messages)
        print(f"\nExtracting from conversation: {full_conversation[:200]}...")
        
        # Build comprehensive bid card data
        bid_card = {
            # CORE PROJECT INFO (1-3)
            'project_type': self._extract_project_type(collected_info, full_conversation),
            'service_type': self._extract_service_type(collected_info, full_conversation),
            'project_description': self._extract_project_description(collected_info, full_conversation),
            
            # CONTEXT & MOTIVATION (4-6)
            'budget_context': self._extract_budget_context(collected_info, full_conversation),
            'timeline_urgency': self._extract_timeline_urgency(collected_info, full_conversation),
            'urgency_reason': collected_info.get('urgency_reason', 'Not specified'),
            'location_zip': collected_info.get('location_zip') or self._extract_zip_code(full_conversation),
            
            # SMART OPPORTUNITIES (7-8)
            'group_bidding_potential': self._assess_group_bidding_potential(collected_info, full_conversation),
            'property_context': self._extract_property_context(collected_info, full_conversation),
            
            # SUPPORTING INFO (9-11)
            'material_preferences': collected_info.get('material_preferences'),
            'images': collected_info.get('uploaded_photos', []),
            'image_analysis': collected_info.get('photo_analyses', []),
            'special_requirements': collected_info.get('special_requirements'),
            
            # INTERNAL SCORING (12)
            'intention_score': self._calculate_intention_score(collected_info, full_conversation),
            
            # EXTRACTED BUSINESS DATA
            'budget_min': self._extract_budget_min(collected_info, full_conversation),
            'budget_max': self._extract_budget_max(collected_info, full_conversation),
            'urgency_level': self._map_urgency_to_level(collected_info.get('timeline_urgency')),
            
            # CONTRACTOR REQUIREMENTS
            'contractor_requirements': self._extract_contractor_requirements(collected_info, full_conversation)
        }
        
        return bid_card
    
    def _extract_project_type(self, collected_info: Dict, conversation: str) -> str:
        """Extract high-level project category"""
        # Check collected_info first
        if collected_info.get('project_type'):
            return collected_info['project_type']
        
        # Fallback to conversation analysis
        text = conversation.lower()
        
        # Enhanced project type mapping
        project_types = [
            ('lawn care', ['lawn', 'grass', 'mowing', 'yard work', 'landscaping', 'overgrown', 'weed', 'fertilize']),
            ('roofing', ['roof', 'shingle', 'leak', 'gutter', 'roofing', 'eaves', 'soffit']),
            ('kitchen remodel', ['kitchen', 'cabinets', 'countertop', 'appliances', 'backsplash']),
            ('bathroom remodel', ['bathroom', 'shower', 'tub', 'vanity', 'toilet', 'tile']),
            ('painting', ['paint', 'painting', 'interior paint', 'exterior paint', 'primer']),
            ('flooring', ['floor', 'carpet', 'hardwood', 'tile', 'laminate', 'vinyl']),
            ('plumbing', ['plumb', 'pipe', 'water', 'drain', 'faucet', 'toilet', 'leak']),
            ('electrical', ['electric', 'wiring', 'outlet', 'panel', 'lighting', 'switch']),
            ('hvac', ['hvac', 'air condition', 'heating', 'cooling', 'ac', 'furnace', 'duct']),
            ('cleaning', ['clean', 'cleaning', 'maid', 'housekeeping', 'deep clean']),
            ('handyman', ['handyman', 'repair', 'fix', 'maintenance', 'odd job']),
            ('mold remediation', ['mold', 'mildew', 'fungus', 'black mold', 'mold removal']),
            ('pressure washing', ['pressure wash', 'power wash', 'clean driveway', 'wash house']),
            ('tree service', ['tree', 'branch', 'trim', 'remove tree', 'stump']),
            ('fence', ['fence', 'fencing', 'gate', 'privacy fence', 'chain link']),
            ('driveway', ['driveway', 'concrete', 'asphalt', 'paving', 'sealing']),
            ('pool service', ['pool', 'swimming pool', 'pool cleaning', 'pool repair'])
        ]
        
        for project_type, keywords in project_types:
            if any(keyword in text for keyword in keywords):
                return project_type
        
        return 'General Home Improvement'
    
    def _extract_service_type(self, collected_info: Dict, conversation: str) -> str:
        """Classify the type of service needed"""
        # Check collected_info first
        if collected_info.get('service_type'):
            return collected_info['service_type']
        
        text = conversation.lower()
        
        # Service type classification based on keywords
        service_keywords = {
            'installation': ['new', 'install', 'replace', 'remodel', 'renovation', 'build', 'putting in', 'add'],
            'repair': ['repair', 'fix', 'broken', 'damaged', 'not working', 'problem', 'issue', 'crack', 'leak'],
            'ongoing_service': ['weekly', 'monthly', 'regular', 'maintenance', 'service', 'cleaning', 'every'],
            'handyman': ['small job', 'quick fix', 'handyman', 'odd job', 'minor', 'simple', 'help with'],
            'appliance_repair': ['washer', 'dryer', 'dishwasher', 'refrigerator', 'oven', 'microwave', 'ac unit'],
            'labor_only': ['labor only', 'just need someone', 'help moving', 'need muscle', 'no materials']
        }
        
        # Score each service type
        scores = {}
        for service_type, keywords in service_keywords.items():
            scores[service_type] = sum(1 for keyword in keywords if keyword in text)
        
        # Return highest scoring service type
        if scores:
            best_service = max(scores, key=scores.get)
            if scores[best_service] > 0:
                return best_service
        
        # Default based on project type
        project_type = self._extract_project_type(collected_info, conversation)
        if 'care' in project_type or 'clean' in project_type:
            return 'ongoing_service'
        elif 'repair' in conversation or 'fix' in conversation:
            return 'repair'
        else:
            return 'installation'
    
    def _extract_project_description(self, collected_info: Dict, conversation: str) -> str:
        """Extract detailed project description"""
        if collected_info.get('project_description'):
            return collected_info['project_description']
        
        # Build description from conversation
        description_parts = []
        
        # Add project type context
        project_type = self._extract_project_type(collected_info, conversation)
        service_type = self._extract_service_type(collected_info, conversation)
        
        description_parts.append(f"{service_type.replace('_', ' ').title()} for {project_type}")
        
        # Add key details from conversation
        text = conversation.lower()
        
        # Extract specific work mentioned
        work_mentions = []
        if 'mowing' in text: work_mentions.append('mowing')
        if 'edging' in text: work_mentions.append('edging')
        if 'trim' in text: work_mentions.append('trimming')
        if 'clean' in text: work_mentions.append('cleaning')
        if 'repair' in text: work_mentions.append('repairs')
        if 'install' in text: work_mentions.append('installation')
        
        if work_mentions:
            description_parts.append(f"Including: {', '.join(work_mentions)}")
        
        # Add urgency context if available
        urgency_reason = collected_info.get('urgency_reason')
        if urgency_reason:
            description_parts.append(f"Reason: {urgency_reason}")
        
        return '. '.join(description_parts)
    
    def _extract_budget_context(self, collected_info: Dict, conversation: str) -> str:
        """Extract budget context (not forcing specific amounts)"""
        if collected_info.get('budget_context'):
            return collected_info['budget_context']
        
        text = conversation.lower()
        
        # Classify budget context
        if any(phrase in text for phrase in ['got quote', 'already quoted', 'contractor said']):
            return 'has_quotes'
        elif any(phrase in text for phrase in ['budget', '$', 'cost', 'price', 'spend']):
            return 'has_budget_range'
        elif any(phrase in text for phrase in ['explore', 'looking at', 'research', 'idea']):
            return 'exploring_options'
        elif any(phrase in text for phrase in ['dream', 'someday', 'future', 'maybe']):
            return 'dream_project'
        else:
            return 'not_discussed'
    
    def _extract_timeline_urgency(self, collected_info: Dict, conversation: str) -> str:
        """Extract timeline urgency level"""
        if collected_info.get('timeline_urgency'):
            return collected_info['timeline_urgency']
        
        text = conversation.lower()
        
        # Emergency indicators
        if any(phrase in text for phrase in ['emergency', 'asap', 'immediately', 'urgent', 'right away']):
            return 'emergency'
        
        # Urgent indicators  
        if any(phrase in text for phrase in ['this week', 'soon', 'quickly', 'fast']):
            return 'urgent'
        
        # Planning indicators
        if any(phrase in text for phrase in ['planning', 'future', 'someday', 'eventually']):
            return 'planning'
        
        # Default to flexible
        return 'flexible'
    
    def _assess_group_bidding_potential(self, collected_info: Dict, conversation: str) -> bool:
        """Assess if project is good for group bidding"""
        if collected_info.get('group_bidding_potential') is not None:
            return collected_info['group_bidding_potential']
        
        project_type = self._extract_project_type(collected_info, conversation)
        timeline_urgency = self._extract_timeline_urgency(collected_info, conversation)
        
        # Good candidates for group bidding
        group_friendly_projects = [
            'lawn care', 'roofing', 'driveway', 'fence', 'exterior painting',
            'pressure washing', 'tree service', 'gutter cleaning'
        ]
        
        # Must not be emergency/urgent
        if timeline_urgency in ['emergency', 'urgent']:
            return False
        
        # Must be standardized work type
        return any(project in project_type for project in group_friendly_projects)
    
    def _extract_property_context(self, collected_info: Dict, conversation: str) -> Optional[str]:
        """Extract property context only if relevant"""
        if collected_info.get('property_context'):
            return collected_info['property_context']
        
        text = conversation.lower()
        context_parts = []
        
        # Property size mentions
        if any(size in text for size in ['large', 'big', 'huge', 'massive']):
            context_parts.append('Large property')
        elif any(size in text for size in ['small', 'tiny', 'compact']):
            context_parts.append('Small property')
        
        # Access mentions
        if any(access in text for access in ['gated', 'restricted', 'hoa', 'apartment']):
            context_parts.append('Restricted access')
        
        # Special features
        if 'pool' in text:
            context_parts.append('Has pool')
        if 'deck' in text:
            context_parts.append('Has deck')
        
        return '; '.join(context_parts) if context_parts else None
    
    def _calculate_intention_score(self, collected_info: Dict, conversation: str) -> int:
        """Calculate 1-10 intention score"""
        if collected_info.get('intention_score'):
            return collected_info['intention_score']
        
        score = 5  # Start neutral
        text = conversation.lower()
        
        # Positive factors
        if self._extract_timeline_urgency(collected_info, conversation) == 'emergency':
            score += 3
        elif self._extract_timeline_urgency(collected_info, conversation) == 'urgent':
            score += 2
        
        if any(phrase in text for phrase in ['ready', 'need to', 'have to', 'must']):
            score += 1
        
        if any(phrase in text for phrase in ['budget', 'quote', 'price', '$']):
            score += 1
        
        if collected_info.get('uploaded_photos'):
            score += 1
        
        # Negative factors
        if any(phrase in text for phrase in ['maybe', 'thinking', 'exploring', 'someday']):
            score -= 2
        
        if 'future' in text:
            score -= 1
        
        # Clamp to 1-10 range
        return max(1, min(10, score))
    
    def _extract_budget_min(self, collected_info: Dict, conversation: str) -> int:
        """Extract minimum budget if mentioned"""
        if collected_info.get('budget_min'):
            return int(collected_info['budget_min'])
        
        # Parse dollar amounts from conversation
        text = conversation.lower()
        amounts = re.findall(r'\$?(\d{1,3}(?:,\d{3})*)', text)
        
        if amounts:
            # Use first reasonable amount as minimum
            for amount in amounts:
                value = int(amount.replace(',', ''))
                if 50 <= value <= 100000:  # Reasonable project range
                    return value
        
        # Default estimates by project type
        project_type = self._extract_project_type(collected_info, conversation)
        
        defaults = {
            'lawn care': 80,
            'handyman': 150,
            'cleaning': 100,
            'painting': 1000,
            'plumbing': 300,
            'electrical': 400,
            'roofing': 5000,
            'kitchen remodel': 15000,
            'bathroom remodel': 8000
        }
        
        for proj_type, default_min in defaults.items():
            if proj_type in project_type:
                return default_min
        
        return 500  # General default
    
    def _extract_budget_max(self, collected_info: Dict, conversation: str) -> int:
        """Extract maximum budget if mentioned"""
        if collected_info.get('budget_max'):
            return int(collected_info['budget_max'])
        
        # Use budget_min * 1.5 as reasonable maximum
        budget_min = self._extract_budget_min(collected_info, conversation)
        return int(budget_min * 1.5)
    
    def _map_urgency_to_level(self, timeline_urgency: Optional[str]) -> str:
        """Map timeline urgency to database urgency level"""
        mapping = {
            'emergency': 'emergency',
            'urgent': 'week',
            'flexible': 'flexible',
            'planning': 'flexible'
        }
        return mapping.get(timeline_urgency, 'flexible')
    
    def _extract_zip_code(self, conversation: str) -> Optional[str]:
        """Extract zip code from conversation"""
        # Find 5-digit zip codes
        zip_matches = re.findall(r'\b(\d{5})\b', conversation)
        return zip_matches[0] if zip_matches else None
    
    def _extract_contractor_requirements(self, collected_info: Dict, conversation: str) -> Dict[str, Any]:
        """Extract contractor requirements"""
        service_type = self._extract_service_type(collected_info, conversation)
        project_type = self._extract_project_type(collected_info, conversation)
        
        # Determine contractor count based on service type and project
        if service_type == 'ongoing_service':
            contractor_count = 2  # Fewer needed for ongoing services
        elif service_type == 'handyman':
            contractor_count = 3  # Standard for handyman
        elif 'remodel' in project_type:
            contractor_count = 5  # More for complex projects
        else:
            contractor_count = 3  # Standard default
        
        return {
            'contractor_count': contractor_count,
            'specialties_required': [service_type, project_type],
            'experience_level': 'standard'
        }