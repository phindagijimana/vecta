#!/bin/bash
# Vecta AI Startup Script

echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║                      Vecta AI - Startup Script                         ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Flask is installed
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Flask is not installed"
    echo ""
    echo "Please install dependencies first:"
    echo "  pip3 install --user flask flask-cors pandas numpy"
    echo ""
    echo "OR install all requirements:"
    echo "  pip3 install --user -r requirements.txt"
    echo ""
    exit 1
fi

echo "✅ Dependencies found"
echo ""
echo "Starting Vecta AI application..."
echo ""
echo "Once started, access at:"
echo "  Main App:   http://localhost:8080"
echo "  Validator:  http://localhost:8080/validate"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo ""

# Start the app
python3 app.py
