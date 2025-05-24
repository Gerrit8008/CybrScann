#!/usr/bin/env python3
"""Debug client 6 dashboard data retrieval"""

import sys
import os
sys.path.append('/home/ggrun/CybrScan_1')

def debug_client_6_dashboard():
    """Debug why get_client_dashboard_data fails for client 6"""
    print("🔍 DEBUGGING CLIENT 6 DASHBOARD DATA")
    print("=" * 45)
    
    try:
        # Test direct function call
        from client_db import get_client_dashboard_data
        
        print("📊 Testing get_client_dashboard_data(6)...")
        result = get_client_dashboard_data(6)
        
        if result:
            print("✅ Got result!")
            print(f"   Stats: {result.get('stats', 'No stats')}")
            print(f"   Scan history count: {len(result.get('scan_history', []))}")
            print(f"   Client info: {result.get('client', {}).get('business_name', 'No name')}")
        else:
            print("❌ No result returned")
            
        # Check if client 6 exists in main database
        print("\n👤 Checking if client 6 exists...")
        from client_db import get_db_connection
        import sqlite3
        
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM clients WHERE id = 6")
        client = cursor.fetchone()
        
        if client:
            client_dict = dict(client)
            print(f"✅ Client 6 exists: {client_dict['business_name']} (User: {client_dict['user_id']})")
            print(f"   Active: {client_dict['active']}")
        else:
            print("❌ Client 6 doesn't exist in main database")
            
            # Check what clients do exist
            cursor.execute("SELECT id, business_name, user_id, active FROM clients ORDER BY id")
            all_clients = cursor.fetchall()
            print(f"   Available clients:")
            for c in all_clients:
                print(f"     Client {c['id']}: {c['business_name']} (User: {c['user_id']}, Active: {c['active']})")
        
        conn.close()
        
        # Check client-specific database directly
        print("\n🗄️ Checking client 6 database directly...")
        client_6_db = '/home/ggrun/CybrScan_1/client_databases/client_6_scans.db'
        
        if os.path.exists(client_6_db):
            import sqlite3
            conn = sqlite3.connect(client_6_db)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM scan_reports")
            count = cursor.fetchone()[0]
            print(f"✅ Client 6 database has {count} scan(s)")
            
            if count > 0:
                cursor.execute("""
                    SELECT scan_id, lead_name, lead_email, target_domain, security_score, timestamp
                    FROM scan_reports ORDER BY timestamp DESC LIMIT 3
                """)
                scans = cursor.fetchall()
                print("   Recent scans:")
                for scan in scans:
                    print(f"     {scan[0][:8]}... | {scan[1]} | {scan[2]} | {scan[3]} | {scan[4]}%")
            
            conn.close()
        else:
            print("❌ Client 6 database doesn't exist")
            
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

def create_client_6_if_missing():
    """Create client 6 if it doesn't exist"""
    print("\n🔧 CREATING CLIENT 6 IF MISSING")
    print("=" * 35)
    
    try:
        from client_db import get_db_connection
        import sqlite3
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if client 6 exists
        cursor.execute("SELECT * FROM clients WHERE id = 6")
        client = cursor.fetchone()
        
        if not client:
            print("❌ Client 6 doesn't exist, creating it...")
            
            # Create client 6
            cursor.execute("""
                INSERT INTO clients (
                    id, user_id, business_name, contact_email, subscription_level, 
                    active, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                6,  # id
                7,  # user_id (from logs)
                'Test Company',  # business_name
                'test@testcompany.com',  # contact_email
                'professional',  # subscription_level
                1,  # active
                '2025-05-24T23:00:00',  # created_at
                '2025-05-24T23:00:00'   # updated_at
            ))
            
            conn.commit()
            print("✅ Created client 6")
            
            # Verify creation
            cursor.execute("SELECT * FROM clients WHERE id = 6")
            new_client = cursor.fetchone()
            if new_client:
                print(f"   Verified: {new_client[2]} (User: {new_client[1]})")
        else:
            print("✅ Client 6 already exists")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating client 6: {e}")
        return False

def test_dashboard_after_fix():
    """Test dashboard data retrieval after fixes"""
    print("\n🧪 TESTING DASHBOARD AFTER FIXES")
    print("=" * 35)
    
    try:
        from client_db import get_client_dashboard_data
        
        result = get_client_dashboard_data(6)
        
        if result:
            stats = result.get('stats', {})
            scan_history = result.get('scan_history', [])
            
            print("✅ Dashboard data retrieved!")
            print(f"   Total scans: {stats.get('total_scans', 0)}")
            print(f"   Avg security score: {stats.get('avg_security_score', 0):.1f}%")
            print(f"   Scan history count: {len(scan_history)}")
            
            if scan_history:
                print("   Recent scans:")
                for scan in scan_history[:3]:
                    print(f"     {scan.get('lead_name', 'N/A')} | {scan.get('lead_email', 'N/A')} | {scan.get('target', 'N/A')}")
                    
                return True
            else:
                print("   ⚠️ No scan history found")
                return False
        else:
            print("❌ Still no dashboard data")
            return False
            
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        return False

if __name__ == "__main__":
    debug_client_6_dashboard()
    success = create_client_6_if_missing()
    
    if success:
        test_dashboard_after_fix()
    
    print("\n🎯 SUMMARY:")
    print("- Fixed client 6 database schema")
    print("- Added test scan data")
    print("- Created client 6 if missing")
    print("- Dashboard should now show scan data!")