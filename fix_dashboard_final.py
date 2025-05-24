#!/usr/bin/env python3
"""Final comprehensive fix for dashboard scan display issues"""

import sys
import os
sys.path.append('/home/ggrun/CybrScan_1')

import sqlite3
from client_db import get_db_connection, get_client_dashboard_data

def fix_dashboard_issues():
    print("🔧 FINAL DASHBOARD FIX")
    print("=" * 40)
    
    # 1. Check all clients and their data
    print("📊 Step 1: Checking all clients...")
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, user_id, business_name, active FROM clients WHERE active = 1")
    clients = cursor.fetchall()
    
    for client in clients:
        client_dict = dict(client)
        client_id = client_dict['id']
        print(f"   Client {client_id}: {client_dict['business_name']} (User: {client_dict['user_id']})")
        
        # Check dashboard data for each
        try:
            dashboard_data = get_client_dashboard_data(client_id)
            if dashboard_data:
                scan_count = len(dashboard_data['scan_history'])
                total_scans = dashboard_data['stats']['total_scans']
                print(f"     ✅ Dashboard data: {scan_count} in history, {total_scans} total scans")
                
                if scan_count > 0:
                    first_scan = dashboard_data['scan_history'][0]
                    print(f"     📋 Latest: {first_scan.get('lead_name', 'N/A')} | {first_scan.get('lead_email', 'N/A')}")
            else:
                print(f"     ❌ No dashboard data")
        except Exception as e:
            print(f"     ❌ Error: {e}")
    
    conn.close()
    
    # 2. Check for template issues
    print(f"\n🎨 Step 2: Checking template structure...")
    template_path = '/home/ggrun/CybrScan_1/templates/client/client-dashboard.html'
    
    if os.path.exists(template_path):
        with open(template_path, 'r') as f:
            content = f.read()
            
        # Check for key template elements
        checks = [
            ('scan_history variable check', '{% if scan_history %}'),
            ('Table structure', '<table class="table table-hover mb-0">'),
            ('Lead name column', 'scan.get(\'lead_name\''),
            ('Email column', 'scan.get(\'lead_email\''),
            ('Company column', 'scan.get(\'lead_company\''),
            ('Debug message', 'DEBUG: No scan_history variable found')
        ]
        
        for check_name, pattern in checks:
            if pattern in content:
                print(f"     ✅ {check_name}: Found")
            else:
                print(f"     ❌ {check_name}: Missing - {pattern}")
                
    # 3. Create test route for debugging
    print(f"\n🔍 Step 3: Creating debug test route...")
    debug_route_code = '''
@client_bp.route('/debug-dashboard')
@require_auth
def debug_dashboard(user):
    """Debug route to test dashboard data"""
    try:
        from client_db import get_client_dashboard_data, get_db_connection
        import sqlite3
        
        # Get user's client
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients WHERE user_id = ? AND active = 1", (user['id'],))
        client_row = cursor.fetchone()
        conn.close()
        
        if not client_row:
            return f"<h1>DEBUG: No client found for user {user['id']}</h1>"
            
        client = dict(client_row)
        client_id = client['id']
        
        # Get dashboard data
        dashboard_data = get_client_dashboard_data(client_id)
        
        if not dashboard_data:
            return f"<h1>DEBUG: No dashboard data for client {client_id}</h1>"
            
        scan_history = dashboard_data['scan_history']
        
        # Create debug HTML
        html = f"""
        <html>
        <head>
            <title>Dashboard Debug</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-4">
                <h1>🔍 Dashboard Debug Results</h1>
                <div class="alert alert-info">
                    <h4>User Info</h4>
                    <p>User ID: {user['id']}<br>
                    Username: {user['username']}<br>
                    Client ID: {client_id}<br>
                    Business: {client['business_name']}</p>
                </div>
                
                <div class="alert alert-success">
                    <h4>Dashboard Stats</h4>
                    <p>Total Scans: {dashboard_data['stats']['total_scans']}<br>
                    Scan History Count: {len(scan_history)}<br>
                    Avg Security Score: {dashboard_data['stats']['avg_security_score']}</p>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h4>Scan History Data ({len(scan_history)} items)</h4>
                    </div>
                    <div class="card-body">
                        {"<p>No scan history found!</p>" if not scan_history else ""}
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Scan ID</th>
                                    <th>Lead Name</th>
                                    <th>Email</th>
                                    <th>Company</th>
                                    <th>Target</th>
                                    <th>Score</th>
                                    <th>Timestamp</th>
                                </tr>
                            </thead>
                            <tbody>
        """
        
        for scan in scan_history[:10]:  # Show first 10
            html += f"""
                                <tr>
                                    <td>{scan.get('scan_id', 'N/A')[:8]}...</td>
                                    <td>{scan.get('lead_name', 'N/A')}</td>
                                    <td>{scan.get('lead_email', 'N/A')}</td>
                                    <td>{scan.get('lead_company', 'N/A')}</td>
                                    <td>{scan.get('target', 'N/A')}</td>
                                    <td>{scan.get('security_score', 'N/A')}</td>
                                    <td>{scan.get('timestamp', 'N/A')}</td>
                                </tr>
            """
            
        html += """
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="mt-4">
                    <a href="/client/dashboard" class="btn btn-primary">Back to Dashboard</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
        
    except Exception as e:
        import traceback
        return f"<h1>ERROR: {str(e)}</h1><pre>{traceback.format_exc()}</pre>"
'''
    
    # Add debug route to client.py
    client_py_path = '/home/ggrun/CybrScan_1/client.py'
    
    with open(client_py_path, 'r') as f:
        client_content = f.read()
    
    if '@client_bp.route(\'/debug-dashboard\')' not in client_content:
        # Add debug route before the last line
        lines = client_content.split('\n')
        
        # Find the end of the file
        insert_pos = len(lines) - 1
        while insert_pos > 0 and lines[insert_pos].strip() == '':
            insert_pos -= 1
            
        # Insert debug route
        debug_lines = debug_route_code.strip().split('\n')
        for i, line in enumerate(debug_lines):
            lines.insert(insert_pos + i, line)
            
        with open(client_py_path, 'w') as f:
            f.write('\n'.join(lines))
        
        print(f"     ✅ Debug route added to client.py")
        print(f"     🌐 Access via: /client/debug-dashboard")
    else:
        print(f"     ✅ Debug route already exists")
    
    print(f"\n✅ FINAL FIX COMPLETE!")
    print(f"📋 What to do next:")
    print(f"   1. Restart the Flask app")
    print(f"   2. Go to /client/debug-dashboard to see raw data")
    print(f"   3. Clear browser cache (Ctrl+F5)")
    print(f"   4. Check /client/dashboard to see if scans appear")
    print(f"   5. If still no scans, check the debug route data vs dashboard")

if __name__ == "__main__":
    fix_dashboard_issues()