"""
Property-based tests for graceful error recovery
**Feature: hyderabad-traffic-guide, Property 11: Graceful error recovery**
"""
import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings
from parsers.config_parser import ConfigParser
from app.traffic_controller import TrafficController
from datetime import datetime


class TestGracefulErrorRecovery:
    """Property-based tests for graceful error recovery"""
    
    @given(
        st.booleans(),  # corrupt_peak_windows
        st.booleans(),  # corrupt_zones
        st.booleans(),  # corrupt_hotspots
        st.booleans(),  # corrupt_templates
        st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc', 'Pd', 'Zs')), min_size=0, max_size=100)  # random_content
    )
    @settings(max_examples=100, deadline=None)
    def test_graceful_error_recovery(self, corrupt_peak_windows, corrupt_zones, corrupt_hotspots, corrupt_templates, random_content):
        """
        **Feature: hyderabad-traffic-guide, Property 11: Graceful error recovery**
        **Validates: Requirements 5.5**
        
        For any configuration containing both valid and invalid data sections, 
        the system should continue operating with valid portions while handling errors gracefully
        """
        # Create a configuration with mixed valid and invalid sections
        config_content = self._create_mixed_config(
            corrupt_peak_windows, corrupt_zones, corrupt_hotspots, corrupt_templates, random_content
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(config_content)
            temp_path = f.name
        
        try:
            # Test that parser can handle mixed valid/invalid configuration
            parser = ConfigParser()
            config = parser.load_config(temp_path)
            
            # System should not crash and should return a configuration object
            assert config is not None, "Configuration should not be None even with corrupted sections"
            
            # Basic structure should always be present
            assert hasattr(config, 'peak_windows'), "Config should have peak_windows attribute"
            assert hasattr(config, 'zones'), "Config should have zones attribute"
            assert hasattr(config, 'hotspots'), "Config should have hotspots attribute"
            assert hasattr(config, 'explanation_templates'), "Config should have explanation_templates attribute"
            assert hasattr(config, 'scoring_rules'), "Config should have scoring_rules attribute"
            
            # Test that traffic controller can still operate with potentially corrupted config
            try:
                controller = TrafficController(temp_path)
                
                # System should be able to handle basic operations even with corrupted config
                # Test with known good locations first
                test_locations = ["Gachibowli", "Hitec City", "Punjagutta", "Unknown Area"]
                test_time = datetime(2024, 1, 15, 9, 0)  # Monday 9 AM
                
                for origin in test_locations[:2]:  # Test with first 2 locations
                    for destination in test_locations[:2]:
                        if origin != destination:
                            try:
                                analysis = controller.analyze_route(origin, destination, test_time)
                                
                                # Analysis should always return a valid structure
                                assert analysis is not None, "Analysis should not be None"
                                assert hasattr(analysis, 'congestion'), "Analysis should have congestion"
                                assert hasattr(analysis, 'hotspot_warnings'), "Analysis should have hotspot_warnings"
                                assert hasattr(analysis, 'departure_window'), "Analysis should have departure_window"
                                assert hasattr(analysis, 'detailed_reasoning'), "Analysis should have detailed_reasoning"
                                
                                # Congestion result should have valid structure
                                assert analysis.congestion is not None, "Congestion result should not be None"
                                assert hasattr(analysis.congestion, 'level'), "Congestion should have level"
                                assert hasattr(analysis.congestion, 'score'), "Congestion should have score"
                                assert hasattr(analysis.congestion, 'triggered_rules'), "Congestion should have triggered_rules"
                                
                                # Level should be one of the valid values
                                valid_levels = ['Low', 'Medium', 'High']
                                assert analysis.congestion.level.value in valid_levels, \
                                    f"Congestion level should be valid, got: {analysis.congestion.level.value}"
                                
                                # Score should be reasonable
                                assert isinstance(analysis.congestion.score, int), "Score should be integer"
                                assert 0 <= analysis.congestion.score <= 2, "Score should be between 0 and 2"
                                
                                # Lists should be lists
                                assert isinstance(analysis.congestion.triggered_rules, list), "Triggered rules should be list"
                                assert isinstance(analysis.hotspot_warnings, list), "Hotspot warnings should be list"
                                
                                # Strings should be strings
                                assert isinstance(analysis.congestion.reasoning, str), "Reasoning should be string"
                                assert isinstance(analysis.congestion.departure_recommendation, str), "Departure rec should be string"
                                assert isinstance(analysis.departure_window, str), "Departure window should be string"
                                assert isinstance(analysis.detailed_reasoning, str), "Detailed reasoning should be string"
                                
                            except Exception as e:
                                # If there's an exception, it should be handled gracefully
                                # The system should not crash completely
                                assert False, f"System should handle errors gracefully, but got: {e}"
                
                # Test unknown area handling
                unknown_analysis = controller.analyze_route("Unknown Area", "Another Unknown", test_time)
                assert unknown_analysis is not None, "Should handle unknown areas gracefully"
                assert "isn't in my local dataset" in unknown_analysis.congestion.reasoning, \
                    "Should provide helpful message for unknown areas"
                
            except Exception as e:
                # Even if controller initialization fails, it should fail gracefully
                # Check that it's a reasonable error message
                error_msg = str(e).lower()
                assert any(keyword in error_msg for keyword in ['configuration', 'config', 'file', 'missing', 'invalid']), \
                    f"Error should be configuration-related, got: {e}"
            
            # Test validation still works with corrupted config
            validation = parser.validate_config(config)
            assert validation is not None, "Validation should not be None"
            assert hasattr(validation, 'is_valid'), "Validation should have is_valid"
            assert hasattr(validation, 'errors'), "Validation should have errors"
            assert hasattr(validation, 'warnings'), "Validation should have warnings"
            assert isinstance(validation.errors, list), "Errors should be a list"
            assert isinstance(validation.warnings, list), "Warnings should be a list"
            
        finally:
            # Clean up temporary file
            Path(temp_path).unlink(missing_ok=True)
    
    def test_missing_config_file_recovery(self):
        """Test graceful handling when configuration file is completely missing"""
        non_existent_path = "/path/that/does/not/exist/config.md"
        
        parser = ConfigParser()
        
        # Should raise FileNotFoundError, but gracefully
        try:
            config = parser.load_config(non_existent_path)
            assert False, "Should raise FileNotFoundError for missing file"
        except FileNotFoundError as e:
            # Error message should be helpful
            assert "Configuration file not found" in str(e)
            # Check that the path is mentioned (handle Windows path separators)
            error_str = str(e).replace('\\', '/')
            assert "path/that/does/not/exist/config.md" in error_str
        except Exception as e:
            assert False, f"Should raise FileNotFoundError, not {type(e).__name__}: {e}"
    
    def test_completely_corrupted_config_recovery(self):
        """Test handling of completely corrupted configuration file"""
        corrupted_configs = [
            "",  # Empty file
            "This is not markdown at all!",  # Not markdown
            "# Title\n\nSome text but no valid sections",  # No valid sections
            "### Invalid Section\n- Random: data\n- That: doesn't match expected format",  # Invalid format
            "### Peak windows\n- Invalid time format: not-a-time",  # Invalid time format
            "### Zones\n- Not proper zone format",  # Invalid zone format
        ]
        
        for i, corrupted_content in enumerate(corrupted_configs):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
                f.write(corrupted_content)
                temp_path = f.name
            
            try:
                parser = ConfigParser()
                config = parser.load_config(temp_path)
                
                # Should not crash, should return some configuration
                assert config is not None, f"Config {i}: Should not be None even with corrupted content"
                
                # Should have basic structure with defaults
                assert config.peak_windows is not None, f"Config {i}: Should have peak windows (possibly defaults)"
                assert config.zones is not None, f"Config {i}: Should have zones (possibly empty)"
                assert config.hotspots is not None, f"Config {i}: Should have hotspots (possibly empty)"
                assert config.explanation_templates is not None, f"Config {i}: Should have templates (possibly defaults)"
                
                # Validation should identify issues
                validation = parser.validate_config(config)
                if corrupted_content.strip() == "" or "Peak windows" not in corrupted_content:
                    # Should be invalid for empty or missing peak windows
                    assert not validation.is_valid or len(validation.warnings) > 0, \
                        f"Config {i}: Should be invalid or have warnings for corrupted content"
                
            finally:
                Path(temp_path).unlink(missing_ok=True)
    
    def _create_mixed_config(self, corrupt_peak_windows, corrupt_zones, corrupt_hotspots, corrupt_templates, random_content):
        """Create a configuration with mixed valid and invalid sections"""
        config_parts = ["# Product Overview: Hyderabad Traffic Guide\n"]
        
        # Add some random content that might interfere
        if random_content.strip():
            config_parts.append(f"\n{random_content}\n")
        
        # Peak windows - either valid or corrupted
        if corrupt_peak_windows:
            config_parts.append("""
### Peak windows
- Invalid morning time: not-a-time
- Weekday evening peak: 25:99–30:00  # Invalid times
- Weekend pattern: corrupted data here
""")
        else:
            config_parts.append("""
### Peak windows
- Weekday morning peak: 08:00–11:00
- Weekday evening peak: 17:00–20:00
- Weekend pattern: lighter mornings
""")
        
        # Zones - either valid or corrupted
        if corrupt_zones:
            config_parts.append("""
### Zones
- invalid_zone_format
- zone_it_corridor
  Missing proper indentation
- zone_central:
    - Improper nesting level
""")
        else:
            config_parts.append("""
### Zones
- zone_it_corridor:
  - Gachibowli
  - Financial District
- zone_central:
  - Punjagutta
  - Ameerpet
""")
        
        # Hotspots - either valid or corrupted
        if corrupt_hotspots:
            config_parts.append("""
### Hotspots (starter list)
- Invalid format without proper structure
Some text that's not a list item
- 
- Empty item above
""")
        else:
            config_parts.append("""
### Hotspots (starter list)
- Gachibowli
- Financial District
- Hitec City
- Punjagutta
""")
        
        # Templates - either valid or corrupted
        if corrupt_templates:
            config_parts.append("""
### Explanation templates
- Missing colon and quotes
- Peak window triggered "Missing colon before this"
- IT corridor triggered: Missing quotes around this
- Hotspot triggered: "Proper format but mixed with invalid ones"
""")
        else:
            config_parts.append("""
### Explanation templates
- Peak window triggered: "Departure time falls in a typical peak window."
- IT corridor triggered: "One endpoint is in the west/IT corridor."
- Hotspot triggered: "This route touches a known slow zone."
- Weekend adjustment: "Weekend traffic is often smoother."
""")
        
        return "".join(config_parts)