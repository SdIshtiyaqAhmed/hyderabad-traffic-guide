"""
Streamlit web application for Hyderabad Traffic Guide
"""
import streamlit as st
from datetime import datetime, time
from typing import Optional, Dict, Tuple
import logging
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time as time_module

from app.traffic_controller import TrafficController
from models.data_models import CongestionLevel


# Set up logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Hyderabad location coordinates (comprehensive database)
HYDERABAD_LOCATIONS = {
    # IT Corridor / West Hyderabad
    "Gachibowli": (17.4400, 78.3489),
    "Financial District": (17.4239, 78.3733),
    "Nanakramguda": (17.4183, 78.3667),
    "Hitec City": (17.4483, 78.3915),
    "Madhapur": (17.4483, 78.3915),
    "Kondapur": (17.4647, 78.3644),
    "Kukatpally": (17.4840, 78.4071),
    "Miyapur": (17.4967, 78.3583),
    "Jubilee Hills": (17.4239, 78.4089),
    "Banjara Hills": (17.4126, 78.4486),
    "Manikonda": (17.4022, 78.3378),
    "Kokapet": (17.4089, 78.3444),
    "Narsingi": (17.3956, 78.3311),
    "Raidurg": (17.4344, 78.3789),
    "Serilingampally": (17.4900, 78.3200),
    "Bachupally": (17.5167, 78.3167),
    "Nizampet": (17.5089, 78.3889),
    "Pragathi Nagar": (17.4956, 78.4089),
    "KPHB Colony": (17.4889, 78.3889),
    "Moosapet": (17.4756, 78.4156),
    
    # Central Business Areas
    "Punjagutta": (17.4239, 78.4489),
    "Ameerpet": (17.4375, 78.4482),
    "Begumpet": (17.4504, 78.4647),
    "Lakdi-ka-pul": (17.3850, 78.4867),
    "Abids": (17.3850, 78.4867),
    "Koti": (17.3753, 78.4815),
    "Somajiguda": (17.4167, 78.4667),
    "Panjagutta": (17.4239, 78.4489),
    "Raj Bhavan": (17.4167, 78.4500),
    "Khairatabad": (17.4000, 78.4667),
    "Nampally": (17.3833, 78.4833),
    "Himayatnagar": (17.4000, 78.4833),
    "Narayanguda": (17.3833, 78.5000),
    "Basheerbagh": (17.3917, 78.4750),
    "Greenlands": (17.4083, 78.4417),
    "Banjara Hills Road No 1": (17.4167, 78.4333),
    "Film Nagar": (17.4167, 78.4000),
    "Yousufguda": (17.4333, 78.4000),
    
    # Dense Core / Old City
    "Charminar": (17.3616, 78.4747),
    "Afzal Gunj": (17.3700, 78.4600),
    "Malakpet": (17.4011, 78.5267),
    "Dilsukhnagar": (17.3687, 78.5244),
    "LB Nagar": (17.3420, 78.5520),
    "Mehdipatnam": (17.3917, 78.4333),
    "Tolichowki": (17.3833, 78.4167),
    "Golconda": (17.3833, 78.4000),
    "Langar Houz": (17.3667, 78.4167),
    "Rajendranagar": (17.3167, 78.4000),
    "Attapur": (17.3667, 78.4000),
    "Shivarampally": (17.3333, 78.3833),
    "Shamshabad": (17.2500, 78.4000),
    "Hayathnagar": (17.3333, 78.5833),
    "Vanasthalipuram": (17.3167, 78.5500),
    "Uppal": (17.4000, 78.5500),
    "Boduppal": (17.4167, 78.5833),
    "Ghatkesar": (17.4500, 78.6833),
    
    # Transit Hubs & Railway Stations
    "Secunderabad": (17.5040, 78.5040),
    "MGBS": (17.3850, 78.4867),
    "Kacheguda": (17.3833, 78.5000),
    "Hyderabad Deccan": (17.3750, 78.4833),
    "Lingampally": (17.4833, 78.3167),
    "Hi-Tech City Metro": (17.4483, 78.3915),
    "Ameerpet Metro": (17.4375, 78.4482),
    "Nagole Metro": (17.3667, 78.5667),
    "Miyapur Metro": (17.4967, 78.3583),
    "LB Nagar Metro": (17.3420, 78.5520),
    
    # Educational Hubs
    "University of Hyderabad": (17.4583, 78.3250),
    "IIIT Hyderabad": (17.4456, 78.3497),
    "ISB Hyderabad": (17.4333, 78.3833),
    "Osmania University": (17.4167, 78.5333),
    "JNTU Hyderabad": (17.4833, 78.3833),
    "Central University": (17.4583, 78.3250),
    
    # Shopping & Entertainment
    "Inorbit Mall": (17.4483, 78.3915),
    "Forum Sujana Mall": (17.4400, 78.3489),
    "GVK One Mall": (17.4239, 78.4489),
    "City Centre Mall": (17.4375, 78.4482),
    "Sarath City Capital Mall": (17.4400, 78.3600),
    "Manjeera Mall": (17.4840, 78.4071),
    "Hyderabad Central": (17.4375, 78.4482),
    "Lulu Mall": (17.4400, 78.3600),
    
    # Hospitals & Healthcare
    "Apollo Hospital": (17.4167, 78.4333),
    "NIMS Hospital": (17.4333, 78.4167),
    "Care Hospital": (17.4239, 78.4089),
    "Continental Hospital": (17.4400, 78.3489),
    "Yashoda Hospital": (17.4011, 78.5267),
    "Rainbow Hospital": (17.4483, 78.3915),
    "Global Hospital": (17.4167, 78.4000),
    
    # Event-Sensitive Corridors
    "Bison Signal": (17.4400, 78.4600),
    "Karkhana": (17.4600, 78.4900),
    "Rasoolpura": (17.4700, 78.4800),
    "Paradise Circle": (17.4667, 78.4833),
    "Tarbund": (17.4833, 78.4833),
    "Bowenpally": (17.4833, 78.4667),
    "Trimulgherry": (17.5000, 78.4833),
    "Alwal": (17.5167, 78.5000),
    "Bollaram": (17.5500, 78.4833),
    
    # Outer Ring Road Areas
    "Shamirpet": (17.5500, 78.4000),
    "Kompally": (17.5333, 78.4833),
    "Medchal": (17.6167, 78.4833),
    "Keesara": (17.5333, 78.5833),
    "Ghatkesar": (17.4500, 78.6833),
    "Pocharam": (17.4167, 78.6167),
    "Ibrahimpatnam": (17.2833, 78.5833),
    "Shadnagar": (17.1000, 78.2000),
    "Chevella": (17.2833, 78.1333),
    "Vikarabad": (17.3333, 77.9000),
    
    # Airport & Surroundings
    "Rajiv Gandhi International Airport": (17.2403, 78.4294),
    "Shamshabad Airport": (17.2403, 78.4294),
    "Airport Road": (17.3000, 78.4000),
    "Aramghar": (17.3167, 78.4333),
}

# Initialize geocoder
@st.cache_resource
def get_geocoder():
    return Nominatim(user_agent="hyderabad_traffic_guide")


def create_abstract_route_map(origin: str, destination: str, analysis=None):
    """Create an abstract route visualization using Streamlit components"""
    try:
        # Get coordinates
        origin_coords = get_location_coordinates(origin)
        dest_coords = get_location_coordinates(destination)
        
        # Find intermediate locations along the route
        intermediate_locations = []
        
        # Simple logic to find locations roughly between origin and destination
        min_lat = min(origin_coords[0], dest_coords[0])
        max_lat = max(origin_coords[0], dest_coords[0])
        min_lon = min(origin_coords[1], dest_coords[1])
        max_lon = max(origin_coords[1], dest_coords[1])
        
        # Find locations within the bounding box
        for location, coords in HYDERABAD_LOCATIONS.items():
            if (location != origin and location != destination and
                min_lat <= coords[0] <= max_lat and
                min_lon <= coords[1] <= max_lon):
                # Calculate distance from the direct route line
                try:
                    distance_to_route = abs((dest_coords[1] - origin_coords[1]) * (origin_coords[0] - coords[0]) - 
                                          (origin_coords[1] - coords[1]) * (dest_coords[0] - origin_coords[0])) / \
                                       ((dest_coords[1] - origin_coords[1])**2 + (dest_coords[0] - origin_coords[0])**2)**0.5
                    
                    # Only include locations close to the route
                    if distance_to_route < 0.05:  # Roughly 5km threshold
                        intermediate_locations.append(location)
                except:
                    continue
        
        # Limit to 3-4 intermediate locations
        intermediate_locations = intermediate_locations[:4]
        
        # Display route using Streamlit components
        st.markdown("### 🗺️ Route Overview")
        
        # Create a container for the route
        with st.container():
            # Origin
            st.success(f"📍 **Start:** {origin}")
            
            # Show intermediate locations if any
            if intermediate_locations:
                st.markdown("**Route passes through:**")
                for location in intermediate_locations:
                    # Check if it's a hotspot
                    is_hotspot = location in [
                        "Gachibowli", "Financial District", "Hitec City", "Madhapur",
                        "Punjagutta", "Ameerpet", "Charminar", "Dilsukhnagar",
                        "Secunderabad", "Bison Signal", "Paradise Circle"
                    ]
                    
                    if is_hotspot:
                        st.warning(f"🔴 {location} (Traffic Hotspot)")
                    else:
                        st.info(f"📍 {location}")
            
            # Destination - color based on traffic analysis
            if analysis and analysis.congestion:
                level = analysis.congestion.level.value
                if level == "LOW":
                    st.success(f"🎯 **End:** {destination}")
                elif level == "MEDIUM":
                    st.warning(f"🎯 **End:** {destination}")
                else:  # HIGH
                    st.error(f"🎯 **End:** {destination}")
            else:
                st.info(f"🎯 **End:** {destination}")
            
            # Distance info
            distance = geodesic(origin_coords, dest_coords).kilometers
            st.markdown(f"**📏 Distance:** ~{distance:.1f} km")
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating abstract route map: {e}")
        st.error("Unable to generate route visualization")
        return False


def get_location_coordinates(location_name: str) -> Tuple[float, float]:
    """Get coordinates for a location, with fallback to geocoding"""
    # First check our predefined locations
    if location_name in HYDERABAD_LOCATIONS:
        return HYDERABAD_LOCATIONS[location_name]
    
    # Fallback to geocoding for unknown locations
    try:
        geocoder = get_geocoder()
        location = geocoder.geocode(f"{location_name}, Hyderabad, Telangana, India")
        if location:
            return (location.latitude, location.longitude)
    except Exception as e:
        logger.warning(f"Geocoding failed for {location_name}: {e}")
    
    # Default to Hyderabad center if all else fails
    return (17.3850, 78.4867)


def create_traffic_map(origin: str, destination: str, analysis=None) -> folium.Map:
    """Create an interactive map showing the route and traffic conditions"""
    try:
        # Get coordinates
        origin_coords = get_location_coordinates(origin)
        dest_coords = get_location_coordinates(destination)
        
        # Calculate center point for map
        center_lat = (origin_coords[0] + dest_coords[0]) / 2
        center_lon = (origin_coords[1] + dest_coords[1]) / 2
        
        # Create map centered on route
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=11,
            tiles='OpenStreetMap'
        )
        
        # Add origin marker
        folium.Marker(
            origin_coords,
            popup=f"📍 Origin: {origin}",
            tooltip=f"Start: {origin}",
            icon=folium.Icon(color='green', icon='play', prefix='fa')
        ).add_to(m)
        
        # Add destination marker
        folium.Marker(
            dest_coords,
            popup=f"🎯 Destination: {destination}",
            tooltip=f"End: {destination}",
            icon=folium.Icon(color='red', icon='stop', prefix='fa')
        ).add_to(m)
        
        # Add route line
        route_color = 'blue'
        if analysis and analysis.congestion:
            if analysis.congestion.level == CongestionLevel.HIGH:
                route_color = 'red'
            elif analysis.congestion.level == CongestionLevel.MEDIUM:
                route_color = 'orange'
            else:
                route_color = 'green'
        
        folium.PolyLine(
            locations=[origin_coords, dest_coords],
            color=route_color,
            weight=6,
            opacity=0.8,
            popup=f"Route: {origin} → {destination}"
        ).add_to(m)
        
        # Add traffic hotspots as markers
        hotspot_locations = [
            "Gachibowli", "Financial District", "Hitec City", "Madhapur",
            "Punjagutta", "Ameerpet", "Charminar", "Dilsukhnagar",
            "Secunderabad", "Bison Signal"
        ]
        
        for hotspot in hotspot_locations:
            if hotspot in HYDERABAD_LOCATIONS:
                coords = HYDERABAD_LOCATIONS[hotspot]
                folium.CircleMarker(
                    coords,
                    radius=8,
                    popup=f"🔴 Traffic Hotspot: {hotspot}",
                    tooltip=f"Hotspot: {hotspot}",
                    color='red',
                    fill=True,
                    fillColor='red',
                    fillOpacity=0.6
                ).add_to(m)
        
        # Add traffic analysis info box
        if analysis and analysis.congestion:
            traffic_info = f"""
            <div style="position: fixed; 
                        top: 10px; right: 10px; width: 200px; height: 120px; 
                        background-color: white; border:2px solid grey; z-index:9999; 
                        font-size:14px; padding: 10px">
                <h4>Traffic Analysis</h4>
                <p><strong>Level:</strong> {analysis.congestion.level.value}</p>
                <p><strong>Recommendation:</strong> {analysis.congestion.departure_recommendation}</p>
            </div>
            """
            m.get_root().html.add_child(folium.Element(traffic_info))
        
        return m
        
    except Exception as e:
        logger.error(f"Error creating map: {e}")
        # Return a basic Hyderabad map if there's an error
        m = folium.Map(location=[17.3850, 78.4867], zoom_start=10)
        return m


def display_route_map(origin: str, destination: str, analysis=None):
    """Display the interactive route map in Streamlit"""
    try:
        st.markdown("### 🗺️ Route Map")
        
        # Create the map
        traffic_map = create_traffic_map(origin, destination, analysis)
        
        # Display map in Streamlit
        map_data = st_folium(
            traffic_map,
            width=700,
            height=400,
            returned_objects=["last_object_clicked"]
        )
        
        # Add map legend
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("🟢 **Low Traffic** - Good to go")
        with col2:
            st.markdown("🟡 **Medium Traffic** - Plan extra time")
        with col3:
            st.markdown("🔴 **High Traffic** - Consider waiting")
        
        st.markdown("---")
        
        # Display distance information
        origin_coords = get_location_coordinates(origin)
        dest_coords = get_location_coordinates(destination)
        distance = geodesic(origin_coords, dest_coords).kilometers
        
        st.info(f"📏 **Approximate Distance:** {distance:.1f} km")
        
    except Exception as e:
        logger.error(f"Error displaying route map: {e}")
        st.error("Unable to display map. Please check your internet connection.")


def initialize_controller() -> Optional[TrafficController]:
    """Initialize traffic controller with error handling"""
    try:
        controller = TrafficController()
        
        # Check if controller initialization failed
        if controller._initialization_error:
            st.error("⚠️ Configuration Error")
            st.error(controller._initialization_error)
            
            # Provide helpful recovery suggestions
            st.info("**Recovery Suggestions:**")
            st.info("1. Check that the `.kiro/steering/product.md` file exists")
            st.info("2. Verify the configuration file format is correct")
            st.info("3. Ensure all required sections are present")
            st.info("4. Contact support if the problem persists")
            
            return None
        
        # Validate configuration if controller was initialized successfully
        if controller.config:
            validation = controller.parser.validate_config(controller.config)
            
            if not validation.is_valid:
                st.warning("⚠️ Configuration Issues Detected")
                st.warning("The system will continue with limited functionality:")
                for error in validation.errors:
                    st.warning(f"• {error}")
                
                # Still return controller for limited functionality
                return controller
            
            if validation.warnings:
                st.info("ℹ️ Configuration Warnings:")
                for warning in validation.warnings:
                    st.info(f"• {warning}")
        
        return controller
        
    except FileNotFoundError as e:
        st.error("⚠️ Configuration File Not Found")
        st.error(str(e))
        st.info("**Setup Instructions:**")
        st.info("1. Ensure the product.md configuration file exists")
        st.info("2. Check the file path and permissions")
        st.info("3. Refer to the documentation for configuration format")
        return None
        
    except Exception as e:
        logger.error(f"Unexpected error initializing controller: {e}")
        st.error("⚠️ System Initialization Error")
        st.error(f"An unexpected error occurred: {e}")
        st.info("**Troubleshooting:**")
        st.info("1. Refresh the page and try again")
        st.info("2. Check system logs for more details")
        st.info("3. Contact support if the problem persists")
        return None


def get_congestion_color(level: CongestionLevel) -> str:
    """Get color for congestion level display"""
    try:
        color_map = {
            CongestionLevel.LOW: "green",
            CongestionLevel.MEDIUM: "orange", 
            CongestionLevel.HIGH: "red"
        }
        return color_map.get(level, "gray")
    except Exception as e:
        logger.error(f"Error getting congestion color: {e}")
        return "gray"


def display_results(analysis, show_reasoning: bool = False):
    """Display traffic analysis results with enhanced visual design"""
    try:
        if not analysis:
            st.error("No analysis results to display")
            return
        
        if not analysis.congestion:
            st.error("Invalid analysis results")
            return
        
        # Create a visually appealing results container
        st.markdown("---")
        
        # Main congestion result with enhanced styling
        congestion_color = get_congestion_color(analysis.congestion.level)
        level_emoji = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}
        emoji = level_emoji.get(analysis.congestion.level.value, "⚪")
        
        # Create columns for better layout
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                color: white;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            ">
                <h2 style="margin: 0; font-size: 2.5em;">{emoji}</h2>
                <h3 style="margin: 10px 0; color: white;">Traffic Level</h3>
                <h2 style="margin: 0; color: white;">{analysis.congestion.level.value}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Departure recommendation with styling
            if analysis.congestion.departure_recommendation:
                rec_color = "#28a745" if "leave now" in analysis.congestion.departure_recommendation.lower() else "#ffc107"
                rec_icon = "🚀" if "leave now" in analysis.congestion.departure_recommendation.lower() else "⏰"
                
                st.markdown(f"""
                <div style="
                    background: {rec_color};
                    padding: 15px;
                    border-radius: 10px;
                    margin-bottom: 15px;
                    color: white;
                ">
                    <h4 style="margin: 0; color: white;">{rec_icon} Recommendation</h4>
                    <p style="margin: 5px 0 0 0; font-size: 1.1em; color: white;">{analysis.congestion.departure_recommendation}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Departure window
            if analysis.departure_window:
                st.markdown(f"""
                <div style="
                    background: #17a2b8;
                    padding: 15px;
                    border-radius: 10px;
                    margin-bottom: 15px;
                    color: white;
                ">
                    <h4 style="margin: 0; color: white;">🕐 Best Departure Window</h4>
                    <p style="margin: 5px 0 0 0; font-size: 1.1em; color: white;">{analysis.departure_window}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Brief explanation
            if analysis.congestion.reasoning:
                st.markdown(f"""
                <div style="
                    background: #6c757d;
                    padding: 15px;
                    border-radius: 10px;
                    color: white;
                ">
                    <h4 style="margin: 0; color: white;">💡 Why This Rating?</h4>
                    <p style="margin: 5px 0 0 0; color: white;">{analysis.congestion.reasoning}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Hotspot warnings with enhanced styling
        if analysis.hotspot_warnings:
            st.markdown("### ⚠️ Traffic Hotspot Warnings")
            for warning in analysis.hotspot_warnings:
                st.markdown(f"""
                <div style="
                    background: #dc3545;
                    padding: 10px 15px;
                    border-radius: 8px;
                    margin: 5px 0;
                    color: white;
                    border-left: 4px solid #721c24;
                ">
                    🚨 {warning}
                </div>
                """, unsafe_allow_html=True)
        
        # Detailed reasoning (if requested)
        if show_reasoning and analysis.detailed_reasoning:
            with st.expander("🔍 Detailed Analysis", expanded=False):
                st.markdown(analysis.detailed_reasoning)
            
    except Exception as e:
        logger.error(f"Error displaying results: {e}")
        st.error("⚠️ Error displaying results")
        st.error(f"Unable to display analysis results: {e}")


def validate_user_input(origin: str, destination: str, departure_time: datetime) -> tuple[bool, str]:
    """Validate user input with helpful error messages"""
    try:
        # Check origin
        if not origin or not origin.strip():
            return False, "Please enter a valid origin location"
        
        # Check destination
        if not destination or not destination.strip():
            return False, "Please enter a valid destination location"
        
        # Check if origin and destination are the same
        if origin.strip().lower() == destination.strip().lower():
            return False, "Origin and destination cannot be the same"
        
        # Check departure time
        if not departure_time:
            return False, "Please select a valid departure time"
        
        # Check if departure time is too far in the past
        now = datetime.now()
        if departure_time < now.replace(hour=0, minute=0, second=0, microsecond=0):
            return False, "Departure time cannot be in the past"
        
        return True, ""
        
    except Exception as e:
        logger.error(f"Error validating user input: {e}")
        return False, f"Input validation error: {e}"


def handle_analysis_error(error_message: str):
    """Handle and display analysis errors with recovery suggestions"""
    st.error("⚠️ Analysis Error")
    st.error(error_message)
    
    st.info("**What you can try:**")
    st.info("1. Check that your location names are spelled correctly")
    st.info("2. Try using nearby landmarks or major areas")
    st.info("3. Refresh the page and try again")
    st.info("4. Contact support if the problem persists")


def display_available_locations(controller: TrafficController):
    """Display all available locations organized by zones with enhanced styling"""
    if not controller.config or not controller.config.zones:
        st.info("Location data is loading...")
        return
    
    st.markdown("### 📍 Available Locations")
    st.markdown("Choose from these Hyderabad areas for accurate traffic analysis:")
    
    # Create tabs for different zones
    zone_names = list(controller.config.zones.keys())
    zone_display_names = {
        "zone_it_corridor": "🏢 IT Corridor",
        "zone_central": "🏛️ Central Areas", 
        "zone_dense_core": "🏘️ Dense Core",
        "zone_transit_hub": "🚉 Transit Hubs",
        "zone_event_sensitive": "⚠️ Event-Sensitive"
    }
    
    tabs = st.tabs([zone_display_names.get(zone, zone) for zone in zone_names])
    
    for i, zone in enumerate(zone_names):
        with tabs[i]:
            areas = controller.config.zones[zone]
            
            # Create a grid layout for areas
            cols = st.columns(3)
            for idx, area in enumerate(areas):
                with cols[idx % 3]:
                    hotspot_indicator = "🔴" if area in controller.config.hotspots else "🟢"
                    hotspot_text = "Traffic Hotspot" if area in controller.config.hotspots else "Normal Traffic"
                    
                    st.markdown(f"""
                    <div style="
                        background: {'#ffe6e6' if area in controller.config.hotspots else '#e6ffe6'};
                        padding: 10px;
                        border-radius: 8px;
                        margin: 5px 0;
                        border-left: 4px solid {'#dc3545' if area in controller.config.hotspots else '#28a745'};
                        text-align: center;
                    ">
                        <div style="font-size: 1.2em;">{hotspot_indicator}</div>
                        <div style="font-weight: bold; margin: 5px 0;">{area}</div>
                        <div style="font-size: 0.8em; color: #666;">{hotspot_text}</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    st.markdown("---")


def display_unknown_area_help(area_name: str):
    """Display help for unknown areas"""
    st.warning(f"⚠️ Unknown Area: {area_name}")
    st.info("This area is not in our local dataset yet.")
    
    st.info("**Suggestions:**")
    st.info("1. Try using a nearby major landmark")
    st.info("2. Use the closest known area or neighborhood")
    st.info("3. Contact us to add this area to our database")

def handle_nightlife_request():
    """Handle nightlife suggestion requests with polite decline"""
    st.info("🏠 This guide focuses on commute efficiency and family-friendly stops. For nightlife suggestions, please consult other local guides.")


def handle_unknown_area(area_name: str):
    """Handle unknown area addition prompts"""
    st.warning(f"⚠️ Area '{area_name}' is not in the local dataset yet.")
    
    with st.expander("Add this area to the dataset", expanded=False):
        st.markdown("To add this area, please provide the following information:")
        
        col1, col2 = st.columns(2)
        with col1:
            area_name_input = st.text_input("Area name", value=area_name, key=f"area_{area_name}")
            zone_tag = st.selectbox(
                "Zone classification",
                ["zone_it_corridor", "zone_central", "zone_dense_core", "zone_transit_hub", "zone_event_sensitive"],
                key=f"zone_{area_name}"
            )
        
        with col2:
            nearby_landmark = st.text_input("Nearby landmark", key=f"landmark_{area_name}")
            is_hotspot = st.checkbox("Is this a traffic hotspot?", key=f"hotspot_{area_name}")
        
        if st.button(f"Submit area information for {area_name}", key=f"submit_{area_name}"):
            st.success(f"Area information submitted! Please add '{area_name}' to the product.md configuration file.")


def main():
    """Main Streamlit application with clean, minimal design"""
    st.set_page_config(
        page_title="Hyderabad Traffic Guide",
        page_icon="🚗",
        layout="wide"
    )
    
    # Clean, minimal CSS
    st.markdown("""
    <style>
    .main {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    .header {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
    }
    
    .stButton > button {
        background: #2563eb;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
    }
    
    .traffic-result {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        text-align: center;
        font-weight: bold;
        border: 2px solid;
    }
    
    .traffic-low { 
        background: #dcfce7 !important; 
        color: #166534 !important; 
        border-color: #22c55e !important;
    }
    .traffic-medium { 
        background: #fed7aa !important; 
        color: #9a3412 !important; 
        border-color: #f97316 !important;
    }
    .traffic-high { 
        background: #fecaca !important; 
        color: #991b1b !important; 
        border-color: #ef4444 !important;
    }
    
    .disclaimer {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 2rem;
        font-size: 0.9rem;
        color: #64748b;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Simple header
    st.markdown("""
    <div class="header">
        <h1>🚗 Hyderabad Traffic Guide</h1>
        <p>Quick traffic suggestions for your commute</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Simple disclaimer at the top
    st.markdown("""
    <div class="disclaimer">
        <strong>Note:</strong> This tool provides traffic suggestions based on general patterns. 
        Actual conditions may vary. For official updates, check local traffic authorities.
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize controller
    controller = initialize_controller()
    if not controller:
        st.stop()
    
    # Simple sidebar
    with st.sidebar:
        st.markdown("### Peak Hours")
        st.info("**Morning:** 8-11 AM\n\n**Evening:** 5-8 PM")
    
    # Get locations
    all_locations = []
    if controller.config and controller.config.zones:
        for zone_areas in controller.config.zones.values():
            all_locations.extend(zone_areas)
    all_locations = sorted(set(all_locations))
    
    # Simple input form
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**From**")
        origin = st.selectbox(
            "Origin",
            options=["Select location..."] + all_locations,
            label_visibility="collapsed"
        )
        if origin == "Select location...":
            origin = ""
    
    with col2:
        st.markdown("**To**")
        destination = st.selectbox(
            "Destination",
            options=["Select location..."] + all_locations,
            label_visibility="collapsed"
        )
        if destination == "Select location...":
            destination = ""
    
    # Time input with session state to prevent reset
    col1, col2 = st.columns(2)
    with col1:
        departure_date = st.date_input("Date", value=datetime.now().date())
    with col2:
        # Initialize time in session state if not exists
        if 'departure_time' not in st.session_state:
            st.session_state.departure_time = datetime.now().time()
        
        departure_time = st.time_input(
            "Time", 
            value=st.session_state.departure_time,
            key="time_input"
        )
        
        # Update session state when time changes
        st.session_state.departure_time = departure_time
    
    departure_datetime = datetime.combine(departure_date, departure_time)
    
    # Analysis button
    if st.button("Get Traffic Suggestion", type="primary", use_container_width=True):
        if not origin or not destination:
            st.error("Please select both origin and destination")
        elif origin == destination:
            st.error("Origin and destination cannot be the same")
        else:
            with st.spinner("Analyzing..."):
                try:
                    # Get analysis (family-friendly by default)
                    analysis = controller.analyze_route_with_preferences(
                        origin=origin,
                        destination=destination,
                        departure_time=departure_datetime,
                        avoid_nightlife=True,
                        prefer_family_friendly=True
                    )
                    
                    if analysis and analysis.congestion:
                        # Show abstract route map first
                        st.markdown("---")
                        create_abstract_route_map(origin, destination, analysis)
                        
                        # Simple traffic result
                        level = analysis.congestion.level.value
                        
                        # Fix case sensitivity issue
                        level_upper = level.upper()
                        
                        if level_upper == "LOW":
                            css_class = "traffic-low"
                            emoji = "🟢"
                        elif level_upper == "MEDIUM":
                            css_class = "traffic-medium"
                            emoji = "🟡"
                        else:  # HIGH or any other value
                            css_class = "traffic-high"
                            emoji = "🔴"
                        
                        st.markdown(f"""
                        <div class="traffic-result {css_class}">
                            <h3>{emoji} {level} TRAFFIC</h3>
                            <p>{analysis.congestion.departure_recommendation}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Simple reasoning
                        if analysis.congestion.reasoning:
                            st.markdown(f"**Why:** {analysis.congestion.reasoning}")
                        
                        # Hotspot warnings (if any)
                        if analysis.hotspot_warnings:
                            st.warning("⚠️ " + " • ".join(analysis.hotspot_warnings))
                    
                    else:
                        st.error("Unable to analyze route")
                        
                except Exception as e:
                    st.error("Analysis failed. Please try again.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Critical error in main application: {e}")
        st.error("⚠️ Critical Application Error")
        st.error(f"The application encountered a critical error: {e}")
        st.info("Please refresh the page and try again. Contact support if the problem persists.")