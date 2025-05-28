# How to Fix Display Issues in Scan Results

This document provides instructions for fixing the display issues in scan results where certain sections are not showing up:

- Operating System and Browser not displayed
- Network Security scan results not displayed
- Web Security not displayed
- System Security not displayed
- Service Category Analysis not displayed
- Access Management results not displayed

## Immediate Fix

To immediately fix an existing scan result, follow these steps:

1. Run the emergency fix script for the specific client and scan:

```bash
python emergency_display_fix.py 5 scan_4a28b22e985e
```

Replace `5` with your client ID and `scan_4a28b22e985e` with your scan ID.

2. If you don't know the scan ID, you can fix the latest scan for a client:

```bash
python emergency_display_fix.py 5
```

3. After running the fix, reload the scan results page in your browser.

## Permanent Fix

For a permanent fix that ensures all future scans display properly:

1. Apply the template fixes:

```bash
python fix_scan_template_display.py
```

2. Update the app to use the patched scan routes:

```bash
python update_to_patched_scan.py
```

3. Apply the direct patch to scan.py:

```bash
python -c "import direct_patch_scan"
```

4. Restart the application server.

## Verifying the Fix

After applying the fixes, you should verify that:

1. Client OS and browser information are displayed correctly
2. Network Security section shows port scan results
3. Web Security section shows SSL certificate and security headers
4. System Security section shows OS updates and firewall status
5. Service Category Analysis section displays all service categories
6. Access Management results are properly displayed

## Troubleshooting

If you still experience issues after applying the fixes:

1. Check the application logs for errors
2. Make sure all the necessary templates exist
3. Verify that the database contains the properly formatted scan results:

```bash
python -c "import sqlite3; conn = sqlite3.connect('client_5_scans.db'); conn.row_factory = sqlite3.Row; cursor = conn.cursor(); cursor.execute('SELECT scan_id, results FROM scans ORDER BY timestamp DESC LIMIT 1'); scan = cursor.fetchone(); import json; results = json.loads(scan['results']); print(f\"Client OS: {results.get('client_info', {}).get('os')}\"); print(f\"Network: {results.get('network', {}).keys()}\"); print(f\"Service Categories: {results.get('service_categories', {}).keys()}\")"
```

## Background on the Fix

The fix works by:

1. Ensuring all necessary fields exist in the scan results
2. Properly formatting network scan results for display
3. Adding missing sections like system security and service categories
4. Ensuring client OS and browser information is available
5. Patching the scan routes to ensure proper results formatting

The permanent fix modifies how scan results are processed and stored to ensure all sections are properly displayed in the results template.