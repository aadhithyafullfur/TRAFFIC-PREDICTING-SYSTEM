@echo off
echo ========================================
echo  Smart Traffic Management System
echo  Setup Script for Windows
echo ========================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found! Please install Python 3.7+ first.
    echo Download from: https://python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Found: %PYTHON_VERSION%
echo.

echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed successfully
echo.

echo Setting up configuration file...
if not exist "config.py" (
    copy config_template.py config.py >nul
    echo ✅ Created config.py from template
    echo.
    echo ⚠️  IMPORTANT: Edit config.py and add your OpenRouteService API key!
    echo    Get a free API key from: https://openrouteservice.org/
) else (
    echo ✅ config.py already exists
)
echo.

echo Checking for required data files...
if not exist "bangalore_traffic.csv" (
    echo ⚠️  bangalore_traffic.csv not found
    echo    This file is required for the application to work
)

if not exist "traffic_classifier.pkl" (
    echo ⚠️  traffic_classifier.pkl not found  
    echo    This file is required for ML predictions
)

echo.
echo ========================================
echo  🎉 Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit config.py and add your API key
echo 2. Ensure you have the required data files
echo 3. Run: start_app.bat
echo.
echo For help, see TROUBLESHOOTING.md
echo.
pause
