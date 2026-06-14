# Smart Home Energy Monitoring System 🏠⚡

A complete IoT energy monitoring solution with both hardware (ESP32) and software (Python simulation) components. Real-time dashboard tracking power consumption, energy costs, and automated safety alerts.

---

## 🚀 Quick Start Guide

### **Prerequisites**
- Python 3.8+ installed
- Git (optional, for cloning)

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

**Dependencies included:**
- `flask>=3.0.0` - Web server framework
- `pandas>=2.0.0` - Data analysis
- `matplotlib>=3.7.0` - Chart generation
- `reportlab>=4.0.0` - PDF generation
- `requests>=2.31.0` - HTTP client

### **2. Start the Server**
```bash
python app.py
```

You should see:
```
╔════════════════════════════════════════════════════════════════╗
║   Smart Home Energy Monitoring System - Flask Server           ║
║   Dashboard: http://localhost:5000                             ║
║   API Docs: http://localhost:5000/api/health                  ║
╚════════════════════════════════════════════════════════════════╝
```

### **3. Open Dashboard**
Navigate to: **http://localhost:5000**

---

## 📁 Project Structure

```
smart home energy monitoring system/
├── app.py                          # Main Flask server (NEW - creates this)
├── requirements.txt                # Python dependencies
├── docs/
│   └── project_guide.md           # Comprehensive documentation
├── arduino_code/
│   └── ESP32_Energy_Monitor.ino   # Embedded firmware
├── circuit_diagram/
│   └── connections.md             # Hardware wiring guide
├── python_simulation/
│   └── energy_simulator.py        # Simulation engine
├── dashboard/
│   ├── index.html                 # Frontend UI
│   ├── app.js                     # (NEW) Real-time updates & interactions
│   └── style.css                  # (NEW - completed) Glassmorphism styling
├── data/                          # (Auto-created) CSV logs
└── outputs/                       # (Auto-created) PDF reports
```

---

## 🎯 Core Features

### **Live Dashboard**
- Real-time voltage, current, power, and energy metrics
- Interactive live power consumption chart (Chart.js)
- System status indicators and alarm notifications
- Glassmorphism dark theme UI

### **Smart Appliances Control**
- Toggle appliances on/off via dashboard
- Predefined load profiles:
  - Air Conditioner: 1200-1800W
  - Refrigerator: 150-250W  
  - Microwave: 800-1200W
  - LED Lighting: 30-90W

### **Safety Features**
- Overload protection (3000W limit)
- Automatic relay trip on overload
- Manual force cutoff button
- Physical buzzer alert on overload state

### **Data Logging & Reports**
- Continuous CSV logging to `data/energy_logs.csv`
- PDF report generation with:
  - Power consumption trend charts
  - Energy/cost summaries
  - Recent log entries
- Downloadable via dashboard

---

## 🔌 API Reference

### **Real-Time Metrics**
```
GET /api/status
```
Returns current system metrics:
```json
{
  "timestamp": "2024-06-14 10:30:45",
  "voltage": 229.5,
  "current": 5.23,
  "power": 1200.0,
  "energy": 0.00150,
  "cost": 0.000225,
  "relay_state": true,
  "is_overloaded": false,
  "appliances": {...},
  "alerts": [...]
}
```

### **Data Retrieval**
```
GET /api/logs?format=csv              # Download CSV
GET /api/logs?format=json             # Get JSON logs
```

### **Appliance Control**
```
POST /api/appliance/{name}
Body: {"state": true/false}
```

### **Relay Control**
```
POST /api/relay/reset                 # Reset overload trip
POST /api/relay/manual-trip           # Force power cutoff
```

### **Energy Management**
```
POST /api/data/reset                  # Clear all logs
GET /api/report                       # Download PDF report
```

### **Health Check**
```
GET /api/health                       # System status
```

---

## 🎮 Dashboard Controls

| Control | Function |
|---------|----------|
| **Appliance Toggles** | Turn appliances on/off to simulate load changes |
| **Trigger Overload Demo** | Automatically turns on high-power devices to test safety |
| **Force Cutoff** | Manually cut power to all loads |
| **Reset Safety Relay** | Restore power after overload trip |
| **Clear Consumption Data** | Wipe all logs and reset counters |
| **PDF Statement** | Generate & download energy report |
| **Raw CSV Data** | Download raw CSV logs |

---

## 🔧 Configuration

### **Calibration Parameters** (in `energy_simulator.py`)
```python
self.voltage_nominal = 230.0      # Nominal AC voltage (V)
self.power_factor = 0.95          # System power factor
self.tariff_rate = 0.15           # Electricity cost ($/kWh)
self.overload_limit = 3000.0      # Safety threshold (W)
```

### **Update Interval**
- Sensor read: **500ms** (configurable in `startLiveUpdates()`)
- Cloud sync: **15 seconds** (ESP32 only)
- Data log: **On every update**

---

## 📊 Simulation Behavior

### **Voltage Fluctuation**
- Base: 230V ± 4V
- Simulates realistic grid variations

### **Load Calculation**
- Each appliance has min/max power range
- Random variation added to simulate real-world behavior
- Current calculated from Power = V × I × PF

### **Energy Integration**
```
Energy(kWh) = Σ(Power(W) × ΔTime(hours)) / 1000
Cost($) = Energy(kWh) × Tariff_Rate($/kWh)
```

### **Overload Trigger**
- Automatic when Power > 3000W
- Relay opens (power cuts)
- LED & buzzer alert activated
- Requires manual or API reset

---

## 🛠️ Hardware Integration (Optional)

### **For Real Hardware (ESP32):**

1. **Components Required:**
   - ESP32 DevKit v1
   - ACS712 Current Sensor (5A/20A/30A)
   - ZMPT101B Voltage Sensor
   - 0.96" SSD1306 OLED Display (I2C)
   - 5V Relay Module
   - Buzzer + LEDs

2. **Compilation:**
   - Use Arduino IDE or PlatformIO
   - Open `arduino_code/ESP32_Energy_Monitor.ino`
   - Configure Wi-Fi credentials and cloud API keys
   - Upload to ESP32

3. **Cloud Integration:**
   - ThingSpeak channel setup
   - Blynk app configuration
   - Both automatically sync with real sensor data

---

## 📈 Expected Performance

| Metric | Typical Value |
|--------|---------------|
| **Dashboard Load Time** | < 2 seconds |
| **API Response Time** | < 100ms |
| **Memory Usage (Python)** | ~50-80MB |
| **CSV File Growth** | ~200 bytes/update (~1MB/day) |
| **PDF Report Generation** | 2-5 seconds |

---

## 🐛 Troubleshooting

### **Dashboard shows "No data available yet"**
- Wait 1-2 seconds for simulator to initialize
- Check browser console (F12) for errors
- Verify Flask server is running on port 5000

### **Charts not updating**
- Ensure JavaScript is enabled
- Check Network tab in DevTools
- Verify `/api/status` endpoint responds

### **Overload never triggers**
- Check `energy_simulator.py` overload_limit setting
- Verify appliance wattages sum > 3000W
- Use "Trigger Overload Demo" button

### **CSV logs not created**
- Verify `data/` directory exists
- Check file permissions
- Restart app.py

### **PDF generation fails**
- Ensure `reportlab` is installed: `pip install reportlab --upgrade`
- Check `outputs/` directory exists
- Verify matplotlib backend is non-interactive

---

## 🎓 Learning Outcomes

By completing this project, you'll understand:

✅ **IoT System Architecture** - Sensor → Microcontroller → Cloud → Dashboard  
✅ **Real-time Data Processing** - Streaming, buffering, and aggregation  
✅ **Web Frontend Development** - HTML5, CSS3, JavaScript, Chart.js  
✅ **REST API Design** - CRUD operations, error handling, status codes  
✅ **Power Systems** - RMS calculations, power factor, energy integration  
✅ **Safety Engineering** - Overload protection, relay logic, alerts  
✅ **Full-Stack Integration** - Backend + Frontend + Hardware coordination  

---

## 📚 Documentation

- **Full Project Guide:** [`docs/project_guide.md`](docs/project_guide.md)
- **Hardware Connections:** [`circuit_diagram/connections.md`](circuit_diagram/connections.md)
- **Arduino Firmware:** [`arduino_code/ESP32_Energy_Monitor.ino`](arduino_code/ESP32_Energy_Monitor.ino)

---

## 🔒 Security Considerations

- Disable debug mode in production: `debug=False` in `app.py`
- Validate all API inputs
- Add authentication for cloud APIs
- Use HTTPS for remote access
- Implement rate limiting for API endpoints
- Sanitize CSV/PDF output data

---

## 📄 License & Attribution

This project is designed for educational purposes. Use freely in:
- Academic portfolios
- Capstone projects
- Technical interview preparation
- IoT learning demonstrations

---

## 🤝 Contributing

To enhance this project:
1. Add database persistence (SQLite/MongoDB)
2. Implement MQTT broker integration
3. Add weather-based load forecasting
4. Create mobile app (React Native/Flutter)
5. Implement ML-based anomaly detection

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review console output and network logs
3. Verify all dependencies are installed
4. Ensure ports 5000 is not in use

---

**Last Updated:** June 14, 2026  
**Version:** 2.1 (Complete Stack)

Happy monitoring! ⚡📊
