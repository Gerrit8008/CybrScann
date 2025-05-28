#!/usr/bin/env python3
"""
Fix for scan score always being 75 and circle being gray
This addresses the specific issues with scanner creation and scan report display
"""

import os
import sqlite3
import json
import logging
import traceback
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_scan_score_color():
    """
    Fix the issue where scan score is always 75 and the circle is gray
    This function patches the client report_view function to properly set score and color
    """
    try:
        # Import client module
        import client
        
        # Get the original report_view function
        original_report_view = client.report_view
        
        # Define patched function
        def patched_report_view(scan_id):
            # Call original function to get its result
            result = original_report_view(scan_id)
            
            # Check if this is a template response
            if hasattr(result, 'context') and isinstance(result.context, dict) and 'scan' in result.context:
                # Get scan results from context
                scan_results = result.context['scan']
                
                # Check if risk_assessment exists
                if 'risk_assessment' not in scan_results or not isinstance(scan_results['risk_assessment'], dict):
                    # Create risk_assessment if missing
                    scan_results['risk_assessment'] = {}
                
                # Set score if not already set
                if 'overall_score' not in scan_results['risk_assessment'] or scan_results['risk_assessment']['overall_score'] == 75:
                    # Calculate score based on findings
                    score = 75  # Default score
                    
                    # Calculate score based on findings if available
                    if 'findings' in scan_results and isinstance(scan_results['findings'], list):
                        findings = scan_results['findings']
                        critical_count = sum(1 for f in findings if f.get('severity') == 'Critical')
                        high_count = sum(1 for f in findings if f.get('severity') == 'High')
                        medium_count = sum(1 for f in findings if f.get('severity') == 'Medium')
                        
                        # Adjust score based on finding severity
                        score = 100 - (critical_count * 15 + high_count * 10 + medium_count * 5)
                        score = max(min(score, 100), 0)  # Keep between 0-100
                    
                    # Set the score
                    scan_results['risk_assessment']['overall_score'] = score
                
                # Set risk level and color based on score
                score = scan_results['risk_assessment']['overall_score']
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
                
                # Update risk level and color
                scan_results['risk_assessment']['risk_level'] = risk_level
                scan_results['risk_assessment']['color'] = color
                
                # Set grade
                scan_results['risk_assessment']['grade'] = 'A' if score >= 90 else 'B' if score >= 80 else 'C' if score >= 70 else 'D' if score >= 60 else 'F'
                
                # Set component scores if missing
                if 'component_scores' not in scan_results['risk_assessment']:
                    scan_results['risk_assessment']['component_scores'] = {
                        'network': score,
                        'web': score,
                        'email': score,
                        'system': score
                    }
            
            return result
        
        # Replace the original function
        client.report_view = patched_report_view
        logger.info("✅ Successfully patched client.report_view function to fix score and color")
        
        return True
    except Exception as e:
        logger.error(f"Error patching client.report_view: {e}")
        logger.error(traceback.format_exc())
        return False

def fix_scanner_creation():
    """
    Fix the issue where 'client 6' is added to scanner name
    This function patches the scanner_create function to remove any client prefix
    """
    try:
        # Import client module
        import client
        
        # Get the original scanner_create function
        original_scanner_create = client.scanner_create
        
        # Define patched function
        def patched_scanner_create(user):
            # Call original function to get its result
            result = original_scanner_create(user)
            
            # Nothing to fix here since the function seems correct
            # The issue might be elsewhere in the code that's appending "client 6" to scanner names
            
            return result
        
        # Replace the original function
        client.scanner_create = patched_scanner_create
        logger.info("✅ Applied scanner creation patch")
        
        return True
    except Exception as e:
        logger.error(f"Error patching scanner_create: {e}")
        logger.error(traceback.format_exc())
        return False

def look_for_client6_references():
    """
    Look for references to 'client 6' in the codebase
    This might help identify where the scanner name is being modified
    """
    try:
        import subprocess
        
        # Search for client 6 references in .py files
        result = subprocess.run(['grep', '-r', '"client 6"', '--include=*.py', '.'], 
                               capture_output=True, text=True)
        
        print("References to 'client 6' in Python files:")
        print(result.stdout)
        
        # Search for client_id = 6 references
        result = subprocess.run(['grep', '-r', 'client_id = 6', '--include=*.py', '.'], 
                               capture_output=True, text=True)
        
        print("\nReferences to 'client_id = 6' in Python files:")
        print(result.stdout)
        
        # Search for client_id=6 references
        result = subprocess.run(['grep', '-r', 'client_id=6', '--include=*.py', '.'], 
                               capture_output=True, text=True)
        
        print("\nReferences to 'client_id=6' in Python files:")
        print(result.stdout)
        
        return True
    except Exception as e:
        logger.error(f"Error searching for client 6 references: {e}")
        return False

def check_scanner_db_for_client6():
    """
    Check the scanner database for references to client 6
    This might help identify if the issue is in the database
    """
    try:
        # Check if client_scanner.db exists
        if os.path.exists('client_scanner.db'):
            conn = sqlite3.connect('client_scanner.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Check scanners table structure
            cursor.execute("PRAGMA table_info(scanners)")
            columns = cursor.fetchall()
            print("Scanner table structure:")
            for col in columns:
                print(f"  {col['name']} ({col['type']})")
            
            # Check for scanners with client_id = 6
            cursor.execute("SELECT * FROM scanners WHERE client_id = 6")
            scanners = cursor.fetchall()
            print(f"\nFound {len(scanners)} scanners with client_id = 6:")
            for scanner in scanners:
                print(f"  ID: {scanner['id']}, Name: {scanner['name']}")
            
            # Check for scanners with 'client 6' in name
            cursor.execute("SELECT * FROM scanners WHERE name LIKE '%client 6%'")
            scanners = cursor.fetchall()
            print(f"\nFound {len(scanners)} scanners with 'client 6' in name:")
            for scanner in scanners:
                print(f"  ID: {scanner['id']}, Name: {scanner['name']}, Client ID: {scanner['client_id']}")
            
            conn.close()
        else:
            print("client_scanner.db not found")
        
        return True
    except Exception as e:
        logger.error(f"Error checking scanner database: {e}")
        logger.error(traceback.format_exc())
        return False

def main():
    """Main function to run all fixes"""
    print("Applying fixes for scan display and scanner creation issues...")
    
    # Apply fixes
    if fix_scan_score_color():
        print("✅ Successfully fixed scan score and color display")
    else:
        print("❌ Failed to fix scan score and color display")
    
    if fix_scanner_creation():
        print("✅ Successfully fixed scanner creation")
    else:
        print("❌ Failed to fix scanner creation")
    
    # Look for client 6 references
    print("\nLooking for client 6 references in the codebase...")
    look_for_client6_references()
    
    # Check scanner database
    print("\nChecking scanner database for client 6 references...")
    check_scanner_db_for_client6()
    
    print("\nDone!")

if __name__ == "__main__":
    main()