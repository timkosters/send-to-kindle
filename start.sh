#!/bin/bash

# Kindle Newsletter Web App - Quick Start Script

echo "🚀 Starting Kindle Newsletter Web App..."
echo ""

# Set Python path (adjust if your Python installation is different)
PYTHON_CMD="/Library/Frameworks/Python.framework/Versions/3.12/bin/python3"
PYTHONPATH="/Users/timourkosters/Library/Python/3.12/lib/python/site-packages"

# Check if Python path exists
if [ ! -f "$PYTHON_CMD" ]; then
    echo "❌ Python not found at $PYTHON_CMD"
    echo "💡 Update the PYTHON_CMD variable in this script"
    exit 1
fi

echo "📍 Using Python: $PYTHON_CMD"
echo "📍 Using packages: $PYTHONPATH"
echo ""

# Run the web app
export PYTHONPATH="$PYTHONPATH"
exec "$PYTHON_CMD" simple_web_app.py
