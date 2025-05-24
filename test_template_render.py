#!/usr/bin/env python3
"""Test actual template rendering with live data"""

import sys
import os
sys.path.append('/home/ggrun/CybrScan_1')

from flask import Flask, render_template_string
from client_db import get_client_dashboard_data

def test_template_render():
    print("🎨 TESTING TEMPLATE RENDERING")
    print("=" * 40)
    
    app = Flask(__name__)
    
    with app.app_context():
        # Get real dashboard data
        data = get_client_dashboard_data(2)
        
        if not data or not data['scan_history']:
            print("❌ No data to test with!")
            return
            
        # Test the exact template logic
        template_snippet = '''
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
                    {% if scan_history %}
                        {% for scan in scan_history[:5] %}
                        <tr>
                            <td>{{ scan.get('timestamp', '')[:10] if scan.get('timestamp') else 'Unknown' }}</td>
                            <td>{{ scan.get('lead_name', 'Anonymous') }}</td>
                            <td>{{ scan.get('lead_email', 'No email') }}</td>
                            <td>{{ scan.get('lead_company', 'Unknown') }}</td>
                            <td>{{ scan.get('target', '') }}</td>
                            <td>{{ scan.get('security_score', 'N/A') }}%</td>
                            <td>Actions</td>
                        </tr>
                        {% endfor %}
                    {% else %}
                        <tr>
                            <td colspan="7" class="text-center py-4">No scan history found.</td>
                        </tr>
                    {% endif %}
                </tbody>
            </table>
        </div>
        '''
        
        # Render with real data
        rendered = render_template_string(template_snippet, scan_history=data['scan_history'])
        
        print("✅ Template rendered successfully!")
        print("\n📄 RENDERED HTML:")
        print("-" * 50)
        
        # Clean up and show just the data rows
        lines = rendered.split('\n')
        in_tbody = False
        for line in lines:
            line = line.strip()
            if '<tbody>' in line:
                in_tbody = True
                continue
            elif '</tbody>' in line:
                break
            elif in_tbody and line and not line.startswith('<'):
                # This is likely data content
                if 'Unknown' not in line and 'No scan' not in line:
                    print(f"   {line}")
                    
        print("\n🔍 DETAILED ROW ANALYSIS:")
        print("-" * 30)
        
        for i, scan in enumerate(data['scan_history'][:3]):
            print(f"Row {i+1}:")
            print(f"  Date: {scan.get('timestamp', '')[:10] if scan.get('timestamp') else 'Unknown'}")
            print(f"  Lead: {scan.get('lead_name', 'Anonymous')}")
            print(f"  Email: {scan.get('lead_email', 'No email')}")
            print(f"  Company: {scan.get('lead_company', 'Unknown')}")
            print(f"  Target: {scan.get('target', '')}")
            print(f"  Score: {scan.get('security_score', 'N/A')}%")
            print()

if __name__ == "__main__":
    test_template_render()