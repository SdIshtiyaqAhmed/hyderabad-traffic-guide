"""
Traffic controller for orchestrating traffic analysis workflow
"""
from datetime import datetime
from typing import Optional
import logging

from models.data_models import (
    TrafficConfig, TrafficAnalysis, CongestionResult, AreaInfo, CongestionLevel
)
from parsers.config_parser import ConfigParser
from scoring.scoring_engine import ScoringEngine
from reasoning.reasoning_engine import ReasoningEngine
from filtering.content_filter import ContentFilter, FilterPreferences


# Set up logging for error tracking
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class TrafficController:
    """Controller class to coordinate analysis workflow"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize traffic controller with configuration
        
        Args:
            config_path: Optional path to configuration file
        """
        self.parser = ConfigParser()
        self.config = None
        self.scoring_engine = None
        self.reasoning_engine = None
        self.content_filter = ContentFilter()
        self._initialization_error = None
        
        try:
            self.config = self.parser.load_config(config_path)
            
            # Validate configuration
            validation = self.parser.validate_config(self.config)
            if not validation.is_valid:
                logger.warning(f"Configuration validation issues: {validation.errors}")
                # Continue with potentially invalid config, but log the issues
            
            if validation.warnings:
                logger.info(f"Configuration warnings: {validation.warnings}")
            
            self.scoring_engine = ScoringEngine(self.config)
            self.reasoning_engine = ReasoningEngine(self.config)
            
        except FileNotFoundError as e:
            self._initialization_error = f"Configuration file not found. Please ensure the product.md file exists at the expected location. Error: {e}"
            logger.error(self._initialization_error)
        except Exception as e:
            self._initialization_error = f"Failed to initialize traffic controller due to configuration issues: {e}"
            logger.error(self._initialization_error)
    
    def analyze_route(self, origin: str, destination: str, 
                     departure_time: datetime) -> TrafficAnalysis:
        """
        Analyze route for traffic conditions and provide recommendations
        
        Args:
            origin: Starting location name
            destination: Ending location name
            departure_time: When the trip will start
            
        Returns:
            TrafficAnalysis with congestion, warnings, and recommendations
        """
        # Check if controller was initialized properly
        if self._initialization_error:
            return self._create_error_analysis(self._initialization_error)
        
        try:
            # Validate inputs
            if not origin or not origin.strip():
                return self._create_error_analysis("Origin location cannot be empty. Please provide a valid starting location.")
            
            if not destination or not destination.strip():
                return self._create_error_analysis("Destination location cannot be empty. Please provide a valid ending location.")
            
            if not departure_time:
                return self._create_error_analysis("Departure time is required. Please provide a valid departure time.")
            
            # Check if areas are known
            origin_info = self.get_area_info(origin)
            destination_info = self.get_area_info(destination)
            
            # Handle unknown areas
            if not origin_info.zone and not origin_info.is_hotspot:
                unknown_suggestion = self.suggest_area_addition(origin)
                return TrafficAnalysis(
                    congestion=CongestionResult(
                        level=self._get_safe_base_level(),
                        score=0,
                        triggered_rules=[],
                        departure_recommendation="Unable to provide recommendation for unknown area",
                        reasoning=unknown_suggestion
                    ),
                    hotspot_warnings=[],
                    departure_window="",
                    detailed_reasoning=unknown_suggestion
                )
            
            if not destination_info.zone and not destination_info.is_hotspot:
                unknown_suggestion = self.suggest_area_addition(destination)
                return TrafficAnalysis(
                    congestion=CongestionResult(
                        level=self._get_safe_base_level(),
                        score=0,
                        triggered_rules=[],
                        departure_recommendation="Unable to provide recommendation for unknown area",
                        reasoning=unknown_suggestion
                    ),
                    hotspot_warnings=[],
                    departure_window="",
                    detailed_reasoning=unknown_suggestion
                )
            
            # Calculate congestion using scoring engine with error handling
            try:
                congestion_result = self.scoring_engine.calculate_congestion(
                    origin, destination, departure_time
                )
            except Exception as e:
                logger.error(f"Error in congestion calculation: {e}")
                # Fall back to conservative estimate
                congestion_result = self._create_fallback_congestion_result(
                    f"Unable to calculate precise congestion due to system error. Using conservative estimate. Error: {e}"
                )
            
            # Generate hotspot warnings with error handling
            try:
                hotspot_warnings = self._generate_hotspot_warnings(origin, destination)
            except Exception as e:
                logger.error(f"Error generating hotspot warnings: {e}")
                hotspot_warnings = ["Unable to generate hotspot warnings due to system error"]
            
            # Generate departure window recommendation with error handling
            try:
                departure_window = self._generate_departure_window(congestion_result, departure_time)
            except Exception as e:
                logger.error(f"Error generating departure window: {e}")
                departure_window = "Unable to generate departure window recommendation"
            
            # Generate detailed reasoning with error handling
            try:
                detailed_reasoning = self.reasoning_engine.format_detailed_reasoning(congestion_result)
            except Exception as e:
                logger.error(f"Error generating detailed reasoning: {e}")
                detailed_reasoning = "Unable to generate detailed reasoning due to system error"
            
            return TrafficAnalysis(
                congestion=congestion_result,
                hotspot_warnings=hotspot_warnings,
                departure_window=departure_window,
                detailed_reasoning=detailed_reasoning
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in route analysis: {e}")
            return self._create_error_analysis(
                f"An unexpected error occurred during route analysis. Please try again or contact support if the problem persists. Error: {e}"
            )
    
    def analyze_route_with_preferences(self, origin: str, destination: str, 
                                     departure_time: datetime,
                                     avoid_nightlife: bool = False,
                                     prefer_family_friendly: bool = False) -> TrafficAnalysis:
        """
        Analyze route for traffic conditions with content filtering preferences
        
        Args:
            origin: Starting location name
            destination: Ending location name
            departure_time: When the trip will start
            avoid_nightlife: Whether to avoid nightlife-heavy corridors
            prefer_family_friendly: Whether to prefer family-friendly suggestions
            
        Returns:
            TrafficAnalysis with filtered content based on preferences
        """
        try:
            # Create filter preferences
            preferences = FilterPreferences(
                avoid_nightlife=avoid_nightlife,
                prefer_family_friendly=prefer_family_friendly
            )
            
            # Get base analysis
            analysis = self.analyze_route(origin, destination, departure_time)
            
            # Apply content filtering to all text outputs
            filtered_analysis = self._apply_content_filtering(analysis, preferences)
            
            return filtered_analysis
            
        except Exception as e:
            logger.error(f"Error in route analysis with preferences: {e}")
            return self._create_error_analysis(
                f"Unable to analyze route with preferences due to system error: {e}"
            )
    
    def get_area_info(self, area_name: str) -> AreaInfo:
        """
        Get information about a specific area
        
        Args:
            area_name: Name of the area to look up
            
        Returns:
            AreaInfo with zone classification and hotspot status
        """
        try:
            if not area_name or not area_name.strip():
                return AreaInfo(name="", zone=None, is_hotspot=False, nearby_landmark=None)
            
            # Handle case where config is not available
            if not self.config:
                return AreaInfo(name=area_name, zone=None, is_hotspot=False, nearby_landmark=None)
            
            area_lower = area_name.lower()
            
            # Check which zone the area belongs to
            zone = None
            if self.config.zones:
                for zone_name, areas in self.config.zones.items():
                    if areas:  # Check if areas list is not None
                        for area in areas:
                            if (area.lower() in area_lower or 
                                area_lower in area.lower() or
                                area.lower() == area_lower):
                                zone = zone_name
                                break
                    if zone:
                        break
            
            # Check if area is a hotspot
            is_hotspot = False
            if self.config.hotspots:
                is_hotspot = any(
                    hotspot.lower() in area_lower or 
                    area_lower in hotspot.lower() or
                    hotspot.lower() == area_lower
                    for hotspot in self.config.hotspots
                )
            
            # Find nearby landmark (use first matching hotspot as landmark)
            nearby_landmark = None
            if is_hotspot and self.config.hotspots:
                for hotspot in self.config.hotspots:
                    if (hotspot.lower() in area_lower or 
                        area_lower in hotspot.lower()):
                        nearby_landmark = hotspot
                        break
            
            return AreaInfo(
                name=area_name,
                zone=zone,
                is_hotspot=is_hotspot,
                nearby_landmark=nearby_landmark
            )
            
        except Exception as e:
            logger.error(f"Error getting area info for {area_name}: {e}")
            # Return safe default
            return AreaInfo(name=area_name, zone=None, is_hotspot=False, nearby_landmark=None)
    
    def suggest_area_addition(self, area_name: str) -> str:
        """
        Generate suggestion prompt for unknown area addition
        
        Args:
            area_name: Name of the unknown area
            
        Returns:
            Suggestion message for area addition
        """
        try:
            if not area_name or not area_name.strip():
                return "Please provide a valid area name for addition to the local dataset."
            
            return f"That area isn't in my local dataset yet—add it to product.md. " \
                   f"To add '{area_name}', please provide: area name, zone tag, nearby landmark, and hotspot status."
        except Exception as e:
            logger.error(f"Error generating area addition suggestion: {e}")
            return "Unable to generate area addition suggestion due to system error."
    
    def _create_error_analysis(self, error_message: str) -> TrafficAnalysis:
        """Create a TrafficAnalysis object for error cases"""
        return TrafficAnalysis(
            congestion=CongestionResult(
                level=CongestionLevel.HIGH,  # Conservative estimate for errors
                score=2,
                triggered_rules=["Error condition"],
                departure_recommendation="Please try again later",
                reasoning=error_message
            ),
            hotspot_warnings=[],
            departure_window="Unable to determine optimal departure window",
            detailed_reasoning=error_message
        )
    
    def _create_fallback_congestion_result(self, error_message: str) -> CongestionResult:
        """Create a fallback congestion result for calculation errors"""
        return CongestionResult(
            level=CongestionLevel.HIGH,  # Conservative estimate
            score=2,
            triggered_rules=["Fallback due to calculation error"],
            departure_recommendation="Consider avoiding peak hours as a precaution",
            reasoning=f"Using conservative traffic estimate. {error_message}"
        )
    
    def _get_safe_base_level(self) -> CongestionLevel:
        """Get a safe base congestion level, handling config errors"""
        try:
            if self.config and self.config.scoring_rules:
                return self.config.scoring_rules.base_score_level
            else:
                return CongestionLevel.LOW  # Safe default
        except Exception:
            return CongestionLevel.LOW  # Safe default
    
    def _generate_hotspot_warnings(self, origin: str, destination: str) -> list[str]:
        """Generate warnings for hotspot locations"""
        try:
            warnings = []
            
            # Check origin
            origin_info = self.get_area_info(origin)
            if origin_info.is_hotspot:
                warnings.append(f"Origin {origin} is a known traffic hotspot")
            
            # Check destination
            destination_info = self.get_area_info(destination)
            if destination_info.is_hotspot:
                warnings.append(f"Destination {destination} is a known traffic hotspot")
            
            return warnings
            
        except Exception as e:
            logger.error(f"Error generating hotspot warnings: {e}")
            return ["Unable to check for traffic hotspots due to system error"]
    
    def _generate_departure_window(self, congestion_result: CongestionResult, 
                                 departure_time: datetime) -> str:
        """Generate departure window recommendation"""
        try:
            if not congestion_result or not departure_time:
                return "Unable to generate departure window recommendation"
            
            if congestion_result.departure_recommendation == "leave now":
                return f"Optimal departure: now (around {departure_time.strftime('%H:%M')})"
            else:
                return f"Consider: {congestion_result.departure_recommendation}"
                
        except Exception as e:
            logger.error(f"Error generating departure window: {e}")
            return "Unable to generate departure window due to system error"
    
    def _apply_content_filtering(self, analysis: TrafficAnalysis, 
                               preferences: FilterPreferences) -> TrafficAnalysis:
        """Apply content filtering to traffic analysis results"""
        try:
            if not analysis or not preferences:
                return analysis
            
            # Filter congestion result text
            filtered_reasoning = self.content_filter.filter_text(
                analysis.congestion.reasoning, preferences
            )
            filtered_departure_rec = self.content_filter.filter_text(
                analysis.congestion.departure_recommendation, preferences
            )
            
            # Create filtered congestion result
            filtered_congestion = CongestionResult(
                level=analysis.congestion.level,
                score=analysis.congestion.score,
                triggered_rules=analysis.congestion.triggered_rules,
                departure_recommendation=filtered_departure_rec,
                reasoning=filtered_reasoning
            )
            
            # Filter other text fields
            filtered_hotspot_warnings = self.content_filter.filter_suggestions(
                analysis.hotspot_warnings, preferences
            )
            filtered_departure_window = self.content_filter.filter_text(
                analysis.departure_window, preferences
            )
            filtered_detailed_reasoning = self.content_filter.filter_text(
                analysis.detailed_reasoning, preferences
            )
            
            return TrafficAnalysis(
                congestion=filtered_congestion,
                hotspot_warnings=filtered_hotspot_warnings,
                departure_window=filtered_departure_window,
                detailed_reasoning=filtered_detailed_reasoning
            )
            
        except Exception as e:
            logger.error(f"Error applying content filtering: {e}")
            # Return original analysis if filtering fails
            return analysis