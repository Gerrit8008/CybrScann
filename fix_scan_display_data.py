#!/usr/bin/env python3
"""
Fix for scan report not displaying port scan results and operating system information
"""

import os
import sys
import json
import sqlite3
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_client_report_view():
    """
    Fix the client.py report_view function to ensure all scan data is properly formatted
    """
    client_path = '/home/ggrun/CybrScan_1/client.py'
    
    if not os.path.exists(client_path):
        logger.error(f"Client file not found: {client_path}")
        return False
    
    # Read the file
    with open(client_path, 'r') as f:
        content = f.read()
    
    # Create an improved client info processing function
    improved_client_info = """
        # Process the scan data to ensure all required fields are present
        def process_scan_data(scan_data):
            \"\"\"Ensure scan data has all required fields for display\"\"\"
            if not isinstance(scan_data, dict):
                return scan_data
                
            # Ensure client_info exists and has OS/browser information
            if 'client_info' not in scan_data or not isinstance(scan_data['client_info'], dict):
                # Create client_info if missing
                scan_data['client_info'] = {
                    'name': scan_data.get('lead_name', scan_data.get('name', 'N/A')),
                    'email': scan_data.get('lead_email', scan_data.get('email', 'N/A')),
                    'company': scan_data.get('lead_company', scan_data.get('company', 'N/A')),
                    'phone': scan_data.get('lead_phone', 'N/A'),
                    'os': 'Unknown',
                    'browser': 'Unknown'
                }
            
            # Extract OS and browser info from user_agent if available
            if scan_data.get('user_agent') and ('os' not in scan_data['client_info'] or scan_data['client_info']['os'] == 'N/A'):
                user_agent = scan_data.get('user_agent', '')
                # Extract OS info
                if 'Windows' in user_agent:
                    os_version = 'Windows'
                    if 'Windows NT 10' in user_agent:
                        os_version = 'Windows 10/11'
                    elif 'Windows NT 6.3' in user_agent:
                        os_version = 'Windows 8.1'
                    elif 'Windows NT 6.2' in user_agent:
                        os_version = 'Windows 8'
                    elif 'Windows NT 6.1' in user_agent:
                        os_version = 'Windows 7'
                    scan_data['client_info']['os'] = os_version
                elif 'Mac OS X' in user_agent:
                    scan_data['client_info']['os'] = 'macOS'
                elif 'Linux' in user_agent:
                    scan_data['client_info']['os'] = 'Linux'
                elif 'Android' in user_agent:
                    scan_data['client_info']['os'] = 'Android'
                elif 'iOS' in user_agent or 'iPhone' in user_agent or 'iPad' in user_agent:
                    scan_data['client_info']['os'] = 'iOS'
                
                # Extract browser info
                if 'Chrome' in user_agent and 'Chromium' not in user_agent:
                    scan_data['client_info']['browser'] = 'Chrome'
                elif 'Firefox' in user_agent:
                    scan_data['client_info']['browser'] = 'Firefox'
                elif 'Safari' in user_agent and 'Chrome' not in user_agent:
                    scan_data['client_info']['browser'] = 'Safari'
                elif 'Edg' in user_agent or 'Edge' in user_agent:
                    scan_data['client_info']['browser'] = 'Edge'
                elif 'MSIE' in user_agent or 'Trident' in user_agent:
                    scan_data['client_info']['browser'] = 'Internet Explorer'
                elif 'Opera' in user_agent or 'OPR' in user_agent:
                    scan_data['client_info']['browser'] = 'Opera'
            
            # Ensure network section has proper structure
            if 'network' not in scan_data or not scan_data['network']:
                scan_data['network'] = {
                    'open_ports': {
                        'count': 0,
                        'list': [],
                        'severity': 'Low'
                    },
                    'gateway': {
                        'info': 'No gateway information available',
                        'results': []
                    }
                }
            elif isinstance(scan_data['network'], list):
                # Convert network list to structured format
                network_results = scan_data['network']
                port_list = []
                gateway_results = []
                
                for item in network_results:
                    if isinstance(item, tuple) and len(item) >= 2:
                        message, severity = item
                        # Extract port information
                        if 'Port ' in message and ' is open' in message:
                            try:
                                port_parts = message.split(' ')
                                port_num = int(port_parts[1])
                                port_list.append(port_num)
                            except:
                                pass
                        
                        # Add to gateway results
                        gateway_results.append([message, severity])
                
                scan_data['network'] = {
                    'open_ports': {
                        'count': len(port_list),
                        'list': port_list,
                        'severity': 'High' if len(port_list) > 5 else 'Medium' if len(port_list) > 2 else 'Low'
                    },
                    'gateway': {
                        'info': 'Gateway security scan results',
                        'results': gateway_results
                    }
                }
            
            # Ensure web security section exists
            if 'web' not in scan_data:
                scan_data['web'] = {'status': 'not_scanned'}
            
            # Ensure system security section exists
            if 'system' not in scan_data:
                scan_data['system'] = {
                    'os_updates': {
                        'status': 'unknown',
                        'message': 'System security check not performed',
                        'severity': 'Medium'
                    },
                    'firewall': {
                        'status': 'Unknown firewall status',
                        'severity': 'Medium'
                    }
                }
            
            # Ensure risk assessment has color
            if 'risk_assessment' in scan_data and isinstance(scan_data['risk_assessment'], dict):
                risk = scan_data['risk_assessment']
                score = risk.get('overall_score', 75)
                
                if 'color' not in risk:
                    # Set color based on score
                    if score >= 90:
                        risk['color'] = '#28a745'  # green
                    elif score >= 80:
                        risk['color'] = '#5cb85c'  # light green
                    elif score >= 70:
                        risk['color'] = '#17a2b8'  # info blue
                    elif score >= 60:
                        risk['color'] = '#ffc107'  # warning yellow
                    elif score >= 50:
                        risk['color'] = '#fd7e14'  # orange
                    else:
                        risk['color'] = '#dc3545'  # red
            
            return scan_data
"""
    
    # Add the improved function after the imports section
    if "import client_db" in content:
        content = content.replace("# Import authentication utilities and database functions", 
                                "# Import authentication utilities and database functions" + improved_client_info)
    
    # Find the report_view function and update it to use the new process_scan_data function
    report_view_pattern = "@client_bp.route('/reports/<scan_id>')"
    if report_view_pattern in content:
        # Find the line where formatted_scan is set
        formatted_scan_lines = ["# Format scan data for template - preserve comprehensive scan data",
                             "formatted_scan = scan"]
        
        # Replace with our updated processing
        new_formatted_scan = """# Format scan data for template - preserve comprehensive scan data
        # Apply processing to ensure all needed data is present
        formatted_scan = process_scan_data(scan)"""
        
        for line in formatted_scan_lines:
            if line in content:
                content = content.replace(line, new_formatted_scan)
                break
    
    # Write the modified file
    with open(client_path, 'w') as f:
        f.write(content)
    
    logger.info(f"✅ Fixed client.py to ensure all scan data is properly formatted")
    return True

def fix_scan_results_structure():
    """
    Fix the structure of scan results in the database to ensure proper display
    """
    client_dbs_dir = '/home/ggrun/CybrScan_1/client_databases'
    if not os.path.exists(client_dbs_dir):
        logger.error(f"Client databases directory not found: {client_dbs_dir}")
        return False
    
    # Track total updates
    total_updates = 0
    
    # Process each client database
    for db_file in os.listdir(client_dbs_dir):
        if not db_file.startswith('client_') or not db_file.endswith('.db'):
            continue
        
        db_path = os.path.join(client_dbs_dir, db_file)
        logger.info(f"Processing database: {db_file}")
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if scans table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scans'")
            if not cursor.fetchone():
                logger.warning(f"No scans table in {db_file}, skipping")
                conn.close()
                continue
            
            # Get scan records with JSON results
            cursor.execute("SELECT id, scan_id, scan_results, user_agent FROM scans WHERE scan_results IS NOT NULL")
            scans = cursor.fetchall()
            
            if not scans:
                logger.info(f"No scan records found in {db_file}")
                conn.close()
                continue
            
            # Update each scan record
            db_updates = 0
            for scan_row in scans:
                scan_id = scan_row[0]
                scan_uid = scan_row[1]
                scan_results_json = scan_row[2]
                user_agent = scan_row[3]
                
                if not scan_results_json or not scan_results_json.strip():
                    continue
                
                try:
                    # Parse JSON
                    scan_data = json.loads(scan_results_json)
                    modified = False
                    
                    # Process client info - add OS and browser data
                    if 'client_info' not in scan_data or not isinstance(scan_data['client_info'], dict):
                        scan_data['client_info'] = {
                            'name': scan_data.get('lead_name', scan_data.get('name', 'N/A')),
                            'email': scan_data.get('lead_email', scan_data.get('email', 'N/A')),
                            'company': scan_data.get('lead_company', scan_data.get('company', 'N/A')),
                            'phone': scan_data.get('lead_phone', 'N/A'),
                            'os': 'Unknown',
                            'browser': 'Unknown'
                        }
                        modified = True
                    
                    # Extract OS and browser info if user_agent is available
                    if user_agent and ('os' not in scan_data['client_info'] or scan_data['client_info']['os'] == 'Unknown'):
                        # Extract OS info
                        if 'Windows' in user_agent:
                            os_version = 'Windows'
                            if 'Windows NT 10' in user_agent:
                                os_version = 'Windows 10/11'
                            elif 'Windows NT 6.3' in user_agent:
                                os_version = 'Windows 8.1'
                            elif 'Windows NT 6.2' in user_agent:
                                os_version = 'Windows 8'
                            elif 'Windows NT 6.1' in user_agent:
                                os_version = 'Windows 7'
                            scan_data['client_info']['os'] = os_version
                            modified = True
                        elif 'Mac OS X' in user_agent:
                            scan_data['client_info']['os'] = 'macOS'
                            modified = True
                        elif 'Linux' in user_agent:
                            scan_data['client_info']['os'] = 'Linux'
                            modified = True
                        elif 'Android' in user_agent:
                            scan_data['client_info']['os'] = 'Android'
                            modified = True
                        elif 'iOS' in user_agent or 'iPhone' in user_agent or 'iPad' in user_agent:
                            scan_data['client_info']['os'] = 'iOS'
                            modified = True
                        
                        # Extract browser info
                        if 'Chrome' in user_agent and 'Chromium' not in user_agent:
                            scan_data['client_info']['browser'] = 'Chrome'
                            modified = True
                        elif 'Firefox' in user_agent:
                            scan_data['client_info']['browser'] = 'Firefox'
                            modified = True
                        elif 'Safari' in user_agent and 'Chrome' not in user_agent:
                            scan_data['client_info']['browser'] = 'Safari'
                            modified = True
                        elif 'Edg' in user_agent or 'Edge' in user_agent:
                            scan_data['client_info']['browser'] = 'Edge'
                            modified = True
                        elif 'MSIE' in user_agent or 'Trident' in user_agent:
                            scan_data['client_info']['browser'] = 'Internet Explorer'
                            modified = True
                        elif 'Opera' in user_agent or 'OPR' in user_agent:
                            scan_data['client_info']['browser'] = 'Opera'
                            modified = True
                    
                    # Process network data - ensure structured format
                    if 'network' in scan_data and isinstance(scan_data['network'], list):
                        network_results = scan_data['network']
                        port_list = []
                        gateway_results = []
                        
                        for item in network_results:
                            if isinstance(item, tuple) and len(item) >= 2:
                                message, severity = item
                                # Extract port information
                                if 'Port ' in message and ' is open' in message:
                                    try:
                                        port_parts = message.split(' ')
                                        port_num = int(port_parts[1])
                                        port_list.append(port_num)
                                    except:
                                        pass
                                
                                # Add to gateway results
                                gateway_results.append([message, severity])
                        
                        scan_data['network'] = {
                            'open_ports': {
                                'count': len(port_list),
                                'list': port_list,
                                'severity': 'High' if len(port_list) > 5 else 'Medium' if len(port_list) > 2 else 'Low'
                            },
                            'gateway': {
                                'info': 'Gateway security scan results',
                                'results': gateway_results
                            }
                        }
                        modified = True
                    
                    # Update the database if modified
                    if modified:
                        cursor.execute(
                            "UPDATE scans SET scan_results = ? WHERE id = ?",
                            (json.dumps(scan_data), scan_id)
                        )
                        db_updates += 1
                        logger.info(f"Updated scan {scan_uid} in {db_file}")
                
                except Exception as e:
                    logger.error(f"Error updating scan {scan_uid} in {db_file}: {e}")
            
            # Commit changes
            if db_updates > 0:
                conn.commit()
                logger.info(f"Updated {db_updates} scan records in {db_file}")
                total_updates += db_updates
            
            conn.close()
        
        except Exception as e:
            logger.error(f"Error processing database {db_file}: {e}")
    
    logger.info(f"Total scan records updated: {total_updates}")
    return total_updates > 0

def main():
    """Main function to apply fix"""
    logger.info("Applying fix for scan display data...")
    
    # Fix client.py to ensure scan data is properly formatted
    fix_client_report_view()
    
    # Fix scan results structure in databases
    fix_scan_results_structure()
    
    logger.info("Fix has been applied!")
    logger.info("To make the changes effective, please restart the application server.")

if __name__ == "__main__":
    main()