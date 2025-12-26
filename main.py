"""
Main entry point for Hyderabad Traffic Guide
"""
from datetime import datetime
from app.traffic_controller import TrafficController

def main():
    """Main application entry point"""
    print("Hyderabad Traffic Guide")
    print("======================")
    
    # Initialize traffic controller
    try:
        controller = TrafficController()
        validation = controller.parser.validate_config(controller.config)
        
        if validation.is_valid:
            print("✓ Configuration loaded and validated successfully")
            print(f"✓ Found {len(controller.config.zones)} zones and {len(controller.config.hotspots)} hotspots")
        else:
            print("✗ Configuration validation failed:")
            for error in validation.errors:
                print(f"  - {error}")
            return
            
    except Exception as e:
        print(f"✗ Failed to initialize traffic controller: {e}")
        return
    
    print("✓ Traffic controller initialized successfully")
    
    # Demo traffic analysis functionality
    print("\nDemo Traffic Analysis:")
    print("---------------------")
    
    # Morning peak IT corridor
    morning_peak = datetime(2024, 1, 1, 9, 0)  # Monday 9 AM
    analysis = controller.analyze_route('Gachibowli', 'Ameerpet', morning_peak)
    print(f"Route: Gachibowli → Ameerpet at {morning_peak.strftime('%A %I:%M %p')}")
    print(f"  Congestion: {analysis.congestion.level.value}")
    print(f"  Recommendation: {analysis.congestion.departure_recommendation}")
    print(f"  Reasoning: {analysis.congestion.reasoning}")
    print(f"  Departure Window: {analysis.departure_window}")
    if analysis.hotspot_warnings:
        print(f"  Warnings: {', '.join(analysis.hotspot_warnings)}")
    print()
    
    # Weekend travel
    weekend = datetime(2024, 1, 6, 10, 0)  # Saturday 10 AM
    analysis2 = controller.analyze_route('Jubilee Hills', 'Secunderabad', weekend)
    print(f"Route: Jubilee Hills → Secunderabad at {weekend.strftime('%A %I:%M %p')}")
    print(f"  Congestion: {analysis2.congestion.level.value}")
    print(f"  Recommendation: {analysis2.congestion.departure_recommendation}")
    print(f"  Reasoning: {analysis2.congestion.reasoning}")
    print(f"  Departure Window: {analysis2.departure_window}")
    if analysis2.hotspot_warnings:
        print(f"  Warnings: {', '.join(analysis2.hotspot_warnings)}")
    print()
    
    # Unknown area handling
    analysis3 = controller.analyze_route('UnknownPlace', 'Gachibowli', morning_peak)
    print(f"Route: UnknownPlace → Gachibowli at {morning_peak.strftime('%A %I:%M %p')}")
    print(f"  Response: {analysis3.congestion.reasoning}")
    print()
    
    print("✓ Traffic controller working correctly!")
    print("Ready to implement remaining components...")

if __name__ == "__main__":
    main()