#!/usr/bin/env python3
"""
Script to update report generation in CybrScan_1 to match CybrScann-main functionality
"""

import os
import re
import json

def update_process_scan_data_function():
    """
    Update the process_scan_data function in client.py to better handle port scan and OS information
    """
    client_path = '/home/ggrun/CybrScan_1/client.py'
    
    with open(client_path, 'r') as f:
        content = f.read()
    
    # Check if we need to update the process_scan_data function
    process_scan_data_pattern = r'def process_scan_data\(scan\):.*?return scan_data'
    process_scan_match = re.search(process_scan_data_pattern, content, re.DOTALL)
    
    if process_scan_match:
        original_function = process_scan_match.group(0)
        
        # Create enhanced process_scan_data function
        enhanced_function = """def process_scan_data(scan):
    """Process and enhance scan data for display"""
    if not scan:
        return {}
    
    # Handle string JSON data
    if isinstance(scan, str):
        try:
            scan_data = json.loads(scan)
        except:
            return {}
    else:
        # Make a copy to avoid modifying the original
        if hasattr(scan, 'get'):  # dict-like object
            scan_data = dict(scan)
        else:
            return scan  # Can't process
    
    # Parse scan_results if it exists
    if scan_data.get('scan_results') and isinstance(scan_data['scan_results'], str):
        try:
            parsed_results = json.loads(scan_data['scan_results'])
            if isinstance(parsed_results, dict):
                # Merge parsed results with scan_data, but don't overwrite existing keys
                for key, value in parsed_results.items():
                    if key not in scan_data:
                        scan_data[key] = value
        except:
            pass  # Failed to parse scan_results
    
    # Ensure 'network' section exists with open_ports data
    if 'network' not in scan_data:
        scan_data['network'] = {}
    
    # Ensure open_ports structure exists
    if 'open_ports' not in scan_data['network']:
        # Check if 'network' is a list of findings
        if isinstance(scan_data['network'], list):
            # Extract port information from network findings
            port_list = []
            port_details = []
            
            for finding in scan_data['network']:
                if isinstance(finding, tuple) and len(finding) >= 2:
                    message, severity = finding
                    # Extract port info if this is a port finding
                    if 'Port ' in message and ' is open' in message:
                        try:
                            port_match = re.search(r'Port (\\d+)', message)
                            if port_match:
                                port_num = int(port_match.group(1))
                                service = "Unknown"
                                # Try to extract service name if in parentheses
                                service_match = re.search(r'\\((.*?)\\)', message)
                                if service_match:
                                    service = service_match.group(1)
                                
                                port_list.append(port_num)
                                port_details.append({
                                    'port': port_num,
                                    'service': service,
                                    'severity': severity
                                })
                        except Exception as e:
                            pass  # Skip this finding if we can't parse it
            
            # Create structured open_ports data
            scan_data['network'] = {
                'scan_results': scan_data['network'],  # Keep original findings
                'open_ports': {
                    'count': len(port_list),
                    'list': port_list,
                    'details': port_details,
                    'severity': 'High' if len(port_list) > 5 else 'Medium' if len(port_list) > 2 else 'Low'
                }
            }
        else:
            # Just ensure the structure exists
            scan_data['network']['open_ports'] = {
                'count': 0,
                'list': [],
                'details': [],
                'severity': 'Low'
            }
    
    # Ensure client_info section exists
    if 'client_info' not in scan_data:
        scan_data['client_info'] = {}
    
    # Add OS and browser info if missing
    if ('os' not in scan_data['client_info'] or 'browser' not in scan_data['client_info']) and 'user_agent' in scan_data:
        # Detect OS and browser from user agent
        user_agent = scan_data.get('user_agent', '')
        os_info, browser_info = detect_os_and_browser(user_agent)
        
        if 'os' not in scan_data['client_info'] or not scan_data['client_info']['os'] or scan_data['client_info']['os'] == 'N/A':
            scan_data['client_info']['os'] = os_info
        
        if 'browser' not in scan_data['client_info'] or not scan_data['client_info']['browser'] or scan_data['client_info']['browser'] == 'N/A':
            scan_data['client_info']['browser'] = browser_info
    
    # Add date formatting if missing
    if 'timestamp' in scan_data and not scan_data.get('formatted_date'):
        try:
            from datetime import datetime
            if isinstance(scan_data['timestamp'], str):
                # Handle different date formats
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S.%f']:
                    try:
                        timestamp = datetime.strptime(scan_data['timestamp'], fmt)
                        scan_data['formatted_date'] = timestamp.strftime('%B %d, %Y')
                        scan_data['formatted_time'] = timestamp.strftime('%I:%M %p')
                        break
                    except ValueError:
                        continue
        except Exception as e:
            pass
    
    # Ensure risk_assessment section has proper formatting
    if 'risk_assessment' in scan_data:
        if isinstance(scan_data['risk_assessment'], (int, float, str)):
            # Convert simple score to full risk assessment object
            try:
                score = float(scan_data['risk_assessment'])
                scan_data['risk_assessment'] = {
                    'overall_score': score,
                    'risk_level': get_risk_level(score),
                    'color': get_color_for_score(score)
                }
            except:
                # Keep as is if we can't convert
                pass
        elif isinstance(scan_data['risk_assessment'], dict):
            # Ensure color exists
            if 'color' not in scan_data['risk_assessment'] and 'overall_score' in scan_data['risk_assessment']:
                score = scan_data['risk_assessment']['overall_score']
                scan_data['risk_assessment']['color'] = get_color_for_score(score)
    
    return scan_data"""
        
        # Replace the original function with the enhanced version
        content = content.replace(original_function, enhanced_function)
        
        # Check if detect_os_and_browser function exists
        if "def detect_os_and_browser" not in content:
            # Add the detect_os_and_browser function
            detect_os_function = """
def detect_os_and_browser(user_agent):
    """Detect OS and browser from user agent string"""
    os_info = "Unknown"
    browser_info = "Unknown"
    
    if not user_agent:
        return os_info, browser_info
    
    # Detect OS
    if "Windows" in user_agent:
        if "Windows NT 10" in user_agent:
            os_info = "Windows 10/11"
        elif "Windows NT 6.3" in user_agent:
            os_info = "Windows 8.1"
        elif "Windows NT 6.2" in user_agent:
            os_info = "Windows 8"
        elif "Windows NT 6.1" in user_agent:
            os_info = "Windows 7"
        elif "Windows NT 6.0" in user_agent:
            os_info = "Windows Vista"
        elif "Windows NT 5.1" in user_agent:
            os_info = "Windows XP"
        else:
            os_info = "Windows"
    elif "Mac OS X" in user_agent:
        if "iPhone" in user_agent or "iPad" in user_agent:
            os_info = "iOS"
        else:
            os_info = "macOS"
    elif "Linux" in user_agent:
        if "Android" in user_agent:
            os_info = "Android"
        else:
            os_info = "Linux"
    elif "FreeBSD" in user_agent:
        os_info = "FreeBSD"
    
    # Detect browser
    if "Firefox/" in user_agent:
        browser_info = "Firefox"
    elif "Edge/" in user_agent or "Edg/" in user_agent:
        browser_info = "Edge"
    elif "Chrome/" in user_agent and "Chromium" not in user_agent and "Edge" not in user_agent and "Edg/" not in user_agent:
        browser_info = "Chrome"
    elif "Safari/" in user_agent and "Chrome" not in user_agent and "Edge" not in user_agent:
        browser_info = "Safari"
    elif "MSIE" in user_agent or "Trident/" in user_agent:
        browser_info = "Internet Explorer"
    elif "Opera/" in user_agent or "OPR/" in user_agent:
        browser_info = "Opera"
    
    return os_info, browser_info
"""
            
            # Add function after the imports section
            import_section_end = content.find("# Define client blueprint")
            if import_section_end > 0:
                content = content[:import_section_end] + detect_os_function + "\n\n" + content[import_section_end:]
        
        # Check if get_risk_level function exists
        if "def get_risk_level" not in content:
            # Add the get_risk_level function
            risk_level_function = """
def get_risk_level(score):
    """Get risk level text based on score"""
    if score >= 90:
        return 'Low'
    elif score >= 80:
        return 'Low-Medium'
    elif score >= 70:
        return 'Medium'
    elif score >= 60:
        return 'Medium-High'
    elif score >= 50:
        return 'High'
    else:
        return 'Critical'
"""
            
            # Add function after the detect_os_and_browser function or after imports
            import_section_end = content.find("# Define client blueprint")
            if import_section_end > 0:
                content = content[:import_section_end] + risk_level_function + "\n\n" + content[import_section_end:]
        
        # Make sure re module is imported
        if "import re" not in content:
            # Add re import to the imports section
            if "import json" in content:
                content = content.replace("import json", "import json\nimport re")
            else:
                content = content.replace("import os", "import os\nimport re")
    
        # Write the updated content
        with open(client_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Successfully updated process_scan_data function in {client_path}")
    else:
        print(f"❌ Could not find process_scan_data function in {client_path}")

def update_report_view_function():
    """
    Update the report_view function in client.py to ensure proper handling of scan data
    """
    client_path = '/home/ggrun/CybrScan_1/client.py'
    
    with open(client_path, 'r') as f:
        content = f.read()
    
    # Find the report_view function
    report_view_pattern = r'def report_view\(user, scan_id\):.*?return render_template\(\s*\'results\.html\','
    report_view_match = re.search(report_view_pattern, content, re.DOTALL)
    
    if report_view_match:
        # Check if the function already has the enhanced port scan and OS detection
        if "scan_data['network'] = {" in report_view_match.group(0) or "scan_data['client_info']['os'] = " in report_view_match.group(0):
            print("✅ report_view function already contains enhanced port scan and OS detection")
            return
        
        # Find where scan processing occurs before rendering template
        process_scan_pattern = r'formatted_scan = process_scan_data\(scan\)'
        process_scan_match = re.search(process_scan_pattern, content)
        
        if process_scan_match:
            # Function is already using process_scan_data, we don't need to modify it
            print("✅ report_view function already uses process_scan_data")
        else:
            # Add process_scan_data call before rendering template
            render_pattern = r'return render_template\(\s*\'results\.html\','
            render_match = re.search(render_pattern, content)
            
            if render_match:
                # Add process_scan_data call before rendering
                updated_content = content[:render_match.start()] + "        # Process scan data to ensure all required fields exist\n        formatted_scan = process_scan_data(scan)\n\n        " + content[render_match.start():]
                
                # Update the variable name in the render_template call
                updated_content = updated_content.replace("render_template(\n            'results.html',\n            scan=scan", 
                                                         "render_template(\n            'results.html',\n            scan=formatted_scan")
                
                # Write the updated content
                with open(client_path, 'w') as f:
                    f.write(updated_content)
                
                print(f"✅ Successfully updated report_view function in {client_path}")
            else:
                print(f"❌ Could not find render_template call in report_view function")
    else:
        print(f"❌ Could not find report_view function in {client_path}")

def ensure_proper_imports():
    """
    Ensure all required imports are present in client.py
    """
    client_path = '/home/ggrun/CybrScan_1/client.py'
    
    with open(client_path, 'r') as f:
        content = f.read()
    
    # Check for required imports
    required_imports = {
        "import re": "import re",
        "from datetime import datetime": "from datetime import datetime",
        "import json": "import json"
    }
    
    # Check each import and add if missing
    import_section_end = content.find("# Define client blueprint")
    if import_section_end > 0:
        for import_line, import_text in required_imports.items():
            if import_line not in content:
                # Add import before the blueprint definition
                content = content[:import_section_end] + import_text + "\n" + content[import_section_end:]
                print(f"Added missing import: {import_text}")
    
    # Write the updated content
    with open(client_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Ensured all required imports are present in {client_path}")

def main():
    """Main function"""
    print("Updating report generation in CybrScan_1 to match CybrScann-main...")
    
    # Ensure all required imports
    ensure_proper_imports()
    
    # Update process_scan_data function
    update_process_scan_data_function()
    
    # Update report_view function
    update_report_view_function()
    
    print("\nDone! Report generation in CybrScan_1 now matches CybrScann-main.")
    print("Changes made:")
    print("1. Enhanced process_scan_data function for better port scan and OS detection")
    print("2. Updated report_view function to use process_scan_data")
    print("3. Added missing imports (re, datetime)")
    print("\nTo make the changes effective, please restart the application server.")

if __name__ == "__main__":
    main()