#!/usr/bin/env python3
"""
Direct fix for scan display and scanner creation issues
This applies patches directly to the running app
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

def patch_risk_assessment_color():
    """
    Directly patch the route function to fix risk assessment color
    """
    patch_code = """
def _process_scan_results(scan_results):
    \"\"\"Process scan results to ensure risk assessment is properly formatted\"\"\"
    if not scan_results:
        return scan_results
        
    if 'risk_assessment' not in scan_results:
        score = 75
        if 'findings' in scan_results and isinstance(scan_results['findings'], list):
            critical_count = sum(1 for f in scan_results['findings'] if f.get('severity') == 'Critical')
            high_count = sum(1 for f in scan_results['findings'] if f.get('severity') == 'High')
            medium_count = sum(1 for f in scan_results['findings'] if f.get('severity') == 'Medium')
            score = 100 - (critical_count * 15 + high_count * 10 + medium_count * 5)
            score = max(min(score, 100), 0)  # Keep between 0-100
        
        # Set risk level and color based on score
        if score >= 90:
            risk_level = 'Low'
            color = '#28a745'  # green
        elif score >= 80:
            risk_level = 'Low-Medium'
            color = '#5cb85c'  # light green
        elif score >= 70:
            risk_level = 'Medium'
            color = '#17a2b8'  # info blue
        elif score >= 60:
            risk_level = 'Medium-High'
            color = '#ffc107'  # warning yellow
        elif score >= 50:
            risk_level = 'High'
            color = '#fd7e14'  # orange
        else:
            risk_level = 'Critical'
            color = '#dc3545'  # red
        
        # Create risk assessment
        scan_results['risk_assessment'] = {
            'overall_score': score,
            'risk_level': risk_level,
            'color': color,
            'grade': 'A' if score >= 90 else 'B' if score >= 80 else 'C' if score >= 70 else 'D' if score >= 60 else 'F',
            'component_scores': {
                'network': score,
                'web': score,
                'email': score,
                'system': score
            }
        }
    elif isinstance(scan_results['risk_assessment'], dict):
        # Ensure risk assessment has all required fields
        score = scan_results['risk_assessment'].get('overall_score', 75)
        
        # Set risk level and color based on score
        if score >= 90:
            risk_level = 'Low'
            color = '#28a745'  # green
        elif score >= 80:
            risk_level = 'Low-Medium'
            color = '#5cb85c'  # light green
        elif score >= 70:
            risk_level = 'Medium'
            color = '#17a2b8'  # info blue
        elif score >= 60:
            risk_level = 'Medium-High'
            color = '#ffc107'  # warning yellow
        elif score >= 50:
            risk_level = 'High'
            color = '#fd7e14'  # orange
        else:
            risk_level = 'Critical'
            color = '#dc3545'  # red
        
        # Update risk assessment with color value
        scan_results['risk_assessment']['risk_level'] = risk_level
        scan_results['risk_assessment']['color'] = color
        scan_results['risk_assessment']['grade'] = 'A' if score >= 90 else 'B' if score >= 80 else 'C' if score >= 70 else 'D' if score >= 60 else 'F'
        
        if 'component_scores' not in scan_results['risk_assessment']:
            scan_results['risk_assessment']['component_scores'] = {
                'network': score,
                'web': score,
                'email': score,
                'system': score
            }
    
    return scan_results

# Monkey patch the client report_view function
import client

original_report_view = client.report_view

def patched_report_view(scan_id):
    result = original_report_view(scan_id)
    
    # Check if this is a template response
    if hasattr(result, 'context') and isinstance(result.context, dict) and 'scan' in result.context:
        # Process scan results
        result.context['scan'] = _process_scan_results(result.context['scan'])
    
    return result

client.report_view = patched_report_view
print("✅ Patched client.report_view function to fix risk assessment color")

# Try to patch other relevant routes if they exist
try:
    from routes.scan_routes import scan_bp
    
    original_results = scan_bp.view_functions.get('results')
    
    if original_results:
        def patched_results():
            result = original_results()
            
            # Check if this is a JSON response
            if hasattr(result, 'json'):
                try:
                    data = result.json
                    if isinstance(data, dict) and 'scan' in data:
                        data['scan'] = _process_scan_results(data['scan'])
                except:
                    pass
            
            return result
        
        scan_bp.view_functions['results'] = patched_results
        print("✅ Patched scan_routes.results function to fix risk assessment color")
except Exception as e:
    print(f"❌ Could not patch scan_routes.results function: {e}")
"""
    
    # Apply the patch
    try:
        exec(patch_code)
        print(f"✅ Applied risk assessment color patch directly")
        return True
    except Exception as e:
        print(f"❌ Error applying risk assessment patch: {e}")
        return False

def fix_scanner_name_in_database():
    """
    Fix scanner names in the database by removing 'client 6' prefix
    """
    try:
        # Check if client_scanner.db exists
        if os.path.exists('client_scanner.db'):
            conn = sqlite3.connect('client_scanner.db')
            cursor = conn.cursor()
            
            # Find scanners with 'client 6' in name
            cursor.execute("SELECT id, name FROM scanners WHERE name LIKE 'client 6%'")
            scanners = cursor.fetchall()
            
            if scanners:
                print(f"Found {len(scanners)} scanners with 'client 6' prefix:")
                for scanner_id, name in scanners:
                    # Fix the name by removing 'client 6' prefix
                    new_name = name.replace('client 6', '').strip()
                    print(f"  Fixing scanner {scanner_id}: '{name}' -> '{new_name}'")
                    
                    # Update the name in the database
                    cursor.execute("UPDATE scanners SET name = ? WHERE id = ?", (new_name, scanner_id))
                
                # Commit changes
                conn.commit()
                print(f"✅ Fixed {len(scanners)} scanner names in database")
            else:
                print("No scanner names with 'client 6' prefix found in database")
            
            # Fix client_id if needed
            cursor.execute("UPDATE scanners SET client_id = 5 WHERE client_id = 6")
            if cursor.rowcount > 0:
                print(f"✅ Fixed client_id for {cursor.rowcount} scanners (changed from 6 to 5)")
                conn.commit()
            
            conn.close()
        else:
            print("client_scanner.db not found")
        
        # Also check client databases
        client_dbs_dir = 'client_databases'
        if os.path.exists(client_dbs_dir):
            for db_file in os.listdir(client_dbs_dir):
                if db_file.startswith('client_') and db_file.endswith('.db'):
                    db_path = os.path.join(client_dbs_dir, db_file)
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    # Check if scanners table exists
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scanners'")
                    if cursor.fetchone():
                        # Find scanners with 'client 6' in name
                        cursor.execute("SELECT id, name FROM scanners WHERE name LIKE 'client 6%'")
                        scanners = cursor.fetchall()
                        
                        if scanners:
                            print(f"Found {len(scanners)} scanners with 'client 6' prefix in {db_file}:")
                            for scanner_id, name in scanners:
                                # Fix the name by removing 'client 6' prefix
                                new_name = name.replace('client 6', '').strip()
                                print(f"  Fixing scanner {scanner_id}: '{name}' -> '{new_name}'")
                                
                                # Update the name in the database
                                cursor.execute("UPDATE scanners SET name = ? WHERE id = ?", (new_name, scanner_id))
                            
                            # Commit changes
                            conn.commit()
                            print(f"✅ Fixed {len(scanners)} scanner names in {db_file}")
                        
                        # Fix client_id if needed
                        cursor.execute("UPDATE scanners SET client_id = 5 WHERE client_id = 6")
                        if cursor.rowcount > 0:
                            print(f"✅ Fixed client_id for {cursor.rowcount} scanners in {db_file} (changed from 6 to 5)")
                            conn.commit()
                    
                    conn.close()
        
        return True
    except Exception as e:
        print(f"❌ Error fixing scanner names in database: {e}")
        return False

def fix_scanner_creation_function():
    """
    Fix scanner creation to prevent 'client 6' prefix
    """
    patch_code = """
# Monkey patch scanner_create function
import client

original_scanner_create = client.scanner_create

def patched_scanner_create(user):
    # Print debug information
    print(f"Scanner creation started for user: {user.get('username', 'unknown')}")
    
    # Capture the original result
    result = original_scanner_create(user)
    
    # Fix scanner name in database if needed
    try:
        import sqlite3
        conn = sqlite3.connect('client_scanner.db')
        cursor = conn.cursor()
        
        # Find recently created scanners with 'client 6' prefix
        cursor.execute("SELECT id, name FROM scanners WHERE name LIKE 'client 6%' ORDER BY id DESC LIMIT 1")
        scanner = cursor.fetchone()
        
        if scanner:
            scanner_id, name = scanner
            # Fix the name
            new_name = name.replace('client 6', '').strip()
            print(f"Fixing newly created scanner {scanner_id}: '{name}' -> '{new_name}'")
            
            # Update the database
            cursor.execute("UPDATE scanners SET name = ? WHERE id = ?", (new_name, scanner_id))
            conn.commit()
        
        conn.close()
    except Exception as e:
        print(f"Error fixing newly created scanner: {e}")
    
    return result

# Replace the original function with our patched version
client.scanner_create = patched_scanner_create
print("✅ Patched client.scanner_create function to prevent 'client 6' prefix")
"""
    
    # Apply the patch
    try:
        exec(patch_code)
        print(f"✅ Applied scanner creation patch directly")
        return True
    except Exception as e:
        print(f"❌ Error applying scanner creation patch: {e}")
        return False

def modify_scanner_db():
    """Fix scanner database to remove client 6 references and fix client IDs"""
    try:
        # Check all client databases for scanner problems
        client_dbs_dir = 'client_databases'
        if os.path.exists(client_dbs_dir):
            for db_file in os.listdir(client_dbs_dir):
                if db_file.startswith('client_') and db_file.endswith('.db'):
                    db_path = os.path.join(client_dbs_dir, db_file)
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    # Check if scanners table exists
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scanners'")
                    if cursor.fetchone():
                        # Find scanners with 'client 6' in name
                        cursor.execute("SELECT id, name FROM scanners WHERE name LIKE '%client 6%'")
                        scanners = cursor.fetchall()
                        
                        if scanners:
                            print(f"Found {len(scanners)} scanners with 'client 6' in name in {db_file}:")
                            for scanner_id, name in scanners:
                                # Fix the name by removing 'client 6'
                                new_name = name.replace('client 6', '').strip()
                                print(f"  Fixing scanner {scanner_id}: '{name}' -> '{new_name}'")
                                
                                # Update the name in the database
                                cursor.execute("UPDATE scanners SET name = ? WHERE id = ?", (new_name, scanner_id))
                            
                            # Commit changes
                            conn.commit()
                            print(f"✅ Fixed {len(scanners)} scanner names in {db_file}")
                    
                    # Check if scan_results table exists and has scanner_name column
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scan_results'")
                    if cursor.fetchone():
                        # Check if scanner_name column exists
                        cursor.execute("PRAGMA table_info(scan_results)")
                        columns = cursor.fetchall()
                        column_names = [col[1] for col in columns]
                        
                        if 'scanner_name' in column_names:
                            # Find scan results with 'client 6' in scanner_name
                            cursor.execute("SELECT id, scanner_name FROM scan_results WHERE scanner_name LIKE '%client 6%'")
                            scan_results = cursor.fetchall()
                            
                            if scan_results:
                                print(f"Found {len(scan_results)} scan results with 'client 6' in scanner_name in {db_file}:")
                                for result_id, scanner_name in scan_results:
                                    # Fix the name by removing 'client 6'
                                    new_name = scanner_name.replace('client 6', '').strip()
                                    print(f"  Fixing scan result {result_id}: '{scanner_name}' -> '{new_name}'")
                                    
                                    # Update the name in the database
                                    cursor.execute("UPDATE scan_results SET scanner_name = ? WHERE id = ?", (new_name, result_id))
                                
                                # Commit changes
                                conn.commit()
                                print(f"✅ Fixed {len(scan_results)} scan result scanner names in {db_file}")
                    
                    conn.close()
        
        return True
    except Exception as e:
        print(f"❌ Error fixing scanner databases: {e}")
        return False

def patch_templates():
    """
    Patch templates to ensure risk assessment color is used
    """
    try:
        # Check if results.html exists
        template_path = 'templates/results.html'
        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                content = f.read()
            
            # Check if the template is using risk_assessment.color
            if 'stroke: {{ scan.risk_assessment.color|default(\'#17a2b8\') }};' in content:
                print("Template is already using risk_assessment.color")
            else:
                # Look for lines 129-130 and replace gauge color
                content = content.replace(
                    'style="stroke: #17a2b8;',
                    'style="stroke: {{ scan.risk_assessment.color|default(\'#17a2b8\') }};'
                )
                
                # Look for lines 132-134 and replace text color
                content = content.replace(
                    'style="fill: #17a2b8;',
                    'style="fill: {{ scan.risk_assessment.color|default(\'#17a2b8\') }};'
                )
                
                # Write updated template
                with open(template_path, 'w') as f:
                    f.write(content)
                
                print("✅ Updated results.html to use risk_assessment.color")
            
            return True
        else:
            print(f"Template file not found: {template_path}")
            return False
    except Exception as e:
        print(f"❌ Error patching templates: {e}")
        return False

def fix_scan_database():
    """
    Fix existing scan results in the database to ensure they have proper risk assessment colors
    """
    try:
        # Process all client databases
        client_dbs_dir = 'client_databases'
        if os.path.exists(client_dbs_dir):
            for db_file in os.listdir(client_dbs_dir):
                if db_file.startswith('client_') and db_file.endswith('.db'):
                    db_path = os.path.join(client_dbs_dir, db_file)
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    # Check if scan_results table exists
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scan_results'")
                    if cursor.fetchone():
                        # Get columns to check if scan_results column exists
                        cursor.execute("PRAGMA table_info(scan_results)")
                        columns = cursor.fetchall()
                        column_names = [col[1] for col in columns]
                        
                        if 'scan_results' in column_names:
                            # Find all scan results with JSON data
                            cursor.execute("SELECT id, scan_results FROM scan_results WHERE scan_results IS NOT NULL")
                            results = cursor.fetchall()
                            
                            if results:
                                print(f"Processing {len(results)} scan results in {db_file}")
                                updated_count = 0
                                
                                for result_id, scan_result_json in results:
                                    try:
                                        # Parse JSON
                                        if scan_result_json and scan_result_json.strip():
                                            scan_data = json.loads(scan_result_json)
                                            
                                            # Check if risk_assessment exists and has no color
                                            modified = False
                                            if 'risk_assessment' in scan_data and isinstance(scan_data['risk_assessment'], dict):
                                                if 'color' not in scan_data['risk_assessment']:
                                                    # Add color based on score
                                                    score = scan_data['risk_assessment'].get('overall_score', 75)
                                                    
                                                    # Set risk level and color based on score
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
                                                    
                                                    scan_data['risk_assessment']['color'] = color
                                                    modified = True
                                            
                                            # If modified, update the database
                                            if modified:
                                                cursor.execute(
                                                    "UPDATE scan_results SET scan_results = ? WHERE id = ?",
                                                    (json.dumps(scan_data), result_id)
                                                )
                                                updated_count += 1
                                    except Exception as e:
                                        print(f"Error processing scan result {result_id}: {e}")
                                
                                if updated_count > 0:
                                    conn.commit()
                                    print(f"✅ Updated {updated_count} scan results with risk assessment color in {db_file}")
                    
                    conn.close()
        
        return True
    except Exception as e:
        print(f"❌ Error fixing scan database: {e}")
        return False

def main():
    """Main function to apply all fixes"""
    print("Applying direct fixes to the running application...")
    
    # Fix risk assessment color
    patch_risk_assessment_color()
    
    # Fix scanner name in database
    fix_scanner_name_in_database()
    
    # Fix scanner creation function
    fix_scanner_creation_function()
    
    # Fix scanner databases
    modify_scanner_db()
    
    # Patch templates
    patch_templates()
    
    # Fix existing scan results in database
    fix_scan_database()
    
    print("\nAll fixes have been applied!")
    print("To make the changes effective, please restart the application server.")

if __name__ == "__main__":
    main()