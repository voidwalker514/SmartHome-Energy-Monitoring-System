/**
 * Smart Home Energy Monitoring System - Frontend JavaScript
 * Handles real-time dashboard updates, charts, and user interactions
 */

// ===== Global Variables =====
let realtimeChart = null;
const chartDataPoints = 60; // Display last 60 data points (30 seconds at 0.5s interval)
let chartLabels = [];
let chartPowerData = [];
let chartCurrentData = [];

// ===== Initialize Dashboard on Page Load =====
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initializing...');
    
    initializeChart();
    startLiveUpdates();
    attachEventListeners();
    updateTimeDisplay();
    
    // Update time every second
    setInterval(updateTimeDisplay, 1000);
});

// ===== Chart Initialization =====
function initializeChart() {
    const ctx = document.getElementById('realtimeChart');
    if (!ctx) return;
    
    realtimeChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartLabels,
            datasets: [
                {
                    label: 'Active Power (W)',
                    data: chartPowerData,
                    borderColor: '#818cf8',
                    backgroundColor: 'rgba(129, 140, 248, 0.1)',
                    borderWidth: 2.5,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 2,
                    pointBackgroundColor: '#818cf8',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 1,
                    yAxisID: 'y'
                },
                {
                    label: 'Load Current (A)',
                    data: chartCurrentData,
                    borderColor: '#22d3ee',
                    backgroundColor: 'rgba(34, 211, 238, 0.05)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 1.5,
                    pointBackgroundColor: '#22d3ee',
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#94a3b8',
                        font: { size: 12, weight: 500 },
                        padding: 15,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.95)',
                    borderColor: 'rgba(99, 102, 241, 0.3)',
                    borderWidth: 1,
                    titleColor: '#f8fafc',
                    bodyColor: '#cbd5e1',
                    padding: 10,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            if (context.datasetIndex === 0) {
                                return 'Power: ' + context.parsed.y.toFixed(1) + ' W';
                            } else {
                                return 'Current: ' + context.parsed.y.toFixed(2) + ' A';
                            }
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    grid: { color: 'rgba(255, 255, 255, 0.05)', drawBorder: false },
                    ticks: { color: '#64748b', font: { size: 10 } },
                    max: chartDataPoints
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    grid: { color: 'rgba(99, 102, 241, 0.1)', drawBorder: false },
                    ticks: { color: '#818cf8', font: { size: 10 } },
                    title: {
                        display: true,
                        text: 'Power (W)',
                        color: '#818cf8',
                        font: { size: 11, weight: 'bold' }
                    },
                    min: 0,
                    max: 3500
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    grid: { drawOnChartArea: false, drawBorder: false },
                    ticks: { color: '#22d3ee', font: { size: 10 } },
                    title: {
                        display: true,
                        text: 'Current (A)',
                        color: '#22d3ee',
                        font: { size: 11, weight: 'bold' }
                    },
                    min: 0,
                    max: 15
                }
            }
        }
    });
}

// ===== Live Data Updates =====
function startLiveUpdates() {
    /**
     * Poll API every 500ms for latest sensor data
     */
    setInterval(async () => {
        try {
            const response = await fetch('/api/status');
            if (!response.ok) {
                console.warn('Status endpoint unavailable');
                return;
            }
            
            const data = await response.json();
            updateDashboard(data);
            updateChart(data);
            updateAppliances(data);
            updateAlerts(data);
        } catch (error) {
            console.error('Fetch error:', error);
        }
    }, 500); // Update every 500ms
}

// ===== Update Dashboard Metrics =====
function updateDashboard(data) {
    // Voltage Display
    document.getElementById('val-voltage').textContent = data.voltage.toFixed(1);
    const voltagePercent = Math.min((data.voltage / 250) * 100, 100);
    document.getElementById('prog-voltage').style.width = voltagePercent + '%';
    
    // Current Display
    document.getElementById('val-current').textContent = data.current.toFixed(2);
    const currentPercent = Math.min((data.current / 13.04) * 100, 100);
    document.getElementById('prog-current').style.width = currentPercent + '%';
    
    // Power Display
    document.getElementById('val-power').textContent = data.power.toFixed(1);
    const powerPercent = Math.min((data.power / 3000) * 100, 100);
    document.getElementById('prog-power').style.width = powerPercent + '%';
    
    // Energy Display
    document.getElementById('val-energy').textContent = data.energy.toFixed(5);
    
    // Cost Display
    document.getElementById('val-cost').textContent = data.cost.toFixed(2);
    
    // Relay Status Display
    const relayText = document.getElementById('val-relay-text');
    const relayCard = document.getElementById('card-relay');
    const relayIcon = document.getElementById('relay-status-icon');
    const btnResetRelay = document.getElementById('btn-reset-relay');
    
    if (data.relay_state) {
        relayText.textContent = 'CLOSED';
        relayCard.classList.remove('state-warning');
        relayCard.classList.add('state-ok');
        relayIcon.classList.remove('color-danger');
        relayIcon.classList.add('color-relay');
        btnResetRelay.disabled = true;
    } else {
        relayText.textContent = 'OPEN (TRIPPED)';
        relayCard.classList.remove('state-ok');
        relayCard.classList.add('state-warning');
        relayIcon.classList.remove('color-relay');
        relayIcon.classList.add('color-danger');
        btnResetRelay.disabled = false;
    }
    
    // System Status Badge Update
    const statusBadge = document.getElementById('status-badge');
    const statusText = document.getElementById('status-text');
    
    if (data.is_overloaded) {
        statusBadge.classList.remove('state-ok');
        statusBadge.classList.add('state-warning');
        statusText.textContent = 'OVERLOAD CONDITION';
        showAlarmBanner(true);
    } else {
        statusBadge.classList.remove('state-warning');
        statusBadge.classList.add('state-ok');
        statusText.textContent = 'SYSTEM NORMAL';
        showAlarmBanner(false);
    }
}

// ===== Update Live Chart =====
function updateChart(data) {
    if (!realtimeChart) return;
    
    // Keep last 60 timestamps
    const now = new Date();
    const timeStr = now.toLocaleTimeString('en-US', { hour12: false });
    
    chartLabels.push(timeStr);
    chartPowerData.push(data.power);
    chartCurrentData.push(data.current);
    
    // Trim to latest N points
    if (chartLabels.length > chartDataPoints) {
        chartLabels.shift();
        chartPowerData.shift();
        chartCurrentData.shift();
    }
    
    realtimeChart.data.labels = chartLabels;
    realtimeChart.data.datasets[0].data = chartPowerData;
    realtimeChart.data.datasets[1].data = chartCurrentData;
    realtimeChart.update('none'); // Update without animation
}

// ===== Update Appliance Status Display =====
function updateAppliances(data) {
    if (!data.appliances) return;
    
    for (const [appName, appState] of Object.entries(data.appliances)) {
        const switchId = `switch-${appName.toLowerCase().replace(/\s+/g, '-')}`;
        const checkbox = document.getElementById(switchId);
        
        if (checkbox) {
            checkbox.checked = appState.is_on;
        }
    }
}

// ===== Update Alert Log =====
function updateAlerts(data) {
    if (!data.alerts || data.alerts.length === 0) return;
    
    const alertList = document.getElementById('alert-list');
    
    // Add only the latest new alert
    const latestAlert = data.alerts[data.alerts.length - 1];
    
    // Check if alert already displayed (by timestamp)
    const existingAlerts = alertList.querySelectorAll('.alert-item');
    const lastDisplayedTimestamp = existingAlerts.length > 0 
        ? existingAlerts[0].querySelector('.alert-time').textContent 
        : null;
    
    if (lastDisplayedTimestamp === latestAlert.timestamp) return; // Already displayed
    
    // Create new alert element
    const alertEl = document.createElement('div');
    alertEl.className = `alert-item alert-${latestAlert.type.toLowerCase()}`;
    
    const badgeClass = {
        'Danger': 'bg-danger',
        'Warning': 'bg-warning',
        'Success': 'bg-success',
        'Info': 'bg-info'
    }[latestAlert.type] || 'bg-info';
    
    alertEl.innerHTML = `
        <span class="alert-time">${latestAlert.timestamp}</span>
        <span class="alert-badge ${badgeClass}">${latestAlert.type}</span>
        <span class="alert-text">${latestAlert.message}</span>
    `;
    
    alertList.insertBefore(alertEl, alertList.firstChild);
    
    // Keep only last 20 alerts
    while (alertList.children.length > 20) {
        alertList.removeChild(alertList.lastChild);
    }
}

// ===== Appliance Control Handlers =====
function attachEventListeners() {
    // Appliance Toggle Switches
    document.querySelectorAll('.appliance-item input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', async function() {
            const applianceName = this.closest('.appliance-item')
                .querySelector('.app-name').textContent;
            
            try {
                const response = await fetch(`/api/appliance/${applianceName}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ state: this.checked })
                });
                
                if (!response.ok) {
                    console.error('Failed to toggle appliance');
                    this.checked = !this.checked; // Revert
                }
            } catch (error) {
                console.error('Appliance control error:', error);
                this.checked = !this.checked; // Revert
            }
        });
    });
    
    // Overload Trigger Demo Button
    document.getElementById('btn-trigger-overload')?.addEventListener('click', async () => {
        const ac = document.getElementById('switch-ac');
        const microwave = document.getElementById('switch-microwave');
        
        // Turn on all high-power devices
        ac.click();
        microwave.click();
        
        console.log('Overload scenario triggered: AC + Microwave ON');
    });
    
    // Reset Relay Button
    document.getElementById('btn-reset-relay')?.addEventListener('click', async () => {
        try {
            const response = await fetch('/api/relay/reset', { method: 'POST' });
            const data = await response.json();
            console.log('Relay reset:', data.message);
        } catch (error) {
            console.error('Reset error:', error);
        }
    });
    
    // Manual Force Cutoff Button
    document.getElementById('btn-manual-trip')?.addEventListener('click', async () => {
        if (confirm('Are you sure you want to manually cut power?')) {
            try {
                await fetch('/api/relay/manual-trip', { method: 'POST' });
                console.log('Relay manually tripped');
            } catch (error) {
                console.error('Trip error:', error);
            }
        }
    });
    
    // Clear Data Button
    document.getElementById('btn-reset-energy')?.addEventListener('click', async () => {
        if (confirm('Clear all accumulated energy data? This cannot be undone.')) {
            try {
                const response = await fetch('/api/data/reset', { method: 'POST' });
                const data = await response.json();
                console.log('Data reset:', data.message);
            } catch (error) {
                console.error('Reset error:', error);
            }
        }
    });
    
    // PDF Download Button
    document.getElementById('btn-pdf-download')?.addEventListener('click', async () => {
        try {
            const response = await fetch('/api/report');
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'energy_report.pdf';
            a.click();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('PDF download error:', error);
            alert('Failed to download PDF report');
        }
    });
    
    // Clear Alerts Button
    document.getElementById('btn-clear-alerts')?.addEventListener('click', () => {
        const alertList = document.getElementById('alert-list');
        // Keep only the first placeholder alert
        while (alertList.children.length > 1) {
            alertList.removeChild(alertList.lastChild);
        }
    });
    
    // Banner Reset Button
    document.getElementById('btn-banner-reset')?.addEventListener('click', async () => {
        try {
            await fetch('/api/relay/reset', { method: 'POST' });
            showAlarmBanner(false);
        } catch (error) {
            console.error('Banner reset error:', error);
        }
    });
}

// ===== Alarm Banner Control =====
function showAlarmBanner(show) {
    const banner = document.getElementById('alarm-banner');
    if (!banner) return;
    
    if (show) {
        banner.classList.remove('hidden');
        playAlarmSound();
    } else {
        banner.classList.add('hidden');
    }
}

// ===== Virtual Buzzer Sound =====
function playAlarmSound() {
    const beep = document.getElementById('beep-sound');
    if (beep) {
        beep.currentTime = 0;
        beep.play().catch(e => console.log('Audio playback prevented:', e));
    }
}

// ===== Update Time Display =====
function updateTimeDisplay() {
    const timeDisplay = document.getElementById('time-display');
    if (timeDisplay) {
        const now = new Date();
        timeDisplay.textContent = now.toLocaleTimeString('en-US', { 
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }
}

// ===== Utility: Format Numbers with Units =====
function formatMetric(value, unit, decimals = 2) {
    return parseFloat(value).toFixed(decimals) + ' ' + unit;
}

console.log('Dashboard JavaScript loaded successfully');
