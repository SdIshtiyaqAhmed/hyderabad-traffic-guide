"""
Scoring engine for calculating traffic congestion scores
"""
from datetime import datetime, time
from typing import List, Tuple
import logging

from models.data_models import (
    TrafficConfig, CongestionResult, CongestionLevel, AreaInfo
)
from reasoning.reasoning_engine import ReasoningEngine


logger = logging.getLogger(__name__)


class ScoringEngine:
    """Engine for computing congestion scores using configuration rules"""
    
    def __init__(self, config: TrafficConfig):
        """Initialize scoring engine with configuration"""
        self.config = config
        self.reasoning_engine = None
        
        try:
            self.reasoning_engine = ReasoningEngine(config)
        except Exception as e:
            logger.error(f"Failed to initialize reasoning engine: {e}")
            # Continue without reasoning engine, will use fallbacks
    
    def calculate_congestion(self, origin: str, destination: str, 
                           departure_time: datetime) -> CongestionResult:
        """
        Calculate congestion score for a route at a specific time
        
        Args:
            origin: Starting location name
            destination: Ending location name  
            departure_time: When the trip will start
            
        Returns:
            CongestionResult with level, score, and reasoning
        """
        try:
            # Validate inputs
            if not origin or not destination or not departure_time:
                return self._create_error_result("Invalid input parameters for congestion calculation")
            
            # Start with base score (Low = 0, Medium = 1, High = 2)
            score = 0
            triggered_rules = []
            
            # Apply peak window penalty with error handling
            try:
                peak_penalty = self._apply_peak_window_penalty(departure_time)
                if peak_penalty > 0:
                    score += peak_penalty
                    triggered_rules.append("Peak window triggered")
            except Exception as e:
                logger.error(f"Error applying peak window penalty: {e}")
                # Continue without peak penalty
            
            # Apply IT corridor multiplier with error handling
            try:
                corridor_penalty = self._apply_corridor_multiplier(
                    [origin, destination], departure_time
                )
                if corridor_penalty > 0:
                    score += corridor_penalty
                    triggered_rules.append("IT corridor triggered")
            except Exception as e:
                logger.error(f"Error applying corridor multiplier: {e}")
                # Continue without corridor penalty
            
            # Apply hotspot penalty with error handling
            try:
                hotspot_penalty = self._apply_hotspot_penalty(
                    [origin, destination], departure_time
                )
                if hotspot_penalty > 0:
                    score += hotspot_penalty
                    triggered_rules.append("Hotspot triggered")
            except Exception as e:
                logger.error(f"Error applying hotspot penalty: {e}")
                # Continue without hotspot penalty
            
            # Apply weekend adjustment with error handling
            try:
                weekend_adjustment = self._apply_weekend_adjustment(
                    departure_time, [origin, destination]
                )
                if weekend_adjustment != 0:
                    score += weekend_adjustment
                    if weekend_adjustment < 0:
                        triggered_rules.append("Weekend adjustment")
            except Exception as e:
                logger.error(f"Error applying weekend adjustment: {e}")
                # Continue without weekend adjustment
            
            # Cap score at High level (2) and floor at Low level (0)
            score = min(max(score, 0), 2)
            
            # Convert score to congestion level
            if score == 0:
                level = CongestionLevel.LOW
            elif score == 1:
                level = CongestionLevel.MEDIUM
            else:
                level = CongestionLevel.HIGH
            
            # Create initial result
            result = CongestionResult(
                level=level,
                score=score,
                triggered_rules=triggered_rules,
                departure_recommendation="",  # Will be set by reasoning engine
                reasoning=""  # Will be set by reasoning engine
            )
            
            # Generate reasoning and departure recommendation using reasoning engine
            try:
                if self.reasoning_engine:
                    reasoning = self.reasoning_engine.generate_explanation(result)
                    departure_recommendation = self.reasoning_engine.get_departure_recommendation(result)
                else:
                    reasoning = self._generate_fallback_reasoning(result)
                    departure_recommendation = self._generate_fallback_departure_recommendation(result)
                
                # Update result with reasoning engine outputs
                result.reasoning = reasoning
                result.departure_recommendation = departure_recommendation
                
            except Exception as e:
                logger.error(f"Error generating reasoning: {e}")
                result.reasoning = self._generate_fallback_reasoning(result)
                result.departure_recommendation = self._generate_fallback_departure_recommendation(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Unexpected error in congestion calculation: {e}")
            return self._create_error_result(f"Unable to calculate congestion due to system error: {e}")
    
    def _apply_peak_window_penalty(self, departure_time: datetime) -> int:
        """Apply penalty for peak window times"""
        try:
            if not departure_time:
                return 0
            
            current_time = departure_time.time()
            is_weekday = departure_time.weekday() < 5  # Monday = 0, Sunday = 6
            
            if not is_weekday:
                return 0
            
            penalty = 0
            
            # Check morning peak with safe access
            if (self.config and self.config.peak_windows and 
                self.config.peak_windows.weekday_morning and
                self._time_in_range(current_time, self.config.peak_windows.weekday_morning)):
                penalty += 1
            
            # Check evening peak with safe access
            if (self.config and self.config.peak_windows and 
                self.config.peak_windows.weekday_evening and
                self._time_in_range(current_time, self.config.peak_windows.weekday_evening)):
                penalty += 1
                
                # Extra penalty for heaviest band (18:00-19:00)
                if time(18, 0) <= current_time <= time(19, 0):
                    penalty += 1
            
            return penalty
            
        except Exception as e:
            logger.error(f"Error in peak window penalty calculation: {e}")
            return 0  # Safe fallback
    
    def _apply_corridor_multiplier(self, locations: List[str], departure_time: datetime) -> int:
        """Apply IT corridor multiplier during peak times"""
        try:
            if not locations or not departure_time:
                return 0
            
            is_weekday = departure_time.weekday() < 5
            if not is_weekday:
                return 0
            
            # Check if any location is in IT corridor with safe access
            if not (self.config and self.config.zones):
                return 0
            
            it_corridor_areas = self.config.zones.get('zone_it_corridor', [])
            if not it_corridor_areas:
                return 0
            
            has_it_corridor = any(
                any(area.lower() in location.lower() or location.lower() in area.lower() 
                    for area in it_corridor_areas if area)
                for location in locations if location
            )
            
            if not has_it_corridor:
                return 0
            
            # Check if time overlaps with peak windows
            current_time = departure_time.time()
            is_peak_time = False
            
            if (self.config.peak_windows and self.config.peak_windows.weekday_morning and
                self._time_in_range(current_time, self.config.peak_windows.weekday_morning)):
                is_peak_time = True
            
            if (self.config.peak_windows and self.config.peak_windows.weekday_evening and
                self._time_in_range(current_time, self.config.peak_windows.weekday_evening)):
                is_peak_time = True
            
            return 1 if is_peak_time else 0
            
        except Exception as e:
            logger.error(f"Error in corridor multiplier calculation: {e}")
            return 0  # Safe fallback
    
    def _apply_hotspot_penalty(self, locations: List[str], departure_time: datetime) -> int:
        """Apply penalty for hotspot locations during peak times"""
        try:
            if not locations or not departure_time:
                return 0
            
            current_time = departure_time.time()
            is_weekday = departure_time.weekday() < 5
            
            # Check if any location is a hotspot with safe access
            if not (self.config and self.config.hotspots):
                return 0
            
            has_hotspot = any(
                any(hotspot.lower() in location.lower() or location.lower() in hotspot.lower()
                    for hotspot in self.config.hotspots if hotspot)
                for location in locations if location
            )
            
            if not has_hotspot:
                return 0
            
            # Apply penalty during peak windows
            is_peak_time = False
            
            if is_weekday and self.config.peak_windows:
                if (self.config.peak_windows.weekday_morning and
                    self._time_in_range(current_time, self.config.peak_windows.weekday_morning)):
                    is_peak_time = True
                
                if (self.config.peak_windows.weekday_evening and
                    self._time_in_range(current_time, self.config.peak_windows.weekday_evening)):
                    is_peak_time = True
            else:
                # Weekend: hotspots can still be busy around major areas
                is_peak_time = True
            
            return 1 if is_peak_time else 0
            
        except Exception as e:
            logger.error(f"Error in hotspot penalty calculation: {e}")
            return 0  # Safe fallback
    
    def _apply_weekend_adjustment(self, departure_time: datetime, locations: List[str]) -> int:
        """Apply weekend traffic adjustment"""
        try:
            if not departure_time or not locations:
                return 0
            
            is_weekend = departure_time.weekday() >= 5  # Saturday = 5, Sunday = 6
            
            if not is_weekend:
                return 0
            
            # Check if near hotspots with safe access
            if not (self.config and self.config.hotspots):
                return -1  # Default weekend reduction if no hotspot data
            
            has_hotspot = any(
                any(hotspot.lower() in location.lower() or location.lower() in hotspot.lower()
                    for hotspot in self.config.hotspots if hotspot)
                for location in locations if location
            )
            
            # Reduce congestion unless near hotspots
            return 0 if has_hotspot else -1
            
        except Exception as e:
            logger.error(f"Error in weekend adjustment calculation: {e}")
            return 0  # Safe fallback
    
    def _time_in_range(self, current_time: time, time_range) -> bool:
        """Check if current time falls within a time range"""
        try:
            if not time_range or not current_time:
                return False
            
            start_time = time_range.start
            end_time = time_range.end
            
            if not start_time or not end_time:
                return False
            
            # Handle ranges that cross midnight
            if start_time <= end_time:
                return start_time <= current_time <= end_time
            else:
                return current_time >= start_time or current_time <= end_time
                
        except Exception as e:
            logger.error(f"Error checking time in range: {e}")
            return False
    
    def _create_error_result(self, error_message: str) -> CongestionResult:
        """Create a congestion result for error cases"""
        return CongestionResult(
            level=CongestionLevel.HIGH,  # Conservative estimate for errors
            score=2,
            triggered_rules=["Error condition"],
            departure_recommendation="Please try again later",
            reasoning=error_message
        )
    
    def _generate_fallback_reasoning(self, result: CongestionResult) -> str:
        """Generate fallback reasoning when reasoning engine is unavailable"""
        try:
            level_text = result.level.value
            rules_text = ", ".join(result.triggered_rules) if result.triggered_rules else "standard analysis"
            return f"Traffic level: {level_text}. Based on: {rules_text}."
        except Exception:
            return "Traffic analysis completed with limited information."
    
    def _generate_fallback_departure_recommendation(self, result: CongestionResult) -> str:
        """Generate fallback departure recommendation when reasoning engine is unavailable"""
        try:
            if result.level == CongestionLevel.LOW:
                return "leave now"
            elif result.level == CongestionLevel.MEDIUM:
                return "consider leaving soon or waiting for off-peak hours"
            else:
                return "wait for off-peak hours if possible"
        except Exception:
            return "check traffic conditions before departing"