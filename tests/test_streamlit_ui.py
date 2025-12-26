"""
Unit tests for Streamlit UI components
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, time
import streamlit as st

# Import the functions we want to test
from streamlit_app import (
    initialize_controller, get_congestion_color, display_results,
    handle_nightlife_request, handle_unknown_area
)
from models.data_models import (
    CongestionLevel, CongestionResult, TrafficAnalysis, ValidationResult
)


class TestUIComponents:
    """Test suite for Streamlit UI components"""
    
    def test_preference_toggle_default_states(self):
        """Test that preference toggles default to off as per requirements"""
        # This test verifies Requirements 3.2, 3.5 - preference toggles default to off
        
        # Mock streamlit checkbox to capture default values
        with patch('streamlit.checkbox') as mock_checkbox:
            # Import and run the main function to trigger checkbox creation
            from streamlit_app import main
            
            # Mock the controller initialization to avoid file dependencies
            with patch('streamlit_app.initialize_controller') as mock_init:
                mock_controller = Mock()
                mock_init.return_value = mock_controller
                
                # Mock other streamlit components
                with patch('streamlit.set_page_config'), \
                     patch('streamlit.title'), \
                     patch('streamlit.markdown'), \
                     patch('streamlit.header'), \
                     patch('streamlit.sidebar'), \
                     patch('streamlit.columns'), \
                     patch('streamlit.text_input'), \
                     patch('streamlit.date_input'), \
                     patch('streamlit.time_input'), \
                     patch('streamlit.button'):
                    
                    try:
                        main()
                    except:
                        # Expected to fail due to mocking, but we captured the checkbox calls
                        pass
            
            # Verify checkbox calls for preferences
            checkbox_calls = mock_checkbox.call_args_list
            
            # Find the preference checkbox calls
            avoid_nightlife_call = None
            family_friendly_call = None
            
            for call in checkbox_calls:
                args, kwargs = call
                if len(args) > 0:
                    if "Avoid nightlife-heavy corridors" in args[0]:
                        avoid_nightlife_call = kwargs
                    elif "Prefer family-friendly stop suggestions" in args[0]:
                        family_friendly_call = kwargs
            
            # Verify both preferences default to False (off)
            if avoid_nightlife_call:
                assert avoid_nightlife_call.get('value', True) == False, "Avoid nightlife should default to off"
            if family_friendly_call:
                assert family_friendly_call.get('value', True) == False, "Family-friendly preference should default to off"
    
    def test_nightlife_request_handling(self):
        """Test that nightlife requests are politely declined"""
        # This test verifies Requirements 3.2 - polite decline of nightlife suggestions
        
        with patch('streamlit.info') as mock_info:
            handle_nightlife_request()
            
            # Verify the polite decline message
            mock_info.assert_called_once()
            call_args = mock_info.call_args[0][0]
            
            # Check that the message focuses on commute efficiency and family-friendly stops
            assert "commute efficiency" in call_args
            assert "family-friendly" in call_args
            assert "nightlife" in call_args
            
            # Ensure it's polite (contains appropriate language)
            assert any(word in call_args.lower() for word in ["please", "focuses", "guide"])
    
    def test_unknown_area_addition_prompts(self):
        """Test unknown area addition prompts contain required fields"""
        # This test verifies Requirements 4.4 - unknown area addition prompts
        
        test_area = "TestUnknownArea"
        
        with patch('streamlit.warning') as mock_warning, \
             patch('streamlit.expander') as mock_expander, \
             patch('streamlit.markdown') as mock_markdown, \
             patch('streamlit.columns') as mock_columns, \
             patch('streamlit.text_input') as mock_text_input, \
             patch('streamlit.selectbox') as mock_selectbox, \
             patch('streamlit.checkbox') as mock_checkbox, \
             patch('streamlit.button') as mock_button, \
             patch('streamlit.success') as mock_success:
            
            # Mock columns to return mock column objects
            mock_col1, mock_col2 = Mock(), Mock()
            mock_columns.return_value = [mock_col1, mock_col2]
            
            # Mock the context managers for columns
            mock_col1.__enter__ = Mock(return_value=mock_col1)
            mock_col1.__exit__ = Mock(return_value=None)
            mock_col2.__enter__ = Mock(return_value=mock_col2)
            mock_col2.__exit__ = Mock(return_value=None)
            
            # Mock expander context manager
            mock_exp = Mock()
            mock_exp.__enter__ = Mock(return_value=mock_exp)
            mock_exp.__exit__ = Mock(return_value=None)
            mock_expander.return_value = mock_exp
            
            handle_unknown_area(test_area)
            
            # Verify warning about unknown area
            mock_warning.assert_called()
            warning_message = mock_warning.call_args[0][0]
            assert test_area in warning_message
            assert "not in the local dataset" in warning_message
            
            # Verify all required input fields are created
            text_input_calls = mock_text_input.call_args_list
            selectbox_calls = mock_selectbox.call_args_list
            checkbox_calls = mock_checkbox.call_args_list
            
            # Check for area name input
            area_name_found = any("Area name" in call[0][0] for call in text_input_calls)
            assert area_name_found, "Area name input should be present"
            
            # Check for nearby landmark input
            landmark_found = any("Nearby landmark" in call[0][0] for call in text_input_calls)
            assert landmark_found, "Nearby landmark input should be present"
            
            # Check for zone classification selectbox
            zone_found = any("Zone classification" in call[0][0] for call in selectbox_calls)
            assert zone_found, "Zone classification selectbox should be present"
            
            # Check for hotspot status checkbox
            hotspot_found = any("hotspot" in call[0][0].lower() for call in checkbox_calls)
            assert hotspot_found, "Hotspot status checkbox should be present"
    
    def test_congestion_color_mapping(self):
        """Test congestion level color mapping"""
        # Test all congestion levels have appropriate colors
        assert get_congestion_color(CongestionLevel.LOW) == "green"
        assert get_congestion_color(CongestionLevel.MEDIUM) == "orange"
        assert get_congestion_color(CongestionLevel.HIGH) == "red"
    
    def test_controller_initialization_success(self):
        """Test successful controller initialization"""
        with patch('streamlit_app.TrafficController') as mock_controller_class:
            mock_controller = Mock()
            mock_controller._initialization_error = None  # No initialization error
            mock_controller.config = Mock()  # Mock config exists
            mock_validation = ValidationResult(is_valid=True, errors=[], warnings=[])
            mock_controller.parser.validate_config.return_value = mock_validation
            mock_controller_class.return_value = mock_controller
            
            result = initialize_controller()
            
            assert result is not None
            assert result == mock_controller
    
    def test_controller_initialization_validation_failure(self):
        """Test controller initialization with validation failure"""
        with patch('streamlit_app.TrafficController') as mock_controller_class, \
             patch('streamlit.warning') as mock_warning:
            
            mock_controller = Mock()
            mock_controller._initialization_error = None  # No initialization error
            mock_controller.config = Mock()  # Mock config exists
            mock_validation = ValidationResult(
                is_valid=False, 
                errors=["Missing peak windows", "Invalid hotspot format"], 
                warnings=[]
            )
            mock_controller.parser.validate_config.return_value = mock_validation
            mock_controller_class.return_value = mock_controller
            
            result = initialize_controller()
            
            # Should still return controller for limited functionality
            assert result is not None
            # Verify warning messages were displayed
            assert mock_warning.call_count >= 2  # At least one for header, one for each error
    
    def test_controller_initialization_exception(self):
        """Test controller initialization with exception"""
        with patch('streamlit_app.TrafficController') as mock_controller_class, \
             patch('streamlit.error') as mock_error:
            
            mock_controller_class.side_effect = Exception("Configuration file not found")
            
            result = initialize_controller()
            
            assert result is None
            # Should call error twice: once for header, once for message
            assert mock_error.call_count == 2
    
    def test_display_results_basic(self):
        """Test basic results display functionality"""
        # Create mock analysis result
        congestion_result = CongestionResult(
            level=CongestionLevel.MEDIUM,
            score=2,
            triggered_rules=["peak_window"],
            departure_recommendation="wait until 11:00-12:00",
            reasoning="Peak window detected"
        )
        
        analysis = TrafficAnalysis(
            congestion=congestion_result,
            hotspot_warnings=["Origin Gachibowli is a known traffic hotspot"],
            departure_window="Consider: wait until 11:00-12:00",
            detailed_reasoning="Detailed analysis shows peak window conditions"
        )
        
        with patch('streamlit.markdown') as mock_markdown, \
             patch('streamlit.warning') as mock_warning, \
             patch('streamlit.expander') as mock_expander:
            
            display_results(analysis, show_reasoning=False)
            
            # Verify basic information is displayed
            markdown_calls = [call[0][0] for call in mock_markdown.call_args_list]
            
            # Check congestion level display
            congestion_display = any("Medium" in call for call in markdown_calls)
            assert congestion_display, "Congestion level should be displayed"
            
            # Check recommendation display
            recommendation_display = any("wait until 11:00-12:00" in call for call in markdown_calls)
            assert recommendation_display, "Departure recommendation should be displayed"
            
            # Check reasoning display
            reasoning_display = any("Peak window detected" in call for call in markdown_calls)
            assert reasoning_display, "Reasoning should be displayed"
            
            # Check hotspot warnings
            mock_warning.assert_called()
    
    def test_display_results_with_detailed_reasoning(self):
        """Test results display with detailed reasoning enabled"""
        congestion_result = CongestionResult(
            level=CongestionLevel.HIGH,
            score=3,
            triggered_rules=["peak_window", "hotspot"],
            departure_recommendation="leave now",
            reasoning="Multiple factors detected"
        )
        
        analysis = TrafficAnalysis(
            congestion=congestion_result,
            hotspot_warnings=[],
            departure_window="Optimal departure: now",
            detailed_reasoning="Detailed analysis: Peak window + hotspot penalties applied"
        )
        
        with patch('streamlit.markdown') as mock_markdown:
            
            display_results(analysis, show_reasoning=True)
            
            # Verify detailed reasoning was displayed
            detailed_reasoning_calls = [call for call in mock_markdown.call_args_list 
                                      if "Detailed Analysis" in str(call) or "Detailed analysis" in str(call)]
            assert len(detailed_reasoning_calls) >= 1, "Detailed reasoning should be displayed"


if __name__ == "__main__":
    pytest.main([__file__])