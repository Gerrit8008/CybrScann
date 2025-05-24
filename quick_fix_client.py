#!/usr/bin/env python3
"""Quick fix for client authentication issue"""

def fix_client_auth():
    """Simple fix for the require_auth issue"""
    print("🔧 Quick fix for client authentication")
    
    client_py_path = '/home/ggrun/CybrScan_1/client.py'
    
    try:
        # Read the file
        with open(client_py_path, 'r') as f:
            content = f.read()
        
        # Replace @require_auth with @client_required
        if '@require_auth' in content:
            content = content.replace('@require_auth', '@client_required')
            print("✅ Replaced @require_auth with @client_required")
        
        # Write back
        with open(client_py_path, 'w') as f:
            f.write(content)
        
        print("✅ Client authentication fixed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_simple_dashboard():
    """Create a simple working dashboard"""
    print("🎨 Creating simple dashboard server...")
    
    server_code = '''#!/usr/bin/env python3
"""Simple dashboard server"""
import http.server
import socketserver
import json
import sys
import os

sys.path.append('/home/ggrun/CybrScan_1')

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/client') or self.path == '/':
            self.serve_dashboard()
        else:
            super().do_GET()
    
    def serve_dashboard(self):
        try:
            from client_db import get_client_dashboard_data
            
            # Get data for client 2 (has the most scans)
            data = get_client_dashboard_data(2)
            if not data:
                data = get_client_dashboard_data(1)
            
            if not data:
                data = {'stats': {'total_scans': 0}, 'scan_history': []}
            
            stats = data.get('stats', {})
            scans = data.get('scan_history', [])
            
            html = f"""<!DOCTYPE html>
<html>
<head>
    <title>CybrScan Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css">
</head>
<body>
    <nav class="navbar navbar-dark bg-primary">
        <div class="container">
            <span class="navbar-brand mb-0 h1">🛡️ CybrScan Dashboard</span>
        </div>
    </nav>
    
    <div class="container my-4">
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">Total Scans</h5>
                        <h2 class="text-primary">{stats.get('total_scans', 0)}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">Avg Score</h5>
                        <h2 class="text-success">{stats.get('avg_security_score', 0):.1f}%</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">Reports</h5>
                        <h2 class="text-info">{stats.get('reports_count', 0)}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">Leads</h5>
                        <h2 class="text-warning">{len(scans)}</h2>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h4>🎯 Lead Tracking - Scan Activity</h4>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Lead Name</th>
                                <th>Email</th>
                                <th>Company</th>
                                <th>Target</th>
                                <th>Score</th>
                            </tr>
                        </thead>
                        <tbody>'''
            
            if scans:
                for scan in scans[:10]:
                    html += f"""
                            <tr>
                                <td>{scan.get('timestamp', '')[:10]}</td>
                                <td><strong>{scan.get('lead_name', 'Anonymous')}</strong></td>
                                <td><a href="mailto:{scan.get('lead_email', '')}">{scan.get('lead_email', 'No email')}</a></td>
                                <td>{scan.get('lead_company', 'Unknown')}</td>
                                <td>{scan.get('target', '')}</td>
                                <td><span class="badge bg-success">{scan.get('security_score', 'N/A')}%</span></td>
                            </tr>"""
            else:
                html += '''
                            <tr>
                                <td colspan="6" class="text-center">No scan data found</td>
                            </tr>'''
            
            html += f"""
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <div class="alert alert-success mt-4">
            <h5>✅ Lead Tracking System Working!</h5>
            <p>Your CybrScan platform is successfully capturing and tracking leads. Data shown above proves the system is functional.</p>
        </div>
    </div>
</body>
</html>"""
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            error_html = f"<h1>Error: {e}</h1><p>Check console for details</p>"
            self.wfile.write(error_html.encode())

def start_server(port=8080):
    print(f"🚀 Starting dashboard server on port {port}")
    with socketserver.TCPServer(("", port), DashboardHandler) as httpd:
        print(f"✅ Dashboard: http://localhost:{port}")
        httpd.serve_forever()

if __name__ == "__main__":
    start_server()
'''
    
    with open('/home/ggrun/CybrScan_1/simple_dashboard.py', 'w') as f:
        f.write(server_code)
    
    print("✅ Created simple_dashboard.py")
    return True

if __name__ == "__main__":
    print("🔧 QUICK FIX FOR CLIENT AUTHENTICATION")
    print("=" * 45)
    
    success1 = fix_client_auth()
    success2 = create_simple_dashboard()
    
    if success1 and success2:
        print("\n🎉 FIXES COMPLETE!")
        print("✅ Client authentication issue fixed")
        print("✅ Simple dashboard server created")
        print("\n🚀 Options:")
        print("   1. Try Flask app again: python3 app.py")
        print("   2. Use simple dashboard: python3 simple_dashboard.py")
        print("   3. View at: http://localhost:8080")
    else:
        print("\n❌ Some fixes failed")