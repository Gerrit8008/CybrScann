#!/usr/bin/env python3
"""
Fix script for scanner_routes.py to add the missing scanner embed route
and fix the error.html template URL.
"""

import os

def fix_scanner_routes():
    """Add the missing /scanner/<scanner_id>/embed route to scanner_routes.py"""
    scanner_routes_path = '/home/ggrun/CybrScan_1/scanner_routes.py'
    
    with open(scanner_routes_path, 'r') as f:
        content = f.read()
    
    # Check if the embed route already exists
    if '@scanner_bp.route(\'/<scanner_id>/embed\')' in content:
        print("Embed route already exists. No changes needed.")
        return
    
    # Add the embed route function at the end of the file
    embed_route = """
@scanner_bp.route('/<scanner_id>/embed')
def scanner_embed(scanner_id):
    '''Embed view for scanner results'''
    try:
        # Get database connection
        conn = get_db_connection()
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
            "SELECT * FROM scans WHERE scanner_id = ? ORDER BY created_at DESC LIMIT 1", 
            (scanner_id,)
        )
        scan = cursor.fetchone()
        
        # Format scan data for template
        scan_data = {}
        if scan:
            # Parse scan data
            import json
            scan_data = json.loads(scan['scan_data'])
            
            # Format dates
            from datetime import datetime
            created_at = datetime.fromisoformat(scan['created_at'])
            scan_data['formatted_date'] = created_at.strftime('%B %d, %Y')
            scan_data['formatted_time'] = created_at.strftime('%I:%M %p')
            
            # Add scan result to data
            scan_data['result'] = scan['result']
            scan_data['risk_assessment'] = scan['risk_assessment']
            
            # Get risk assessment color
            risk_score = int(scan['risk_assessment'])
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
    
    # Add the embed route to the file
    content = content.rstrip() + embed_route
    
    with open(scanner_routes_path, 'w') as f:
        f.write(content)
    
    print("Added scanner embed route to scanner_routes.py")

def fix_error_template():
    """Fix the error.html template URL for the home button"""
    error_template_path = '/home/ggrun/CybrScan_1/templates/error.html'
    
    with open(error_template_path, 'r') as f:
        content = f.read()
    
    # Replace the incorrect URL with the correct one
    if 'url_for(\'main.landing_page\')' in content:
        content = content.replace('url_for(\'main.landing_page\')', 'url_for(\'index\')')
        
        with open(error_template_path, 'w') as f:
            f.write(content)
        
        print("Fixed error.html template URL")
    else:
        print("Error template URL already fixed or using a different pattern")

if __name__ == "__main__":
    print("Fixing scanner embed route and error template...")
    fix_scanner_routes()
    fix_error_template()
    print("Done!")