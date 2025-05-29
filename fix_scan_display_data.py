#\!/usr/bin/env python3
"""
Fix script to ensure port scan results and OS information are properly displayed in reports
"""

import os
import re
import json

def fix_client_report_processing():
    """
    Fix client.py to properly process and display port scan results and OS information
    """
    client_path = '/home/ggrun/CybrScan_1/client.py'
    
    if not os.path.exists(client_path):
        print(f"Error: {client_path} not found")
        return False
    
    # Read the client.py file
    with open(client_path, 'r') as f:
        content = f.read()
    
    # Add process_scan_data function if it doesn't exist
    if "def process_scan_data(" not in content:
        # Find where to insert the function - just before the client blueprint definition
        insert_point = content.find("# Define client blueprint")
        if insert_point == -1:
            insert_point = content.find("client_bp = Blueprint(")
        
        if insert_point > 0:
            process_scan_function = """
def process_scan_data(scan):
    '''Process and enhance scan data for display'''
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
                            port_match = re.search(r'Port (\d+)', message)
                            if port_match:
                                port_num = int(port_match.group(1))
                                service = "Unknown"
                                # Try to extract service name if in parentheses
                                service_match = re.search(r'\((.*?)\)', message)
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
        
        if 'os' not in scan_data['client_info'] or not scan_data['client_info']['os']:
            scan_data['client_info']['os'] = os_info
        
        if 'browser' not in scan_data['client_info'] or not scan_data['client_info']['browser']:
            scan_data['client_info']['browser'] = browser_info
    
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
    
    return scan_data

def detect_os_and_browser(user_agent):
    '''Detect OS and browser from user agent string'''
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

def get_risk_level(score):
    '''Get risk level text based on score'''
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
            
            # Insert the process_scan_data function at the appropriate point
            content = content[:insert_point] + process_scan_function + "\n\n" + content[insert_point:]
    
    # Write the modified file
    with open(client_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Successfully updated {client_path} to properly process scan data including ports and OS information")
    
    return True

def main():
    """Main function to apply fix"""
    print("Applying fix for client report processing to display port scan and OS data...")
    
    # Fix client report processing
    fix_client_report_processing()
    
    print("\nFix has been applied\!")
    print("To make the changes effective, please restart the application server.")

if __name__ == "__main__":
    main()
