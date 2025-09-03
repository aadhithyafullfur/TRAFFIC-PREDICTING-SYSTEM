# 🔧 Troubleshooting Guide - Smart Traffic Management System

## Common Connection Issues & Solutions

### 🚨 "Connection error" - Streamlit Not Running

**Problem**: Browser shows "Connection error" or "Is Streamlit still running?"

**Solutions**:

#### Method 1: Use the Startup Script
```bash
# Double-click this file or run in terminal:
start_app.bat
```

#### Method 2: Manual Restart
```bash
# Open terminal in project folder and run:
streamlit run smart_traffic_app.py --server.port 8501
```

#### Method 3: Different Port
```bash
# If port 8501 is busy, try:
streamlit run smart_traffic_app.py --server.port 8502
```

### 🐛 Other Common Issues

#### Issue: "Module not found" errors
**Solution**: Install missing packages
```bash
pip install streamlit folium streamlit-folium pandas joblib openrouteservice plotly scikit-learn
```

#### Issue: "File not found" errors
**Solution**: Ensure these files exist in the project folder:
- `bangalore_traffic.csv`
- `traffic_classifier.pkl`
- `config.py`
- `smart_traffic_app.py`

#### Issue: Map not showing
**Solutions**:
1. Check internet connection (required for OpenRouteService)
2. Verify API key in `config.py`
3. Select different locations from dropdowns

#### Issue: Slow loading
**Solutions**:
1. Wait for data to load (8.9M records)
2. Clear browser cache
3. Restart the application

### 🌐 Browser Compatibility

**Recommended Browsers**:
- ✅ Chrome (latest)
- ✅ Firefox (latest)
- ✅ Edge (latest)
- ⚠️ Safari (may have some styling issues)

### 📱 Mobile Usage

The app is responsive and works on mobile devices, but desktop is recommended for the best experience.

### 🔗 URL Access

**Local Access**: `http://localhost:8501`
**Network Access**: `http://YOUR_IP:8501` (if firewall allows)

### 🚀 Performance Tips

1. **First Launch**: May take 30-60 seconds to load all data
2. **Route Calculation**: Requires internet connection
3. **Best Performance**: Use on desktop with good internet connection

### 📞 Still Having Issues?

1. **Check Terminal Output**: Look for error messages in the command prompt
2. **Restart Computer**: Sometimes helps with port conflicts
3. **Antivirus**: Temporarily disable if blocking connections
4. **Firewall**: Allow Python/Streamlit through firewall

### 🔧 Advanced Troubleshooting

#### Clear Streamlit Cache
```bash
streamlit cache clear
```

#### Reset Configuration
```bash
streamlit config show
```

#### Run with Debug Info
```bash
streamlit run smart_traffic_app.py --logger.level debug
```

### ✅ Quick Health Check

Run this command to verify everything is working:
```bash
python -c "import streamlit, pandas, joblib; print('✅ All packages working')"
```

---

## 🆘 Emergency Restart Procedure

If nothing works, follow these steps:

1. **Close all browser tabs**
2. **Stop all Python processes** (Ctrl+C in terminal)
3. **Wait 10 seconds**
4. **Run**: `start_app.bat`
5. **Open browser to**: `http://localhost:8501`

---

*For technical support, check the project README.md or create an issue on GitHub.*
