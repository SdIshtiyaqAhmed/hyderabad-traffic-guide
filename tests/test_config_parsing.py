"""
Property-based tests for configuration parsing
**Feature: hyderabad-traffic-guide, Property 8: Configuration parsing completeness**
"""
import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings
from parsers.config_parser import ConfigParser
from models.data_models import TrafficConfig


class TestConfigurationParsing:
    """Property-based tests for configuration parsing completeness"""
    
    @given(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc', 'Pd', 'Zs'))))
    @settings(max_examples=100, deadline=None)
    def test_configuration_parsing_completeness(self, content):
        """
        **Feature: hyderabad-traffic-guide, Property 8: Configuration parsing completeness**
        **Validates: Requirements 4.2**
        
        For any valid Product_Config file, the parser should successfully extract 
        all required sections: peak windows, hotspots, zone classifications, and explanation templates
        """
        # Create a valid configuration content with the given text as additional content
        valid_config_content = self._create_valid_config_base() + "\n" + content
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(valid_config_content)
            temp_path = f.name
        
        try:
            parser = ConfigParser()
            config = parser.load_config(temp_path)
            
            # Verify all required sections are extracted
            assert config is not None, "Configuration should not be None"
            assert config.peak_windows is not None, "Peak windows should be extracted"
            assert config.zones is not None, "Zones should be extracted"
            assert config.hotspots is not None, "Hotspots should be extracted"
            assert config.explanation_templates is not None, "Explanation templates should be extracted"
            assert config.scoring_rules is not None, "Scoring rules should be extracted"
            
            # Verify peak windows have required fields
            assert config.peak_windows.weekday_morning is not None, "Weekday morning peak should be extracted"
            assert config.peak_windows.weekday_evening is not None, "Weekday evening peak should be extracted"
            assert config.peak_windows.weekend_pattern is not None, "Weekend pattern should be extracted"
            
            # Verify zones is a dictionary
            assert isinstance(config.zones, dict), "Zones should be a dictionary"
            
            # Verify hotspots is a list
            assert isinstance(config.hotspots, list), "Hotspots should be a list"
            
            # Verify explanation templates is a dictionary
            assert isinstance(config.explanation_templates, dict), "Explanation templates should be a dictionary"
            
        finally:
            # Clean up temporary file
            Path(temp_path).unlink(missing_ok=True)
    
    def test_actual_product_config_parsing(self):
        """Test parsing the actual product.md configuration file"""
        parser = ConfigParser()
        config = parser.load_config()
        
        # Verify all required sections are present and properly parsed
        assert config.peak_windows is not None
        assert config.peak_windows.weekday_morning.start.hour == 8
        assert config.peak_windows.weekday_morning.end.hour == 11
        assert config.peak_windows.weekday_evening.start.hour == 17
        assert config.peak_windows.weekday_evening.end.hour == 20
        
        # Verify zones are properly parsed
        assert len(config.zones) >= 5, "Should have at least 5 zones"
        assert 'zone_it_corridor' in config.zones
        assert 'zone_central' in config.zones
        assert 'zone_dense_core' in config.zones
        
        # Verify hotspots are properly parsed
        assert len(config.hotspots) >= 20, "Should have at least 20 hotspots"
        assert 'Gachibowli' in config.hotspots
        assert 'Hitec City' in config.hotspots
        
        # Verify explanation templates are present
        assert len(config.explanation_templates) >= 4, "Should have at least 4 explanation templates"
        assert 'Peak window triggered' in config.explanation_templates
        assert 'IT corridor triggered' in config.explanation_templates
    
    def _create_valid_config_base(self) -> str:
        """Create a minimal valid configuration for testing"""
        return """
# Product Overview: Hyderabad Traffic Guide

### Peak windows
- Weekday morning peak: 08:00–11:00
- Weekday evening peak: 17:00–20:00
- Weekend pattern: lighter mornings

### Hotspots (starter list)
- Gachibowli
- Financial District
- Hitec City

### Explanation templates
- Peak window triggered: "Departure time falls in a typical peak window."
- IT corridor triggered: "One endpoint is in the west/IT corridor."

### Zones
- zone_it_corridor:
  - Gachibowli
  - Financial District
- zone_central:
  - Punjagutta
  - Ameerpet
"""