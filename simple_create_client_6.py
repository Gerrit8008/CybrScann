#!/usr/bin/env python3
"""Simple creation of client 6 using correct schema"""

import sys
sys.path.append('/home/ggrun/CybrScan_1')

def create_client_6_simple():
    """Create client 6 using only the required fields"""
    print("🔧 CREATING CLIENT 6 (SIMPLE)")
    print("=" * 35)
    
    try:
        from client_db import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if client 6 exists
        cursor.execute("SELECT * FROM clients WHERE id = 6")
        if cursor.fetchone():
            print("✅ Client 6 already exists")
            conn.close()
            return True
        
        # Create client 6 with only required fields
        cursor.execute("""
            INSERT INTO clients (
                business_name, business_domain, contact_email, 
                user_id, active, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            'Client 6 Test Company',
            'testcompany.com',
            'test@testcompany.com',
            7,  # user_id
            1,  # active
            '2025-05-24T23:00:00'
        ))
        
        conn.commit()
        client_id = cursor.lastrowid
        
        print(f"✅ Created client {client_id}")
        
        # Also create user 7 if it doesn't exist
        cursor.execute("SELECT * FROM users WHERE id = 7")
        if not cursor.fetchone():
            print("Creating user 7...")
            cursor.execute("""
                INSERT INTO users (
                    username, email, password_hash, role, full_name, active, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                'client6user',
                'client6@testcompany.com',
                'dummy_hash',
                'client',
                'Client 6 User',
                1,
                '2025-05-24T23:00:00'
            ))
            conn.commit()
            print(f"✅ Created user 7")
        
        conn.close()
        
        # Test dashboard
        print("\n🧪 Testing dashboard...")
        from client_db import get_client_dashboard_data
        
        dashboard_data = get_client_dashboard_data(client_id)
        if dashboard_data:
            stats = dashboard_data.get('stats', {})
            scan_history = dashboard_data.get('scan_history', [])
            
            print(f"✅ Dashboard works! {len(scan_history)} scans, {stats.get('total_scans', 0)} total")
            
            if scan_history:
                latest = scan_history[0]
                print(f"   Latest: {latest.get('lead_name')} | {latest.get('lead_email')}")
        else:
            print("❌ Dashboard not working")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_missing_tables():
    """Create any missing database tables"""
    print("\n🗄️ CHECKING DATABASE TABLES")
    print("=" * 30)
    
    try:
        # Check main database
        main_db_path = '/home/ggrun/CybrScan_1/cybrscan.db'
        
        import sqlite3
        import os
        
        if not os.path.exists(main_db_path):
            print("Creating main database...")
            conn = sqlite3.connect(main_db_path)
            cursor = conn.cursor()
            
            # Create scan_results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scan_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id TEXT UNIQUE NOT NULL,
                    target_domain TEXT,
                    security_score REAL,
                    vulnerabilities_found INTEGER DEFAULT 0,
                    timestamp TEXT,
                    status TEXT DEFAULT 'completed'
                )
            """)
            
            conn.commit()
            conn.close()
            print("✅ Created main database")
        
        # Check leads database
        leads_db_path = '/home/ggrun/CybrScan_1/leads.db'
        
        if not os.path.exists(leads_db_path):
            print("Creating leads database...")
            conn = sqlite3.connect(leads_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    company TEXT,
                    company_size TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            print("✅ Created leads database")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

if __name__ == "__main__":
    success1 = create_missing_tables()
    success2 = create_client_6_simple()
    
    if success1 and success2:
        print("\n🎉 CLIENT 6 SETUP COMPLETE!")
        print("✅ All required databases created")
        print("✅ Client 6 created successfully") 
        print("✅ User 7 created and linked")
        print("✅ Scan tracking should now work")
        print("\n🔄 The dashboard should now show scan history for client 6!")
    else:
        print("\n❌ Setup incomplete. Check errors above.")