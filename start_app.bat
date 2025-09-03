@echo off
echo ========================================
echo  Smart Traffic Management System
echo  Professional Startup Script
echo ========================================
echo.

echo Checking Python environment...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found! Please install Python.
    pause
    exit /b 1
)

echo.
echo Checking required packages...
python -c "import streamlit, folium, pandas, joblib, openrouteservice, plotly" 2>nul
if %errorlevel% neq 0 (
    echo Installing missing packages...
    pip install streamlit folium streamlit-folium pandas joblib openrouteservice plotly scikit-learn
)

echo.
echo Checking data files...
if not exist "bangalore_traffic.csv" (
    echo ERROR: bangalore_traffic.csv not found!
    pause
    exit /b 1
)

if not exist "traffic_classifier.pkl" (
    echo ERROR: traffic_classifier.pkl not found!
    pause
    exit /b 1
)

echo.
echo Starting Smart Traffic Management System...
echo.
echo The app will open at: http://localhost:8501
echo.
echo ========================================
echo  Press Ctrl+C to stop the application
echo ========================================
echo.

streamlit run smart_traffic_app.py --server.port 8501 --server.headless false

echo.
echo Application stopped.
pause
