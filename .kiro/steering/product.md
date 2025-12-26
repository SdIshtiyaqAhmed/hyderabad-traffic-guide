---
inclusion: always
---
# Product Overview: Hyderabad Traffic Guide

## Purpose
Hyderabad Traffic Guide is a local commute helper that suggests better departure windows and flags common congestion hotspots using Hyderabad-specific patterns and rules captured in this file.
It provides quick, practical guidance for everyday trips (work, errands, airport/rail, short city hops) without requiring users to understand complex traffic analytics.

## Target Users
- Daily office commuters traveling to/from western Hyderabad (IT corridor) and central hubs
- Students and parents planning school/college drop-offs and pickups
- Delivery riders and frequent intra-city travelers who need “best time to leave” guidance

## Key Features
- Congestion score (Low/Medium/High) computed from local heuristics in this file
- “Leave now vs wait” recommendation with a suggested departure window
- Hotspot warnings near known junctions/corridors and recurring bottleneck patterns
- Optional “Latest alerts” section (manual/demo feed, or sourced from official advisories)

## Content Rules
- Never suggest pubs/bars/nightlife as stop recommendations.
- When proposing breaks, prefer neutral “quiet/family-friendly” options.
- If user asks for nightlife suggestions, respond politely that the guide focuses on commute efficiency and family-friendly stops.

## Local Rules (Hyderabad)

### City mental model
Western Hyderabad (Cyberabad/IT corridor) experiences pronounced office commute waves and recurring bottlenecks due to the concentration of IT hubs.
Treat this corridor as a special zone where the same clock time can vary significantly in travel time compared to non-IT corridors.

### Peak windows
These windows are defaults for heuristic scoring and should be treated as “likely congestion” periods on weekdays.
- Weekday morning peak: 08:00–11:00 (highest probability if origin or destination is in/near the IT corridor)
- Weekday evening peak: 17:00–20:00 (often extends later on busy corridors; treat 18:00–19:00 as the heaviest band)
- Weekend pattern: lighter mornings; evenings can still be busy around major malls/markets and event corridors (use hotspot proximity to decide)

### Hotspots (starter list)
Use this list to add “hotspot penalty” to congestion scoring when the route starts/ends near these areas or when the user selects them explicitly.

- IT corridor / west:
  - Gachibowli
  - Financial District
  - Nanakramguda
  - Hitec City
  - Madhapur
  - Kondapur
  - Kukatpally
  - Miyapur
  - Jubilee Hills
  - Banjara Hills

- Central business / arterials:
  - Punjagutta
  - Ameerpet
  - Begumpet
  - Lakdi-ka-pul
  - Abids

- Old city / dense cores (often slower roads and frequent bottlenecks):
  - Charminar
  - Afzal Gunj
  - Malakpet
  - Dilsukhnagar
  - LB Nagar

- Transit hubs / long-trip connectors:
  - Secunderabad
  - MGBS
  - Koti

- Event-sensitive corridors (diversions/restrictions can spike delays):
  - Bison Signal
  - Karkhana
  - Rasoolpura / CTO-side corridors

### Scoring logic (heuristics)
The app should compute a congestion score using only the rules below unless a separate “alerts feed” overrides it.

Use the following approach:
- Base score:
  - Start at Low
  - If time falls in weekday morning peak or evening peak → raise by one level
  - If time falls in 18:00–19:00 band → raise by an additional level (cap at High)
- Corridor multiplier:
  - If either endpoint is in the IT corridor list and time overlaps a weekday peak window → raise by one additional level (cap at High)
- Hotspot penalty:
  - If origin or destination matches a hotspot → raise by one level during peak windows (cap at High)
- Weekend handling:
  - If weekend and not near hotspots → reduce by one level (floor at Low)

### Explanation templates
Use these templates to generate “Show reasoning” output:
- Peak window triggered: “Departure time falls in a typical peak window.”
- IT corridor triggered: “One endpoint is in the west/IT corridor, which usually amplifies peak-hour congestion.”
- Hotspot triggered: “This route touches a known slow zone, so delays are more likely.”
- Weekend adjustment: “Weekend traffic is often smoother unless you’re near busy hotspots.”

### Output rules (what the assistant/app must say)
- Always return:
  - Congestion level (Low/Medium/High)
  - A recommended departure suggestion: “leave now” or “wait until <window>”
  - A short explanation referencing which rule triggered (peak window, IT corridor, hotspot)
- If the user asks for a corridor/area not listed here:
  - Respond: “That area isn’t in my local dataset yet—add it to product.md”
  - Ask for: area name, zone tag, nearby landmark, hotspot yes/no

## Local Dataset (editable)

### Zones
Use these tags in the app for quick classification.
- zone_it_corridor:
  - Gachibowli
  - Financial District
  - Nanakramguda
  - Hitec City
  - Madhapur
  - Kondapur
  - Kukatpally
  - Miyapur
  - Jubilee Hills
  - Banjara Hills
- zone_central:
  - Punjagutta
  - Ameerpet
  - Begumpet
  - Lakdi-ka-pul
  - Abids
  - Koti
- zone_dense_core:
  - Charminar
  - Afzal Gunj
  - Malakpet
  - Dilsukhnagar
  - LB Nagar
- zone_transit_hub:
  - Secunderabad
  - MGBS
- zone_event_sensitive:
  - Bison Signal
  - Karkhana
  - Rasoolpura / CTO

### Route templates (optional, for explanations)
- If traveling to/from zone_it_corridor during weekday peak, expect slower movement; suggest leaving before 08:00 or after 11:00 in the morning, and before 17:00 or after 20:00 in the evening when feasible.
- If an advisory mentions diversions/avoid-junction windows, show it in “Latest alerts” and recommend detours away from named junction chains.

## Alerts Feed (demo schema)
If the prototype includes a manual JSON/YAML alerts file, it should follow this schema and be displayed separately from heuristic predictions.
- id: string
- title: string
- start_time: ISO string
- end_time: ISO string
- affected_areas: [string]
- advisory_text: string
- suggested_detours: [string]
- source_label: string (e.g., “Traffic advisory PDF”)

## Non-goals
- This tool does not guarantee exact ETA; it provides practical guidance based on local heuristics and optional advisories.
- This tool should not present itself as official enforcement guidance unless an alert is explicitly sourced from an official advisory.