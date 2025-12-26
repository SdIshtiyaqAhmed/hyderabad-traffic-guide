"""
Property-based tests for configuration validation
**Feature: hyderabad-traffic-guide, Property 10: Configuration validation**
"""
import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings
from parsers.config_parser import ConfigParser
from models.data_models import TrafficConfig, PeakWindows, TimeRange, ScoringRules, CongestionLevel
from datetime import time


class TestConfigurationValidation:
    """Property-based tests for configuration validation"""
    
    @given(
        st.booleans(),  # has_peak_windows
        st.booleans(),  # has_zones
        st.booleans(),  # has_hotspots
        st.booleans(),  # has_templates
    )
    @settings(max_examples=100)
    def test_configuration_validation(self, has_peak_windows, has_zones, has_hotspots, has_templates):
        """
        **Feature: hyderabad-traffic-guide, Property 10: Configuration validation**
        **Validates: Requirements 5.1, 5.2**
        
        For any Product_Config file with missing or malformed sections, 
        the validation process should identify specific issues and provide clear error messages
        """
        # Create a configuration with potentially missing sections
        config_content = self._create_config_with_missing_sections(
            has_peak_windows, has_zones, has_hotspots, has_templates
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(config_content)
            temp_path = f.name
        
        try:
            parser = ConfigParser()
            config = parser.load_config(temp_path)
            validation = parser.validate_config(config)
            
            # Verify validation correctly identifies missing sections
            if not has_peak_windows:
                assert not validation.is_valid, "Should be invalid when peak windows are missing"
                assert any("peak window" in error.lower() for error in validation.errors), \
                    f"Should have error about missing peak windows. Actual errors: {validation.errors}"
            
            if not has_zones:
                assert not validation.is_valid, "Should be invalid when zones are missing"
                assert any("zones" in error.lower() for error in validation.errors), \
                    f"Should have error about missing zones. Actual errors: {validation.errors}"
            
            # If all required sections are present, validation should pass
            if has_peak_windows and has_zones:
                assert validation.is_valid, "Should be valid when required sections are present"
            
            # Validation result should always have proper structure
            assert isinstance(validation.is_valid, bool), "is_valid should be boolean"
            assert isinstance(validation.errors, list), "errors should be a list"
            assert isinstance(validation.warnings, list), "warnings should be a list"
            
            # All error messages should be strings
            for error in validation.errors:
                assert isinstance(error, str), "All errors should be strings"
                assert len(error) > 0, "Error messages should not be empty"
            
            # All warning messages should be strings
            for warning in validation.warnings:
                assert isinstance(warning, str), "All warnings should be strings"
                assert len(warning) > 0, "Warning messages should not be empty"
                
        finally:
            # Clean up temporary file
            Path(temp_path).unlink(missing_ok=True)
    
    def test_malformed_peak_windows_validation(self):
        """Test validation of malformed peak windows"""
        # Create config with malformed peak windows
        malformed_config = """
# Product Overview: Hyderabad Traffic Guide

### Peak windows
- Invalid format here
- No proper time ranges

### Zones
- zone_it_corridor:
  - Gachibowli
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(malformed_config)
            temp_path = f.name
        
        try:
            parser = ConfigParser()
            config = parser.load_config(temp_path)
            validation = parser.validate_config(config)
            
            # Should still be valid because parser provides defaults
            # but may have warnings about using defaults
            assert isinstance(validation.is_valid, bool)
            assert isinstance(validation.errors, list)
            assert isinstance(validation.warnings, list)
            
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_empty_configuration_validation(self):
        """Test validation of completely empty configuration"""
        empty_config = "# Empty configuration file"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(empty_config)
            temp_path = f.name
        
        try:
            parser = ConfigParser()
            config = parser.load_config(temp_path)
            validation = parser.validate_config(config)
            
            # Should be invalid due to missing required sections
            assert not validation.is_valid, "Empty config should be invalid"
            assert len(validation.errors) > 0, "Should have validation errors"
            
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def _create_config_with_missing_sections(self, has_peak_windows, has_zones, has_hotspots, has_templates):
        """Create a configuration with potentially missing sections"""
        config_parts = ["# Product Overview: Hyderabad Traffic Guide\n"]
        
        if has_peak_windows:
            config_parts.append("""
### Peak windows
- Weekday morning peak: 08:00–11:00
- Weekday evening peak: 17:00–20:00
- Weekend pattern: lighter mornings
""")
        
        if has_zones:
            config_parts.append("""
### Zones
- zone_it_corridor:
  - Gachibowli
  - Financial District
- zone_central:
  - Punjagutta
  - Ameerpet
""")
        
        if has_hotspots:
            config_parts.append("""
### Hotspots (starter list)
- Gachibowli
- Financial District
- Hitec City
""")
        
        if has_templates:
            config_parts.append("""
### Explanation templates
- Peak window triggered: "Departure time falls in a typical peak window."
- IT corridor triggered: "One endpoint is in the west/IT corridor."
""")
        
        return "".join(config_parts)