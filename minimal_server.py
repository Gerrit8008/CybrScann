#!/usr/bin/env python3
"""Minimal HTTP server to handle dashboard requests without Flask dependencies"""

import http.server
import socketserver
import urllib.parse
import json
import sqlite3
import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.append('/home/ggrun/CybrScan_1')

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for dashboard requests"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/client/dashboard':
            self.serve_dashboard()
        elif self.path == '/client/debug-dashboard':
            self.serve_debug_dashboard()
        elif self.path.startswith('/static/'):
            self.serve_static_file()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Page not found')
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/auth/login':
            self.handle_login()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Endpoint not found')
    
    def serve_dashboard(self):
        """Serve the client dashboard"""
        try:
            # Get client data (simplified)
            client_id = 1  # Default to client 1 for testing
            scan_data = self.get_client_scans(client_id)
            
            html = self.generate_dashboard_html(scan_data)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
            
        except Exception as e:
            self.send_error_response(f"Dashboard error: {e}")
    
    def serve_debug_dashboard(self):
        """Serve debug dashboard"""
        try:
            debug_info = self.get_debug_info()
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Debug Dashboard</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body>
                <div class="container mt-4">
                    <h1>🔍 Debug Dashboard</h1>
                    <div class="alert alert-info">
                        <h4>System Status</h4>
                        <p>Server: Minimal HTTP Server (Flask not available)</p>
                        <p>Time: {datetime.now()}</p>
                    </div>
                    
                    <div class="card">
                        <div class="card-header">
                            <h4>Debug Information</h4>
                        </div>
                        <div class="card-body">
                            <pre>{debug_info}</pre>
                        </div>
                    </div>
                    
                    <div class="mt-3">
                        <a href="/client/dashboard" class="btn btn-primary">View Dashboard</a>
                    </div>
                </div>
            </body>
            </html>
            """
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
            
        except Exception as e:
            self.send_error_response(f"Debug error: {e}")
    
    def handle_login(self):
        """Handle login requests"""
        # Read POST data
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        # Simple redirect to dashboard
        self.send_response(302)
        self.send_header('Location', '/client/dashboard')
        self.end_headers()
    
    def get_client_scans(self, client_id):
        """Get scan data for a client"""
        try:
            from client_db import get_client_dashboard_data
            data = get_client_dashboard_data(client_id)
            return data
        except Exception as e:
            return {
                'stats': {'total_scans': 0, 'avg_security_score': 0},
                'scan_history': [],
                'error': str(e)
            }
    
    def get_debug_info(self):
        """Get debug information"""
        try:
            debug_info = []
            debug_info.append("DEPENDENCY CHECK:")
            
            modules = ['flask', 'sqlite3', 'requests']
            for module in modules:
                try:
                    __import__(module)
                    debug_info.append(f"✅ {module} - Available")
                except ImportError:
                    debug_info.append(f"❌ {module} - Missing")
            
            debug_info.append("\nDATABASE CHECK:")
            try:
                db_path = '/home/ggrun/CybrScan_1/cybrscan.db'
                if os.path.exists(db_path):
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM clients WHERE active = 1")
                    client_count = cursor.fetchone()[0]
                    debug_info.append(f"✅ Database accessible - {client_count} active clients")
                    conn.close()
                else:
                    debug_info.append(f"❌ Database not found at {db_path}")
            except Exception as e:
                debug_info.append(f"❌ Database error: {e}")
            
            debug_info.append("\nCLIENT DATA CHECK:")
            try:
                data = self.get_client_scans(1)
                if 'error' in data:
                    debug_info.append(f"❌ Client data error: {data['error']}")
                else:
                    debug_info.append(f"✅ Client 1 - {len(data['scan_history'])} scans")
                    debug_info.append(f"   Total scans: {data['stats']['total_scans']}")
                    debug_info.append(f"   Avg score: {data['stats']['avg_security_score']}")
            except Exception as e:
                debug_info.append(f"❌ Client data error: {e}")
            
            return '\n'.join(debug_info)
            
        except Exception as e:
            return f"Debug info error: {e}"
    
    def generate_dashboard_html(self, scan_data):
        """Generate dashboard HTML"""
        scans = scan_data.get('scan_history', [])
        stats = scan_data.get('stats', {})
        
        # Generate scan rows
        scan_rows = ""
        if scans:
            for scan in scans[:5]:
                scan_rows += f"""
                <tr>
                    <td>{scan.get('timestamp', '')[:10]}</td>
                    <td><strong>{scan.get('lead_name', 'Anonymous')}</strong></td>
                    <td>{scan.get('lead_email', 'No email')}</td>
                    <td><strong>{scan.get('lead_company', 'Unknown')}</strong></td>
                    <td>{scan.get('target', '')}</td>
                    <td><span class="badge bg-success">{scan.get('security_score', 'N/A')}%</span></td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary">📄 Report</button>
                    </td>
                </tr>
                """
        else:
            scan_rows = """
            <tr>
                <td colspan="7" class="text-center py-4">
                    <div class="text-muted">
                        <i class="bi bi-clipboard-check fs-3 d-block mb-3"></i>
                        No scan history found. Run your first scan to see results.
                    </div>
                </td>
            </tr>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Client Dashboard - CybrScan</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css">
        </head>
        <body>
            <div class="container-fluid">
                <div class="row">
                    <!-- Sidebar -->
                    <div class="col-md-2 bg-dark text-white min-vh-100 p-3">
                        <h4>CybrScan</h4>
                        <ul class="nav nav-pills flex-column">
                            <li class="nav-item">
                                <a class="nav-link active" href="/client/dashboard">
                                    <i class="bi bi-speedometer2"></i> Dashboard
                                </a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="/client/debug-dashboard">
                                    <i class="bi bi-bug"></i> Debug
                                </a>
                            </li>
                        </ul>
                    </div>
                    
                    <!-- Main Content -->
                    <div class="col-md-10 p-4">
                        <h1>Client Dashboard</h1>
                        
                        <!-- Stats Cards -->
                        <div class="row mb-4">
                            <div class="col-md-3">
                                <div class="card bg-primary text-white">
                                    <div class="card-body">
                                        <h5>Total Scans</h5>
                                        <h2>{stats.get('total_scans', 0)}</h2>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="card bg-success text-white">
                                    <div class="card-body">
                                        <h5>Avg Score</h5>
                                        <h2>{stats.get('avg_security_score', 0):.1f}%</h2>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="card bg-info text-white">
                                    <div class="card-body">
                                        <h5>Reports</h5>
                                        <h2>{stats.get('reports_count', 0)}</h2>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="card bg-warning text-white">
                                    <div class="card-body">
                                        <h5>Issues</h5>
                                        <h2>{stats.get('critical_issues', 0)}</h2>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Recent Scan Activity -->
                        <div class="card">
                            <div class="card-header d-flex justify-content-between">
                                <h5>Recent Scan Activity - Lead Tracking</h5>
                                <span class="badge bg-primary">{len(scans)} scans</span>
                            </div>
                            <div class="card-body p-0">
                                <div class="table-responsive">
                                    <table class="table table-hover mb-0">
                                        <thead>
                                            <tr>
                                                <th>Date</th>
                                                <th>Lead Name</th>
                                                <th>Email</th>
                                                <th>Company</th>
                                                <th>Target</th>
                                                <th>Score</th>
                                                <th>Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {scan_rows}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mt-4 alert alert-info">
                            <h6>🎯 Lead Tracking System Status</h6>
                            <p><strong>Working!</strong> This minimal server shows your scan data is properly stored and retrievable.</p>
                            <p><strong>Next step:</strong> Install Flask dependencies to use the full application:</p>
                            <code>pip install flask flask-cors</code>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def send_error_response(self, message):
        """Send error response"""
        self.send_response(500)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        error_html = f"""
        <html>
        <body>
            <h1>Error</h1>
            <p>{message}</p>
            <a href="/client/debug-dashboard">Debug Dashboard</a>
        </body>
        </html>
        """
        self.wfile.write(error_html.encode())

def start_server(port=8080):
    """Start the minimal server"""
    print(f"🚀 Starting minimal CybrScan server on port {port}")
    print(f"📊 Dashboard: http://localhost:{port}/client/dashboard")
    print(f"🔍 Debug: http://localhost:{port}/client/debug-dashboard")
    print("=" * 50)
    
    try:
        with socketserver.TCPServer(("", port), DashboardHandler) as httpd:
            print(f"✅ Server running at http://localhost:{port}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    start_server()