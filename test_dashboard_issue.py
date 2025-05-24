#!/usr/bin/env python3
"""Direct test of dashboard route logic"""

import sys
import os
sys.path.append('/home/ggrun/CybrScan_1')

import sqlite3
from client_db import get_client_dashboard_data, get_db_connection

def test_client_lookup():
    """Test client lookup like the dashboard route does"""
    print("🔍 TESTING CLIENT DASHBOARD ROUTE LOGIC")
    print("=" * 50)
    
    # Test with client ID 2 (from our debug)
    user = {
        'id': 2,
        'username': 'testuser',
        'role': 'client'
    }
    
    # Simulate the route logic
    client = None
    client_id = None
    
    try:
        # Get user's client profile
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM clients WHERE user_id = ? AND active = 1", (user['id'],))
        client_row = cursor.fetchone()
        
        if client_row:
            client = dict(client_row)
            client_id = client['id']
            print(f"✅ Found client: ID={client_id}, Business={client.get('business_name', 'N/A')}")
        else:
            print(f"❌ No client found for user {user['id']}")
            conn.close()
            return
            
        conn.close()
        
        # Get dashboard data
        print(f"\n📊 Getting dashboard data for client {client_id}...")
        dashboard_data = get_client_dashboard_data(client_id)
        
        if dashboard_data:
            scan_history = dashboard_data['scan_history']
            stats = dashboard_data['stats']
            
            print(f"✅ Dashboard data retrieved:")
            print(f"   - Stats: {stats}")
            print(f"   - Scan history count: {len(scan_history)}")
            
            if scan_history:
                print(f"\n📋 First 3 scans that would be passed to template:")
                for i, scan in enumerate(scan_history[:3]):
                    print(f"   {i+1}. {scan.get('lead_name', 'Anonymous')} | {scan.get('lead_email', 'No email')} | {scan.get('target', 'No target')}")
                    
                print(f"\n🎯 Template variables that would be created:")
                template_vars = {
                    'scan_history': scan_history,
                    'total_scans': stats.get('total_scans', 0),
                    'client_stats': stats
                }
                
                print(f"   - scan_history: {len(template_vars['scan_history'])} items")
                print(f"   - total_scans: {template_vars['total_scans']}")
                print(f"   - Has scan data: {bool(template_vars['scan_history'])}")
                
                # Test template logic
                print(f"\n🔍 Template condition test:")
                print(f"   - if scan_history: {bool(template_vars['scan_history'])}")
                print(f"   - scan_history[:5]: {len(template_vars['scan_history'][:5])} items")
                
            else:
                print("❌ No scan history in dashboard data!")
                
        else:
            print("❌ No dashboard data returned!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_client_lookup()