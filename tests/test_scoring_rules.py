"""
Property-based tests for scoring rule application
**Feature: hyderabad-traffic-guide, Property 4: Scoring rule application**
"""
from datetime import datetime, time
from hypothesis import given, strategies as st, settings, assume
from parsers.config_parser import ConfigParser
from scoring.scoring_engine import ScoringEngine
from models.data_models import CongestionLevel


class TestScoringRuleApplication:
    """Property-based tests for scoring rule application"""
    
    def setup_method(self):
        """Set up test configuration"""
        parser = ConfigParser()
        self.config = parser.load_config()
        self.engine = ScoringEngine(self.config)
    
    @given(
        st.sampled_from(['Gachibowli', 'Hitec City', 'Financial District', 'Madhapur']),  # IT corridor areas
        st.sampled_from(['Punjagutta', 'Ameerpet', 'Charminar', 'Secunderabad']),  # Non-IT areas
        st.integers(min_value=8, max_value=10),  # Morning peak hours
        st.integers(min_value=0, max_value=59),  # Minutes
        st.integers(min_value=0, max_value=4),   # Weekdays (Mon-Fri)
    )
    @settings(max_examples=100)
    def test_scoring_rule_application_morning_peak(self, it_area, other_area, hour, minute, weekday):
        """
        **Feature: hyderabad-traffic-guide, Property 4: Scoring rule application**
        **Validates: Requirements 2.1, 2.2, 2.3, 2.5**
        
        For any route and time combination, when peak window conditions are detected, 
        IT corridor multipliers apply, or hotspot penalties trigger, the congestion score 
        should increase by the specified amount while respecting the High level cap
        """
        # Create datetime for morning peak on weekday
        test_time = datetime(2024, 1, 1 + weekday, hour, minute)  # Monday = 0
        
        # Test IT corridor during peak (should have multiple penalties)
        result_it = self.engine.calculate_congestion(it_area, other_area, test_time)
        
        # Test non-IT corridor during peak (should have peak penalty only)
        result_non_it = self.engine.calculate_congestion(other_area, 'Unknown Area', test_time)
        
        # Verify peak window penalty is applied
        assert 'Peak window triggered' in result_it.triggered_rules, \
            f"Peak window should be triggered for {test_time.time()}"
        assert 'Peak window triggered' in result_non_it.triggered_rules, \
            f"Peak window should be triggered for {test_time.time()}"
        
        # Verify IT corridor multiplier is applied
        assert 'IT corridor triggered' in result_it.triggered_rules, \
            f"IT corridor should be triggered for {it_area}"
        
        # Verify IT corridor has higher or equal score than non-IT
        assert result_it.score >= result_non_it.score, \
            f"IT corridor score ({result_it.score}) should be >= non-IT score ({result_non_it.score})"
        
        # Verify score is capped at High level (2)
        assert result_it.score <= 2, f"Score should be capped at 2, got {result_it.score}"
        assert result_non_it.score <= 2, f"Score should be capped at 2, got {result_non_it.score}"
        
        # Verify congestion level is valid
        assert result_it.level in [CongestionLevel.LOW, CongestionLevel.MEDIUM, CongestionLevel.HIGH]
        assert result_non_it.level in [CongestionLevel.LOW, CongestionLevel.MEDIUM, CongestionLevel.HIGH]
    
    @given(
        st.sampled_from(['Gachibowli', 'Hitec City', 'Financial District', 'Madhapur']),  # IT corridor areas
        st.integers(min_value=17, max_value=19),  # Evening peak hours
        st.integers(min_value=0, max_value=59),   # Minutes
        st.integers(min_value=0, max_value=4),    # Weekdays (Mon-Fri)
    )
    @settings(max_examples=100)
    def test_scoring_rule_application_evening_peak(self, it_area, hour, minute, weekday):
        """Test scoring rules during evening peak with IT corridor"""
        # Create datetime for evening peak on weekday
        test_time = datetime(2024, 1, 1 + weekday, hour, minute)
        
        result = self.engine.calculate_congestion(it_area, 'Other Area', test_time)
        
        # Verify peak window penalty is applied
        assert 'Peak window triggered' in result.triggered_rules
        
        # Verify IT corridor multiplier is applied
        assert 'IT corridor triggered' in result.triggered_rules
        
        # Verify extra penalty for heaviest band (18:00-19:00)
        if hour == 18:
            # Should have high congestion due to multiple penalties
            assert result.score >= 2, f"Should have high score during heaviest band, got {result.score}"
        
        # Verify score respects cap
        assert result.score <= 2, f"Score should be capped at 2, got {result.score}"
    
    @given(
        st.sampled_from(['Gachibowli', 'Charminar', 'Dilsukhnagar', 'MGBS']),  # Hotspot areas
        st.integers(min_value=8, max_value=10),   # Morning peak hours
        st.integers(min_value=0, max_value=59),   # Minutes
        st.integers(min_value=0, max_value=4),    # Weekdays
    )
    @settings(max_examples=100)
    def test_hotspot_penalty_application(self, hotspot_area, hour, minute, weekday):
        """Test hotspot penalty application during peak times"""
        test_time = datetime(2024, 1, 1 + weekday, hour, minute)
        
        result = self.engine.calculate_congestion(hotspot_area, 'Other Area', test_time)
        
        # Verify hotspot penalty is applied during peak
        assert 'Hotspot triggered' in result.triggered_rules, \
            f"Hotspot should be triggered for {hotspot_area} during peak"
        
        # Verify score is increased
        assert result.score >= 1, f"Hotspot should increase score, got {result.score}"
        
        # Verify score respects cap
        assert result.score <= 2, f"Score should be capped at 2, got {result.score}"
    
    @given(
        st.sampled_from(['Random Area 1', 'Random Area 2', 'Unknown Place']),  # Non-hotspot areas
        st.integers(min_value=12, max_value=16),  # Non-peak hours
        st.integers(min_value=0, max_value=59),   # Minutes
        st.integers(min_value=0, max_value=4),    # Weekdays
    )
    @settings(max_examples=100)
    def test_no_penalties_during_non_peak(self, area, hour, minute, weekday):
        """Test that no penalties are applied during non-peak hours"""
        test_time = datetime(2024, 1, 1 + weekday, hour, minute)
        
        result = self.engine.calculate_congestion(area, 'Other Area', test_time)
        
        # Should have minimal penalties during non-peak
        assert result.score <= 1, f"Non-peak should have low score, got {result.score}"
        
        # Peak window should not be triggered
        assert 'Peak window triggered' not in result.triggered_rules, \
            f"Peak window should not trigger at {test_time.time()}"
    
    @given(
        st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs'))),
        st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs'))),
        st.integers(min_value=0, max_value=23),   # Hours
        st.integers(min_value=0, max_value=59),   # Minutes
        st.integers(min_value=0, max_value=6),    # All days of week
    )
    @settings(max_examples=100)
    def test_score_capping_property(self, origin, destination, hour, minute, weekday):
        """Test that scores are always properly capped"""
        assume(len(origin.strip()) > 0 and len(destination.strip()) > 0)
        
        test_time = datetime(2024, 1, 1 + weekday, hour, minute)
        
        result = self.engine.calculate_congestion(origin, destination, test_time)
        
        # Verify score is within valid range
        assert 0 <= result.score <= 2, f"Score {result.score} should be between 0 and 2"
        
        # Verify congestion level matches score
        if result.score == 0:
            assert result.level == CongestionLevel.LOW
        elif result.score == 1:
            assert result.level == CongestionLevel.MEDIUM
        else:  # score == 2
            assert result.level == CongestionLevel.HIGH
        
        # Verify result structure
        assert isinstance(result.triggered_rules, list)
        assert isinstance(result.departure_recommendation, str)
        assert isinstance(result.reasoning, str)
        assert len(result.departure_recommendation) > 0