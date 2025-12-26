# Hyderabad Traffic Guide

A clean, minimal web application that provides quick traffic suggestions for everyday trips within Hyderabad. Get instant "leave now" or "wait until" recommendations based on local traffic patterns and hotspots.

## Features

- **🚗 Simple Traffic Analysis**: Get Low/Medium/High congestion ratings with clear recommendations
- **⏰ Smart Timing**: Departure suggestions based on Hyderabad's peak hours and traffic patterns  
- **🗺️ Abstract Route Visualization**: See your route with traffic hotspots highlighted
- **🏠 Family-Friendly Focus**: All suggestions prioritize safe, family-friendly routes
- **📱 Clean Interface**: Minimal, distraction-free design focused on essential information
- **🎯 Local Knowledge**: Specialized for Hyderabad's IT corridor, central areas, and known hotspots

## Quick Start

### Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Launch the web application**:
   ```bash
   streamlit run streamlit_app.py
   ```
   Open your browser to `http://localhost:8501`

### Using the App

1. **Select locations** from the dropdown menus (100+ Hyderabad areas available)
2. **Choose your departure time** using the date and time pickers
3. **Click "Get Traffic Suggestion"** for instant analysis
4. **View results** with color-coded traffic levels and route visualization

## Interface Overview

### Main Features
- **Location Selection**: Choose from comprehensive list of Hyderabad areas
- **Time Selection**: Pick any future departure time
- **Traffic Analysis**: Get instant Low 🟢 / Medium 🟡 / High 🔴 ratings
- **Route Visualization**: See abstract route map with hotspots marked
- **Clear Recommendations**: Simple "leave now" or "wait until X" guidance

### Sidebar Information
- **Peak Hours**: Quick reference for morning (8-11 AM) and evening (5-8 PM) rush
- **Minimal Design**: Only essential information, no clutter

## Covered Areas

The app includes 100+ locations across Hyderabad:

### 🏢 IT Corridor
Gachibowli, Financial District, Hitec City, Madhapur, Kondapur, Kukatpally, Miyapur, Jubilee Hills, Banjara Hills, and more

### 🏛️ Central Areas  
Punjagutta, Ameerpet, Begumpet, Lakdi-ka-pul, Abids, Koti, Somajiguda, and more

### 🏘️ Dense Core
Charminar, Dilsukhnagar, LB Nagar, Malakpet, Mehdipatnam, and more

### 🚉 Transit Hubs
Secunderabad, MGBS, Kacheguda, Metro stations, and more

### ⚠️ Event-Sensitive Areas
Bison Signal, Paradise Circle, Karkhana, and other areas prone to diversions

## How It Works

### Traffic Analysis Logic
- **Peak Hours**: Weekday mornings (8-11 AM) and evenings (5-8 PM) get higher congestion scores
- **IT Corridor Boost**: Routes to/from tech hubs get additional congestion during peak hours  
- **Hotspot Penalties**: Known traffic bottlenecks increase congestion ratings
- **Weekend Adjustments**: Lighter traffic on weekends unless near busy areas

### Color-Coded Results
- **🟢 Green (Low)**: Good to go, minimal delays expected
- **🟡 Orange (Medium)**: Plan extra time, moderate congestion likely
- **🔴 Red (High)**: Consider waiting or expect significant delays

### Route Visualization
- **Abstract Route Map**: Shows your journey path with key locations
- **Hotspot Warnings**: Traffic-prone areas highlighted in red
- **Distance Information**: Approximate route distance displayed

## Important Note

**This tool provides traffic suggestions based on general patterns. Actual conditions may vary. For official updates, check local traffic authorities.**

The app uses local heuristics and patterns rather than real-time data, making it a helpful planning tool but not a guarantee of exact conditions.

## Technical Details

### Architecture
```
Streamlit Web App → Traffic Controller → Scoring Engine → Configuration Rules
```

### Configuration
All traffic knowledge is stored in `.kiro/steering/product.md` including:
- Peak time windows
- Area classifications  
- Known hotspots
- Scoring rules

### Dependencies
- **Streamlit**: Web interface
- **Folium**: Route visualization  
- **Geopy**: Location handling
- **Python 3.8+**: Core runtime

## Project Structure

```
├── app/                   # Traffic controller and orchestration
│   ├── __init__.py
│   └── traffic_controller.py
├── models/                # Core data models
│   ├── __init__.py
│   └── data_models.py     # TrafficConfig, CongestionResult, etc.
├── parsers/               # Configuration parsing
│   ├── __init__.py
│   └── config_parser.py   # Loads and validates product.md
├── scoring/               # Traffic scoring engine
│   ├── __init__.py
│   └── scoring_engine.py  # Heuristic-based congestion calculation
├── reasoning/             # Explanation generation
│   ├── __init__.py
│   └── reasoning_engine.py # Generates human-readable explanations
├── filtering/             # Content filtering
│   ├── __init__.py
│   └── content_filter.py  # Family-friendly content filtering
├── tests/                 # Comprehensive test suite
│   ├── __init__.py
│   ├── test_*.py         # Unit and property-based tests
│   └── test_traffic_controller_integration.py # End-to-end tests
├── .kiro/
│   └── steering/
│       └── product.md     # Configuration file with all traffic rules
├── main.py               # Command-line demo
├── streamlit_app.py      # Web application
└── requirements.txt      # Python dependencies
```

## Configuration

All traffic knowledge is centralized in `.kiro/steering/product.md`. This file contains:

- **Peak Windows**: Weekday morning (8:00-11:00) and evening (17:00-20:00) rush hours
- **Zone Classifications**: IT corridor, central, dense core, transit hubs, event-sensitive
- **Hotspots**: Known congestion areas across different zones
- **Explanation Templates**: Human-readable reasoning for different scenarios
- **Scoring Rules**: Heuristic logic for congestion calculation

### Adding New Areas

When the system encounters an unknown area, it will prompt for:
1. Area name
2. Zone classification (zone_it_corridor, zone_central, etc.)
3. Nearby landmark
4. Hotspot status (yes/no)

Add new areas to the appropriate zone in `product.md`:

```markdown
### Zones
- zone_central:
  - Existing Area 1
  - Existing Area 2
  - Your New Area  # Add here
```

And to hotspots if applicable:

```markdown
### Hotspots
- Central business / arterials:
  - Existing Hotspot 1
  - Your New Area  # Add here if it's a hotspot
```

## API Reference

### TrafficController

Main orchestration class for traffic analysis.

```python
from app.traffic_controller import TrafficController

controller = TrafficController()
```

#### Methods

**`analyze_route(origin, destination, departure_time)`**
- Analyzes traffic conditions for a specific route and time
- Returns `TrafficAnalysis` with congestion level, warnings, and recommendations

**`analyze_route_with_preferences(origin, destination, departure_time, avoid_nightlife, prefer_family_friendly)`**
- Same as `analyze_route` but applies content filtering based on preferences
- Filters out nightlife references and emphasizes family-friendly options

**`get_area_info(area_name)`**
- Returns `AreaInfo` with zone classification and hotspot status
- Useful for understanding how areas are categorized

**`suggest_area_addition(area_name)`**
- Generates prompt for adding unknown areas to the configuration
- Returns formatted message with required information

### Data Models

**`CongestionLevel`**: Enum with LOW, MEDIUM, HIGH values

**`CongestionResult`**: Contains level, score, triggered rules, recommendation, and reasoning

**`TrafficAnalysis`**: Complete analysis with congestion result, hotspot warnings, departure window, and detailed reasoning

**`AreaInfo`**: Area classification with name, zone, hotspot status, and nearby landmark

## Testing

The project includes comprehensive testing:

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Run Specific Test Categories
```bash
# Unit tests
python -m pytest tests/test_config_parsing.py -v

# Property-based tests
python -m pytest tests/test_scoring_rules.py -v

# Integration tests
python -m pytest tests/test_traffic_controller_integration.py -v
```

### Test Coverage
- **Unit Tests**: Test specific functions and edge cases
- **Property-Based Tests**: Test universal properties across random inputs
- **Integration Tests**: Test complete end-to-end workflows
- **Error Handling**: Test graceful degradation and recovery

## Architecture

The system follows a layered architecture:

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

### Key Principles
- **Configuration-driven**: All domain knowledge externalized to product.md
- **Stateless processing**: Each request is independent
- **Modular design**: Clear interfaces between components
- **Testable components**: Each layer can be tested independently
- **Graceful error handling**: System continues operating with partial failures

## Troubleshooting

### Common Issues

**Configuration file not found**
```
Error: Configuration file not found: .kiro/steering/product.md
```
- Ensure the product.md file exists in the correct location
- Check file permissions

**Invalid configuration format**
```
Warning: Configuration validation issues: ['Peak windows configuration is missing']
```
- Verify all required sections are present in product.md
- Check markdown formatting and section headers

**Unknown area responses**
```
"That area isn't in my local dataset yet—add it to product.md"
```
- Add the area to the appropriate zone in product.md
- Include in hotspots list if it's a congestion area

**Import errors**
```
ModuleNotFoundError: No module named 'streamlit'
```
- Install dependencies: `pip install -r requirements.txt`
- Ensure you're using the correct Python environment

### Getting Help

1. **Check the logs**: The system logs warnings and errors to help diagnose issues
2. **Validate configuration**: Run `python main.py` to check configuration status
3. **Test specific components**: Use the test suite to isolate issues
4. **Review requirements**: Ensure all dependencies are installed correctly

## Development

### Adding New Features

1. **Update requirements**: Add acceptance criteria to requirements.md
2. **Design components**: Update design.md with new interfaces
3. **Implement incrementally**: Follow the task-based approach
4. **Write tests**: Include both unit and property-based tests
5. **Update configuration**: Add any new rules to product.md

### Code Style

- Follow Python PEP 8 conventions
- Use type hints for better code clarity
- Include docstrings for public methods
- Handle errors gracefully with informative messages
- Keep functions focused and testable

## License

This project is designed for local Hyderabad traffic guidance and educational purposes.

## Contributing

When contributing:
1. Ensure all tests pass
2. Update documentation for new features
3. Follow the configuration-driven approach
4. Include appropriate error handling
5. Test with various input scenarios