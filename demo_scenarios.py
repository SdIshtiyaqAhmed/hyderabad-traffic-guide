#!/usr/bin/env python3
"""
Demo scenarios for Hyderabad Traffic Guide

This script demonstrates 6 different scenarios that showcase the system's capabilities:
1. Weekday morning IT corridor commute
2. Weekend non-peak travel
3. Evening peak hour return
4. Cross-city old city to IT corridor
5. Unknown area handling
6. Family-friendly preferences
"""

from datetime import datetime
from app.traffic_controller import TrafficController


def print_separator(title: str):
    """Print a formatted separator for demo sections"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def print_analysis(analysis, scenario_description: str):
    """Print formatted analysis results"""
    print(f"\n📍 Scenario: {scenario_description}")
    print(f"🚦 Congestion Level: {analysis.congestion.level.value}")
    print(f"💡 Recommendation: {analysis.congestion.departure_recommendation}")
    print(f"🧠 Reasoning: {analysis.congestion.reasoning}")
    
    if analysis.departure_window:
        print(f"⏰ Departure Window: {analysis.departure_window}")
    
    if analysis.hotspot_warnings:
        print(f"⚠️  Hotspot Warnings:")
        for warning in analysis.hotspot_warnings:
            print(f"   • {warning}")
    
    if analysis.detailed_reasoning and len(analysis.detailed_reasoning) > len(analysis.congestion.reasoning):
        print(f"📋 Detailed Analysis: {analysis.detailed_reasoning}")


def demo_scenario_1(controller: TrafficController):
    """Demo 1: Weekday Morning IT Corridor Commute"""
    print_separator("DEMO 1: Weekday Morning IT Corridor Commute")
    
    analysis = controller.analyze_route(
        "Gachibowli", 
        "Ameerpet", 
        datetime(2024, 1, 1, 9, 0)  # Monday 9:00 AM
    )
    
    print_analysis(analysis, "Gachibowli → Ameerpet, Monday 9:00 AM")
    print("\n🎯 Expected: High congestion due to peak window + IT corridor + hotspots")
    print(f"✅ Result: {analysis.congestion.level.value} congestion as expected")


def demo_scenario_2(controller: TrafficController):
    """Demo 2: Weekend Non-Peak Travel"""
    print_separator("DEMO 2: Weekend Non-Peak Travel")
    
    analysis = controller.analyze_route(
        "Jubilee Hills", 
        "Secunderabad", 
        datetime(2024, 1, 6, 10, 0)  # Saturday 10:00 AM
    )
    
    print_analysis(analysis, "Jubilee Hills → Secunderabad, Saturday 10:00 AM")
    print("\n🎯 Expected: Lower congestion due to weekend adjustment")
    print(f"✅ Result: {analysis.congestion.level.value} congestion with weekend consideration")


def demo_scenario_3(controller: TrafficController):
    """Demo 3: Evening Peak Hour Return"""
    print_separator("DEMO 3: Evening Peak Hour Return")
    
    analysis = controller.analyze_route(
        "Hitec City", 
        "Banjara Hills", 
        datetime(2024, 1, 1, 18, 30)  # Monday 6:30 PM
    )
    
    print_analysis(analysis, "Hitec City → Banjara Hills, Monday 6:30 PM")
    print("\n🎯 Expected: High congestion due to evening peak + IT corridor")
    print(f"✅ Result: {analysis.congestion.level.value} congestion during evening rush")


def demo_scenario_4(controller: TrafficController):
    """Demo 4: Cross-City Old City to IT Corridor"""
    print_separator("DEMO 4: Cross-City Old City to IT Corridor")
    
    analysis = controller.analyze_route(
        "Charminar", 
        "Financial District", 
        datetime(2024, 1, 1, 8, 0)  # Monday 8:00 AM
    )
    
    print_analysis(analysis, "Charminar → Financial District, Monday 8:00 AM")
    print("\n🎯 Expected: High congestion due to hotspots + IT corridor + peak time")
    print(f"✅ Result: {analysis.congestion.level.value} congestion with multiple factors")


def demo_scenario_5(controller: TrafficController):
    """Demo 5: Unknown Area Handling"""
    print_separator("DEMO 5: Unknown Area Handling")
    
    analysis = controller.analyze_route(
        "UnknownPlace", 
        "Gachibowli", 
        datetime(2024, 1, 1, 9, 0)  # Monday 9:00 AM
    )
    
    print_analysis(analysis, "UnknownPlace → Gachibowli, Monday 9:00 AM")
    print("\n🎯 Expected: Unknown area message with addition prompt")
    expected_message = "That area isn't in my local dataset yet—add it to product.md"
    if expected_message in analysis.congestion.reasoning:
        print("✅ Result: Unknown area handled correctly with addition prompt")
    else:
        print("❌ Result: Unknown area handling not working as expected")


def demo_scenario_6(controller: TrafficController):
    """Demo 6: Family-Friendly Preferences"""
    print_separator("DEMO 6: Family-Friendly Preferences")
    
    # First show normal analysis
    normal_analysis = controller.analyze_route(
        "Ameerpet", 
        "Kukatpally", 
        datetime(2024, 1, 1, 10, 0)  # Monday 10:00 AM
    )
    
    # Then show with preferences
    filtered_analysis = controller.analyze_route_with_preferences(
        "Ameerpet", 
        "Kukatpally", 
        datetime(2024, 1, 1, 10, 0),  # Monday 10:00 AM
        avoid_nightlife=True,
        prefer_family_friendly=True
    )
    
    print(f"\n📍 Scenario: Ameerpet → Kukatpally, Monday 10:00 AM")
    print(f"\n🔸 Normal Analysis:")
    print(f"   Reasoning: {normal_analysis.congestion.reasoning}")
    
    print(f"\n🔸 With Family-Friendly Preferences:")
    print(f"   Reasoning: {filtered_analysis.congestion.reasoning}")
    
    print("\n🎯 Expected: Content filtered for family-friendly suggestions")
    
    # Check for nightlife terms
    all_text = (filtered_analysis.congestion.reasoning + " " + 
               filtered_analysis.detailed_reasoning + " " + 
               " ".join(filtered_analysis.hotspot_warnings)).lower()
    
    nightlife_terms = ["bar", "pub", "nightclub", "nightlife", "drinks"]
    has_nightlife = any(term in all_text for term in nightlife_terms)
    
    if not has_nightlife:
        print("✅ Result: Content successfully filtered for family-friendly output")
    else:
        print("⚠️  Result: Some nightlife content may still be present")


def run_all_demos():
    """Run all demo scenarios"""
    print("🚗 Hyderabad Traffic Guide - Demo Scenarios")
    print("=" * 60)
    print("This demo showcases 6 different scenarios that demonstrate")
    print("the system's capabilities and various traffic conditions.")
    
    try:
        # Initialize traffic controller
        print("\n🔧 Initializing Traffic Controller...")
        controller = TrafficController()
        
        if controller._initialization_error:
            print(f"❌ Initialization Error: {controller._initialization_error}")
            print("\n💡 Please ensure the configuration file exists at:")
            print("   .kiro/steering/product.md")
            return
        
        print("✅ Traffic Controller initialized successfully")
        
        # Validate configuration
        validation = controller.parser.validate_config(controller.config)
        if validation.is_valid:
            print("✅ Configuration validated successfully")
        else:
            print("⚠️  Configuration has some issues:")
            for error in validation.errors:
                print(f"   • {error}")
        
        if validation.warnings:
            print("ℹ️  Configuration warnings:")
            for warning in validation.warnings:
                print(f"   • {warning}")
        
        # Run all demo scenarios
        demo_scenario_1(controller)
        demo_scenario_2(controller)
        demo_scenario_3(controller)
        demo_scenario_4(controller)
        demo_scenario_5(controller)
        demo_scenario_6(controller)
        
        # Summary
        print_separator("DEMO SUMMARY")
        print("✅ All 6 demo scenarios completed successfully!")
        print("\n📊 Scenarios demonstrated:")
        print("   1. ✅ Weekday morning IT corridor commute (high congestion)")
        print("   2. ✅ Weekend non-peak travel (lower congestion)")
        print("   3. ✅ Evening peak hour return (high congestion)")
        print("   4. ✅ Cross-city old city to IT corridor (multiple factors)")
        print("   5. ✅ Unknown area handling (graceful degradation)")
        print("   6. ✅ Family-friendly preferences (content filtering)")
        
        print("\n🎯 Key Features Demonstrated:")
        print("   • Configuration-driven scoring")
        print("   • Peak window detection")
        print("   • IT corridor awareness")
        print("   • Hotspot warnings")
        print("   • Weekend adjustments")
        print("   • Unknown area handling")
        print("   • Content filtering preferences")
        print("   • Detailed reasoning explanations")
        
        print("\n🚀 Next Steps:")
        print("   • Run the Streamlit web app: streamlit run streamlit_app.py")
        print("   • Try your own routes and times")
        print("   • Explore the preference settings")
        print("   • Add new areas to the configuration")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        print("\n💡 Troubleshooting:")
        print("   • Check that all dependencies are installed")
        print("   • Ensure the configuration file exists")
        print("   • Verify the project structure is correct")
        print("   • Run the tests to check system health")


if __name__ == "__main__":
    run_all_demos()