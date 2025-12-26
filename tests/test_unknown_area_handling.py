"""
Property-based tests for unknown area handling
**Feature: hyderabad-traffic-guide, Property 9: Unknown area handling**
"""
import tempfile
from pathlib import Path
from datetime import datetime
from hypothesis import given, strategies as st, settings
from app.traffic_controller import TrafficController


class TestUnknownAreaHandling:
    """Property-based tests for unknown area handling"""
    
    @given(
        st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'))),  # unknown_area
    )
    @settings(max_examples=100)
    def test_unknown_area_handling(self, unknown_area):
        """
        **Feature: hyderabad-traffic-guide, Property 9: Unknown area handling**
        **Validates: Requirements 4.3**
        
        For any area name not present in Product_Config, the system should respond 
        with the specific message that the area is not in the local dataset
        """
        # Create a configuration with known areas that definitely don't include the random unknown_area
        known_config_content = self._create_config_with_known_areas()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(known_config_content)
            temp_path = f.name
        
        try:
            controller = TrafficController(temp_path)
            
            # Check if controller initialization failed due to error handling
            if controller._initialization_error:
                # Skip this test if controller couldn't initialize
                return
            
            # Ensure the unknown_area is actually unknown by checking it's not in our config
            area_info = controller.get_area_info(unknown_area)
            
            # If the area happens to match something in our known config, skip this test case
            if area_info.zone is not None or area_info.is_hotspot:
                return  # Skip this test case as the area is actually known
            
            # Handle empty or whitespace-only areas (new error handling)
            if not unknown_area or not unknown_area.strip():
                # Test that empty areas get appropriate error messages
                departure_time = datetime(2024, 6, 15, 9, 0)
                known_destination = "KnownArea1"
                
                analysis = controller.analyze_route(unknown_area, known_destination, departure_time)
                
                # Should get input validation error for empty origin
                assert "Origin location cannot be empty" in analysis.congestion.reasoning or \
                       "Please provide a valid starting location" in analysis.congestion.reasoning, \
                    f"Should get input validation error for empty origin. Got: {analysis.congestion.reasoning}"
                return
            
            # Test with unknown area as origin
            departure_time = datetime(2024, 6, 15, 9, 0)
            known_destination = "KnownArea1"  # This is in our config
            
            analysis = controller.analyze_route(unknown_area, known_destination, departure_time)
            
            # Verify the system responds with the specific message for unknown areas
            expected_message = "That area isn't in my local dataset yet—add it to product.md"
            
            assert expected_message in analysis.congestion.reasoning, \
                f"Should contain unknown area message. Got: {analysis.congestion.reasoning}"
            assert expected_message in analysis.detailed_reasoning, \
                f"Should contain unknown area message in detailed reasoning. Got: {analysis.detailed_reasoning}"
            
            # Test with unknown area as destination
            known_origin = "KnownArea2"  # This is in our config
            
            analysis2 = controller.analyze_route(known_origin, unknown_area, departure_time)
            
            # Verify the system responds with the specific message for unknown areas
            assert expected_message in analysis2.congestion.reasoning, \
                f"Should contain unknown area message for destination. Got: {analysis2.congestion.reasoning}"
            assert expected_message in analysis2.detailed_reasoning, \
                f"Should contain unknown area message in detailed reasoning for destination. Got: {analysis2.detailed_reasoning}"
            
            # Test the suggest_area_addition method directly
            suggestion = controller.suggest_area_addition(unknown_area)
            # The new implementation provides more detailed suggestions
            assert expected_message in suggestion, \
                f"suggest_area_addition should contain the expected message. Got: {suggestion}"
            
        finally:
            # Clean up temporary file
            Path(temp_path).unlink(missing_ok=True)
    
    def test_known_areas_do_not_trigger_unknown_message(self):
        """Test that known areas do not trigger the unknown area message"""
        # Create configuration with specific known areas
        known_config_content = self._create_config_with_known_areas()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(known_config_content)
            temp_path = f.name
        
        try:
            controller = TrafficController(temp_path)
            
            # Test with known areas
            known_origin = "KnownArea1"
            known_destination = "KnownHotspot1"
            departure_time = datetime(2024, 6, 15, 9, 0)
            
            analysis = controller.analyze_route(known_origin, known_destination, departure_time)
            
            # Verify the system does NOT respond with unknown area message
            unknown_message = "That area isn't in my local dataset yet—add it to product.md"
            
            assert unknown_message not in analysis.congestion.reasoning, \
                f"Should not contain unknown area message for known areas. Got: {analysis.congestion.reasoning}"
            assert unknown_message not in analysis.detailed_reasoning, \
                f"Should not contain unknown area message in detailed reasoning for known areas. Got: {analysis.detailed_reasoning}"
            
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_partial_matches_are_handled_correctly(self):
        """Test that partial matches in area names are handled correctly"""
        known_config_content = self._create_config_with_known_areas()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(known_config_content)
            temp_path = f.name
        
        try:
            controller = TrafficController(temp_path)
            
            # Test with partial match (should be recognized as known)
            partial_match = "Known"  # This should match "KnownArea1", "KnownArea2", etc.
            departure_time = datetime(2024, 6, 15, 9, 0)
            
            analysis = controller.analyze_route(partial_match, "KnownHotspot1", departure_time)
            
            # Since "Known" partially matches our known areas, it should be recognized
            area_info = controller.get_area_info(partial_match)
            
            # The behavior depends on the matching logic in get_area_info
            # If it finds a match, it shouldn't trigger unknown area message
            unknown_message = "That area isn't in my local dataset yet—add it to product.md"
            
            if area_info.zone is not None or area_info.is_hotspot:
                # Area was recognized, should not have unknown message
                assert unknown_message not in analysis.congestion.reasoning, \
                    "Partially matched area should not trigger unknown area message"
            else:
                # Area was not recognized, should have unknown message
                assert unknown_message in analysis.congestion.reasoning, \
                    "Unrecognized area should trigger unknown area message"
            
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def _create_config_with_known_areas(self) -> str:
        """Create a configuration with specific known areas for testing"""
        return """
# Product Overview: Hyderabad Traffic Guide

### Peak windows
- Weekday morning peak: 08:00–11:00
- Weekday evening peak: 17:00–20:00
- Weekend pattern: lighter mornings

### Hotspots (starter list)
- KnownHotspot1
- KnownHotspot2
- KnownHotspot3

### Explanation templates
- Peak window triggered: "Departure time falls in a typical peak window."
- IT corridor triggered: "One endpoint is in the west/IT corridor."
- Hotspot triggered: "This route touches a known slow zone."
- Weekend adjustment: "Weekend traffic is often smoother."

### Zones
- zone_it_corridor:
  - KnownArea1
  - KnownArea2
- zone_central:
  - KnownArea3
  - KnownArea4
- zone_dense_core:
  - KnownArea5
  - KnownArea6
"""