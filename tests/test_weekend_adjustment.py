"""
Property-based tests for weekend adjustment
**Feature: hyderabad-traffic-guide, Property 5: Weekend adjustment**
"""
from datetime import datetime
from hypothesis import given, strategies as st, settings, assume
from parsers.config_parser import ConfigParser
from scoring.scoring_engine import ScoringEngine
from models.data_models import CongestionLevel


class TestWeekendAdjustment:
    """Property-based tests for weekend adjustment"""
    
    def setup_method(self):
        """Set up test configuration"""
        parser = ConfigParser()
        self.config = parser.load_config()
        self.engine = ScoringEngine(self.config)
    
    @given(
        st.sampled_from(['Random Area', 'Unknown Place', 'Test Location']),  # Non-hotspot areas
        st.sampled_from(['Another Area', 'Different Place', 'Other Location']),  # Non-hotspot areas
        st.integers(min_value=0, max_value=23),   # Hours
        st.integers(min_value=0, max_value=59),   # Minutes
        st.integers(min_value=5, max_value=6),    # Weekend days (Sat=5, Sun=6)
    )
    @settings(max_examples=100)
    def test_weekend_adjustment_non_hotspot(self, origin, destination, hour, minute, weekend_day):
        """
        **Feature: hyderabad-traffic-guide, Property 5: Weekend adjustment**
        **Validates: Requirements 2.4**
        
        For any weekend route calculation, the congestion score should be reduced by one level 
        unless the route involves hotspot locations
        """
        # Ensure areas are not hotspots
        assume(not any(hotspot.lower() in origin.lower() or origin.lower() in hotspot.lower() 
                      for hotspot in self.config.hotspots))
        assume(not any(hotspot.lower() in destination.lower() or destination.lower() in hotspot.lower() 
                      for hotspot in self.config.hotspots))
        
        # Create weekend datetime
        weekend_time = datetime(2024, 1, 1 + weekend_day, hour, minute)  # Start from Monday
        
        # Create equivalent weekday datetime for comparison
        weekday_time = datetime(2024, 1, 1, hour, minute)  # Monday
        
        # Calculate congestion for both
        weekend_result = self.engine.calculate_congestion(origin, destination, weekend_time)
        weekday_result = self.engine.calculate_congestion(origin, destination, weekday_time)
        
        # Weekend should have weekend adjustment applied (unless no reduction possible)
        if weekday_result.score > 0:
            # Weekend should have lower or equal score
            assert weekend_result.score <= weekday_result.score, \
                f"Weekend score ({weekend_result.score}) should be <= weekday score ({weekday_result.score})"
            
            # If weekend adjustment was applied, it should be in triggered rules
            if weekend_result.score < weekday_result.score:
                assert 'Weekend adjustment' in weekend_result.triggered_rules, \
                    "Weekend adjustment should be in triggered rules when score is reduced"
        
        # Verify weekend result is valid
        assert weekend_result.score >= 0, f"Weekend score should be >= 0, got {weekend_result.score}"
        assert weekend_result.level in [CongestionLevel.LOW, CongestionLevel.MEDIUM, CongestionLevel.HIGH]
    
    @given(
        st.sampled_from(['Gachibowli', 'Charminar', 'Dilsukhnagar', 'MGBS', 'Hitec City']),  # Hotspot areas
        st.sampled_from(['Random Area', 'Other Place']),  # Non-hotspot destination
        st.integers(min_value=0, max_value=23),   # Hours
        st.integers(min_value=0, max_value=59),   # Minutes
        st.integers(min_value=5, max_value=6),    # Weekend days
    )
    @settings(max_examples=100)
    def test_weekend_adjustment_with_hotspot(self, hotspot_origin, destination, hour, minute, weekend_day):
        """Test that weekend adjustment is NOT applied when route involves hotspots"""
        # Create weekend datetime
        weekend_time = datetime(2024, 1, 1 + weekend_day, hour, minute)
        
        # Create equivalent weekday datetime for comparison
        weekday_time = datetime(2024, 1, 1, hour, minute)  # Monday
        
        # Calculate congestion for both
        weekend_result = self.engine.calculate_congestion(hotspot_origin, destination, weekend_time)
        weekday_result = self.engine.calculate_congestion(hotspot_origin, destination, weekday_time)
        
        # Weekend adjustment should NOT be applied due to hotspot
        assert 'Weekend adjustment' not in weekend_result.triggered_rules, \
            "Weekend adjustment should not be applied when route involves hotspots"
        
        # Hotspot penalty should still be applied on weekends
        assert 'Hotspot triggered' in weekend_result.triggered_rules, \
            "Hotspot penalty should be applied on weekends"
        
        # Verify result is valid
        assert weekend_result.score >= 0, f"Weekend score should be >= 0, got {weekend_result.score}"
        assert weekend_result.level in [CongestionLevel.LOW, CongestionLevel.MEDIUM, CongestionLevel.HIGH]
    
    @given(
        st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs'))),
        st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs'))),
        st.integers(min_value=0, max_value=23),   # Hours
        st.integers(min_value=0, max_value=59),   # Minutes
    )
    @settings(max_examples=100)
    def test_weekend_vs_weekday_comparison(self, origin, destination, hour, minute):
        """Test weekend vs weekday score comparison"""
        assume(len(origin.strip()) > 0 and len(destination.strip()) > 0)
        
        # Create weekend and weekday datetimes
        weekend_time = datetime(2024, 1, 6, hour, minute)  # Saturday
        weekday_time = datetime(2024, 1, 1, hour, minute)  # Monday
        
        weekend_result = self.engine.calculate_congestion(origin, destination, weekend_time)
        weekday_result = self.engine.calculate_congestion(origin, destination, weekday_time)
        
        # Check if either location is a hotspot
        has_hotspot = any(
            any(hotspot.lower() in location.lower() or location.lower() in hotspot.lower()
                for hotspot in self.config.hotspots)
            for location in [origin, destination]
        )
        
        if not has_hotspot:
            # Without hotspots, weekend should have lower or equal score
            assert weekend_result.score <= weekday_result.score, \
                f"Weekend without hotspots should have <= score than weekday: {weekend_result.score} vs {weekday_result.score}"
        
        # Both results should be valid
        assert weekend_result.score >= 0 and weekend_result.score <= 2
        assert weekday_result.score >= 0 and weekday_result.score <= 2
        assert weekend_result.level in [CongestionLevel.LOW, CongestionLevel.MEDIUM, CongestionLevel.HIGH]
        assert weekday_result.level in [CongestionLevel.LOW, CongestionLevel.MEDIUM, CongestionLevel.HIGH]
    
    @given(
        st.integers(min_value=5, max_value=6),    # Weekend days only
        st.integers(min_value=0, max_value=23),   # Hours
        st.integers(min_value=0, max_value=59),   # Minutes
    )
    @settings(max_examples=100)
    def test_weekend_floor_at_low_level(self, weekend_day, hour, minute):
        """Test that weekend adjustment floors at Low level (score 0)"""
        weekend_time = datetime(2024, 1, 1 + weekend_day, hour, minute)
        
        # Use non-hotspot areas to ensure weekend adjustment applies
        result = self.engine.calculate_congestion('Test Area', 'Other Area', weekend_time)
        
        # Score should never go below 0
        assert result.score >= 0, f"Score should be floored at 0, got {result.score}"
        
        # If score is 0, level should be LOW
        if result.score == 0:
            assert result.level == CongestionLevel.LOW, \
                f"Score 0 should map to LOW level, got {result.level}"