# Scan Report Architecture

This document explains how scan reports are processed, enhanced, and displayed in the CybrScann platform.

## Overview

The scan report system transforms raw scan data into comprehensive, client-friendly reports. The process involves several key components:

1. **Data Collection**: Raw scan data is collected during scanning operations
2. **Data Processing**: Raw data is enhanced with additional derived information
3. **Data Storage**: Processed data is stored in the database
4. **Report Generation**: Data is retrieved and formatted for display
5. **Report Display**: Rendered as HTML for viewing by clients

## Key Components

### 1. Scanner Data Processor (`scanner/data_processor.py`)

The core of the scan report system is the `scanner/data_processor.py` module, which contains:

- `process_scan_data(scan)`: Transforms raw scan data into a structured format
- `enhance_report_view(scan)`: Further enhances scan data specifically for report display
- Helper functions:
  - `detect_os_and_browser(user_agent)`: Extracts OS and browser info from user agent
  - `get_risk_level(score)`: Converts numeric scores to text risk levels
  - `get_color_for_score(score)`: Determines color coding based on risk score

### 2. Report View Function (`client.py`)

The `report_view` function in `client.py` handles:
- Retrieving scan data from the database
- Applying the data processing enhancements
- Fetching scanner branding information
- Rendering the report template

### 3. Report Template (`templates/results.html`)

The HTML template that displays the scan report with:
- Overall risk score and visualization
- Client information section
- Network security findings (including port scan results)
- Web security findings
- Email security findings
- System security findings (including OS information)
- Recommendations section

## Data Flow

1. Client requests a report at `/reports/<scan_id>`
2. `report_view` function retrieves raw scan data
3. `enhance_report_view` processes and enhances the data
4. Processed data is passed to the `results.html` template
5. Template renders the data into a formatted HTML report

## Critical Data Structures

### Network Data Structure

```json
{
  "network": {
    "scan_results": [...],
    "open_ports": {
      "count": 3,
      "list": [80, 443, 22],
      "details": [
        {"port": 80, "service": "HTTP", "severity": "Medium"},
        {"port": 443, "service": "HTTPS", "severity": "Low"},
        {"port": 22, "service": "SSH", "severity": "High"}
      ],
      "severity": "Medium"
    }
  }
}
```

### Client Information Structure

```json
{
  "client_info": {
    "name": "John Doe",
    "email": "john@example.com",
    "company": "Example Corp",
    "phone": "555-123-4567",
    "os": "Windows 10/11",
    "browser": "Chrome"
  }
}
```

### Risk Assessment Structure

```json
{
  "risk_assessment": {
    "overall_score": 75,
    "risk_level": "Medium",
    "color": "#17a2b8",
    "critical_issues": 0,
    "high_issues": 1,
    "medium_issues": 2,
    "low_issues": 3
  }
}
```

## Maintaining Report Functionality

When making changes to the codebase, follow these guidelines to ensure report functionality is maintained:

### DO:

✅ Use the modular `scanner/data_processor.py` for all scan data processing  
✅ Run tests with `test_scan_processor.py` after any changes to verify functionality  
✅ Add new fields to the report by extending the data processor and template together  
✅ Document any changes to the data structures used in reports  

### DON'T:

❌ Modify the core processing functions without thorough testing  
❌ Change the structure of data expected by the report template  
❌ Remove fields from the processed data that the template requires  
❌ Bypass the data processing steps when displaying reports  

## Testing Report Functionality

To verify that report functionality is maintained:

1. Generate test scan data:
   ```python
   python -c "import json; print(json.dumps({
     'scan_id': 'test_scan',
     'timestamp': '2025-05-29 12:34:56',
     'network': [('Port 80 is open (HTTP)', 'Medium')],
     'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0',
     'risk_assessment': 75
   }))"
   ```

2. Process the data:
   ```python
   from scanner.data_processor import enhance_report_view
   processed_data = enhance_report_view(test_data)
   ```

3. Verify critical fields are present:
   ```python
   assert 'network' in processed_data
   assert 'open_ports' in processed_data['network']
   assert 'client_info' in processed_data
   assert 'os' in processed_data['client_info']
   assert 'risk_assessment' in processed_data
   ```

## Conclusion

The scan report system is a critical component of the CybrScann platform. By understanding its architecture and following these guidelines, you can maintain and extend report functionality while restructuring the codebase for better maintainability.