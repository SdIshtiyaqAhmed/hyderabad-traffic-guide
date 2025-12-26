"""
Content filtering system for family-friendly recommendations
"""
import re
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class FilterPreferences:
    """User preferences for content filtering"""
    avoid_nightlife: bool = False
    prefer_family_friendly: bool = False


class ContentFilter:
    """System for filtering content based on family-friendly preferences"""
    
    def __init__(self):
        """Initialize content filter with filtering rules"""
        # Nightlife-related terms to filter out
        self.nightlife_terms = [
            'pub', 'bar', 'club', 'nightclub', 'disco', 'lounge', 'brewery',
            'wine', 'beer', 'alcohol', 'drinks', 'party', 'nightlife',
            'late night', 'after hours', 'cocktail', 'spirits', 'liquor'
        ]
        
        # Inappropriate content terms
        self.inappropriate_terms = [
            'adult', 'mature', '18+', 'restricted', 'explicit',
            'gambling', 'casino', 'betting'
        ]
        
        # Family-friendly replacement phrases
        self.family_friendly_replacements = {
            'stop': 'quiet rest area',
            'break': 'family-friendly break',
            'rest': 'peaceful rest stop',
            'suggestion': 'family-appropriate suggestion',
            'recommendation': 'suitable recommendation'
        }
        
        # Nightlife-heavy corridors in Hyderabad
        self.nightlife_corridors = [
            'jubilee hills', 'banjara hills', 'gachibowli', 'hitech city',
            'madhapur', 'kondapur'
        ]
    
    def filter_text(self, text: str, preferences: FilterPreferences) -> str:
        """
        Filter text content based on preferences
        
        Args:
            text: Original text to filter
            preferences: User filtering preferences
            
        Returns:
            Filtered text with inappropriate content removed/replaced
        """
        if not text:
            return text
        
        filtered_text = text
        
        if preferences.avoid_nightlife or preferences.prefer_family_friendly:
            # Remove nightlife terms
            filtered_text = self._remove_nightlife_content(filtered_text)
            
            # Remove inappropriate content
            filtered_text = self._remove_inappropriate_content(filtered_text)
        
        if preferences.prefer_family_friendly:
            # Apply family-friendly replacements
            filtered_text = self._apply_family_friendly_replacements(filtered_text)
        
        return filtered_text
    
    def filter_suggestions(self, suggestions: List[str], preferences: FilterPreferences) -> List[str]:
        """
        Filter a list of suggestions based on preferences
        
        Args:
            suggestions: List of suggestion strings
            preferences: User filtering preferences
            
        Returns:
            Filtered list of suggestions
        """
        if not preferences.avoid_nightlife and not preferences.prefer_family_friendly:
            return suggestions
        
        filtered_suggestions = []
        
        for suggestion in suggestions:
            # Filter the suggestion text
            filtered_suggestion = self.filter_text(suggestion, preferences)
            
            # Only include if it passes content checks
            if self._passes_content_check(filtered_suggestion, preferences):
                filtered_suggestions.append(filtered_suggestion)
        
        return filtered_suggestions
    
    def should_filter_corridor(self, corridor_name: str, preferences: FilterPreferences) -> bool:
        """
        Check if a corridor should be filtered based on nightlife content
        
        Args:
            corridor_name: Name of the corridor/area
            preferences: User filtering preferences
            
        Returns:
            True if corridor should be filtered out
        """
        if not preferences.avoid_nightlife:
            return False
        
        corridor_lower = corridor_name.lower()
        
        # Check if it's a known nightlife-heavy corridor
        return any(nightlife_area in corridor_lower for nightlife_area in self.nightlife_corridors)
    
    def get_family_friendly_alternative(self, original_text: str) -> str:
        """
        Get family-friendly alternative for potentially inappropriate content
        
        Args:
            original_text: Original text that may need alternatives
            
        Returns:
            Family-friendly alternative text
        """
        # If text contains nightlife references, provide neutral alternative
        text_lower = original_text.lower()
        
        if any(term in text_lower for term in self.nightlife_terms):
            return "Consider alternative routes for a more suitable travel experience."
        
        if any(term in text_lower for term in self.inappropriate_terms):
            return "Please consider family-appropriate travel options."
        
        return original_text
    
    def _remove_nightlife_content(self, text: str) -> str:
        """Remove nightlife-related content from text"""
        filtered_text = text
        
        for term in self.nightlife_terms:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(term) + r'\b'
            filtered_text = re.sub(pattern, '', filtered_text, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        filtered_text = re.sub(r'\s+', ' ', filtered_text).strip()
        
        return filtered_text
    
    def _remove_inappropriate_content(self, text: str) -> str:
        """Remove inappropriate content from text"""
        filtered_text = text
        
        for term in self.inappropriate_terms:
            pattern = r'\b' + re.escape(term) + r'\b'
            filtered_text = re.sub(pattern, '', filtered_text, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        filtered_text = re.sub(r'\s+', ' ', filtered_text).strip()
        
        return filtered_text
    
    def _apply_family_friendly_replacements(self, text: str) -> str:
        """Apply family-friendly replacements to text"""
        filtered_text = text
        
        for original, replacement in self.family_friendly_replacements.items():
            # Only replace if the context suggests it's about suggestions/recommendations
            if 'suggest' in text.lower() or 'recommend' in text.lower():
                pattern = r'\b' + re.escape(original) + r'\b'
                filtered_text = re.sub(pattern, replacement, filtered_text, flags=re.IGNORECASE)
        
        return filtered_text
    
    def _passes_content_check(self, text: str, preferences: FilterPreferences) -> bool:
        """Check if text passes content filtering requirements"""
        if not text or not text.strip():
            return False
        
        text_lower = text.lower()
        
        if preferences.avoid_nightlife:
            # Should not contain nightlife terms
            if any(term in text_lower for term in self.nightlife_terms):
                return False
        
        if preferences.prefer_family_friendly:
            # Should not contain inappropriate terms
            if any(term in text_lower for term in self.inappropriate_terms):
                return False
        
        return True