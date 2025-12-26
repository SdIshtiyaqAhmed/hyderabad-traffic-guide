"""
Configuration parser for loading and validating product.md
"""
import re
from datetime import time
from pathlib import Path
from typing import Dict, List, Optional

from models.data_models import (
    TrafficConfig, PeakWindows, TimeRange, ScoringRules, 
    ValidationResult, CongestionLevel
)


class ConfigParser:
    """Parser for product.md configuration file"""
    
    def __init__(self):
        self.config_path = Path(".kiro/steering/product.md")
    
    def load_config(self, file_path: Optional[str] = None) -> TrafficConfig:
        """Load configuration from product.md file"""
        config_file = Path(file_path) if file_path else self.config_path
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        content = config_file.read_text(encoding='utf-8')
        
        # Parse different sections
        peak_windows = self._parse_peak_windows(content)
        zones = self._parse_zones(content)
        hotspots = self._parse_hotspots(content)
        explanation_templates = self._parse_explanation_templates(content)
        scoring_rules = self._create_default_scoring_rules()
        
        return TrafficConfig(
            peak_windows=peak_windows,
            zones=zones,
            hotspots=hotspots,
            explanation_templates=explanation_templates,
            scoring_rules=scoring_rules
        )
    
    def validate_config(self, config: TrafficConfig) -> ValidationResult:
        """Validate the loaded configuration"""
        errors = []
        warnings = []
        
        # Validate peak windows
        if not config.peak_windows:
            errors.append("Peak windows configuration is missing")
        else:
            if not config.peak_windows.weekday_morning:
                errors.append("Weekday morning peak window is missing")
            if not config.peak_windows.weekday_evening:
                errors.append("Weekday evening peak window is missing")
        
        # Validate zones
        if not config.zones:
            errors.append("Zones configuration is missing")
        elif len(config.zones) == 0:
            warnings.append("No zones defined in configuration")
        
        # Validate hotspots
        if not config.hotspots:
            warnings.append("No hotspots defined in configuration")
        
        # Validate explanation templates
        required_templates = [
            "Peak window triggered",
            "IT corridor triggered", 
            "Hotspot triggered",
            "Weekend adjustment"
        ]
        
        for template in required_templates:
            if template not in config.explanation_templates:
                warnings.append(f"Missing explanation template: {template}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def extract_zones(self, config: TrafficConfig) -> Dict[str, List[str]]:
        """Extract zone information from configuration"""
        return config.zones
    
    def extract_peak_windows(self, config: TrafficConfig) -> PeakWindows:
        """Extract peak windows from configuration"""
        return config.peak_windows
    
    def extract_hotspots(self, config: TrafficConfig) -> List[str]:
        """Extract hotspots from configuration"""
        return config.hotspots
    
    def _parse_peak_windows(self, content: str) -> PeakWindows:
        """Parse peak windows from markdown content"""
        # Look for peak windows section
        peak_section = self._extract_section(content, "Peak windows")
        
        if not peak_section.strip():
            # Return None-like structure to indicate missing peak windows
            return PeakWindows(
                weekday_morning=None,
                weekday_evening=None,
                weekend_pattern=""
            )
        
        # Default values based on product.md
        morning_start = time(8, 0)
        morning_end = time(11, 0)
        evening_start = time(17, 0)
        evening_end = time(20, 0)
        
        # Parse morning peak with error handling
        morning_match = re.search(r'morning peak:\s*(\d{2}):(\d{2})–(\d{2}):(\d{2})', peak_section)
        if morning_match:
            try:
                morning_start = time(int(morning_match.group(1)), int(morning_match.group(2)))
                morning_end = time(int(morning_match.group(3)), int(morning_match.group(4)))
            except (ValueError, OverflowError):
                # Invalid time values, use defaults
                pass
        
        # Parse evening peak with error handling
        evening_match = re.search(r'evening peak:\s*(\d{2}):(\d{2})–(\d{2}):(\d{2})', peak_section)
        if evening_match:
            try:
                evening_start = time(int(evening_match.group(1)), int(evening_match.group(2)))
                evening_end = time(int(evening_match.group(3)), int(evening_match.group(4)))
            except (ValueError, OverflowError):
                # Invalid time values, use defaults
                pass
        
        return PeakWindows(
            weekday_morning=TimeRange(morning_start, morning_end),
            weekday_evening=TimeRange(evening_start, evening_end),
            weekend_pattern="lighter mornings; evenings can still be busy"
        )
    
    def _parse_zones(self, content: str) -> Dict[str, List[str]]:
        """Parse zones from markdown content"""
        zones = {}
        
        # Look for zones section
        zones_section = self._extract_section(content, "Zones")
        
        if not zones_section.strip():
            return zones  # Return empty dict if no zones section found
        
        # Parse each zone - handle the format: "- zone_name:" followed by indented areas
        lines = zones_section.split('\n')
        current_zone = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('- zone_'):
                # Extract zone name (remove the colon at the end)
                current_zone = line[2:].rstrip(':')
                zones[current_zone] = []
            elif line.startswith('- ') and current_zone:
                # This is an area under the current zone
                area = line[2:].strip()
                if area:
                    zones[current_zone].append(area)
        
        return zones
    
    def _parse_hotspots(self, content: str) -> List[str]:
        """Parse hotspots from markdown content"""
        hotspots = []
        
        # Look for hotspots section
        hotspots_section = self._extract_section(content, "Hotspots")
        
        # Extract all areas mentioned in the hotspots section
        # Skip section headers and category labels
        lines = hotspots_section.split('\n')
        
        for line in lines:
            line = line.strip()
            # Skip empty lines, section headers, and category descriptions
            if (line.startswith('- ') and 
                not line.endswith(':') and 
                'IT corridor' not in line and 
                'Central business' not in line and 
                'Old city' not in line and 
                'Transit hubs' not in line and 
                'Event-sensitive' not in line):
                
                hotspot = line[2:].strip()
                if hotspot:
                    hotspots.append(hotspot)
        
        return hotspots
    
    def _parse_explanation_templates(self, content: str) -> Dict[str, str]:
        """Parse explanation templates from markdown content"""
        templates = {}
        
        # Look for explanation templates section
        templates_section = self._extract_section(content, "Explanation templates")
        
        # Parse template patterns
        template_pattern = r'- (.+?):\s*"(.+?)"'
        matches = re.findall(template_pattern, templates_section)
        
        for key, value in matches:
            templates[key] = value
        
        # Add default templates if not found
        default_templates = {
            "Peak window triggered": "Departure time falls in a typical peak window.",
            "IT corridor triggered": "One endpoint is in the west/IT corridor, which usually amplifies peak-hour congestion.",
            "Hotspot triggered": "This route touches a known slow zone, so delays are more likely.",
            "Weekend adjustment": "Weekend traffic is often smoother unless you're near busy hotspots."
        }
        
        for key, value in default_templates.items():
            if key not in templates:
                templates[key] = value
        
        return templates
    
    def _create_default_scoring_rules(self) -> ScoringRules:
        """Create default scoring rules based on product.md logic"""
        return ScoringRules(
            base_score_level=CongestionLevel.LOW,
            peak_window_penalty=1,
            it_corridor_multiplier=1,
            hotspot_penalty=1,
            weekend_reduction=1
        )
    
    def _extract_section(self, content: str, section_name: str) -> str:
        """Extract a specific section from markdown content"""
        # Look for section header (case insensitive)
        pattern = rf'###?\s*{re.escape(section_name)}.*?\n(.*?)(?=###|\Z)'
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        
        if match:
            return match.group(1)
        
        return ""