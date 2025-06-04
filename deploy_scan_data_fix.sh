#!/bin/bash
# Deploy script for the scan data processing fix

set -e  # Exit on error

echo "=== Deploying Scan Data Processing Fix ==="
echo

# 1. Run the fix script
echo "Applying fixes to scan data processing..."
python3 fix_scan_data_processor.py

# 2. Run the test script
echo
echo "Running tests to verify the changes..."
python3 test_scan_data_processing.py

# 3. Create a backup of the original files
echo
echo "Creating backup of original files..."
cp client_db.py client_db.py.pre_scan_data_fix
cp client.py client.py.pre_scan_data_fix
echo "Backups created: client_db.py.pre_scan_data_fix, client.py.pre_scan_data_fix"

echo
echo "=== Deployment Complete ==="
echo "The scan data processing fix has been successfully applied."
echo "Port scan results and OS information should now display correctly in reports."
echo
echo "To make the changes effective, please restart the application server:"
echo "  ./run_server.sh"
echo
echo "If you encounter any issues, you can restore the original files from the backups:"
echo "  cp client_db.py.pre_scan_data_fix client_db.py"
echo "  cp client.py.pre_scan_data_fix client.py"