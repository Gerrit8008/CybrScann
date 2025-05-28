# Running the Fixed Security Scanner

This document provides instructions for running and testing the fixed security scanner.

## Option 1: Running via the Web Interface

1. Start the Flask application:
   ```bash
   python app.py
   ```

2. Access the fixed scanner at:
   ```
   http://localhost:5000/fixed-scan
   ```

3. Enter the following information:
   - **Name**: Test User
   - **Email**: test@example.com
   - **Company**: Test Company
   - **Website to Scan**: example.com (or any domain you want to scan)

4. Select the scan options you want to enable:
   - Network Security
   - Web Security
   - Email Security
   - SSL/TLS Security

5. Click "Start Security Scan" and watch the real-time progress

6. When the scan completes, click "View Detailed Report" to see the comprehensive results

## Option 2: Running via Command Line Test Script

For quick testing without starting the web application, use the included test script:

```bash
python run_fixed_scan_test.py example.com
```

This will:
1. Run a comprehensive scan against example.com
2. Display real-time progress in the console
3. Save the complete results to a JSON file in the scan_results directory
4. Print a summary of the key findings

You can specify a different domain as an argument:

```bash
python run_fixed_scan_test.py yourdomain.com
```

## Option 3: Running via Python Code

You can also run the scanner programmatically from your own Python code:

```python
from fixed_scan_core import run_fixed_scan

# Define client information
client_info = {
    'name': 'Test User',
    'email': 'test@example.com',
    'company': 'Test Company',
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124'
}

# Progress callback for real-time updates
def progress_callback(data):
    print(f"Progress: {data['progress']}% - {data['task']}")

# Run the scan
results = run_fixed_scan(
    target_domain="example.com",
    client_info=client_info,
    scan_options={
        'network_scan': True,
        'web_scan': True,
        'email_scan': True,
        'ssl_scan': True
    },
    progress_callback=progress_callback
)

# Process the results
print(f"Scan completed with risk level: {results['risk_assessment']['risk_level']}")
print(f"Overall score: {results['risk_assessment']['overall_score']}/100")
```

## Option 4: Integration with Existing Application

To integrate the fixed scanner with your existing application:

```python
from integrate_fixed_scan import integrate_fixed_scan

# Get the updated Flask app with fixed scanner integrated
app = integrate_fixed_scan()

# Run the app
app.run(host='0.0.0.0', port=5000)
```

## Verifying All Scan Types Are Working

To verify that all scan types are working properly, check the following sections in the scan results:

1. **Client Information**
   - Verify OS and browser detection is working
   - Check that target domain is displayed

2. **Network Security**
   - Verify open ports are listed with severity
   - Check gateway information is displayed

3. **Web Security**
   - Verify SSL certificate information is displayed
   - Check security headers analysis
   - Verify sensitive content findings

4. **Email Security**
   - Verify SPF, DKIM, and DMARC findings
   - Check email security recommendations

5. **System Security**
   - Verify OS updates and firewall status
   - Check technology stack detection

6. **Service Categories**
   - Verify all findings are properly categorized
   - Check that risk levels are appropriate

## Troubleshooting

If any scan types are not working properly:

1. Check the logs for error messages
2. Verify that the target domain is accessible
3. Ensure all required Python packages are installed
4. Check for any network restrictions that might prevent scanning

For web interface issues:

1. Check the browser console for JavaScript errors
2. Verify that the fixed scan blueprint is registered in app.py
3. Ensure the template is being loaded correctly