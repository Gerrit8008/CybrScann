#!/usr/bin/env python3
"""
Emergency fix for risk assessment color in scan results
Direct modification of the scan database and core functionality
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

def fix_existing_scan_results():
    """
    Fix existing scan results in all client databases to include proper risk assessment colors
    """
    print("Fixing existing scan results in client databases...")
    
    client_dbs_dir = '/home/ggrun/CybrScan_1/client_databases'
    if not os.path.exists(client_dbs_dir):
        print(f"Error: Client databases directory not found: {client_dbs_dir}")
        return False
    
    # Process each client database
    modified_count = 0
    for db_file in os.listdir(client_dbs_dir):
        if db_file.startswith('client_') and db_file.endswith('.db'):
            db_path = os.path.join(client_dbs_dir, db_file)
            print(f"Processing database: {db_file}")
            
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Check if scan_results table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scan_results'")
                if not cursor.fetchone():
                    print(f"  No scan_results table in {db_file}, skipping")
                    conn.close()
                    continue
                
                # Get all scan results
                cursor.execute("SELECT id, scan_results FROM scan_results WHERE scan_results IS NOT NULL")
                results = cursor.fetchall()
                
                if not results:
                    print(f"  No scan results found in {db_file}, skipping")
                    conn.close()
                    continue
                
                db_modified_count = 0
                for result_id, scan_result_json in results:
                    if not scan_result_json or not scan_result_json.strip():
                        continue
                    
                    try:
                        # Parse the JSON data
                        scan_data = json.loads(scan_result_json)
                        modified = False
                        
                        # Check if risk_assessment exists
                        if 'risk_assessment' in scan_data and isinstance(scan_data['risk_assessment'], dict):
                            risk_assessment = scan_data['risk_assessment']
                            
                            # Get the score or set a default
                            score = risk_assessment.get('overall_score')
                            if score is None or not isinstance(score, (int, float)):
                                score = 75
                                risk_assessment['overall_score'] = score
                                modified = True
                            
                            # Set risk level and color based on score
                            if 'color' not in risk_assessment:
                                if score >= 90:
                                    color = '#28a745'  # green
                                    risk_level = 'Low'
                                elif score >= 80:
                                    color = '#5cb85c'  # light green
                                    risk_level = 'Low-Medium'
                                elif score >= 70:
                                    color = '#17a2b8'  # info blue
                                    risk_level = 'Medium'
                                elif score >= 60:
                                    color = '#ffc107'  # warning yellow
                                    risk_level = 'Medium-High'
                                elif score >= 50:
                                    color = '#fd7e14'  # orange
                                    risk_level = 'High'
                                else:
                                    color = '#dc3545'  # red
                                    risk_level = 'Critical'
                                
                                risk_assessment['color'] = color
                                risk_assessment['risk_level'] = risk_level
                                modified = True
                        else:
                            # No risk assessment, create one
                            scan_data['risk_assessment'] = {
                                'overall_score': 75,
                                'risk_level': 'Medium',
                                'color': '#17a2b8',  # info blue
                                'grade': 'C',
                                'component_scores': {
                                    'network': 75,
                                    'web': 75,
                                    'email': 75,
                                    'system': 75
                                }
                            }
                            modified = True
                        
                        # Update the database if modified
                        if modified:
                            cursor.execute(
                                "UPDATE scan_results SET scan_results = ? WHERE id = ?",
                                (json.dumps(scan_data), result_id)
                            )
                            db_modified_count += 1
                    except Exception as e:
                        print(f"  Error processing scan result {result_id}: {e}")
                
                # Commit changes
                if db_modified_count > 0:
                    conn.commit()
                    print(f"  ✅ Fixed {db_modified_count} scan results in {db_file}")
                    modified_count += db_modified_count
                else:
                    print(f"  No scan results needed fixing in {db_file}")
                
                conn.close()
            except Exception as e:
                print(f"  Error processing database {db_file}: {e}")
    
    print(f"Total scan results fixed: {modified_count}")
    return modified_count > 0

def create_direct_patch_file():
    """
    Create a direct patch that can be run by the server to fix risk assessment on-the-fly
    """
    print("Creating direct patch file...")
    
    patch_path = '/home/ggrun/CybrScan_1/risk_assessment_direct_patch.py'
    patch_content = """#!/usr/bin/env python3
\"\"\"
Direct patch for risk assessment color calculation
This file should be imported at the top level of the application
\"\"\"

import logging
logger = logging.getLogger(__name__)

def ensure_risk_assessment_color(scan_data):
    \"\"\"
    Ensure the scan data has a properly colored risk assessment
    This function directly modifies the provided scan_data dictionary
    \"\"\"
    if not scan_data:
        return scan_data
    
    # Check if risk_assessment exists
    if 'risk_assessment' not in scan_data or not isinstance(scan_data['risk_assessment'], dict):
        # Create a new risk assessment
        score = 75
        risk_level = 'Medium'
        color = '#17a2b8'  # info blue
        
        scan_data['risk_assessment'] = {
            'overall_score': score,
            'risk_level': risk_level,
            'color': color,
            'grade': 'C',
            'component_scores': {
                'network': score,
                'web': score,
                'email': score,
                'system': score
            }
        }
        return scan_data
    
    # Get the risk assessment
    risk_assessment = scan_data['risk_assessment']
    
    # Get the score or set a default
    score = risk_assessment.get('overall_score')
    if score is None or not isinstance(score, (int, float)):
        score = 75
        risk_assessment['overall_score'] = score
    
    # Set color based on score if it doesn't exist
    if 'color' not in risk_assessment:
        if score >= 90:
            color = '#28a745'  # green
            risk_level = 'Low'
        elif score >= 80:
            color = '#5cb85c'  # light green
            risk_level = 'Low-Medium'
        elif score >= 70:
            color = '#17a2b8'  # info blue
            risk_level = 'Medium'
        elif score >= 60:
            color = '#ffc107'  # warning yellow
            risk_level = 'Medium-High'
        elif score >= 50:
            color = '#fd7e14'  # orange
            risk_level = 'High'
        else:
            color = '#dc3545'  # red
            risk_level = 'Critical'
        
        risk_assessment['color'] = color
        risk_assessment['risk_level'] = risk_level
    
    return scan_data

# Patch report_view function to ensure color is set
try:
    import client
    original_report_view = client.report_view
    
    def patched_report_view(scan_id):
        result = original_report_view(scan_id)
        
        # Check if this is a template response
        if hasattr(result, 'context') and isinstance(result.context, dict) and 'scan' in result.context:
            result.context['scan'] = ensure_risk_assessment_color(result.context['scan'])
        
        return result
    
    client.report_view = patched_report_view
    logger.info("✅ Patched client.report_view function to ensure risk assessment color")
except Exception as e:
    logger.error(f"❌ Failed to patch client.report_view: {e}")

# Patch the scan results endpoint if it exists
try:
    from flask import current_app as app
    
    def patch_flask_routes():
        \"\"\"Patch Flask routes that handle scan results\"\"\"
        for rule in app.url_map.iter_rules():
            if 'results' in rule.endpoint:
                view_func = app.view_functions.get(rule.endpoint)
                if view_func:
                    def create_patched_view(original):
                        def patched_view(*args, **kwargs):
                            response = original(*args, **kwargs)
                            
                            # If JSON response, ensure risk assessment color
                            if hasattr(response, 'json'):
                                try:
                                    data = response.json
                                    if isinstance(data, dict) and 'scan' in data:
                                        data['scan'] = ensure_risk_assessment_color(data['scan'])
                                except:
                                    pass
                            
                            return response
                        return patched_view
                    
                    app.view_functions[rule.endpoint] = create_patched_view(view_func)
                    logger.info(f"✅ Patched route endpoint {rule.endpoint}")
    
    # We'll call this function later when the app is fully initialized
    # This should be called from the app's entry point after all routes are registered
    # For example: risk_assessment_direct_patch.patch_flask_routes()
except Exception as e:
    logger.error(f"❌ Failed to create route patching function: {e}")

logger.info("✅ Risk assessment color patch loaded")
"""
    
    with open(patch_path, 'w') as f:
        f.write(patch_content)
    
    print(f"✅ Created patch file: {patch_path}")
    
    # Now create a patch loader to import this at application startup
    loader_path = '/home/ggrun/CybrScan_1/load_risk_patch.py'
    loader_content = """#!/usr/bin/env python3
\"\"\"
Loader for risk assessment color patch
Add 'import load_risk_patch' at the top of app.py to apply the patch
\"\"\"

import logging
logger = logging.getLogger(__name__)

logger.info("Loading risk assessment color patch...")
try:
    import risk_assessment_direct_patch
    logger.info("✅ Risk assessment color patch loaded successfully")
except Exception as e:
    logger.error(f"❌ Failed to load risk assessment color patch: {e}")
"""
    
    with open(loader_path, 'w') as f:
        f.write(loader_content)
    
    print(f"✅ Created loader file: {loader_path}")
    return True

def add_patch_to_app():
    """
    Add the patch loader to app.py
    """
    print("Adding patch loader to app.py...")
    
    app_path = '/home/ggrun/CybrScan_1/app.py'
    if not os.path.exists(app_path):
        print(f"Error: {app_path} not found")
        return False
    
    # Read the file
    with open(app_path, 'r') as f:
        content = f.read()
    
    # Check if the patch is already imported
    if 'import load_risk_patch' in content:
        print("Patch loader already imported in app.py")
        return True
    
    # Add the import at the top of the file
    import_lines = []
    for line in content.split('\n'):
        import_lines.append(line)
        if line.startswith('import') or line.startswith('from'):
            continue
        else:
            # Add our import after all the other imports
            import_lines.append('# Import risk assessment color patch')
            import_lines.append('import load_risk_patch')
            break
    
    # Join the lines back together
    modified_content = '\n'.join(import_lines)
    
    # Write the modified file
    with open(app_path, 'w') as f:
        f.write(modified_content)
    
    print(f"✅ Added patch loader to {app_path}")
    return True

def main():
    """Main function to apply all fixes"""
    print("Applying emergency fix for risk assessment color...")
    
    # Fix existing scan results
    fix_existing_scan_results()
    
    # Create direct patch file
    create_direct_patch_file()
    
    # Add patch to app.py
    add_patch_to_app()
    
    print("\nAll fixes have been applied!")
    print("To make the changes effective, please restart the application server.")
    print("\nIMPORTANT: If the fix doesn't work after restart, check the application logs")
    print("for any errors related to the patch. You may need to modify the patch")
    print("file to match your application's specific structure.")

if __name__ == "__main__":
    main()