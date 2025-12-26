"""
Property-based tests for departure recommendations format
**Feature: hyderabad-traffic-guide, Property 3: Departure recommendations format**
"""
import re
from datetime import datetime
from hypothesis import given, strategies as st, settings, assume
from parsers.config_parser import ConfigParser
from scoring.scoring_engine import ScoringEngine
from reasoning.reasoning_engine import ReasoningEngine
from models.data_models import CongestionLevel


class TestDepartureRecommendationsFormat:
    """Property-based tests for departure recommendations format"""
    
    def setup_method(self):
        """Set up test configuration"""
        parser = ConfigParser()
        self.config = parser.load_config()
        self.engine = ScoringEngine(self.config)
        self.reasoning_engine = ReasoningEngine(self.config)
    
    @given(
        st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs', 'Nd', 'Pc'))),
        st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs', 'Nd', 'Pc'))),
        st.integers(min_value=2024, max_value=2025),  # Year
        st.integers(min_value=1, max_value=12),       # Month
        st.integers(min_value=1, max_value=28),       # Day (safe for all months)
        st.integers(min_value=0, max_value=23),       # Hour
        st.integers(min_value=0, max_value=59),       # Minute
    )
    @settings(max_examples=100)
    def test_departure_recommendations_format(self, origin, destination, year, month, day, hour, minute):
        """
        **Feature: hyderabad-traffic-guide, Property 3: Departure recommendations format**
        **Validates: Requirements 1.3**
        
        For any congestion calculation, the system should provide a departure recommendation 
        that follows either "leave now" or "wait until [specific time window]" format
        """
        # Ensure inputs are not empty after stripping
        assume(len(origin.strip()) > 0)
        assume(len(destination.strip()) > 0)
        
        # Create datetime
        test_time = datetime(year, month, day, hour, minute)
        
        # Calculate congestion
        result = self.engine.calculate_congestion(origin.strip(), destination.strip(), test_time)
        
        # Verify departure recommendation is not empty
        assert len(result.departure_recommendation) > 0, \
            "Departure recommendation should not be empty"
        
        # Verify departure recommendation follows the required format
        recommendation = result.departure_recommendation.lower().strip()
        
        # Should follow either "leave now" or "wait until [specific time window]" format
        leave_now_pattern = r'^leave now$'
        wait_until_pattern = r'^wait until .+'
        
        matches_leave_now = re.match(leave_now_pattern, recommendation)
        matches_wait_until = re.match(wait_until_pattern, recommendation)
        
        assert matches_leave_now or matches_wait_until, \
            f"Departure recommendation '{result.departure_recommendation}' must follow either " \
            f"'leave now' or 'wait until [specific time window]' format"
        
        # Verify the recommendation is consistent with congestion level
        if result.level == CongestionLevel.LOW:
            # Low congestion should typically recommend leaving now
            assert matches_leave_now, \
                f"Low congestion should recommend 'leave now', got '{result.departure_recommendation}'"
        
        # Verify recommendation is a proper sentence (starts with lowercase or uppercase)
        first_char = result.departure_recommendation[0]
        assert first_char.isalpha(), \
            f"Departure recommendation should start with a letter, got '{result.departure_recommendation}'"
        
        # Verify recommendation doesn't contain invalid characters or formatting
        assert not result.departure_recommendation.startswith(' '), \
            "Departure recommendation should not start with whitespace"
        assert not result.departure_recommendation.endswith(' '), \
            "Departure recommendation should not end with whitespace"
    
    @given(
        st.sampled_from([CongestionLevel.LOW, CongestionLevel.MEDIUM, CongestionLevel.HIGH]),
        st.lists(st.sampled_from(['Peak window triggered', 'IT corridor triggered', 
                                'Hotspot triggered', 'Weekend adjustment']), 
                min_size=0, max_size=4, unique=True),
        st.integers(min_value=0, max_value=2)
    )
    @settings(max_examples=100)
    def test_reasoning_engine_departure_format(self, level, triggered_rules, score):
        """Test ReasoningEngine directly for departure recommendation format"""
        from models.data_models import CongestionResult
        
        # Create a mock result
        result = CongestionResult(
            level=level,
            score=score,
            triggered_rules=triggered_rules,
            departure_recommendation="",  # Will be set by reasoning engine
            reasoning=""
        )
        
        # Get departure recommendation from reasoning engine
        recommendation = self.reasoning_engine.get_departure_recommendation(result)
        
        # Verify format
        assert len(recommendation) > 0, "Departure recommendation should not be empty"
        
        recommendation_lower = recommendation.lower().strip()
        
        # Should follow either "leave now" or "wait until [specific time window]" format
        leave_now_pattern = r'^leave now$'
        wait_until_pattern = r'^wait until .+'
        
        matches_leave_now = re.match(leave_now_pattern, recommendation_lower)
        matches_wait_until = re.match(wait_until_pattern, recommendation_lower)
        
        assert matches_leave_now or matches_wait_until, \
            f"Departure recommendation '{recommendation}' must follow either " \
            f"'leave now' or 'wait until [specific time window]' format"
    
    @given(
        st.sampled_from(['Gachibowli', 'Hitec City', 'Financial District']),  # IT corridor areas
        st.sampled_from(['Charminar', 'Dilsukhnagar', 'MGBS']),  # Hotspot areas
        st.integers(min_value=8, max_value=10),   # Morning peak hours
        st.integers(min_value=0, max_value=59),   # Minutes
        st.integers(min_value=0, max_value=4),    # Weekdays
    )
    @settings(max_examples=100)
    def test_high_congestion_wait_format(self, it_area, hotspot_area, hour, minute, weekday):
        """Test that high congestion scenarios produce proper wait recommendations"""
        test_time = datetime(2024, 1, 1 + weekday, hour, minute)
        
        # This should produce high congestion due to multiple factors
        result = self.engine.calculate_congestion(it_area, hotspot_area, test_time)
        
        # High congestion should typically recommend waiting
        if result.level == CongestionLevel.HIGH:
            recommendation = result.departure_recommendation.lower().strip()
            
            # Should be a wait recommendation
            wait_pattern = r'^wait until .+'
            assert re.match(wait_pattern, recommendation), \
                f"High congestion should recommend waiting, got '{result.departure_recommendation}'"
            
            # Should specify a time or condition
            assert 'until' in recommendation, \
                f"Wait recommendation should specify 'until' condition, got '{result.departure_recommendation}'"
    
    @given(
        st.sampled_from(['Random Area 1', 'Unknown Place', 'Test Location']),  # Non-hotspot areas
        st.integers(min_value=12, max_value=16),  # Non-peak hours
        st.integers(min_value=0, max_value=59),   # Minutes
        st.integers(min_value=0, max_value=4),    # Weekdays
    )
    @settings(max_examples=100)
    def test_low_congestion_leave_now_format(self, area, hour, minute, weekday):
        """Test that low congestion scenarios produce proper leave now recommendations"""
        test_time = datetime(2024, 1, 1 + weekday, hour, minute)
        
        result = self.engine.calculate_congestion(area, 'Other Area', test_time)
        
        # Low congestion should typically recommend leaving now
        if result.level == CongestionLevel.LOW:
            recommendation = result.departure_recommendation.lower().strip()
            
            # Should be leave now recommendation
            assert recommendation == 'leave now', \
                f"Low congestion should recommend 'leave now', got '{result.departure_recommendation}'"
    
    @given(
        st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cc', 'Cf'))),
        st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cc', 'Cf'))),
        st.datetimes(min_value=datetime(2024, 1, 1), max_value=datetime(2025, 12, 31))
    )
    @settings(max_examples=100)
    def test_extreme_inputs_departure_format(self, origin, destination, test_time):
        """Test departure recommendation format with extreme or unusual inputs"""
        assume(len(origin.strip()) > 0)
        assume(len(destination.strip()) > 0)
        
        result = self.engine.calculate_congestion(origin.strip(), destination.strip(), test_time)
        
        # Even with extreme inputs, should follow proper format
        recommendation = result.departure_recommendation.lower().strip()
        
        leave_now_pattern = r'^leave now$'
        wait_until_pattern = r'^wait until .+'
        
        matches_leave_now = re.match(leave_now_pattern, recommendation)
        matches_wait_until = re.match(wait_until_pattern, recommendation)
        
        assert matches_leave_now or matches_wait_until, \
            f"Even with extreme inputs, departure recommendation '{result.departure_recommendation}' " \
            f"must follow proper format"
        
        # Should not be empty or just whitespace
        assert len(result.departure_recommendation.strip()) > 0, \
            "Departure recommendation should not be empty or just whitespace"
        
        # Should not contain newlines or tabs
        assert '\n' not in result.departure_recommendation, \
            "Departure recommendation should not contain newlines"
        assert '\t' not in result.departure_recommendation, \
            "Departure recommendation should not contain tabs"