"""
Property-based tests for valid congestion levels
**Feature: hyderabad-traffic-guide, Property 2: Valid congestion levels**
"""
from datetime import datetime
from hypothesis import given, strategies as st, settings, assume
from parsers.config_parser import ConfigParser
from scoring.scoring_engine import ScoringEngine
from models.data_models import CongestionLevel


class TestValidCongestionLevels:
    """Property-based tests for valid congestion levels"""
    
    def setup_method(self):
        """Set up test configuration"""
        parser = ConfigParser()
        self.config = parser.load_config()
        self.engine = ScoringEngine(self.config)
    
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
    def test_valid_congestion_levels(self, origin, destination, year, month, day, hour, minute):
        """
        **Feature: hyderabad-traffic-guide, Property 2: Valid congestion levels**
        **Validates: Requirements 1.2**
        
        For any input combination, the system should return exactly one of the three 
        valid congestion levels: Low, Medium, or High
        """
        # Ensure inputs are not empty after stripping
        assume(len(origin.strip()) > 0)
        assume(len(destination.strip()) > 0)
        
        # Create datetime
        test_time = datetime(year, month, day, hour, minute)
        
        # Calculate congestion
        result = self.engine.calculate_congestion(origin.strip(), destination.strip(), test_time)
        
        # Verify exactly one of the three valid congestion levels is returned
        valid_levels = {CongestionLevel.LOW, CongestionLevel.MEDIUM, CongestionLevel.HIGH}
        assert result.level in valid_levels, \
            f"Congestion level must be one of {valid_levels}, got {result.level}"
        
        # Verify the level is exactly one of the enum values
        assert isinstance(result.level, CongestionLevel), \
            f"Result level must be CongestionLevel enum, got {type(result.level)}"
        
        # Verify level corresponds to score correctly
        if result.score == 0:
            assert result.level == CongestionLevel.LOW, \
                f"Score 0 should map to LOW, got {result.level}"
        elif result.score == 1:
            assert result.level == CongestionLevel.MEDIUM, \
                f"Score 1 should map to MEDIUM, got {result.level}"
        elif result.score == 2:
            assert result.level == CongestionLevel.HIGH, \
                f"Score 2 should map to HIGH, got {result.level}"
        else:
            assert False, f"Invalid score {result.score}, should be 0, 1, or 2"
        
        # Verify result structure is complete
        assert hasattr(result, 'level'), "Result must have level attribute"
        assert hasattr(result, 'score'), "Result must have score attribute"
        assert hasattr(result, 'triggered_rules'), "Result must have triggered_rules attribute"
        assert hasattr(result, 'departure_recommendation'), "Result must have departure_recommendation attribute"
        assert hasattr(result, 'reasoning'), "Result must have reasoning attribute"
        
        # Verify types
        assert isinstance(result.score, int), f"Score must be integer, got {type(result.score)}"
        assert isinstance(result.triggered_rules, list), f"Triggered rules must be list, got {type(result.triggered_rules)}"
        assert isinstance(result.departure_recommendation, str), f"Departure recommendation must be string, got {type(result.departure_recommendation)}"
        assert isinstance(result.reasoning, str), f"Reasoning must be string, got {type(result.reasoning)}"
    
    @given(
        st.sampled_from(['', '   ', '\t', '\n']),  # Empty or whitespace origins
        st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))),
        st.datetimes(min_value=datetime(2024, 1, 1), max_value=datetime(2025, 12, 31))
    )
    @settings(max_examples=100)
    def test_empty_origin_handling(self, empty_origin, destination, test_time):
        """Test handling of empty or whitespace-only origins"""
        assume(len(destination.strip()) > 0)
        
        # System should still return valid congestion level even with empty origin
        result = self.engine.calculate_congestion(empty_origin, destination, test_time)
        
        # Should still return valid congestion level
        assert result.level in [CongestionLevel.LOW, CongestionLevel.MEDIUM, CongestionLevel.HIGH]
        assert isinstance(result.level, CongestionLevel)
        assert 0 <= result.score <= 2
    
    @given(
        st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))),
        st.sampled_from(['', '   ', '\t', '\n']),  # Empty or whitespace destinations
        st.datetimes(min_value=datetime(2024, 1, 1), max_value=datetime(2025, 12, 31))
    )
    @settings(max_examples=100)
    def test_empty_destination_handling(self, origin, empty_destination, test_time):
        """Test handling of empty or whitespace-only destinations"""
        assume(len(origin.strip()) > 0)
        
        # System should still return valid congestion level even with empty destination
        result = self.engine.calculate_congestion(origin, empty_destination, test_time)
        
        # Should still return valid congestion level
        assert result.level in [CongestionLevel.LOW, CongestionLevel.MEDIUM, CongestionLevel.HIGH]
        assert isinstance(result.level, CongestionLevel)
        assert 0 <= result.score <= 2
    
    @given(
        st.sampled_from(['Gachibowli', 'Hitec City', 'Charminar', 'MGBS', 'Random Area']),
        st.sampled_from(['Financial District', 'Ameerpet', 'Dilsukhnagar', 'Other Place']),
        st.datetimes(min_value=datetime(2024, 1, 1), max_value=datetime(2025, 12, 31))
    )
    @settings(max_examples=100)
    def test_known_areas_congestion_levels(self, origin, destination, test_time):
        """Test congestion levels for known areas"""
        result = self.engine.calculate_congestion(origin, destination, test_time)
        
        # Verify valid congestion level
        assert result.level in [CongestionLevel.LOW, CongestionLevel.MEDIUM, CongestionLevel.HIGH]
        
        # Verify consistency: same inputs should produce same results
        result2 = self.engine.calculate_congestion(origin, destination, test_time)
        assert result.level == result2.level, "Same inputs should produce same congestion level"
        assert result.score == result2.score, "Same inputs should produce same score"
    
    @given(
        st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cc', 'Cf'))),
        st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cc', 'Cf'))),
        st.datetimes(min_value=datetime(1900, 1, 1), max_value=datetime(2100, 12, 31))
    )
    @settings(max_examples=100)
    def test_extreme_inputs_congestion_levels(self, origin, destination, test_time):
        """Test congestion levels with extreme or unusual inputs"""
        assume(len(origin.strip()) > 0)
        assume(len(destination.strip()) > 0)
        
        result = self.engine.calculate_congestion(origin.strip(), destination.strip(), test_time)
        
        # Even with extreme inputs, should return valid congestion level
        assert result.level in [CongestionLevel.LOW, CongestionLevel.MEDIUM, CongestionLevel.HIGH]
        assert isinstance(result.level, CongestionLevel)
        assert 0 <= result.score <= 2
        
        # Result should have all required fields
        assert len(result.departure_recommendation) > 0, "Departure recommendation should not be empty"
        assert isinstance(result.reasoning, str), "Reasoning should be a string"
        assert isinstance(result.triggered_rules, list), "Triggered rules should be a list"