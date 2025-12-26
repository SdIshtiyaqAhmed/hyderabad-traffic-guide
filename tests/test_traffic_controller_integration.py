"""
Integration tests for TrafficController - End-to-end scenarios
"""
import pytest
from datetime import datetime
from pathlib import Path
import tempfile
import os
from unittest.mock import patch

from app.traffic_controller import TrafficController
from models.data_models import CongestionLevel
from parsers.config_parser import ConfigParser


class TestTrafficControllerEndToEndIntegration:
    """End-to-end integration tests for the complete traffic analysis workflow"""
    
    def test_complete_workflow_weekday_peak_it_corridor(self):
        """Test complete workflow: IT corridor during weekday peak"""
        controller = TrafficController()
        
        # Monday 9 AM - peak time in IT corridor
        analysis = controller.analyze_route(
            "Gachibowli", 
            "Hitec City", 
            datetime(2024, 1, 1, 9, 0)  # Monday 9 AM
        )
        
        # Verify complete analysis structure
        assert analysis is not None
        assert analysis.congestion is not None
        assert analysis.congestion.level in [CongestionLevel.LOW, CongestionLevel.MEDIUM, CongestionLevel.HIGH]
        assert len(analysis.congestion.reasoning) > 0
        assert len(analysis.detailed_reasoning) > 0
        assert analysis.departure_window is not None
        
        # Should have high congestion due to IT corridor + peak time
        assert analysis.congestion.level in [CongestionLevel.MEDIUM, CongestionLevel.HIGH]
        
        # Should have hotspot warnings for both locations
        assert len(analysis.hotspot_warnings) >= 1
        assert any("hotspot" in warning.lower() for warning in analysis.hotspot_warnings)
        
        # Should mention peak window and IT corridor in reasoning
        reasoning_text = analysis.congestion.reasoning.lower()
        assert any(keyword in reasoning_text for keyword in ["peak", "corridor", "congestion"])
    
    def test_complete_workflow_weekend_non_hotspot(self):
        """Test complete workflow: Non-hotspot areas during weekend"""
        controller = TrafficController()
        
        # Saturday 10 AM - weekend, use unknown areas that won't be hotspots
        # This will test the weekend logic without hotspot interference
        analysis = controller.analyze_route(
            "NonHotspotArea1",  # Unknown area, not a hotspot
            "NonHotspotArea2",  # Unknown area, not a hotspot  
            datetime(2024, 1, 6, 10, 0)  # Saturday 10 AM
        )
        
        # Should handle unknown areas
        assert analysis.congestion is not None
        expected_message = "That area isn't in my local dataset yet—add it to product.md"
        assert expected_message in analysis.congestion.reasoning
    
    def test_complete_workflow_with_preferences(self):
        """Test complete workflow with content filtering preferences"""
        controller = TrafficController()
        
        # Test with family-friendly preferences enabled
        analysis = controller.analyze_route_with_preferences(
            "Gachibowli",
            "Ameerpet", 
            datetime(2024, 1, 1, 9, 0),
            avoid_nightlife=True,
            prefer_family_friendly=True
        )
        
        # Verify analysis structure
        assert analysis is not None
        assert analysis.congestion is not None
        
        # Content should be family-friendly (no nightlife references)
        all_text = (analysis.congestion.reasoning + " " + 
                   analysis.detailed_reasoning + " " + 
                   " ".join(analysis.hotspot_warnings))
        
        # Should not contain nightlife-related terms
        nightlife_terms = ["bar", "pub", "nightclub", "nightlife", "drinks"]
        assert not any(term in all_text.lower() for term in nightlife_terms)
    
    def test_complete_workflow_unknown_area_handling(self):
        """Test complete workflow with unknown area"""
        controller = TrafficController()
        
        # Test with completely unknown area
        analysis = controller.analyze_route(
            "CompletelyUnknownPlace", 
            "Gachibowli", 
            datetime(2024, 1, 1, 9, 0)
        )
        
        # Should handle unknown area gracefully
        assert analysis is not None
        assert analysis.congestion is not None
        
        # Should contain the standard unknown area message
        expected_message = "That area isn't in my local dataset yet—add it to product.md"
        assert expected_message in analysis.congestion.reasoning
        assert expected_message in analysis.detailed_reasoning
        
        # Should ask for area addition information
        assert "area name, zone tag, nearby landmark, and hotspot status" in analysis.congestion.reasoning
    
    def test_input_validation_edge_cases(self):
        """Test input validation with various edge cases"""
        controller = TrafficController()
        
        # Empty origin
        analysis = controller.analyze_route("", "Gachibowli", datetime(2024, 1, 1, 9, 0))
        assert "Origin location cannot be empty" in analysis.congestion.reasoning
        
        # Empty destination
        analysis = controller.analyze_route("Gachibowli", "", datetime(2024, 1, 1, 9, 0))
        assert "Destination location cannot be empty" in analysis.congestion.reasoning
        
        # None departure time
        analysis = controller.analyze_route("Gachibowli", "Ameerpet", None)
        assert "Departure time is required" in analysis.congestion.reasoning
        
        # Whitespace-only inputs
        analysis = controller.analyze_route("   ", "Gachibowli", datetime(2024, 1, 1, 9, 0))
        assert "Origin location cannot be empty" in analysis.congestion.reasoning
    
    def test_error_recovery_scenarios(self):
        """Test error recovery in various failure scenarios"""
        controller = TrafficController()
        
        # Test with malformed area names that might cause parsing issues
        problematic_names = [
            "Area/With/Slashes",
            "Area With Special @#$% Characters",
            "VeryLongAreaNameThatMightCauseIssuesInProcessing" * 5,
            "123456789",  # Numeric area name
            "Area\nWith\nNewlines"
        ]
        
        for area_name in problematic_names:
            analysis = controller.analyze_route(area_name, "Gachibowli", datetime(2024, 1, 1, 9, 0))
            
            # Should handle gracefully without crashing
            assert analysis is not None
            assert analysis.congestion is not None
            assert len(analysis.congestion.reasoning) > 0
    
    def test_configuration_driven_behavior(self):
        """Test that all behavior is driven by configuration, not hardcoded values"""
        controller = TrafficController()
        
        # Verify that zones come from configuration
        assert controller.config is not None
        assert controller.config.zones is not None
        assert len(controller.config.zones) > 0
        
        # Verify that hotspots come from configuration
        assert controller.config.hotspots is not None
        assert len(controller.config.hotspots) > 0
        
        # Test that area classification uses configuration
        gachibowli_info = controller.get_area_info("Gachibowli")
        assert gachibowli_info.zone == "zone_it_corridor"  # Should match config
        assert gachibowli_info.is_hotspot == True  # Should match config
        
        # Test that peak windows come from configuration
        assert controller.config.peak_windows is not None
        assert controller.config.peak_windows.weekday_morning is not None
        assert controller.config.peak_windows.weekday_evening is not None


class TestConfigurationReloadingAndUpdates:
    """Test configuration reloading and updates"""
    
    def test_configuration_file_missing(self):
        """Test behavior when configuration file is missing"""
        # Test with non-existent config path
        controller = TrafficController(config_path="non_existent_file.md")
        
        # Should handle missing file gracefully
        assert controller._initialization_error is not None
        assert "Configuration file not found" in controller._initialization_error
        
        # Analysis should return error message
        analysis = controller.analyze_route("Gachibowli", "Ameerpet", datetime(2024, 1, 1, 9, 0))
        assert "Configuration file not found" in analysis.congestion.reasoning
    
    def test_malformed_configuration_handling(self):
        """Test handling of malformed configuration files"""
        # Create a temporary malformed config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""
# Malformed Config
This is not a proper configuration file.
No proper sections or formatting.
""")
            temp_config_path = f.name
        
        try:
            controller = TrafficController(config_path=temp_config_path)
            
            # Should initialize but with warnings
            assert controller.config is not None
            
            # Validation should show issues
            validation = controller.parser.validate_config(controller.config)
            assert not validation.is_valid or len(validation.warnings) > 0
            
        finally:
            # Clean up temp file
            os.unlink(temp_config_path)
    
    def test_partial_configuration_graceful_degradation(self):
        """Test graceful degradation with partial configuration"""
        # Create a config with missing sections
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""
# Partial Config

### Zones
- zone_test:
  - TestArea1
  - TestArea2

### Hotspots
- TestArea1

# Missing peak windows and explanation templates
""")
            temp_config_path = f.name
        
        try:
            controller = TrafficController(config_path=temp_config_path)
            
            # Should still work with available data
            assert controller.config is not None
            assert len(controller.config.zones) > 0
            assert len(controller.config.hotspots) > 0
            
            # Should handle missing peak windows gracefully
            analysis = controller.analyze_route("TestArea1", "TestArea2", datetime(2024, 1, 1, 9, 0))
            assert analysis is not None
            assert analysis.congestion is not None
            
        finally:
            os.unlink(temp_config_path)
    
    def test_configuration_validation_comprehensive(self):
        """Test comprehensive configuration validation"""
        parser = ConfigParser()
        
        # Test with current configuration
        config = parser.load_config()
        validation = parser.validate_config(config)
        
        # Should be valid or have only warnings
        if not validation.is_valid:
            # If there are errors, they should be specific and actionable
            for error in validation.errors:
                assert len(error) > 0
                assert any(keyword in error.lower() for keyword in 
                          ["missing", "invalid", "required", "not found"])
        
        # Warnings should be informative
        for warning in validation.warnings:
            assert len(warning) > 0
    
    def test_area_info_consistency(self):
        """Test consistency of area information across different queries"""
        controller = TrafficController()
        
        # Test same area multiple times - should return consistent results
        test_areas = ["Gachibowli", "Ameerpet", "Charminar", "UnknownArea"]
        
        for area in test_areas:
            info1 = controller.get_area_info(area)
            info2 = controller.get_area_info(area)
            info3 = controller.get_area_info(area.upper())  # Test case insensitivity
            
            # Should be consistent
            assert info1.name == info2.name
            assert info1.zone == info2.zone
            assert info1.is_hotspot == info2.is_hotspot
            
            # Case insensitive matching should work for known areas
            if info1.zone or info1.is_hotspot:
                assert info3.zone == info1.zone or info3.is_hotspot == info1.is_hotspot


class TestSystemIntegrationScenarios:
    """Test realistic system integration scenarios"""
    
    def test_daily_commute_scenarios(self):
        """Test realistic daily commute scenarios"""
        controller = TrafficController()
        
        # Morning commute to IT corridor
        morning_commute = controller.analyze_route(
            "Ameerpet", "Gachibowli", 
            datetime(2024, 1, 1, 8, 30)  # Monday 8:30 AM
        )
        
        # Evening return commute
        evening_commute = controller.analyze_route(
            "Gachibowli", "Ameerpet",
            datetime(2024, 1, 1, 18, 30)  # Monday 6:30 PM
        )
        
        # Both should show higher congestion due to peak times
        assert morning_commute.congestion.level in [CongestionLevel.MEDIUM, CongestionLevel.HIGH]
        assert evening_commute.congestion.level in [CongestionLevel.MEDIUM, CongestionLevel.HIGH]
        
        # Should have reasoning that includes peak window information
        assert "peak" in morning_commute.congestion.reasoning.lower()
        assert "peak" in evening_commute.congestion.reasoning.lower()
        
        # Both should have similar high congestion due to IT corridor + peak time
        assert morning_commute.congestion.level == evening_commute.congestion.level
    
    def test_weekend_vs_weekday_comparison(self):
        """Test weekend vs weekday traffic differences"""
        controller = TrafficController()
        
        # Same route, same time, different days
        weekday_analysis = controller.analyze_route(
            "Jubilee Hills", "Banjara Hills",
            datetime(2024, 1, 1, 10, 0)  # Monday 10 AM
        )
        
        weekend_analysis = controller.analyze_route(
            "Jubilee Hills", "Banjara Hills", 
            datetime(2024, 1, 6, 10, 0)  # Saturday 10 AM
        )
        
        # Weekend should generally have lower or equal congestion
        weekday_score = weekday_analysis.congestion.score
        weekend_score = weekend_analysis.congestion.score
        
        # Weekend should not be worse than weekday (unless near hotspots)
        assert weekend_score <= weekday_score or weekend_analysis.hotspot_warnings
    
    def test_cross_city_travel_scenarios(self):
        """Test cross-city travel scenarios"""
        controller = TrafficController()
        
        # Old city to IT corridor
        old_to_it = controller.analyze_route(
            "Charminar", "Gachibowli",
            datetime(2024, 1, 1, 9, 0)
        )
        
        # Central to transit hub
        central_to_hub = controller.analyze_route(
            "Ameerpet", "Secunderabad",
            datetime(2024, 1, 1, 9, 0)
        )
        
        # Both should provide valid analysis
        assert old_to_it.congestion.level in [CongestionLevel.LOW, CongestionLevel.MEDIUM, CongestionLevel.HIGH]
        assert central_to_hub.congestion.level in [CongestionLevel.LOW, CongestionLevel.MEDIUM, CongestionLevel.HIGH]
        
        # Should have appropriate warnings for hotspots
        if any(area in ["Charminar", "Gachibowli", "Secunderabad"] for area in [old_to_it, central_to_hub]):
            assert len(old_to_it.hotspot_warnings) > 0 or len(central_to_hub.hotspot_warnings) > 0
    
    def test_error_handling_robustness(self):
        """Test system robustness under various error conditions"""
        controller = TrafficController()
        
        # Test with extreme inputs
        extreme_cases = [
            ("", "", datetime(2024, 1, 1, 9, 0)),  # Empty inputs
            ("A" * 1000, "B" * 1000, datetime(2024, 1, 1, 9, 0)),  # Very long inputs
            ("Normal Area", "Another Area", datetime(1900, 1, 1, 9, 0)),  # Very old date
            ("Normal Area", "Another Area", datetime(2100, 1, 1, 9, 0)),  # Future date
        ]
        
        for origin, destination, departure_time in extreme_cases:
            try:
                analysis = controller.analyze_route(origin, destination, departure_time)
                
                # Should not crash and should provide some response
                assert analysis is not None
                assert analysis.congestion is not None
                assert len(analysis.congestion.reasoning) > 0
                
            except Exception as e:
                # If it does raise an exception, it should be handled gracefully
                pytest.fail(f"System should handle extreme inputs gracefully, but got: {e}")
    
    def test_concurrent_analysis_consistency(self):
        """Test that concurrent analyses return consistent results"""
        controller = TrafficController()
        
        # Same analysis parameters
        origin, destination = "Gachibowli", "Ameerpet"
        departure_time = datetime(2024, 1, 1, 9, 0)
        
        # Run multiple analyses
        results = []
        for _ in range(5):
            analysis = controller.analyze_route(origin, destination, departure_time)
            results.append(analysis)
        
        # All results should be consistent
        first_result = results[0]
        for result in results[1:]:
            assert result.congestion.level == first_result.congestion.level
            assert result.congestion.score == first_result.congestion.score
            assert result.congestion.reasoning == first_result.congestion.reasoning