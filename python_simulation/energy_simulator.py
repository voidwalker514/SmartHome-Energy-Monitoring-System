import os
import time
import random
import csv
import datetime
import pandas as pd
import matplotlib
matplotlib.use('Agg') # Non-interactive backend for server compatibility
import matplotlib.pyplot as plt

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class SmartHomeSimulator:
    def __init__(self, log_dir="data", output_dir="outputs"):
        self.log_dir = log_dir
        self.output_dir = output_dir
        self.log_file = os.path.join(self.log_dir, "energy_logs.csv")
        
        # Ensure directories exist
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # System Constants
        self.voltage_nominal = 230.0  # Volts
        self.power_factor = 0.95      # Standard resistive-inductive mixed PF
        self.tariff_rate = 0.15       # $ per kWh
        self.overload_limit = 3000.0  # Watts
        
        # Live System States
        self.voltage = 230.0
        self.current = 0.0
        self.power = 0.0
        self.cumulative_kwh = 0.0
        self.estimated_cost = 0.0
        
        self.is_overloaded = False
        self.relay_state = True       # True = closed (power on), False = open (power off)
        self.last_update_time = time.time()
        
        # Load profile definitions (Appliance Name: [Min Watts, Max Watts, IsOn])
        self.appliances = {
            "Air Conditioner": [1200, 1800, True],
            "Refrigerator": [150, 250, True],
            "Microwave": [800, 1200, False],
            "LED Lighting": [30, 90, True]
        }
        
        # Alert Logs
        self.alerts = []
        
        # Initialize CSV log file with headers if it doesn't exist
        if not os.path.exists(self.log_file):
            self.write_header_to_csv()
            
    def write_header_to_csv(self):
        with open(self.log_file, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Voltage", "Current", "Power", "Energy", "Cost", "RelayState", "AlertStatus"])

    def update(self):
        """
        Main calculation loop. Updates voltages, current values, power consumption,
        integrates energy metrics using delta time, and checks for overload limits.
        """
        now = time.time()
        dt = now - self.last_update_time
        self.last_update_time = now
        
        if not self.relay_state:
            # Relay is open, no current flows
            self.voltage = 0.0
            self.current = 0.0
            self.power = 0.0
            return self.get_status()

        # Simulate small grid voltage fluctuations (226V - 234V)
        self.voltage = self.voltage_nominal + random.uniform(-4.0, 4.0)
        
        # Calculate total power based on active appliances
        total_w = 0.0
        for name, profile in self.appliances.items():
            is_on = profile[2]
            if is_on:
                # Add random noise to appliance load
                base_w = random.uniform(profile[0], profile[1])
                total_w += base_w
        
        self.power = total_w
        self.current = self.power / (self.voltage * self.power_factor)
        
        # Integrate energy: kWh = (Power_W * dt_hours) / 1000
        dt_hours = dt / 3600.0
        self.cumulative_kwh += (self.power / 1000.0) * dt_hours
        self.estimated_cost = self.cumulative_kwh * self.tariff_rate
        
        # Check Overload Limit (3000W)
        if self.power > self.overload_limit:
            self.trigger_overload_trip()
            
        return self.get_status()

    def trigger_overload_trip(self):
        self.is_overloaded = True
        self.relay_state = False
        self.voltage = 0.0
        self.current = 0.0
        self.power = 0.0
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.alerts.append({
            "timestamp": timestamp,
            "type": "Danger",
            "message": f"OVERLOAD DETECTED! Total Power exceeded limit ({self.overload_limit}W). Safety relay tripped."
        })
        print(f"[{timestamp}] ALERT: Safety Relay Tripped due to Overload!")

    def toggle_appliance(self, name, state):
        """Turn appliance on (True) or off (False)"""
        if name in self.appliances:
            self.appliances[name][2] = bool(state)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            state_str = "ON" if state else "OFF"
            self.alerts.append({
                "timestamp": timestamp,
                "type": "Info",
                "message": f"Appliance '{name}' switched {state_str}."
            })
            return True
        return False

    def reset_relay(self):
        """Resets the overload safety trip"""
        if self.is_overloaded:
            self.is_overloaded = False
            # Turn off high-load appliances that caused the trip to avoid re-tripping
            if "Microwave" in self.appliances:
                self.appliances["Microwave"][2] = False
            self.relay_state = True
            self.last_update_time = time.time()
            
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.alerts.append({
                "timestamp": timestamp,
                "type": "Success",
                "message": "Overload state cleared. System power restored."
            })
            print(f"[{timestamp}] System manual reset successful.")
            return True
        return False

    def get_status(self):
        """Returns current system metrics and appliance states"""
        appliance_states = {}
        for name, profile in self.appliances.items():
            appliance_states[name] = {
                "min_w": profile[0],
                "max_w": profile[1],
                "is_on": profile[2]
            }
            
        return {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "voltage": round(self.voltage, 2),
            "current": round(self.current, 3),
            "power": round(self.power, 2),
            "energy": round(self.cumulative_kwh, 5),
            "cost": round(self.estimated_cost, 4),
            "relay_state": self.relay_state,
            "is_overloaded": self.is_overloaded,
            "appliances": appliance_states,
            "alerts": self.alerts[-10:]  # Send last 10 alerts
        }

    def log_to_csv(self):
        """Append current metrics to local CSV database"""
        status = self.get_status()
        with open(self.log_file, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                status["timestamp"],
                status["voltage"],
                status["current"],
                status["power"],
                status["energy"],
                status["cost"],
                1 if status["relay_state"] else 0,
                "TRIPPED" if status["is_overloaded"] else "OK"
            ])

    def generate_chart(self):
        """Generate Matplotlib trend chart for the PDF report"""
        if not os.path.exists(self.log_file):
            return None
            
        try:
            df = pd.read_csv(self.log_file)
            if len(df) < 2:
                return None
                
            # Keep last 50 data points for clarity
            df = df.tail(50)
            
            # Format index for dates
            df['Time'] = pd.to_datetime(df['Timestamp']).dt.strftime('%H:%M:%S')
            
            plt.figure(figsize=(10, 5))
            plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
            
            plt.plot(df['Time'], df['Power'], label='Power Consumption (W)', color='#6366f1', linewidth=2.5, marker='o', markersize=3)
            plt.fill_between(df['Time'], df['Power'], color='#818cf8', alpha=0.15)
            
            plt.title('Live Power Consumption Trend (W)', fontsize=14, fontweight='bold', pad=15)
            plt.xlabel('TimeStamp', fontsize=11, labelpad=8)
            plt.ylabel('Power (W)', fontsize=11, labelpad=8)
            plt.xticks(rotation=45, ha='right', fontsize=9)
            plt.yticks(fontsize=9)
            plt.tight_layout()
            
            chart_path = os.path.join(self.output_dir, "summary_charts.png")
            plt.savefig(chart_path, dpi=150)
            plt.close()
            return chart_path
        except Exception as e:
            print(f"Error generating Matplotlib chart: {e}")
            return None

    def generate_pdf_report(self):
        """Generate a complete PDF invoice/energy report using ReportLab"""
        pdf_path = os.path.join(self.output_dir, "energy_report.pdf")
        
        # Make sure chart is refreshed
        chart_path = self.generate_chart()
        
        doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                                rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=24,
            textColor=colors.HexColor('#1e1b4b'),
            spaceAfter=15
        )
        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            textColor=colors.HexColor('#475569'),
            spaceAfter=25
        )
        section_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=colors.HexColor('#4f46e5'),
            spaceBefore=15,
            spaceAfter=10
        )
        normal_style = ParagraphStyle(
            'BodyNormal',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.HexColor('#1e293b'),
            leading=14
        )
        
        # Header Info
        story.append(Paragraph("Smart Home Energy Consumption Report", title_style))
        story.append(Paragraph(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Target: Smart Home Simulator Node 01", subtitle_style))
        story.append(Spacer(1, 10))
        
        # Summary Metrics
        if os.path.exists(self.log_file):
            try:
                df = pd.read_csv(self.log_file)
                total_records = len(df)
                avg_voltage = round(df['Voltage'].mean(), 2) if total_records > 0 else 0
                max_power = round(df['Power'].max(), 2) if total_records > 0 else 0
                total_energy = round(df['Energy'].iloc[-1], 4) if total_records > 0 else 0
                total_cost = round(df['Cost'].iloc[-1], 4) if total_records > 0 else 0
            except:
                avg_voltage, max_power, total_energy, total_cost = 230.0, 0.0, 0.0, 0.0
        else:
            avg_voltage, max_power, total_energy, total_cost = 230.0, 0.0, 0.0, 0.0
            
        summary_data = [
            [Paragraph("<b>Metric</b>", normal_style), Paragraph("<b>Value</b>", normal_style), Paragraph("<b>Unit</b>", normal_style)],
            ["Nominal Voltage", f"{avg_voltage}", "V AC"],
            ["Peak Power Recorded", f"{max_power}", "W"],
            ["Accumulated Energy", f"{total_energy}", "kWh"],
            ["Current Estimated Cost", f"${total_cost}", "USD"],
            ["Tariff Plan Rate", f"${self.tariff_rate}", "per kWh"]
        ]
        
        t_summary = Table(summary_data, colWidths=[200, 150, 150])
        t_summary.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('TOPPADDING', (0,0), (-1,0), 6),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('TOPPADDING', (0,1), (-1,-1), 8),
            ('BOTTOMPADDING', (0,1), (-1,-1), 8),
        ]))
        
        story.append(Paragraph("System Consumption Summary", section_style))
        story.append(t_summary)
        story.append(Spacer(1, 20))
        
        # Add Chart Image if available
        if chart_path and os.path.exists(chart_path):
            story.append(Paragraph("Power Consumption Trend Analysis", section_style))
            img = Image(chart_path, width=500, height=250)
            story.append(img)
            story.append(Spacer(1, 20))
            
        # Recent Log Table
        story.append(Paragraph("Recent Power Log Entries", section_style))
        log_headers = [Paragraph("<b>Timestamp</b>", normal_style), 
                       Paragraph("<b>Voltage (V)</b>", normal_style), 
                       Paragraph("<b>Current (A)</b>", normal_style), 
                       Paragraph("<b>Power (W)</b>", normal_style), 
                       Paragraph("<b>Energy (kWh)</b>", normal_style)]
        
        log_table_data = [log_headers]
        if os.path.exists(self.log_file):
            try:
                recent_logs = df.tail(10).values.tolist()
                for row in recent_logs:
                    log_table_data.append([
                        row[0],                  # Timestamp
                        str(round(row[1], 1)),   # V
                        str(round(row[2], 2)),   # I
                        str(round(row[3], 1)),   # P
                        str(round(row[4], 4))    # kWh
                    ])
            except Exception as e:
                print(f"Log formatting fail: {e}")
                
        t_logs = Table(log_table_data, colWidths=[160, 80, 80, 90, 90])
        t_logs.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#6366f1')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        
        # Wrap table style fonts
        for r_idx in range(len(log_table_data)):
            for c_idx in range(len(log_table_data[r_idx])):
                if r_idx == 0:
                    continue
                # Make standard strings for inside grid
                val = log_table_data[r_idx][c_idx]
                log_table_data[r_idx][c_idx] = Paragraph(val, normal_style)
                
        story.append(t_logs)
        story.append(Spacer(1, 20))
        
        # Footer Note
        story.append(Paragraph("<b>Disclaimer:</b> This report is generated dynamically by the Smart Home Energy Monitoring simulation engine. Real-world implementations utilize calibrated physical current (ACS712) and voltage (ZMPT101B) sensors with microcontrollers streaming to Cloud endpoints.", ParagraphStyle('FooterStyle', parent=styles['Italic'], fontSize=8, textColor=colors.HexColor('#64748b'))))
        
        doc.build(story)
        print(f"PDF Energy Report generated at {pdf_path}")
        return pdf_path

if __name__ == "__main__":
    sim = SmartHomeSimulator()
    print("Testing Simulator Run for 5 steps...")
    for _ in range(5):
        print(sim.update())
        sim.log_to_csv()
        time.sleep(1)
    sim.generate_pdf_report()
