#!/usr/bin/env python3
"""
Direct database and template fixes for scanner name and risk assessment color issues
This script doesn't rely on Flask or other external dependencies
"""

import os
import sys
import json
import sqlite3
import logging
from datetime import datetime
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_template_file():
    """
    Fix the results.html template to properly use risk assessment colors
    """
    try:
        template_path = '/home/ggrun/CybrScan_1/templates/results.html'
        if not os.path.exists(template_path):
            print(f"Template file not found: {template_path}")
            return False
        
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Check if we already made the fix
        if 'stroke: {{ scan.risk_assessment.color|default' in content:
            print("Template is already fixed to use risk_assessment.color")
            return True
        
        # Fix circle color - look for the SVG circle with class="gauge-value"
        content = re.sub(
            r'style="stroke: #17a2b8;',
            r'style="stroke: {{ scan.risk_assessment.color|default(\'#17a2b8\') }};',
            content
        )
        
        # Fix text color - look for the text with class="gauge-text"
        content = re.sub(
            r'style="fill: #17a2b8;',
            r'style="fill: {{ scan.risk_assessment.color|default(\'#17a2b8\') }};',
            content
        )
        
        # Save the updated template
        with open(template_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Fixed template file {template_path} to use risk_assessment.color")
        return True
    except Exception as e:
        print(f"❌ Error fixing template: {e}")
        return False

def fix_client_database_scan_results():
    """
    Fix scan results in client databases to include proper risk assessment colors
    """
    try:
        client_dbs_dir = '/home/ggrun/CybrScan_1/client_databases'
        if not os.path.exists(client_dbs_dir):
            print(f"Client databases directory not found: {client_dbs_dir}")
            return False
        
        # Process each client database
        for db_file in os.listdir(client_dbs_dir):
            if db_file.startswith('client_') and db_file.endswith('.db'):
                db_path = os.path.join(client_dbs_dir, db_file)
                
                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    # Check if scan_results table exists
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scan_results'")
                    if not cursor.fetchone():
                        print(f"No scan_results table in {db_file}, skipping")
                        conn.close()
                        continue
                    
                    # Check table structure for scan_results column
                    cursor.execute("PRAGMA table_info(scan_results)")
                    columns = cursor.fetchall()
                    column_names = [col[1] for col in columns]
                    
                    if 'scan_results' not in column_names:
                        print(f"No scan_results column in {db_file}, skipping")
                        conn.close()
                        continue
                    
                    # Process scan results to add color
                    cursor.execute("SELECT id, scan_results FROM scan_results WHERE scan_results IS NOT NULL")
                    results = cursor.fetchall()
                    
                    if not results:
                        print(f"No scan results found in {db_file}, skipping")
                        conn.close()
                        continue
                    
                    fixed_count = 0
                    for result_id, result_json in results:
                        if not result_json or not result_json.strip():
                            continue
                        
                        try:
                            # Parse the JSON data
                            scan_data = json.loads(result_json)
                            
                            # Check if risk_assessment exists
                            modified = False
                            if 'risk_assessment' in scan_data and isinstance(scan_data['risk_assessment'], dict):
                                # Add color based on score if it doesn't exist
                                if 'color' not in scan_data['risk_assessment']:
                                    score = scan_data['risk_assessment'].get('overall_score', 75)
                                    
                                    # Determine color based on score
                                    if score >= 90:
                                        color = '#28a745'  # green
                                    elif score >= 80:
                                        color = '#5cb85c'  # light green
                                    elif score >= 70:
                                        color = '#17a2b8'  # info blue
                                    elif score >= 60:
                                        color = '#ffc107'  # warning yellow
                                    elif score >= 50:
                                        color = '#fd7e14'  # orange
                                    else:
                                        color = '#dc3545'  # red
                                    
                                    # Add color to risk assessment
                                    scan_data['risk_assessment']['color'] = color
                                    modified = True
                            
                            # Update the database if we modified the data
                            if modified:
                                cursor.execute(
                                    "UPDATE scan_results SET scan_results = ? WHERE id = ?",
                                    (json.dumps(scan_data), result_id)
                                )
                                fixed_count += 1
                        except Exception as e:
                            print(f"Error processing scan result {result_id} in {db_file}: {e}")
                    
                    # Commit changes if we fixed any scan results
                    if fixed_count > 0:
                        conn.commit()
                        print(f"✅ Fixed {fixed_count} scan results in {db_file}")
                    else:
                        print(f"No scan results needed fixing in {db_file}")
                    
                    # Fix scanner names with "client 6" prefix
                    # Check if scanner_name column exists
                    if 'scanner_name' in column_names:
                        cursor.execute("SELECT id, scanner_name FROM scan_results WHERE scanner_name LIKE '%client 6%'")
                        scanner_results = cursor.fetchall()
                        
                        if scanner_results:
                            print(f"Found {len(scanner_results)} scan results with 'client 6' in scanner_name in {db_file}")
                            for result_id, scanner_name in scanner_results:
                                # Fix scanner name
                                new_name = scanner_name.replace('client 6', '').strip()
                                cursor.execute(
                                    "UPDATE scan_results SET scanner_name = ? WHERE id = ?",
                                    (new_name, result_id)
                                )
                            
                            conn.commit()
                            print(f"✅ Fixed {len(scanner_results)} scanner names in scan results in {db_file}")
                    
                    conn.close()
                except Exception as e:
                    print(f"Error processing database {db_file}: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Error fixing client database scan results: {e}")
        return False

def fix_scanner_names():
    """
    Fix scanner names in all databases by removing 'client 6' prefix
    """
    try:
        # First check the main scanner database
        scanner_db_path = '/home/ggrun/CybrScan_1/client_scanner.db'
        if os.path.exists(scanner_db_path):
            conn = sqlite3.connect(scanner_db_path)
            cursor = conn.cursor()
            
            # Check if scanners table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scanners'")
            if cursor.fetchone():
                # Fix scanner names
                cursor.execute("SELECT id, name FROM scanners WHERE name LIKE '%client 6%'")
                scanners = cursor.fetchall()
                
                if scanners:
                    print(f"Found {len(scanners)} scanners with 'client 6' in name in client_scanner.db:")
                    for scanner_id, name in scanners:
                        # Fix scanner name
                        new_name = name.replace('client 6', '').strip()
                        print(f"  Fixing scanner {scanner_id}: '{name}' -> '{new_name}'")
                        cursor.execute("UPDATE scanners SET name = ? WHERE id = ?", (new_name, scanner_id))
                    
                    conn.commit()
                    print(f"✅ Fixed {len(scanners)} scanner names in client_scanner.db")
                
                # Fix client IDs
                cursor.execute("UPDATE scanners SET client_id = 5 WHERE client_id = 6")
                if cursor.rowcount > 0:
                    conn.commit()
                    print(f"✅ Fixed client_id for {cursor.rowcount} scanners in client_scanner.db")
            
            conn.close()
        else:
            print("client_scanner.db not found, skipping")
        
        # Now check client databases for scanners table
        client_dbs_dir = '/home/ggrun/CybrScan_1/client_databases'
        if os.path.exists(client_dbs_dir):
            for db_file in os.listdir(client_dbs_dir):
                if db_file.startswith('client_') and db_file.endswith('.db'):
                    db_path = os.path.join(client_dbs_dir, db_file)
                    
                    try:
                        conn = sqlite3.connect(db_path)
                        cursor = conn.cursor()
                        
                        # Check if scanners table exists
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scanners'")
                        if cursor.fetchone():
                            # Fix scanner names
                            cursor.execute("SELECT id, name FROM scanners WHERE name LIKE '%client 6%'")
                            scanners = cursor.fetchall()
                            
                            if scanners:
                                print(f"Found {len(scanners)} scanners with 'client 6' in name in {db_file}:")
                                for scanner_id, name in scanners:
                                    # Fix scanner name
                                    new_name = name.replace('client 6', '').strip()
                                    print(f"  Fixing scanner {scanner_id}: '{name}' -> '{new_name}'")
                                    cursor.execute("UPDATE scanners SET name = ? WHERE id = ?", (new_name, scanner_id))
                                
                                conn.commit()
                                print(f"✅ Fixed {len(scanners)} scanner names in {db_file}")
                            
                            # Fix client IDs
                            cursor.execute("UPDATE scanners SET client_id = 5 WHERE client_id = 6")
                            if cursor.rowcount > 0:
                                conn.commit()
                                print(f"✅ Fixed client_id for {cursor.rowcount} scanners in {db_file}")
                        
                        conn.close()
                    except Exception as e:
                        print(f"Error processing scanners in database {db_file}: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Error fixing scanner names: {e}")
        return False

def main():
    """Main function to apply all fixes"""
    print("Applying direct fixes to databases and templates...")
    
    # Fix template file
    fix_template_file()
    
    # Fix scanner names in all databases
    fix_scanner_names()
    
    # Fix scan results in client databases
    fix_client_database_scan_results()
    
    print("\nAll fixes have been applied!")
    print("To make the changes effective, please restart the application server.")

if __name__ == "__main__":
    main()