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
from streamlit_folium import st_folium
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
        "1st Main Road": (12.9784, 77.5994),
        "2nd Cross": (12.9352, 77.6245),
        "2nd Cross Road": (12.9628, 77.6447),
        "2nd Main Road": (12.9863, 77.6189),
        "3rd Cross": (12.9256, 77.6693),
        "4th Cross": (12.9087, 77.6014),
        "Albert Victor Road": (12.9663, 77.5967),
        "Ali Asker Road": (12.9945, 77.5861),
        "Annaswamy Mudaliar Road": (12.9665, 77.5942),
        "Artillery Road": (12.9759, 77.6158),
        "Assayyee Road - Annaswamy Mudaliar Road": (12.9653, 77.5951),
        "Atturu-Ananthapura Road": (12.9001, 77.5623),
        "Avenue Road": (12.9732, 77.5816),
        "BTM Layout": (12.9162, 77.6101),
        "Banasawadi-Ramamurthynagar Road": (13.0139, 77.6612),
        "Bangalore University Road": (13.0344, 77.5652),
        "Bannerghatta Road": (12.8913, 77.5979),
        "Bazaar Street": (12.9675, 77.5783),
        "Bedarahalli-Ullalu Road": (12.8614, 77.5337),
        "Begur Main Road": (12.8581, 77.6412),
        "Bellary Road": (13.0068, 77.5893),
        "Brigade Road": (12.9754, 77.6045),
        "Brunton Road": (12.9761, 77.6073),
        "Byappanahalli Main Road": (12.9782, 77.6385),
        "Campbell Road": (12.9892, 77.5819),
        "Castle Street": (12.9738, 77.5967),
        "Central Street": (12.9739, 77.6112),
        "Chamarajpet - Sarjapur Road": (12.9541, 77.5653),
        "Church Street": (12.9723, 77.6118),
        "City Bus Road": (12.9779, 77.5716),
        "Cleveland Road": (12.9726, 77.6089),
        "Commercial Street": (12.9771, 77.6105),
        "Commissariat Road": (12.9738, 77.6115),
        "Convent Road": (12.9712, 77.6062),
        "Crescent Road": (12.9881, 77.5931),
        "Cubbon Road": (12.9765, 77.5947),
        "Cunningham Road": (12.9789, 77.6022),
        "Devanga Hostel Road": (12.9628, 77.5791),
        "Diagonal Road": (12.9762, 77.5923),
        "Dickenson Road": (12.9715, 77.6221),
        "Double Road": (12.9632, 77.5841),
        "Dr.Rajkumar Road": (12.9981, 77.5521),
        "Electronic City": (12.8452, 77.6604),
        "Electronic City Phase 1": (12.8456, 77.6643),
        "Haines Road": (12.9584, 77.6037),
        "Hennur Main Road": (13.0415, 77.6213),
        "Hosur Road": (12.9169, 77.6298),
        "Indiranagar 100 Feet Road": (12.9784, 77.6392),
        "Infantry Road": (12.9812, 77.5998),
        "Jayachamaraja Wodeyar Road": (12.9738, 77.5876),
        "Kasturba Road": (12.9746, 77.5932),
        "Koramangala 5th Block": (12.9345, 77.6232),
        "Koramangala - Indiranagar Road": (12.9654, 77.6287),
        "Langford Road": (12.9574, 77.5978),
        "Lavelle Road": (12.9709, 77.6012),
        "Mahatma Gandhi Road": (12.9765, 77.6045),
        "Marathahalli": (12.9592, 77.6974),
        "Mysore Road": (12.9563, 77.5132),
        "Old Madras Road": (12.9987, 77.6789),
        "Outer Ring Road": (12.9345, 77.6891),
        "Palace Road": (12.9987, 77.5921),
        "Prime Street": (12.9721, 77.6045),
        "Race Course Road": (12.9843, 77.5987),
        "Rajaram Mohan Roy Road": (12.9632, 77.5789),
        "Residency Road": (12.9712, 77.6012),
        "Richmond Road": (12.9612, 77.6012),
        "Sarjapura Road": (12.9012, 77.6891),
        "Silk Board": (12.9172, 77.6237),
        "Sri Rama Temple Street": (12.9432, 77.5678),
        "Vidyaranyapura Road": (13.0789, 77.5432),
        "Whitefield": (12.9698, 77.7499),
        "Whitefield Main Road": (12.9784, 77.7321),
        "Hebbal": (13.0358, 77.5970),
        "Majestic": (12.9763, 77.5715)
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

# Debug information
with st.expander("🔧 Debug Information", expanded=False):
    st.write(f"From location: {from_location}")
    st.write(f"To location: {to_location}")
    st.write(f"From location in coords_map: {from_location in coords_map}")
    st.write(f"To location in coords_map: {to_location in coords_map}")
    st.write(f"Locations same? {from_location == to_location}")
    st.write(f"Total locations in coords_map: {len(coords_map)}")
    if from_location not in coords_map:
        st.error(f"❌ '{from_location}' not found in coordinates map")
    if to_location not in coords_map:
        st.error(f"❌ '{to_location}' not found in coordinates map")

if from_location != to_location and from_location in coords_map and to_location in coords_map:
    with st.spinner("🔄 Calculating optimal routes..."):
        route_map, route_details, best_route = create_route_map(from_location, to_location, coords_map)
    
    if route_map:
        st.markdown("### 🗺 Interactive Route Map")
        st_folium(route_map, width=800, height=500, returned_objects=[])
        
        st.markdown("### 📊 Detailed Route Analysis & Comparison")
        
        if route_details:
            # First, show a summary table
            st.markdown("#### 📋 Quick Route Summary")
            
            # Create comparison table
            comparison_df = pd.DataFrame({
                'Route': [f"Route {detail['number']}" for detail in route_details],
                'Distance (km)': [f"{detail['distance']:.1f}" for detail in route_details],
                'Time (mins)': [f"{detail['duration']:.0f}" for detail in route_details],
                'Speed (km/h)': [f"{(detail['distance'] / (detail['duration']/60)):.1f}" for detail in route_details],
                'Status': ['🌟 RECOMMENDED' if detail == best_route else '⭐ Alternative' for detail in route_details]
            })
            
            st.dataframe(
                comparison_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Route": st.column_config.TextColumn("Route", width="small"),
                    "Distance (km)": st.column_config.TextColumn("Distance", width="small"),
                    "Time (mins)": st.column_config.TextColumn("Duration", width="small"),
                    "Speed (km/h)": st.column_config.TextColumn("Avg Speed", width="small"),
                    "Status": st.column_config.TextColumn("Recommendation", width="medium")
                }
            )
            
            st.markdown("#### 🎯 Detailed Route Cards")
            
            # Enhanced route cards with cleaner approach
            cols = st.columns(len(route_details))
            for idx, detail in enumerate(route_details):
                with cols[idx]:
                    is_best = detail == best_route
                    
                    # Calculate additional metrics
                    avg_speed = detail['distance'] / (detail['duration']/60)
                    time_diff = detail['duration'] - best_route['duration'] if not is_best else 0
                    distance_diff = detail['distance'] - best_route['distance'] if not is_best else 0
                    
                    # Route header
                    if is_best:
                        st.markdown(f"""
                        <div style='text-align: center; padding: 15px; background: linear-gradient(135deg, #FFD700, #FFA500); 
                                    border-radius: 15px; margin-bottom: 15px; color: white; font-weight: bold;'>
                            <h2 style='margin: 0; color: white;'>🌟 Route {detail['number']}</h2>
                            <div style='font-size: 14px; margin-top: 5px;'>⭐ RECOMMENDED ⭐</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style='text-align: center; padding: 15px; background: {detail['color']}; 
                                    border-radius: 15px; margin-bottom: 15px; color: white; font-weight: bold;'>
                            <h2 style='margin: 0; color: white;'>🔹 Route {detail['number']}</h2>
                            <div style='font-size: 14px; margin-top: 5px; opacity: 0.9;'>Alternative Route</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Main metrics using Streamlit metrics
                    st.metric(
                        label="🚗 Distance", 
                        value=f"{detail['distance']:.1f} km",
                        delta=f"{distance_diff:+.1f} km" if not is_best and distance_diff != 0 else None
                    )
                    
                    st.metric(
                        label="⏱️ Duration", 
                        value=f"{detail['duration']:.0f} mins",
                        delta=f"{time_diff:+.0f} mins" if not is_best and time_diff != 0 else None
                    )
                    
                    st.metric(
                        label="⚡ Avg Speed", 
                        value=f"{avg_speed:.1f} km/h"
                    )
                    
                    # Route color indicator
                    if is_best:
                        st.markdown(f"""
                        <div style='text-align: center; margin: 15px 0; padding: 10px; 
                                    background: #FFF8DC; border-radius: 8px; border: 2px solid #FFD700;'>
                            <span style='color: #FF8C00; font-size: 24px;'>●</span><br>
                            <small style='color: #666;'>Map Color: Orange</small>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style='text-align: center; margin: 15px 0; padding: 10px; 
                                    background: #F8F9FA; border-radius: 8px; border: 2px solid {detail['color']};'>
                            <span style='color: {detail['color']}; font-size: 24px;'>●</span><br>
                            <small style='color: #666;'>Map Color</small>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Performance indicator
                    if is_best:
                        st.success("🏆 Fastest Route!")
                    elif time_diff <= 5:
                        st.info("⭐ Good Alternative")
                    else:
                        st.warning("⏳ Slower Option")
            
            # Enhanced recommendation section
            st.markdown("#### 🏆 Smart Recommendation")
            
            # Calculate savings and benefits
            if len(route_details) > 1:
                slowest_route = max(route_details, key=lambda x: x['duration'])
                time_saved = slowest_route['duration'] - best_route['duration']
                
                longest_route = max(route_details, key=lambda x: x['distance'])
                distance_saved = longest_route['distance'] - best_route['distance']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.success(f"""
                    ### � **Optimal Choice: Route {best_route['number']}**
                    
                    **Why this route is best:**
                    - ⚡ **Fastest**: {best_route['duration']:.0f} minutes
                    - �️ **Distance**: {best_route['distance']:.1f} km  
                    - 🚗 **Speed**: {(best_route['distance'] / (best_route['duration']/60)):.1f} km/h
                    - ⏰ **Time Saved**: Up to {time_saved:.0f} minutes
                    - 📏 **Distance Saved**: Up to {distance_saved:.1f} km
                    """)
                
                with col2:
                    st.info(f"""
                    ### 📊 **Journey Context**
                    
                    **Current Conditions:**
                    - �️ **Weather**: {weather}
                    - 🕐 **Time**: {hour}:00
                    - 🚦 **Traffic**: {traffic_status}
                    - 🎯 **Confidence**: {confidence:.0%}
                    
                    **Trip Summary:**
                    - 📍 **From**: {from_location}
                    - 📍 **To**: {to_location}
                    """)
            
            # Traffic-aware insights
            st.markdown("#### 💡 Smart Insights")
            insights_col1, insights_col2, insights_col3 = st.columns(3)
            
            with insights_col1:
                if best_route['duration'] < 20:
                    st.success("🚀 **Quick Journey** - Under 20 minutes!")
                elif best_route['duration'] < 45:
                    st.info("⏱️ **Moderate Journey** - Good timing")
                else:
                    st.warning("🐌 **Longer Journey** - Consider alternative timing")
            
            with insights_col2:
                if prediction == 0:
                    st.success("✅ **Low Traffic** - Perfect time to travel!")
                else:
                    st.warning("⚠️ **High Traffic** - Extra time recommended")
            
            with insights_col3:
                if weather == "Clear":
                    st.success("☀️ **Clear Weather** - Smooth driving conditions")
                elif weather == "Rainy":
                    st.warning("🌧️ **Rainy Weather** - Drive carefully!")
                else:
                    st.info(f"🌤️ **{weather} Weather** - Moderate conditions")
                    
        else:
            st.warning("⚠️ No route details available")
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
