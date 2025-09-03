#!/bin/bash

echo "🚦 Smart Traffic Management System - Setup Script"
echo "================================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7+ first."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo

# Setup config file
if [ ! -f "config.py" ]; then
    echo "⚙️ Setting up configuration file..."
    cp config_template.py config.py
    echo "✅ Created config.py from template"
    echo "⚠️  IMPORTANT: Edit config.py and add your OpenRouteService API key!"
    echo "   Get a free API key from: https://openrouteservice.org/"
else
    echo "✅ config.py already exists"
fi

echo

# Check for data files
if [ ! -f "bangalore_traffic.csv" ]; then
    echo "⚠️  bangalore_traffic.csv not found"
    echo "   This file is required for the application to work"
fi

if [ ! -f "traffic_classifier.pkl" ]; then
    echo "⚠️  traffic_classifier.pkl not found"
    echo "   This file is required for the ML predictions"
fi

echo
echo "🎉 Setup complete!"
echo
echo "Next steps:"
echo "1. Edit config.py and add your OpenRouteService API key"
echo "2. Ensure you have the required data files"
echo "3. Run: streamlit run smart_traffic_app.py"
echo
echo "For troubleshooting, see TROUBLESHOOTING.md"
