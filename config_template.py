"""
Configuration file for Smart Traffic Management System
Contains API keys, settings, and constants

IMPORTANT: This is a template file.
- Copy this file to 'config.py'
- Replace 'YOUR_API_KEY_HERE' with your actual OpenRouteService API key
- Get a free API key from: https://openrouteservice.org/
"""

# OpenRouteService API Configuration
# Get your free API key from: https://openrouteservice.org/
ORS_API_KEY = "YOUR_API_KEY_HERE"

# Application Settings
APP_TITLE = "Smart Traffic Management System"
APP_VERSION = "2.0"
APP_DESCRIPTION = "Intelligent Traffic Prediction & Route Optimization for Bangalore"

# Data File Paths
TRAFFIC_DATA_FILE = "bangalore_traffic.csv"
MODEL_FILE = "traffic_classifier.pkl"

# Map Configuration
DEFAULT_ZOOM = 13
MAP_TILES = 'OpenStreetMap'

# Traffic Prediction Settings
DEFAULT_VEHICLE_COUNT = 75
CONFIDENCE_THRESHOLD = 0.7

# Route Planning Settings
MAX_ALTERNATIVE_ROUTES = 3
ROUTE_SHARE_FACTOR = 0.5

# UI Configuration
SIDEBAR_EXPANDED = True
LAYOUT_MODE = "wide"
