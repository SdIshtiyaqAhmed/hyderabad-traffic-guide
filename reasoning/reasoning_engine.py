"""
Reasoning engine for generating explanations and departure recommendations
"""
from datetime import datetime, time
from typing import List
import logging

from models.data_models import (
    TrafficConfig, CongestionResult, CongestionLevel
)


logger = logging.getLogger(__name__)


class ReasoningEngine:
    """Engine for generating explanations and departure recommendations"""
    
    def __init__(self, config: TrafficConfig):
        """Initialize reasoning engine with configuration"""
        self.config = config
        
        # Family-friendly content rules from product.md
        self.family_friendly_phrases = [
            "quiet area", "family-friendly location", "peaceful route",
            "suitable for families", "appropriate stop", "safe area"
        ]
    
    def generate_explanation(self, result: CongestionResult) -> str:
        """
        Generate brief explanation for congestion result
        
        Args:
            result: CongestionResult with triggered rules and score
            
        Returns:
            Brief explanation string referencing which rule triggered the score
        """
        try:
            if not result or not result.triggered_rules:
                return "No special traffic conditions detected."
            
            # Use the first triggered rule as primary explanation
            primary_rule = result.triggered_rules[0]
            
            # Safe access to explanation templates
            template = "Standard traffic analysis applied."
            if (self.config and self.config.explanation_templates and 
                primary_rule in self.config.explanation_templates):
                template = self.config.explanation_templates[primary_rule]
            else:
                template = f"{primary_rule} applied."
            
            # Ensure family-friendly language
            return self._ensure_family_friendly_language(template)
            
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return "Traffic analysis completed."
    
    def get_departure_recommendation(self, result: CongestionResult) -> str:
        """
        Generate departure recommendation based on congestion level
        
        Args:
            result: CongestionResult with congestion level and context
            
        Returns:
            Departure recommendation following "leave now" or "wait until specific time window" format
        """
        try:
            if not result:
                return "check traffic conditions before departing"
            
            if result.level == CongestionLevel.LOW:
                return "leave now"
            elif result.level == CongestionLevel.MEDIUM:
                return "leave now"
            else:  # HIGH
                # For high congestion, recommend waiting
                if result.triggered_rules and "Peak window triggered" in result.triggered_rules:
                    # Check if we can determine which peak window
                    if "IT corridor triggered" in result.triggered_rules:
                        return "wait until after 20:00"
                    else:
                        return "wait until after peak hours"
                else:
                    return "wait until traffic conditions improve"
                    
        except Exception as e:
            logger.error(f"Error generating departure recommendation: {e}")
            return "check traffic conditions before departing"
    
    def format_detailed_reasoning(self, result: CongestionResult) -> str:
        """
        Generate detailed reasoning using configuration templates
        
        Args:
            result: CongestionResult with all triggered rules and context
            
        Returns:
            Detailed reasoning string with full explanation
        """
        try:
            if not result:
                return "Unable to generate detailed reasoning due to missing result data."
            
            if not result.triggered_rules:
                return "No special traffic conditions detected. Base congestion level applied."
            
            reasoning_parts = []
            
            # Add explanation for each triggered rule
            for rule in result.triggered_rules:
                try:
                    template = "Standard analysis applied."
                    if (self.config and self.config.explanation_templates and 
                        rule in self.config.explanation_templates):
                        template = self.config.explanation_templates[rule]
                    else:
                        template = f"{rule} applied."
                    
                    reasoning_parts.append(self._ensure_family_friendly_language(template))
                except Exception as e:
                    logger.error(f"Error processing rule {rule}: {e}")
                    reasoning_parts.append(f"{rule} applied.")
            
            # Add score interpretation
            try:
                score_explanation = self._get_score_explanation(result.level, result.score)
                reasoning_parts.append(score_explanation)
            except Exception as e:
                logger.error(f"Error generating score explanation: {e}")
                reasoning_parts.append("Traffic analysis completed.")
            
            # Add departure recommendation reasoning
            try:
                departure_reasoning = self._get_departure_reasoning(result)
                reasoning_parts.append(departure_reasoning)
            except Exception as e:
                logger.error(f"Error generating departure reasoning: {e}")
                reasoning_parts.append("Consider current traffic conditions for departure timing.")
            
            return " ".join(reasoning_parts)
            
        except Exception as e:
            logger.error(f"Error formatting detailed reasoning: {e}")
            return "Traffic analysis completed with limited information."
    
    def handle_nightlife_request(self) -> str:
        """
        Handle requests for nightlife suggestions according to product.md rules
        
        Returns:
            Polite decline message focusing on commute efficiency
        """
        try:
            return ("I focus on commute efficiency and family-friendly travel guidance. "
                    "For the best travel experience, I recommend quiet areas and "
                    "family-appropriate stops along your route.")
        except Exception as e:
            logger.error(f"Error handling nightlife request: {e}")
            return "I focus on providing family-friendly travel guidance."
    
    def generate_family_friendly_suggestion(self, area_type: str = "stop") -> str:
        """
        Generate family-friendly suggestion text
        
        Args:
            area_type: Type of suggestion (stop, break, rest, etc.)
            
        Returns:
            Family-friendly suggestion text
        """
        try:
            suggestions = {
                "stop": "Consider a quiet rest area suitable for families",
                "break": "Take a peaceful break at a family-friendly location",
                "rest": "Find a safe and appropriate rest stop",
                "suggestion": "Here's a family-appropriate travel suggestion",
                "recommendation": "This route offers suitable options for family travel"
            }
            
            return suggestions.get(area_type, "Consider family-friendly options along your route")
            
        except Exception as e:
            logger.error(f"Error generating family-friendly suggestion: {e}")
            return "Consider appropriate options along your route"
    
    def _ensure_family_friendly_language(self, text: str) -> str:
        """Ensure text uses family-friendly language per product.md rules"""
        try:
            if not text:
                return text
            
            # Replace any potentially inappropriate terms with family-friendly alternatives
            text_lower = text.lower()
            
            # Check for nightlife terms and replace with neutral language
            nightlife_terms = ['pub', 'bar', 'club', 'nightclub', 'lounge', 'brewery']
            for term in nightlife_terms:
                if term in text_lower:
                    return "Consider alternative routes for optimal travel conditions."
            
            # Ensure suggestions use family-friendly phrasing
            if any(word in text_lower for word in ['stop', 'break', 'rest', 'suggest']):
                if 'quiet' not in text_lower and 'family' not in text_lower:
                    # Add family-friendly qualifier
                    text = text.replace('stop', 'quiet stop')
                    text = text.replace('break', 'family-friendly break')
                    text = text.replace('rest', 'peaceful rest')
            
            return text
            
        except Exception as e:
            logger.error(f"Error ensuring family-friendly language: {e}")
            return text  # Return original text if processing fails
    
    def _get_score_explanation(self, level: CongestionLevel, score: int) -> str:
        """Generate explanation for the final score"""
        try:
            if level == CongestionLevel.LOW:
                return "Overall congestion is expected to be low."
            elif level == CongestionLevel.MEDIUM:
                return "Moderate congestion is expected."
            else:  # HIGH
                if score >= 2:
                    return "High congestion is expected due to multiple factors."
                else:
                    return "High congestion is expected."
        except Exception as e:
            logger.error(f"Error generating score explanation: {e}")
            return "Traffic analysis completed."
    
    def _get_departure_reasoning(self, result: CongestionResult) -> str:
        """Generate reasoning for departure recommendation"""
        try:
            if not result:
                return "Consider current traffic conditions for departure timing."
            
            if result.level == CongestionLevel.LOW:
                return "Traffic conditions are favorable for immediate departure."
            elif result.level == CongestionLevel.MEDIUM:
                return "Traffic conditions are manageable for immediate departure."
            else:  # HIGH
                if result.triggered_rules and "Peak window triggered" in result.triggered_rules:
                    return "Consider waiting until after peak hours for better travel conditions."
                else:
                    return "Consider waiting for traffic conditions to improve."
                    
        except Exception as e:
            logger.error(f"Error generating departure reasoning: {e}")
            return "Consider current traffic conditions for departure timing."