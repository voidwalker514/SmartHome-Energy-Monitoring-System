#!/bin/bash
# Smart Home Energy Monitoring System - Quick Start Script (Linux/Mac)
# This script sets up and runs the entire project

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   Smart Home Energy Monitoring System - Quick Start            ║"
echo "║   Python 3.8+ Required                                         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found! Please install Python 3.8 or higher."
    echo "   Install via: apt-get install python3 (Ubuntu/Debian) or brew install python3 (Mac)"
    exit 1
fi

echo "✅ Python detected: $(python3 --version)"
echo ""

# Check if requirements are already installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 Installing dependencies from requirements.txt..."
    python3 -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    echo "✅ Dependencies installed successfully"
else
    echo "✅ Dependencies already installed"
fi

echo ""
echo "📁 Creating necessary directories..."
mkdir -p data
mkdir -p outputs
echo "✅ Directories ready"

echo ""
echo "🚀 Starting Flask server..."
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "  Dashboard will be available at: http://localhost:5000"
echo "  "
echo "  Press Ctrl+C to stop the server"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

python3 app.py
