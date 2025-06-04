#!/usr/bin/env python3
"""
Scanner Data Processor - Enhanced functions for processing scan data

This module contains functions for processing and enhancing scan data 
for display, including port scan results and OS detection. These functions 
ensure that scan reports display all relevant information correctly.
"""

import re
import json
import logging
from datetime import datetime

def process_scan_data(scan):
    """
    Process and enhance scan data for display
    
    This function takes raw scan data and enhances it with:
    1. Port scan results extraction and formatting
    2. OS and browser detection from user agent
    3. Risk assessment score and color calculation
    4. Date formatting and statistics calculation
    
    Args:
        scan: The raw scan data, can be dict, string, or other format
        
    Returns:
        dict: Enhanced scan data ready for display
    """
    if not scan:
        return {}
    
    # Handle string JSON data
    if isinstance(scan, str):
        try:
            scan_data = json.loads(scan)
        except Exception as e:
            logging.error(f"Error parsing scan JSON string: {e}")
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
        except Exception as e:
            logging.error(f"Error parsing scan_results JSON: {e}")
    
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
                            logging.error(f"Error parsing port finding: {e}")
            
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
            except Exception as e:
                logging.error(f"Error converting risk assessment score: {e}")
        elif isinstance(scan_data['risk_assessment'], dict):
            # Ensure color exists
            if 'color' not in scan_data['risk_assessment'] and 'overall_score' in scan_data['risk_assessment']:
                score = scan_data['risk_assessment']['overall_score']
                scan_data['risk_assessment']['color'] = get_color_for_score(score)
    
    # Format risk levels for client-friendly display (from CybrScann-main)
    if 'risk_assessment' in scan_data:
        risk_level = scan_data['risk_assessment'].get('risk_level', 'Unknown')
        if risk_level.lower() == 'critical':
            scan_data['risk_color'] = 'danger'
        elif risk_level.lower() == 'high':
            scan_data['risk_color'] = 'warning'
        elif risk_level.lower() == 'medium':
            scan_data['risk_color'] = 'info'
        else:
            scan_data['risk_color'] = 'success'
    
    # Format dates for display (from CybrScann-main)
    if 'timestamp' in scan_data:
        try:
            dt = datetime.fromisoformat(scan_data['timestamp'])
            scan_data['formatted_date'] = dt.strftime('%B %d, %Y at %I:%M %p')
        except Exception as e:
            logging.error(f"Error formatting timestamp: {e}")
    
    # Add summary statistics (from CybrScann-main)
    if 'risk_assessment' in scan_data:
        risk_assessment = scan_data['risk_assessment']
        scan_data['total_issues'] = (
            risk_assessment.get('critical_issues', 0) +
            risk_assessment.get('high_issues', 0) +
            risk_assessment.get('medium_issues', 0) +
            risk_assessment.get('low_issues', 0)
        )
    
    return scan_data

def detect_os_and_browser(user_agent):
    """
    Detect operating system and browser from user agent string
    
    Args:
        user_agent: The browser user agent string
        
    Returns:
        tuple: (os_info, browser_info)
    """
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
    """
    Get risk level text based on score
    
    Args:
        score: The numerical risk score (0-100)
        
    Returns:
        str: Risk level description
    """
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

def get_color_for_score(score):
    """
    Get appropriate color code based on risk score
    
    Args:
        score: The numerical risk score (0-100)
        
    Returns:
        str: Hex color code
    """
    if score >= 90:
        return '#28a745'  # green
    elif score >= 80:
        return '#5cb85c'  # light green
    elif score >= 70:
        return '#17a2b8'  # info blue
    elif score >= 60:
        return '#ffc107'  # warning yellow
    elif score >= 50:
        return '#fd7e14'  # orange
    else:
        return '#dc3545'  # red

def enhance_report_view(scan):
    """
    Enhance scan data specifically for report view
    
    This function builds on process_scan_data but adds additional
    processing specifically needed for the report view template.
    
    Args:
        scan: The raw scan data
        
    Returns:
        dict: Fully enhanced scan data ready for report template
    """
    # First apply standard processing
    formatted_scan = process_scan_data(scan)
    
    # If we still don't have client_info, add it while preserving existing data
    if not formatted_scan.get('client_info'):
        # Add missing client_info structure
        formatted_scan['client_info'] = {
            'name': scan.get('lead_name', formatted_scan.get('name', 'N/A')),
            'email': scan.get('lead_email', formatted_scan.get('email', 'N/A')),
            'company': scan.get('lead_company', formatted_scan.get('company', 'N/A')),
            'phone': scan.get('lead_phone', 'N/A'),
            'os': scan.get('user_agent', 'N/A'),
            'browser': scan.get('user_agent', 'N/A')
        }
    
    # Ensure risk_assessment has required structure for template
    if not formatted_scan.get('risk_assessment') or not isinstance(formatted_scan.get('risk_assessment'), dict):
        formatted_scan['risk_assessment'] = {
            'overall_score': scan.get('security_score', 75),
            'risk_level': scan.get('risk_level', 'Medium'),
            'color': get_color_for_score(scan.get('security_score', 75)),
            'critical_issues': 0,
            'high_issues': 1,
            'medium_issues': 1,
            'low_issues': 1
        }
    
    # If parsed_results exists and has comprehensive data, use it
    if scan and scan.get('parsed_results') and scan['parsed_results'].get('findings'):
        # Merge the parsed results with our formatted data
        for key, value in scan['parsed_results'].items():
            # Don't overwrite client_info and risk_assessment we've already carefully prepared
            if key not in ['client_info', 'risk_assessment']:
                formatted_scan[key] = value
    
    return formatted_scan