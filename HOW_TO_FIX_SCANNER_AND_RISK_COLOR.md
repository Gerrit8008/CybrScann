# How to Fix Scanner Names and Risk Assessment Color Issues

This document explains how to fix two critical issues with the CybrScan platform:

1. Scanner names being created with "client 6" prefix
2. Risk assessment scores always showing as 75 with a gray circle instead of colored according to the actual score

## The Solution: direct_fix.py

We've created a comprehensive fix script that addresses both issues. The script:

1. Fixes the risk assessment color calculation and display in reports
2. Removes "client 6" prefixes from scanner names in all databases
3. Patches the scanner creation function to prevent future issues
4. Updates existing scan results in databases to include proper color information
5. Modifies templates to ensure risk assessment colors are displayed properly

## How to Apply the Fix

1. Make sure your application server is running
2. Open a terminal window
3. Navigate to your CybrScan installation directory:
   ```
   cd /home/ggrun/CybrScan_1
   ```
4. Run the direct fix script:
   ```
   python3 direct_fix.py
   ```
5. Restart your application server to apply all changes:
   ```
   # If using a systemd service:
   sudo systemctl restart cybrscan.service
   
   # If running manually with flask:
   # First, stop the current process (Ctrl+C)
   # Then start it again:
   python3 app.py
   ```

## What the Fix Does

### 1. Risk Assessment Color Fix

- Adds proper color calculation based on security score
- Modifies templates to use the correct color values
- Updates existing scan results to include color information
- Ensures new scan results have correct risk assessment colors

### 2. Scanner Name Fix

- Removes "client 6" prefix from all existing scanner names
- Fixes scanner creation to prevent adding "client 6" prefix to new scanners
- Updates scan results to use correct scanner names

## Verification

After applying the fix and restarting the server:

1. Check existing scanners - they should no longer have "client 6" in their names
2. Run a new scan - the risk assessment score should be displayed with an appropriate color (not gray)
3. Create a new scanner - it should be created without the "client 6" prefix

## Technical Details

The fix works by:

1. Monkey patching the client.report_view function to ensure risk assessment includes color information
2. Updating database records directly to fix scanner names and client IDs
3. Patching the client.scanner_create function to prevent future issues
4. Modifying templates to use the risk assessment color information

If you experience any issues after applying the fix, please contact technical support.