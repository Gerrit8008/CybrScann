#!/usr/bin/env python3
"""
Direct fix for scan records in client databases
Updates scan results to include proper risk assessment colors
"""

import os
import sys
import json
import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_color_for_score(score):
    """Get appropriate color based on score"""
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

def update_scan_records_in_database():
    """
    Update scan records in all client databases to include risk assessment color
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
            
            # Check if scans table exists and has scan_results column
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scans'")
            if not cursor.fetchone():
                logger.warning(f"No scans table in {db_file}, skipping")
                conn.close()
                continue
            
            # Get columns to check if scan_results column exists
            cursor.execute("PRAGMA table_info(scans)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'scan_results' not in column_names:
                logger.warning(f"No scan_results column in {db_file}, skipping")
                conn.close()
                continue
            
            # Get scan records with JSON results
            cursor.execute("SELECT id, scan_id, scan_results, security_score FROM scans WHERE scan_results IS NOT NULL")
            scans = cursor.fetchall()
            
            if not scans:
                logger.info(f"No scan records with scan_results found in {db_file}")
                conn.close()
                continue
            
            # Update each scan record
            db_updates = 0
            for scan_row in scans:
                scan_id = scan_row[0]
                scan_uid = scan_row[1]
                scan_results_json = scan_row[2]
                security_score = scan_row[3]
                
                if not scan_results_json or not scan_results_json.strip():
                    continue
                
                try:
                    # Parse JSON
                    scan_data = json.loads(scan_results_json)
                    modified = False
                    
                    # Check if risk_assessment exists
                    if 'risk_assessment' in scan_data and isinstance(scan_data['risk_assessment'], dict):
                        risk_assessment = scan_data['risk_assessment']
                        
                        # Add color if missing
                        if 'color' not in risk_assessment:
                            score = risk_assessment.get('overall_score', security_score)
                            if not isinstance(score, (int, float)):
                                score = security_score if isinstance(security_score, (int, float)) else 75
                            
                            risk_assessment['color'] = get_color_for_score(score)
                            modified = True
                    else:
                        # Create risk assessment if missing
                        score = security_score if isinstance(security_score, (int, float)) else 75
                        
                        scan_data['risk_assessment'] = {
                            'overall_score': score,
                            'risk_level': 'Medium' if 50 <= score < 80 else 'Low' if score >= 80 else 'High',
                            'color': get_color_for_score(score),
                            'component_scores': {
                                'network': score,
                                'web': score,
                                'email': score,
                                'system': score
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
    logger.info("Applying direct fix for scan records...")
    
    # Update scan records in all databases
    update_scan_records_in_database()
    
    logger.info("Fix has been applied!")
    logger.info("To make the changes effective, please restart the application server.")

if __name__ == "__main__":
    main()