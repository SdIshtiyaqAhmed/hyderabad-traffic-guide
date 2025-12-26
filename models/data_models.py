"""
Core data models for Hyderabad Traffic Guide
"""
from dataclasses import dataclass
from datetime import datetime, time
from enum import Enum
from typing import Dict, List, Optional


class CongestionLevel(Enum):
    """Enumeration for congestion levels"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


@dataclass
class TimeRange:
    """Represents a time range with start and end times"""
    start: time
    end: time


@dataclass
class PeakWindows:
    """Peak traffic windows configuration"""
    weekday_morning: Optional[TimeRange]
    weekday_evening: Optional[TimeRange]
    weekend_pattern: str


@dataclass
class ScoringRules:
    """Rules for scoring traffic congestion"""
    base_score_level: CongestionLevel
    peak_window_penalty: int
    it_corridor_multiplier: int
    hotspot_penalty: int
    weekend_reduction: int


@dataclass
class TrafficConfig:
    """Main configuration structure loaded from product.md"""
    peak_windows: PeakWindows
    zones: Dict[str, List[str]]
    hotspots: List[str]
    explanation_templates: Dict[str, str]
    scoring_rules: ScoringRules


@dataclass
class CongestionResult:
    """Result of congestion analysis"""
    level: CongestionLevel
    score: int
    triggered_rules: List[str]
    departure_recommendation: str
    reasoning: str


@dataclass
class AreaInfo:
    """Information about a specific area"""
    name: str
    zone: Optional[str]
    is_hotspot: bool
    nearby_landmark: Optional[str]


@dataclass
class TrafficAnalysis:
    """Complete traffic analysis result"""
    congestion: CongestionResult
    hotspot_warnings: List[str]
    departure_window: str
    detailed_reasoning: str


@dataclass
class ValidationResult:
    """Result of configuration validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]