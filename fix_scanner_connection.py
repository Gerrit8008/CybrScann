#!/usr/bin/env python3
"""
Fix script for scanner_routes.py to use the correct database connection
"""

import os
import sqlite3

def fix_scanner_connection():
    """Fix the scanner_routes.py file to use the correct database connection"""
    scanner_routes_path = '/home/ggrun/CybrScan_1/scanner_routes.py'
    
    with open(scanner_routes_path, 'r') as f:
        content = f.read()
    
    # Update the embed route to use the correct database connection
    embed_route = """
@scanner_bp.route('/<scanner_id>/embed')
def scanner_embed(scanner_id):
    '''Embed view for scanner results'''
    try:
        # Connect directly to client_scanner.db instead of using get_db_connection()
        conn = sqlite3.connect('client_scanner.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get scanner details
        cursor.execute(
            "SELECT * FROM scanners WHERE scanner_id = ?", 
            (scanner_id,)
        )
        scanner = cursor.fetchone()
        
        if not scanner:
            return render_template('error.html', message="Scanner not found"), 404
        
        # Get client info
        cursor.execute(
            "SELECT * FROM clients WHERE id = ?", 
            (scanner['client_id'],)
        )
        client = cursor.fetchone()
        
        if not client:
            return render_template('error.html', message="Client not found"), 404
        
        # Get most recent scan
        cursor.execute(
            "SELECT * FROM scan_history WHERE scanner_id = ? ORDER BY created_at DESC LIMIT 1", 
            (scanner_id,)
        )
        scan = cursor.fetchone()
        
        # Format scan data for template
        scan_data = {}
        if scan:
            # Parse scan data
            import json
            scan_data = json.loads(scan['results'])
            
            # Format dates
            from datetime import datetime
            created_at = datetime.fromisoformat(scan['created_at'])
            scan_data['formatted_date'] = created_at.strftime('%B %d, %Y')
            scan_data['formatted_time'] = created_at.strftime('%I:%M %p')
            
            # Add scan result to data
            scan_data['result'] = 'completed'
            scan_data['risk_assessment'] = scan['security_score']
            
            # Get risk assessment color
            risk_score = int(scan['security_score'])
            if risk_score < 30:
                risk_color = "green"
            elif risk_score < 70:
                risk_color = "yellow"
            else:
                risk_color = "red"
            
            scan_data['risk_color'] = risk_color
        
        conn.close()
        
        # Render embed template
        return render_template(
            'scanner_template.html',
            scanner=scanner,
            client=client,
            scan_data=scan_data,
            standalone=True
        )
        
    except Exception as e:
        return render_template('error.html', message=f"Error: {str(e)}"), 500
"""
    
    # Replace the existing embed route with our fixed version
    start_index = content.find('@scanner_bp.route(\'/<scanner_id>/embed\')')
    if start_index == -1:
        print("Could not find the scanner embed route in scanner_routes.py")
        return False
    
    # Find the end of the function
    end_index = content.find('\n\n', start_index)
    if end_index == -1:
        # If we can't find two newlines, try to find the end of the file
        end_index = len(content)
    
    # Replace the function
    new_content = content[:start_index] + embed_route + content[end_index:]
    
    with open(scanner_routes_path, 'w') as f:
        f.write(new_content)
    
    print("Updated scanner_routes.py with the correct database connection")
    return True

if __name__ == "__main__":
    print("Fixing scanner database connection issue...")
    fix_scanner_connection()
    print("Done!")