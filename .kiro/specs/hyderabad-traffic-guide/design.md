# Design Document

## Overview

The Hyderabad Traffic Guide is a Streamlit-based web application that provides intelligent traffic guidance for local commuters. The system follows a configuration-driven approach where all Hyderabad-specific traffic knowledge is centralized in a single product configuration file, enabling easy maintenance and updates without code changes.

The application implements a heuristic-based scoring system that evaluates traffic conditions based on time windows, geographical zones, and known hotspots to provide practical departure recommendations.

## Architecture

The system follows a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────┐
│           Streamlit UI              │
├─────────────────────────────────────┤
│         Traffic Controller          │
├─────────────────────────────────────┤
│    Scoring Engine    │   Reasoning  │
├─────────────────────────────────────┤
│       Configuration Parser          │
├─────────────────────────────────────┤
│      Product Config (.md file)      │
└─────────────────────────────────────┘
```

**Key Architectural Principles:**
- Configuration-driven: All domain knowledge externalized to product.md
- Stateless processing: Each request is independent
- Modular design: Clear interfaces between components
- Testable components: Each layer can be tested independently

## Components and Interfaces

### Configuration Parser
**Purpose:** Loads and validates traffic rules from product.md
**Interface:**
```python
class ConfigParser:
    def load_config(self, file_path: str) -> TrafficConfig
    def validate_config(self, config: TrafficConfig) -> ValidationResult
    def extract_zones(self, config: TrafficConfig) -> Dict[str, List[str]]
    def extract_peak_windows(self, config: TrafficConfig) -> PeakWindows
    def extract_hotspots(self, config: TrafficConfig) -> List[str]
```

### Scoring Engine
**Purpose:** Computes congestion scores using configuration rules
**Interface:**
```python
class ScoringEngine:
    def calculate_congestion(self, origin: str, destination: str, 
                           departure_time: datetime) -> CongestionResult
    def apply_peak_window_penalty(self, base_score: int, time: datetime) -> int
    def apply_corridor_multiplier(self, score: int, locations: List[str]) -> int
    def apply_hotspot_penalty(self, score: int, locations: List[str]) -> int
```

### Reasoning Engine
**Purpose:** Generates explanations for scoring decisions
**Interface:**
```python
class ReasoningEngine:
    def generate_explanation(self, result: CongestionResult) -> str
    def get_departure_recommendation(self, result: CongestionResult) -> str
    def format_detailed_reasoning(self, result: CongestionResult) -> str
```

### Traffic Controller
**Purpose:** Orchestrates the traffic analysis workflow
**Interface:**
```python
class TrafficController:
    def analyze_route(self, origin: str, destination: str, 
                     departure_time: datetime) -> TrafficAnalysis
    def get_area_info(self, area_name: str) -> AreaInfo
    def suggest_area_addition(self, area_name: str) -> str
```

## Data Models

### Core Data Structures

```python
@dataclass
class TrafficConfig:
    peak_windows: PeakWindows
    zones: Dict[str, List[str]]
    hotspots: List[str]
    explanation_templates: Dict[str, str]
    scoring_rules: ScoringRules

@dataclass
class PeakWindows:
    weekday_morning: TimeRange
    weekday_evening: TimeRange
    weekend_pattern: str

@dataclass
class CongestionResult:
    level: CongestionLevel  # Low, Medium, High
    score: int
    triggered_rules: List[str]
    departure_recommendation: str
    reasoning: str

@dataclass
class TrafficAnalysis:
    congestion: CongestionResult
    hotspot_warnings: List[str]
    departure_window: str
    detailed_reasoning: str

enum CongestionLevel:
    LOW = "Low"
    MEDIUM = "Medium" 
    HIGH = "High"
```

## Error Handling

### Configuration Errors
- **Missing product.md**: Display clear error message and setup instructions
- **Malformed configuration**: Validate sections and provide specific error details
- **Invalid time formats**: Parse with fallback defaults and log warnings
- **Missing required sections**: Continue with available data, warn about limitations

### User Input Errors
- **Unknown locations**: Check against configuration, suggest addition process
- **Invalid time formats**: Provide input validation with helpful error messages
- **Empty inputs**: Display validation messages and input requirements

### Runtime Errors
- **Scoring calculation failures**: Fall back to conservative (High) congestion estimates
- **Template rendering errors**: Use fallback explanation text
- **File I/O errors**: Cache last known good configuration when possible

## Testing Strategy

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

## Correctness Properties

Based on the prework analysis, I'll consolidate related properties to eliminate redundancy and focus on unique validation value:

**Property 1: Configuration-driven scoring**
*For any* origin and destination locations, the congestion score calculation should reference only rules loaded from Product_Config and never use hardcoded values
**Validates: Requirements 4.1**

**Property 2: Valid congestion levels**
*For any* input combination, the system should return exactly one of the three valid congestion levels: Low, Medium, or High
**Validates: Requirements 1.2**

**Property 3: Departure recommendations format**
*For any* congestion calculation, the system should provide a departure recommendation that follows either "leave now" or "wait until [specific time window]" format
**Validates: Requirements 1.3**

**Property 4: Scoring rule application**
*For any* route and time combination, when peak window conditions are detected, IT corridor multipliers apply, or hotspot penalties trigger, the congestion score should increase by the specified amount while respecting the High level cap
**Validates: Requirements 2.1, 2.2, 2.3, 2.5**

**Property 5: Weekend adjustment**
*For any* weekend route calculation, the congestion score should be reduced by one level unless the route involves hotspot locations
**Validates: Requirements 2.4**

**Property 6: Family-friendly content filtering**
*For any* system-generated suggestion or stop recommendation, the output text should contain only "quiet/family-friendly" phrasing and exclude nightlife-related content
**Validates: Requirements 3.1**

**Property 7: Preference-based filtering**
*For any* route recommendation, when nightlife avoidance preferences are enabled, the system should filter suggestions to exclude nightlife-heavy corridors
**Validates: Requirements 3.4**

**Property 8: Configuration parsing completeness**
*For any* valid Product_Config file, the parser should successfully extract all required sections: peak windows, hotspots, zone classifications, and explanation templates
**Validates: Requirements 4.2**

**Property 9: Unknown area handling**
*For any* area name not present in Product_Config, the system should respond with the specific message that the area is not in the local dataset
**Validates: Requirements 4.3**

**Property 10: Configuration validation**
*For any* Product_Config file with missing or malformed sections, the validation process should identify specific issues and provide clear error messages
**Validates: Requirements 5.1, 5.2**

**Property 11: Graceful error recovery**
*For any* configuration containing both valid and invalid data sections, the system should continue operating with valid portions while handling errors gracefully
**Validates: Requirements 5.5**

### Dual Testing Approach

**Unit Testing:**
- Test specific examples of peak window detection
- Verify hotspot penalty calculations with known locations
- Test configuration parsing with sample files
- Validate error handling with malformed inputs
- Test UI component rendering and preference toggles

**Property-Based Testing:**
- Use Hypothesis library for Python to generate random test cases
- Configure each property test to run minimum 100 iterations
- Generate random location pairs, times, and configuration variations
- Test scoring consistency across input variations
- Validate that all outputs conform to expected formats and constraints

Each property-based test will be tagged with comments explicitly referencing the design document property using the format: **Feature: hyderabad-traffic-guide, Property {number}: {property_text}**

The combination of unit tests (specific examples) and property tests (universal properties) ensures comprehensive coverage where unit tests catch concrete bugs and property tests verify general correctness across the input space.