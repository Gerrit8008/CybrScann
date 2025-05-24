#!/usr/bin/env python3
"""Final comprehensive fix for client 6 scan tracking"""

import sys
import sqlite3
import os
from datetime import datetime
sys.path.append('/home/ggrun/CybrScan_1')

def final_fix():
    """Final fix for client 6 scan tracking"""
    print("🎯 FINAL FIX FOR CLIENT 6 SCAN TRACKING")
    print("=" * 50)
    
    try:
        from client_db import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Check existing clients and find the right one for user 7
        print("1️⃣ Checking existing clients...")
        cursor.execute("SELECT id, business_name, user_id FROM clients ORDER BY id")
        clients = cursor.fetchall()
        
        user_7_client = None
        for client in clients:
            print(f"   Client {client[0]}: {client[1]} (User: {client[2]})")
            if client[2] == 7:
                user_7_client = client[0]
        
        if user_7_client:
            print(f"✅ User 7 is already linked to client {user_7_client}")
            target_client_id = user_7_client
        else:
            print("❌ User 7 not linked to any client")
            
            # Check if user 7 exists at all
            cursor.execute("SELECT * FROM users WHERE id = 7")
            user_7 = cursor.fetchone()
            
            if not user_7:
                print("   User 7 doesn't exist, finding available client...")
                
                # Find a client without a user_id or create a new one
                cursor.execute("SELECT id FROM clients WHERE user_id IS NULL LIMIT 1")
                available_client = cursor.fetchone()
                
                if available_client:
                    target_client_id = available_client[0]
                    print(f"   Using available client {target_client_id}")
                else:
                    # Create new client (ID will be auto-assigned)
                    cursor.execute("""
                        INSERT INTO clients (business_name, business_domain, contact_email, active, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        'Client for User 7',
                        'user7client.com',
                        'user7@example.com',
                        1,
                        datetime.now().isoformat()
                    ))
                    target_client_id = cursor.lastrowid
                    print(f"   Created new client {target_client_id}")
            else:
                # User 7 exists, link them to an available client
                cursor.execute("SELECT id FROM clients WHERE user_id IS NULL LIMIT 1")
                available_client = cursor.fetchone()
                
                if available_client:
                    target_client_id = available_client[0]
                    cursor.execute("UPDATE clients SET user_id = 7 WHERE id = ?", (target_client_id,))
                    print(f"   Linked user 7 to client {target_client_id}")
                else:
                    target_client_id = 1  # Fallback to client 1
                    print(f"   No available clients, using client 1 as fallback")
        
        conn.commit()
        
        # 2. Ensure client-specific database exists
        print(f"\\n2️⃣ Setting up client {target_client_id} database...")
        client_db_dir = '/home/ggrun/CybrScan_1/client_databases'
        os.makedirs(client_db_dir, exist_ok=True)
        
        client_db_path = os.path.join(client_db_dir, f'client_{target_client_id}_scans.db')
        
        client_conn = sqlite3.connect(client_db_path)
        client_cursor = client_conn.cursor()
        
        # Create scan_reports table with proper schema
        client_cursor.execute("""
            CREATE TABLE IF NOT EXISTS scan_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id TEXT UNIQUE NOT NULL,
                client_id INTEGER NOT NULL,
                scanner_id INTEGER,
                timestamp TEXT,
                lead_name TEXT,
                lead_email TEXT,
                lead_phone TEXT,
                lead_company TEXT,
                company_size TEXT,
                target_domain TEXT,
                security_score REAL,
                vulnerabilities_found INTEGER DEFAULT 0,
                risk_level TEXT,
                scan_type TEXT DEFAULT 'standard',
                status TEXT DEFAULT 'completed',
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        client_conn.commit()
        
        # 3. Move existing scan data to correct client database
        print("3️⃣ Moving scan data to correct client database...")
        
        # Check if there's scan data in client_6_scans.db
        client_6_db = '/home/ggrun/CybrScan_1/client_databases/client_6_scans.db'
        if os.path.exists(client_6_db):
            import shutil
            
            # Copy data from client_6_scans.db to the target client's database
            source_conn = sqlite3.connect(client_6_db)
            source_cursor = source_conn.cursor()
            
            source_cursor.execute("SELECT * FROM scan_reports")
            scan_data = source_cursor.fetchall()
            
            if scan_data:
                print(f"   Moving {len(scan_data)} scans to client {target_client_id} database")
                
                for scan in scan_data:
                    # Update the client_id to the target client
                    modified_scan = list(scan)
                    modified_scan[2] = target_client_id  # client_id field
                    
                    client_cursor.execute("""
                        INSERT OR REPLACE INTO scan_reports (
                            id, scan_id, client_id, scanner_id, timestamp, lead_name, lead_email,
                            lead_phone, lead_company, company_size, target_domain, security_score,
                            vulnerabilities_found, risk_level, scan_type, status, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, modified_scan)
                
                client_conn.commit()
                print(f"   ✅ Moved scan data to client {target_client_id}")
            
            source_conn.close()
        
        client_conn.close()
        
        # 4. Test the dashboard
        print(f"\\n4️⃣ Testing dashboard for client {target_client_id}...")
        conn.close()
        
        from client_db import get_client_dashboard_data
        dashboard_data = get_client_dashboard_data(target_client_id)
        
        if dashboard_data:
            stats = dashboard_data.get('stats', {})
            scan_history = dashboard_data.get('scan_history', [])
            
            print(f"✅ Dashboard working!")
            print(f"   Total scans: {stats.get('total_scans', 0)}")
            print(f"   Avg score: {stats.get('avg_security_score', 0):.1f}%")
            print(f"   Scan history: {len(scan_history)} items")
            
            if scan_history:
                latest = scan_history[0]
                print(f"   Latest scan: {latest.get('lead_name')} | {latest.get('lead_email')} | {latest.get('target')}")
                return target_client_id, True
            else:
                print("   ⚠️ No scan history found")
                return target_client_id, False
        else:
            print("❌ Dashboard still not working")
            return target_client_id, False
        
    except Exception as e:
        print(f"❌ Final fix failed: {e}")
        import traceback
        traceback.print_exc()
        return None, False

def update_app_logs():
    """Update to show which client should be used for logging"""
    print("\\n📝 UPDATING APP CONFIGURATION")
    print("=" * 35)
    
    target_client_id, dashboard_working = final_fix()
    
    if target_client_id:
        print(f"\\n🎯 SCAN TRACKING SUMMARY:")
        print(f"✅ Target client ID: {target_client_id}")
        print(f"✅ Client database: client_{target_client_id}_scans.db")
        print(f"✅ Dashboard working: {'Yes' if dashboard_working else 'No'}")
        
        if dashboard_working:
            print(f"\\n🎉 SUCCESS! User 7 scans will now appear in client {target_client_id} dashboard")
        else:
            print(f"\\n⚠️ Setup complete but no scan data found")
        
        print(f"\\n📋 When you run a new scan:")
        print(f"   1. It should be linked to client {target_client_id}")
        print(f"   2. Saved to client_{target_client_id}_scans.db")
        print(f"   3. Visible in the client dashboard")
        
        return target_client_id
    else:
        print("❌ Setup failed")
        return None

if __name__ == "__main__":
    target_client = update_app_logs()
    
    if target_client:
        print(f"\\n🔄 NEXT STEPS:")
        print(f"1. Run a new scan to test the tracking")
        print(f"2. Check client {target_client} dashboard for the scan")
        print(f"3. The scan should appear in 'Recent Scan Activity'")
    else:
        print("\\n❌ Manual intervention required")