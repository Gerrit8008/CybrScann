#!/bin/bash
# Script to run the application server

echo "Starting CybrScan server..."
echo "Applying fixes first..."

# Apply our fixes first
python3 fix_scan_display_data.py

# Try to start the server with various methods
if command -v gunicorn &> /dev/null; then
    echo "Using gunicorn to start server..."
    gunicorn -w 4 -b 0.0.0.0:5000 app:app
elif command -v python3 &> /dev/null; then
    echo "Using python3 to start server..."
    python3 app.py
else
    echo "No suitable method found to start the server."
    exit 1
fi