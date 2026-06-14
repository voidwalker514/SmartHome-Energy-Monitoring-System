"""
Flask Server for Smart Home Energy Monitoring System
Provides REST API endpoints and serves the web dashboard
"""

from flask import Flask, render_template, jsonify, request, send_file, send_from_directory
from python_simulation.energy_simulator import SmartHomeSimulator
import threading
import time
import os
from datetime import datetime
import json

# ===== Flask App Initialization =====
app = Flask(__name__, 
            template_folder='dashboard',
            static_folder='dashboard')

# ===== Global Simulator Instance =====
simulator = SmartHomeSimulator(log_dir="data", output_dir="outputs")
simulation_thread = None
is_running = False
last_status = None

# ===== Simulation Background Thread =====
def run_simulation():
    """Background thread that continuously updates the simulator"""
    global last_status, simulator
    
    while is_running:
        try:
            status = simulator.update()
            last_status = status
            simulator.log_to_csv()
            time.sleep(0.5)  # Update every 500ms for realistic data
        except Exception as e:
            print(f"Simulation error: {e}")
            time.sleep(1)

def start_simulation():
    """Start the background simulation thread"""
    global simulation_thread, is_running
    
    if not is_running:
        is_running = True
        simulation_thread = threading.Thread(target=run_simulation, daemon=True)
        simulation_thread.start()
        print("[INFO] Simulation started")

def stop_simulation():
    """Stop the background simulation thread"""
    global is_running
    is_running = False
    print("[INFO] Simulation stopped")

# ===== Routes: Static Files & Pages =====
@app.route('/')
def index():
    """Serve the main dashboard HTML"""
    return send_from_directory('dashboard', 'index.html')

@app.route('/style.css')
def serve_css():
    """Serve the CSS stylesheet"""
    return send_from_directory('dashboard', 'style.css')

@app.route('/app.js')
def serve_js():
    """Serve the JavaScript file"""
    return send_from_directory('dashboard', 'app.js')

# ===== API Routes: Real-time Data =====
@app.route('/api/status', methods=['GET'])
def get_status():
    """
    Return current system status as JSON
    {
        "timestamp": "2024-06-14 10:30:45",
        "voltage": 229.50,
        "current": 5.23,
        "power": 1200.00,
        "energy": 0.00150,
        "cost": 0.000225,
        "relay_state": true,
        "is_overloaded": false,
        "appliances": { ... },
        "alerts": [ ... ]
    }
    """
    if last_status:
        return jsonify(last_status)
    else:
        return jsonify({"error": "No data available yet"}), 503

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """
    Return raw CSV data as downloadable file or JSON
    Query param: ?format=json or ?format=csv (default)
    """
    format_type = request.args.get('format', 'csv')
    log_file = os.path.join(simulator.log_dir, 'energy_logs.csv')
    
    if not os.path.exists(log_file):
        return jsonify({"error": "No logs available"}), 404
    
    if format_type == 'json':
        # Convert CSV to JSON
        import pandas as pd
        try:
            df = pd.read_csv(log_file)
            return jsonify(df.to_dict('records'))
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        # Download CSV file
        return send_file(log_file, 
                        mimetype='text/csv',
                        as_attachment=True,
                        download_name='energy_logs.csv')

@app.route('/api/appliance/<name>', methods=['POST'])
def control_appliance(name):
    """
    Toggle an appliance on/off
    POST body: {"state": true/false}
    """
    data = request.get_json()
    state = data.get('state', False)
    
    success = simulator.toggle_appliance(name, state)
    
    if success:
        return jsonify({
            "message": f"Appliance '{name}' set to {'ON' if state else 'OFF'}",
            "status": simulator.get_status()
        })
    else:
        return jsonify({"error": f"Appliance '{name}' not found"}), 404

@app.route('/api/relay/reset', methods=['POST'])
def reset_relay():
    """
    Attempt to reset the overload relay
    """
    success = simulator.reset_relay()
    
    if success:
        return jsonify({
            "message": "Safety relay reset successfully",
            "status": simulator.get_status()
        })
    else:
        return jsonify({
            "message": "Relay not in overload state, no reset needed",
            "status": simulator.get_status()
        })

@app.route('/api/relay/manual-trip', methods=['POST'])
def manual_trip():
    """
    Manually force the relay open (cut power)
    """
    simulator.relay_state = False
    simulator.current = 0.0
    simulator.power = 0.0
    simulator.voltage = 0.0
    
    alert_msg = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "Warning",
        "message": "Relay manually tripped via dashboard control."
    }
    simulator.alerts.append(alert_msg)
    
    return jsonify({
        "message": "Relay manually opened (power cut off)",
        "status": simulator.get_status()
    })

@app.route('/api/data/reset', methods=['POST'])
def reset_data():
    """
    Clear all accumulated energy and cost data
    """
    old_kwh = simulator.cumulative_kwh
    simulator.cumulative_kwh = 0.0
    simulator.estimated_cost = 0.0
    simulator.alerts = []
    
    # Create new CSV file
    simulator.write_header_to_csv()
    
    return jsonify({
        "message": f"Data reset. Previously accumulated: {old_kwh:.4f} kWh",
        "status": simulator.get_status()
    })

@app.route('/api/report', methods=['GET'])
def generate_report():
    """
    Generate and download PDF energy report
    """
    try:
        pdf_path = simulator.generate_pdf_report()
        return send_file(pdf_path,
                        mimetype='application/pdf',
                        as_attachment=True,
                        download_name='energy_report.pdf')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        "status": "healthy",
        "simulator_running": is_running,
        "timestamp": datetime.now().isoformat()
    })

# ===== Error Handlers =====
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500

# ===== Application Lifecycle =====
@app.before_request
def before_request():
    """Initialize simulation on first request"""
    global is_running
    if not is_running:
        start_simulation()

@app.teardown_appcontext
def shutdown_session(exception=None):
    """Cleanup on shutdown"""
    pass

if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║   Smart Home Energy Monitoring System - Flask Server           ║
    ║   Dashboard: http://localhost:5000                             ║
    ║   API Docs: http://localhost:5000/api/health                  ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    # Create necessary directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('outputs', exist_ok=True)
    
    # Start server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False  # Prevent running simulation twice
    )
