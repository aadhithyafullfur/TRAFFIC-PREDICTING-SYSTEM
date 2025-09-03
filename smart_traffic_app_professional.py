"""
Smart Traffic Predictor & Route Advisor
A professional traffic management system for Bangalore city

Author: Smart Traffic Team
Version: 2.0
"""

import streamlit as st
import pandas as pd
import joblib
import openrouteservice
import folium
from streamlit_folium import folium_static
from config import ORS_API_KEY
from openrouteservice.exceptions import ApiError
import logging
import time
from datetime import datetime
import plotly.graph_objects as go

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Smart Traffic Management System",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #2a5298;
    }
    .route-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and cache data for better performance"""
    try:
        traffic_data = pd.read_csv("bangalore_traffic.csv")
        logger.info(f"Loaded traffic data with {len(traffic_data)} records")
        return traffic_data
    except Exception as e:
        logger.error(f"Error loading traffic data: {e}")
        st.error("Failed to load traffic data. Please check if the file exists.")
        return None

@st.cache_resource
def load_model():
    """Load and cache ML model"""
    try:
        model = joblib.load("traffic_classifier.pkl")
        logger.info("ML model loaded successfully")
        return model
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        st.error("Failed to load ML model. Please check if the file exists.")
        return None

@st.cache_data
def get_location_coordinates():
    """Return comprehensive location coordinates for Bangalore"""
    return {
        "Brigade Road": (12.9754, 77.6045),
        "Commercial Street": (12.9771, 77.6105),
        "MG Road": (12.9765, 77.6045),
        "Church Street": (12.9723, 77.6118),
        "Electronic City": (12.8452, 77.6604),
        "Whitefield": (12.9698, 77.7499),
        "Koramangala": (12.9345, 77.6232),
        "BTM Layout": (12.9162, 77.6101),
        "Indiranagar": (12.9784, 77.6392),
        "Marathahalli": (12.9592, 77.6974),
        "Hebbal": (13.0358, 77.5970),
        "Silk Board": (12.9172, 77.6237),
        "Bannerghatta Road": (12.8913, 77.5979),
        "Hosur Road": (12.9169, 77.6298),
        "Outer Ring Road": (12.9345, 77.6891),
        "Sarjapura Road": (12.9012, 77.6891),
        "Mysore Road": (12.9563, 77.5132),
        "Tumkur Road": (13.0287, 77.5619),
        "Bellary Road": (13.0068, 77.5893),
        "Old Airport Road": (12.9587, 77.6784),
        "Double Road": (12.9632, 77.5841),
        "Richmond Road": (12.9612, 77.6012),
        "Residency Road": (12.9712, 77.6012),
        "Cunningham Road": (12.9789, 77.6022),
        "Lavelle Road": (12.9709, 77.6012),
        "Infantry Road": (12.9812, 77.5998),
        "Race Course Road": (12.9843, 77.5987),
        "Palace Road": (12.9987, 77.5921),
        "Majestic": (12.9763, 77.5715),
        "City Railway Station": (12.9763, 77.5715)
    }

def get_vehicle_count(location, hour, weather, traffic_data):
    """Calculate estimated vehicle count based on historical data"""
    try:
        filter_conditions = [
            (traffic_data["LOCATION"] == location) &
            (pd.to_datetime(traffic_data["TIME"], format="%H:%M").dt.hour == hour) &
            (traffic_data["WEATHER"] == weather),
            
            (traffic_data["LOCATION"] == location) &
            (pd.to_datetime(traffic_data["TIME"], format="%H:%M").dt.hour == hour),
            
            (traffic_data["LOCATION"] == location)
        ]

        vehicle_count = 75  # Default fallback value

        for condition in filter_conditions:
            filtered = traffic_data[condition]
            if not filtered.empty:
                vehicle_count = int(filtered["VEHICLE_COUNT"].mean())
                break
                
        return vehicle_count
    except Exception as e:
        logger.error(f"Error calculating vehicle count: {e}")
        return 75

def predict_traffic(model, location, hour, weather, vehicle_count):
    """Predict traffic conditions using ML model"""
    try:
        input_data = pd.DataFrame(columns=model.feature_names_in_)
        input_data.loc[0] = 0
        input_data.at[0, "HOUR"] = hour
        input_data.at[0, "VEHICLE_COUNT"] = vehicle_count

        weather_col = f"WEATHER_{weather}"
        location_col = f"LOCATION_{location}"
        
        if weather_col in input_data.columns:
            input_data.at[0, weather_col] = 1
        if location_col in input_data.columns:
            input_data.at[0, location_col] = 1

        prediction = model.predict(input_data)[0]
        confidence = model.predict_proba(input_data)[0].max()
        
        return prediction, confidence
    except Exception as e:
        logger.error(f"Error predicting traffic: {e}")
        return 1, 0.5

def create_route_map(from_location, to_location, coords_map):
    """Create interactive route map with multiple route options"""
    try:
        client = openrouteservice.Client(key=ORS_API_KEY)
        from_coords = coords_map[from_location][::-1]
        to_coords = coords_map[to_location][::-1]

        route = client.directions(
            coordinates=[from_coords, to_coords],
            profile='driving-car',
            format='geojson',
            validate=True,
            alternative_routes={"share_factor": 0.5, "target_count": 3},
        )

        midpoint = [
            (coords_map[from_location][0] + coords_map[to_location][0])/2,
            (coords_map[from_location][1] + coords_map[to_location][1])/2
        ]
        
        m = folium.Map(location=midpoint, zoom_start=13, tiles='OpenStreetMap')
        colors = ['blue', 'green', 'purple']
        route_details = []
        
        for i, feature in enumerate(route['features']):
            summary = feature['properties']['summary']
            route_details.append({
                "number": i+1,
                "distance": summary['distance']/1000,
                "duration": summary['duration']/60,
                "color": colors[i % len(colors)]
            })

        best_route = min(route_details, key=lambda x: x['duration'])
        best_route['color'] = 'orange'

        for i, feature in enumerate(route['features']):
            current_color = route_details[i]['color']
            folium.GeoJson(
                feature,
                name=f"Route {i+1}",
                style_function=lambda x, color=current_color: {
                    'color': color,
                    'weight': 4,
                    'opacity': 0.8
                }
            ).add_to(m)

        folium.Marker(
            location=coords_map[from_location],
            popup=f"🚀 Start: {from_location}",
            icon=folium.Icon(color="green", icon="play")
        ).add_to(m)

        folium.Marker(
            location=coords_map[to_location],
            popup=f"🎯 Destination: {to_location}",
            icon=folium.Icon(color="red", icon="stop")
        ).add_to(m)

        return m, route_details, best_route

    except ApiError as e:
        logger.error(f"API Error creating route map: {e}")
        return None, [], {}
    except Exception as e:
        logger.error(f"Error creating route map: {e}")
        return None, [], {}

# Initialize data
traffic_data = load_data()
model = load_model()

if traffic_data is None or model is None:
    st.stop()

# Main header
st.markdown("""
<div class="main-header">
    <h1>🚦 Smart Traffic Management System</h1>
    <p>Intelligent Traffic Prediction & Route Optimization for Bangalore</p>
</div>
""", unsafe_allow_html=True)

# Extract location list from model features
location_list = sorted({col.split("LOCATION_")[-1] for col in model.feature_names_in_ if col.startswith("LOCATION_")})
weather_options = ["Clear", "Rainy", "Cloudy", "Foggy"]

# Sidebar for input controls
with st.sidebar:
    st.header("🎛️ Trip Configuration")
    
    st.subheader("📍 Route Selection")
    from_location = st.selectbox("From Location", location_list, help="Select your starting point")
    to_location = st.selectbox("To Location", location_list, help="Select your destination")
    
    if from_location == to_location:
        st.warning("⚠️ Please select different locations for route planning")
    
    st.subheader("🌤️ Conditions")
    weather = st.selectbox("Weather Condition", weather_options, help="Current weather conditions")
    hour = st.slider("Time of Day", 0, 23, 9, format="%d:00", help="Hour of the day (24-hour format)")
    
    current_time = datetime.now()
    st.info(f"🕐 Current time: {current_time.strftime('%H:%M')}")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📊 Traffic Analysis")
    
    vehicle_count = get_vehicle_count(to_location, hour, weather, traffic_data)
    prediction, confidence = predict_traffic(model, to_location, hour, weather, vehicle_count)
    
    traffic_status = "Low Traffic" if prediction == 0 else "High Traffic"
    status_color = "🟢" if prediction == 0 else "🔴"
    
    st.markdown(f"### {status_color} Predicted Traffic: **{traffic_status}**")
    
    col1a, col1b, col1c = st.columns(3)
    
    with col1a:
        st.metric("🚗 Vehicle Count", f"{vehicle_count:,}", help="Estimated vehicles at destination")
    
    with col1b:
        st.metric("🎯 Confidence", f"{confidence:.1%}", help="Model prediction confidence")
    
    with col1c:
        st.metric("⏰ Time", f"{hour:02d}:00", help="Selected hour")

with col2:
    st.header("📈 Traffic Insights")
    
    if prediction == 0:
        st.success("✅ Good time to travel!")
        level_value = 30
    else:
        st.warning("⚠️ Expect delays")
        level_value = 80
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = level_value,
        title = {'text': "Traffic Level"},
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "red" if prediction == 1 else "green"},
            'steps': [
                {'range': [0, 30], 'color': "lightgreen"},
                {'range': [30, 70], 'color': "yellow"},
                {'range': [70, 100], 'color': "lightcoral"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)

# Route Planning Section
st.header("🗺️ Route Planning & Navigation")

coords_map = get_location_coordinates()

if from_location != to_location and from_location in coords_map and to_location in coords_map:
    with st.spinner("🔄 Calculating optimal routes..."):
        route_map, route_details, best_route = create_route_map(from_location, to_location, coords_map)
    
    if route_map:
        st.markdown("### 🗺 Interactive Route Map")
        folium_static(route_map, width=800, height=500)
        
        st.markdown("### 📊 Route Comparison")
        
        if route_details:
            cols = st.columns(len(route_details))
            for idx, detail in enumerate(route_details):
                with cols[idx]:
                    is_best = detail == best_route
                    border_color = "orange" if is_best else detail['color']
                    emoji = "🌟" if is_best else "🔹"
                    
                    st.markdown(f"""
                    <div style='border: 2px solid {border_color}; border-radius: 8px; padding: 12px; margin: 8px;
                                {"background: #FFF7E6" if is_best else ""}'>
                        <h4>{emoji} Route {detail['number']}</h4>
                        📏 Distance: {detail['distance']:.1f} km<br>
                        ⏱ Time: {detail['duration']:.1f} mins<br>
                        🎨 Color: <span style='color: {border_color}'>●</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            if best_route:
                st.success(f"""
                🏆 **Recommended Route: Route {best_route['number']}**
                - ⚡ Fastest option: {best_route['duration']:.1f} minutes
                - 📏 Distance: {best_route['distance']:.1f} km
                - 🌦 Weather: {weather} conditions considered
                - 🕒 Time: {hour}:00 traffic patterns
                """)
    else:
        st.error("❌ Unable to fetch route information. Please check your internet connection or try again later.")

elif from_location == to_location:
    st.info("🔄 Please select different start and destination locations to view routes.")
else:
    st.warning("⚠️ Route mapping not available for selected locations. Showing traffic prediction only.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; margin-top: 2rem;'>
    <p>🚦 Smart Traffic Management System | Powered by AI & Real-time Data</p>
    <p>Made with ❤️ for Bangalore Traffic Management</p>
</div>
""", unsafe_allow_html=True)
