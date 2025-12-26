"""
Property-based tests for preference-based filtering
**Feature: hyderabad-traffic-guide, Property 7: Preference-based filtering**
"""
from datetime import datetime
from hypothesis import given, strategies as st, settings, assume
from parsers.config_parser import ConfigParser
from app.traffic_controller import TrafficController


class TestPreferenceBasedFiltering:
    """Property-based tests for preference-based filtering"""
    
    def setup_method(self):
        """Set up test configuration"""
        parser = ConfigParser()
        self.config = parser.load_config()
        self.controller = TrafficController()
    
    @given(
        st.sampled_from(['Gachibowli', 'Hitec City', 'Charminar', 'Punjagutta', 'Ameerpet']),
        st.sampled_from(['Financial District', 'Madhapur', 'Secunderabad', 'MGBS', 'Dilsukhnagar']),
        st.integers(min_value=0, max_value=23),   # Hours
        st.integers(min_value=0, max_value=59),   # Minutes
        st.integers(min_value=0, max_value=6),    # All days of week
        st.booleans(),  # Nightlife avoidance preference
        st.booleans(),  # Family-friendly preference
    )
    @settings(max_examples=100)
    def test_preference_based_filtering(self, origin, destination, hour, minute, weekday, 
                                      avoid_nightlife, prefer_family_friendly):
        """
        **Feature: hyderabad-traffic-guide, Property 7: Preference-based filtering**
        **Validates: Requirements 3.4**
        
        For any route recommendation, when nightlife avoidance preferences are enabled, 
        the system should filter suggestions to exclude nightlife-heavy corridors
        """
        test_time = datetime(2024, 1, 1 + weekday, hour, minute)
        
        # Get traffic analysis with preferences
        analysis = self.controller.analyze_route_with_preferences(
            origin, destination, test_time, 
            avoid_nightlife=avoid_nightlife,
            prefer_family_friendly=prefer_family_friendly
        )
        
        # Collect all recommendation text
        recommendation_text = ' '.join([
            analysis.congestion.reasoning,
            analysis.congestion.departure_recommendation,
            analysis.departure_window,
            analysis.detailed_reasoning
        ] + analysis.hotspot_warnings).lower()
        
        # Define nightlife-heavy corridors (areas known for nightlife)
        nightlife_corridors = [
            'jubilee hills', 'banjara hills', 'gachibowli', 'hitech city',
            'madhapur', 'kondapur'  # These areas have nightlife venues
        ]
        
        if avoid_nightlife:
            # When nightlife avoidance is enabled, recommendations should not 
            # explicitly suggest routes through nightlife-heavy corridors
            # or mention nightlife-related venues
            nightlife_terms = [
                'pub', 'bar', 'club', 'nightclub', 'lounge', 'brewery',
                'nightlife', 'late night entertainment', 'party area'
            ]
            
            for term in nightlife_terms:
                assert term not in recommendation_text, \
                    f"Nightlife term '{term}' should be filtered out when avoid_nightlife=True"
        
        if prefer_family_friendly:
            # When family-friendly preference is enabled, suggestions should
            # use appropriate language and avoid inappropriate content
            family_friendly_indicators = [
                'family', 'quiet', 'safe', 'appropriate', 'suitable'
            ]
            
            # Should not contain adult-oriented content
            adult_terms = ['adult', 'mature', '18+', 'restricted']
            for term in adult_terms:
                assert term not in recommendation_text, \
                    f"Adult term '{term}' should be filtered out when prefer_family_friendly=True"
        
        # Verify the analysis structure is maintained regardless of preferences
        assert analysis.congestion is not None
        assert isinstance(analysis.hotspot_warnings, list)
        assert isinstance(analysis.departure_window, str)
        assert isinstance(analysis.detailed_reasoning, str)
    
    @given(
        st.sampled_from(['Jubilee Hills', 'Banjara Hills', 'Gachibowli', 'Hitech City']),  # Nightlife areas
        st.sampled_from(['Ameerpet', 'Secunderabad', 'Charminar', 'MGBS']),  # Non-nightlife areas
        st.integers(min_value=18, max_value=23),  # Evening/night hours
        st.integers(min_value=0, max_value=59),
        st.integers(min_value=4, max_value=6),    # Weekend days (Fri-Sun)
    )
    @settings(max_examples=100)
    def test_nightlife_corridor_filtering(self, nightlife_area, regular_area, hour, minute, weekday):
        """Test filtering of nightlife-heavy corridors during evening/night hours"""
        test_time = datetime(2024, 1, 1 + weekday, hour, minute)
        
        # Test with nightlife avoidance enabled
        analysis_avoid = self.controller.analyze_route_with_preferences(
            nightlife_area, regular_area, test_time, 
            avoid_nightlife=True,
            prefer_family_friendly=True
        )
        
        # Test without nightlife avoidance
        analysis_normal = self.controller.analyze_route_with_preferences(
            nightlife_area, regular_area, test_time, 
            avoid_nightlife=False,
            prefer_family_friendly=False
        )
        
        # Both should provide valid analysis
        assert analysis_avoid.congestion is not None
        assert analysis_normal.congestion is not None
        
        # With avoidance enabled, should not mention nightlife venues
        avoid_text = analysis_avoid.detailed_reasoning.lower()
        nightlife_venues = ['pub', 'bar', 'club', 'nightclub', 'lounge']
        
        for venue in nightlife_venues:
            assert venue not in avoid_text, \
                f"Nightlife venue '{venue}' should be filtered when avoid_nightlife=True"
    
    @given(
        st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs'))),
        st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs'))),
        st.integers(min_value=0, max_value=23),
        st.integers(min_value=0, max_value=59),
        st.integers(min_value=0, max_value=6),
        st.booleans(),
        st.booleans(),
    )
    @settings(max_examples=100)
    def test_preference_consistency(self, origin, destination, hour, minute, weekday, 
                                  avoid_nightlife, prefer_family_friendly):
        """Test that preferences are consistently applied across all outputs"""
        assume(len(origin.strip()) > 0 and len(destination.strip()) > 0)
        
        test_time = datetime(2024, 1, 1 + weekday, hour, minute)
        
        analysis = self.controller.analyze_route_with_preferences(
            origin, destination, test_time,
            avoid_nightlife=avoid_nightlife,
            prefer_family_friendly=prefer_family_friendly
        )
        
        # Collect all text outputs
        all_outputs = [
            analysis.congestion.reasoning,
            analysis.congestion.departure_recommendation,
            analysis.departure_window,
            analysis.detailed_reasoning
        ] + analysis.hotspot_warnings
        
        # Filter out empty strings
        text_outputs = [output for output in all_outputs if output and output.strip()]
        
        if avoid_nightlife or prefer_family_friendly:
            # All outputs should be consistent with preferences
            for output in text_outputs:
                output_lower = output.lower()
                
                # Should not contain nightlife terms
                nightlife_terms = ['pub', 'bar', 'club', 'nightclub', 'lounge', 'brewery']
                for term in nightlife_terms:
                    assert term not in output_lower, \
                        f"Nightlife term '{term}' found in output when preferences should filter it"
                
                # Should not contain inappropriate content
                inappropriate_terms = ['adult', 'mature', '18+', 'explicit']
                for term in inappropriate_terms:
                    assert term not in output_lower, \
                        f"Inappropriate term '{term}' found in output when preferences should filter it"
        
        # Verify outputs are not empty (preferences shouldn't break functionality)
        assert len(text_outputs) > 0, "Preferences should not result in empty outputs"
        
        # Verify core functionality is maintained
        assert analysis.congestion.level is not None
        assert analysis.congestion.score >= 0
        assert isinstance(analysis.congestion.triggered_rules, list)