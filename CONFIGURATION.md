# Configuration Guide - Hyderabad Traffic Guide

Simple guide to understanding how the traffic analysis works through the configuration file.

## Overview

All traffic knowledge is stored in one file:
```
.kiro/steering/product.md
```

This file contains the local traffic patterns, area classifications, and rules that power the app's suggestions.

## How It Works

### Traffic Analysis Logic
The app uses simple heuristics based on:

1. **Peak Hours**: Weekday mornings (8-11 AM) and evenings (5-8 PM)
2. **Area Types**: IT corridor, central business, dense core, transit hubs
3. **Known Hotspots**: Areas prone to congestion
4. **Weekend Adjustments**: Lighter traffic patterns on weekends

### Configuration Sections

**Peak Windows:**
```markdown
### Peak windows
- Weekday morning peak: 08:00–11:00
- Weekday evening peak: 17:00–20:00
```

**Area Classifications:**
```markdown
### Zones
- zone_it_corridor: Gachibowli, Hitec City, Madhapur...
- zone_central: Ameerpet, Punjagutta, Begumpet...
- zone_dense_core: Charminar, Dilsukhnagar, LB Nagar...
```

**Traffic Hotspots:**
```markdown
### Hotspots
- IT corridor / west: Gachibowli, Financial District...
- Central business: Punjagutta, Ameerpet...
```

## Scoring Logic

The app calculates congestion using:

1. **Base Score**: Starts at Low
2. **Peak Time Boost**: +1 level during rush hours  
3. **IT Corridor Boost**: +1 level for tech hub routes during peaks
4. **Hotspot Penalty**: +1 level when route touches known bottlenecks
5. **Weekend Reduction**: -1 level on weekends (unless near hotspots)

Final result: Low 🟢 / Medium 🟡 / High 🔴

## Adding New Areas

When the app encounters unknown locations, add them to `product.md`:

1. **Find the appropriate zone** (IT corridor, central, etc.)
2. **Add to the zone list**
3. **Add to hotspots if it's a congestion area**

Example:
```markdown
### Zones
- zone_central:
  - Existing Area 1
  - Your New Area  # Add here

### Hotspots  
- Central business:
  - Your New Area  # Add here if it causes traffic
```

## Important Notes

- **Pattern-Based**: Uses local knowledge, not real-time data
- **Heuristic Approach**: Simple rules for quick suggestions
- **Family-Friendly**: All suggestions avoid nightlife areas
- **Disclaimer Required**: Always remind users this is guidance, not guarantees
- Create new categories as needed
- Use consistent naming with zones section

### 3. Zones
Classifies areas into functional zones:

```markdown
### Zones
- zone_it_corridor:
  - Gachibowli
  - Financial District
  - Nanakramguda
  
- zone_central:
  - Punjagutta
  - Ameerpet
  - Begumpet
```

**Zone Types:**
- `zone_it_corridor`: Western Hyderabad tech hubs
- `zone_central`: Central business areas
- `zone_dense_core`: Old city dense areas
- `zone_transit_hub`: Major transport connections
- `zone_event_sensitive`: Areas affected by events/diversions

### 4. Explanation Templates
Provides human-readable explanations:

```markdown
### Explanation templates
- Peak window triggered: "Departure time falls in a typical peak window."
- IT corridor triggered: "One endpoint is in the west/IT corridor, which usually amplifies peak-hour congestion."
- Hotspot triggered: "This route touches a known slow zone, so delays are more likely."
- Weekend adjustment: "Weekend traffic is often smoother unless you're near busy hotspots."
```

### 5. Scoring Logic
Defines how congestion scores are calculated:

```markdown
### Scoring logic (heuristics)
- Base score: Start at Low
- If time falls in weekday morning peak or evening peak → raise by one level
- If either endpoint is in the IT corridor list and time overlaps a weekday peak window → raise by one additional level
- If origin or destination matches a hotspot → raise by one level during peak windows
- Weekend handling: If weekend and not near hotspots → reduce by one level
```

## Adding New Areas

### Step 1: Determine Zone Classification
Choose the appropriate zone based on the area's characteristics:

- **IT Corridor**: Tech companies, modern infrastructure, office complexes
- **Central**: Business districts, commercial areas, government offices
- **Dense Core**: Old city areas, narrow roads, high population density
- **Transit Hub**: Railway stations, bus terminals, airports
- **Event Sensitive**: Areas prone to diversions, event venues

### Step 2: Add to Zones Section
```markdown
### Zones
- zone_central:
  - Existing Area 1
  - Existing Area 2
  - Your New Area  # Add here
```

### Step 3: Add to Hotspots (if applicable)
If the area experiences regular congestion:

```markdown
### Hotspots
- Central business / arterials:
  - Existing Hotspot 1
  - Your New Area  # Add here
```

### Step 4: Test the Addition
```bash
python -c "
from app.traffic_controller import TrafficController
controller = TrafficController()
info = controller.get_area_info('Your New Area')
print(f'Zone: {info.zone}, Hotspot: {info.is_hotspot}')
"
```

## Customizing Traffic Rules

### Adjusting Peak Windows

**Current Settings:**
- Morning: 08:00–11:00
- Evening: 17:00–20:00

**To Modify:**
1. Update the times in the peak windows section
2. Consider local commute patterns
3. Account for flexible work schedules

**Example for Different City:**
```markdown
### Peak windows
- Weekday morning peak: 07:30–10:30
- Weekday evening peak: 16:30–19:30
- Weekend pattern: lighter throughout, busy near malls 14:00-18:00
```

### Modifying Scoring Rules

The scoring logic follows this pattern:
1. **Base Score**: Always starts at Low
2. **Peak Window Penalty**: +1 level during peak times
3. **IT Corridor Multiplier**: +1 level for IT corridor during peaks
4. **Hotspot Penalty**: +1 level for hotspots during peaks
5. **Weekend Adjustment**: -1 level on weekends (unless hotspots)
6. **Score Capping**: Maximum level is High

**To Adjust Penalties:**
Modify the scoring logic section to change penalty amounts or conditions.

### Customizing Explanations

Update explanation templates to match local terminology:

```markdown
### Explanation templates
- Peak window triggered: "Rush hour traffic expected at this time."
- IT corridor triggered: "Tech corridor experiences heavy commuter traffic."
- Hotspot triggered: "This area is known for traffic bottlenecks."
- Weekend adjustment: "Weekend traffic is typically lighter."
```

## Validation and Testing

### Validate Configuration
```bash
python -c "
from parsers.config_parser import ConfigParser
parser = ConfigParser()
config = parser.load_config()
validation = parser.validate_config(config)
print('Valid:', validation.is_valid)
print('Errors:', validation.errors)
print('Warnings:', validation.warnings)
"
```

### Test Specific Areas
```bash
python -c "
from app.traffic_controller import TrafficController
controller = TrafficController()
analysis = controller.analyze_route('YourArea1', 'YourArea2', datetime(2024, 1, 1, 9, 0))
print(f'Congestion: {analysis.congestion.level.value}')
print(f'Reasoning: {analysis.congestion.reasoning}')
"
```

### Run Full Test Suite
```bash
python -m pytest tests/ -v
```

## Common Configuration Patterns

### Adding a New City District

1. **Identify the district type** (business, residential, industrial)
2. **Choose appropriate zone** classification
3. **Assess traffic patterns** (is it a hotspot?)
4. **Add to both zones and hotspots** if applicable

Example:
```markdown
### Zones
- zone_central:
  - Existing Areas...
  - New Business District

### Hotspots
- Central business / arterials:
  - Existing Hotspots...
  - New Business District  # If it has traffic issues
```

### Configuring for Different Cities

To adapt for another city:

1. **Replace area names** with local areas
2. **Adjust peak windows** for local commute patterns
3. **Redefine zones** based on city layout
4. **Update hotspots** with known congestion areas
5. **Modify explanation templates** for local terminology

### Seasonal Adjustments

For seasonal traffic patterns, you can:

1. **Create seasonal configuration files**
2. **Update hotspots** for seasonal events
3. **Adjust peak windows** for school schedules
4. **Add event-sensitive areas** for festivals/events

## Advanced Configuration

### Custom Zone Types

Create new zone types for specific needs:

```markdown
### Zones
- zone_industrial:
  - Industrial Area 1
  - Manufacturing Hub
  
- zone_educational:
  - University Area
  - School District
  
- zone_medical:
  - Hospital Complex
  - Medical District
```

### Time-Specific Rules

While the current system uses general peak windows, you can add more specific rules in the explanation templates:

```markdown
### Explanation templates
- School hours triggered: "School pickup/drop-off time causes additional congestion."
- Event day triggered: "Special event in the area may cause delays."
- Construction zone: "Ongoing construction work may slow traffic."
```

### Multi-Language Support

Add local language explanations:

```markdown
### Explanation templates
- Peak window triggered: "Departure time falls in a typical peak window. | రష్ అవర్ సమయంలో ట్రాఫిక్ ఎక్కువగా ఉంటుంది."
```

## Troubleshooting Configuration

### Common Issues

**1. Areas Not Recognized**
- Check spelling matches exactly between zones and hotspots
- Ensure proper indentation in markdown
- Verify area is listed under a zone

**2. Scoring Not Working as Expected**
- Verify peak windows are in correct format (HH:MM–HH:MM)
- Check that hotspots are properly categorized
- Ensure zones are correctly assigned

**3. Validation Errors**
- Check all required sections are present
- Verify markdown formatting is correct
- Ensure no duplicate area names

### Debugging Tools

**Check Area Classification:**
```bash
python -c "
from app.traffic_controller import TrafficController
controller = TrafficController()
areas = ['Area1', 'Area2', 'Area3']
for area in areas:
    info = controller.get_area_info(area)
    print(f'{area}: zone={info.zone}, hotspot={info.is_hotspot}')
"
```

**Test Scoring Logic:**
```bash
python -c "
from datetime import datetime
from app.traffic_controller import TrafficController
controller = TrafficController()
times = [
    datetime(2024, 1, 1, 9, 0),   # Monday 9 AM
    datetime(2024, 1, 1, 18, 0),  # Monday 6 PM
    datetime(2024, 1, 6, 10, 0),  # Saturday 10 AM
]
for time in times:
    analysis = controller.analyze_route('TestArea1', 'TestArea2', time)
    print(f'{time}: {analysis.congestion.level.value}')
"
```

## Best Practices

1. **Keep area names consistent** across all sections
2. **Use descriptive zone classifications** that match local geography
3. **Regularly update hotspots** based on changing traffic patterns
4. **Test changes thoroughly** before deploying
5. **Document custom modifications** for future reference
6. **Backup configuration** before making major changes
7. **Use version control** to track configuration changes

## Configuration Examples

### Small City Configuration
```markdown
### Zones
- zone_downtown:
  - Main Street
  - City Center
  - Business District

- zone_residential:
  - North Side
  - South Side
  - Suburbs

### Hotspots
- Downtown core:
  - Main Street
  - City Center

### Peak windows
- Weekday morning peak: 07:30–09:30
- Weekday evening peak: 16:30–18:30
- Weekend pattern: light traffic, busy near shopping areas
```

### Large Metropolitan Configuration
```markdown
### Zones
- zone_cbd:
  - Financial District
  - Government Quarter
  - Business Center

- zone_tech_corridor:
  - Tech Park 1
  - Tech Park 2
  - Innovation District

- zone_industrial:
  - Industrial Zone A
  - Manufacturing Hub
  - Port Area

### Peak windows
- Weekday morning peak: 07:00–10:00
- Weekday evening peak: 17:00–20:00
- Weekend pattern: lighter mornings, busy evenings near entertainment districts
```

This configuration system provides flexibility to adapt the traffic guide for different cities, traffic patterns, and local conditions while maintaining the core functionality and user experience.